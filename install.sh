#!/bin/bash

# エラーが発生した場合即座に終了
set -e

echo "Timecard System Installer"
echo "========================"

# ヘルプ関数
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --break-system-packages    Force install Python packages even if it might break system packages"
    echo "  --help                     Show this help message"
}

# コマンドライン引数の解析
BREAK_SYSTEM_PACKAGES=0
for arg in "$@"; do
    case $arg in
        --break-system-packages)
            BREAK_SYSTEM_PACKAGES=1
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            show_help
            exit 1
            ;;
    esac
done

# sudo権限のチェック
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# バックアップディレクトリの作成
BACKUP_DIR="/opt/timecard/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Step 1: Installing system packages..."
apt-get update
apt-get install -y \
    python3-pip \
    python3-venv \
    python3-yaml \
    libusb-1.0-0-dev \
    python3-dev \
    build-essential

echo "Step 2: Creating Python virtual environment..."
VENV_DIR="/opt/timecard/venv"
python3 -m venv "$VENV_DIR"

echo "Step 3: Installing Python packages..."
if [ $BREAK_SYSTEM_PACKAGES -eq 1 ]; then
    echo "Installing packages with --break-system-packages flag..."
    "$VENV_DIR/bin/pip3" install --break-system-packages nfcpy gspread oauth2client
else
    echo "Installing packages in virtual environment..."
    "$VENV_DIR/bin/pip3" install nfcpy gspread oauth2client
fi

echo "Step 4: Creating application directories..."
mkdir -p /opt/timecard/src
mkdir -p /etc/timecard

echo "Step 5: Backing up existing configuration..."
if [ -d "/opt/timecard/src" ]; then
    cp -r /opt/timecard/src/* "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d "/etc/timecard" ]; then
    cp -r /etc/timecard/* "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "Step 6: Copying new files..."
cp src/* /opt/timecard/src/
cp config/* /etc/timecard/

# Pythonスクリプトの実行ファイルのラッパーを作成
echo "Step 7: Creating Python wrapper script..."
cat > /opt/timecard/src/timecard_wrapper.sh << 'EOF'
#!/bin/bash
source /opt/timecard/venv/bin/activate
exec python3 /opt/timecard/src/main.py "$@"
EOF

chmod +x /opt/timecard/src/timecard_wrapper.sh
chmod +x /opt/timecard/src/main.py

echo "Step 8: Setting up systemd service..."
cat > /etc/systemd/system/timecard.service << EOF
[Unit]
Description=Timecard System Service
After=network.target

[Service]
ExecStart=/opt/timecard/src/timecard_wrapper.sh
WorkingDirectory=/opt/timecard
User=root
Group=root
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "Step 9: Setting up permissions..."
chown -R root:root /opt/timecard
chown -R root:root /etc/timecard
chmod 755 /opt/timecard
chmod 755 /etc/timecard

echo "Step 10: Enabling and starting service..."
systemctl daemon-reload
systemctl enable timecard
systemctl start timecard

echo "Installation completed successfully!"
echo "Backup of previous installation (if any) is stored in: $BACKUP_DIR"
echo ""
echo "Please ensure to:"
echo "1. Place your Google API credentials in /etc/timecard/credentials.json"
echo "2. Update the configuration in /etc/timecard/config.yaml if needed"
echo "3. Check the service status with: systemctl status timecard"
echo ""
echo "If you experience any issues with nfcpy installation, run:"
echo "sudo $0 --break-system-packages"
