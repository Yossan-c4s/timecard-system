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

# 現在のディレクトリのパスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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
    build-essential \
    python3-pygame

echo "Step 2: Creating Python virtual environment..."
VENV_DIR="/opt/timecard/venv"
python3 -m venv "$VENV_DIR"

echo "Step 3: Installing Python packages..."
if [ $BREAK_SYSTEM_PACKAGES -eq 1 ]; then
    "$VENV_DIR/bin/pip3" install --break-system-packages -r "$SCRIPT_DIR/requirements.txt"
else
    "$VENV_DIR/bin/pip3" install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Step 4: Creating application directories..."
mkdir -p /opt/timecard/{src,sounds}
mkdir -p /etc/timecard
mkdir -p /var/log/timecard

echo "Step 5: Backing up existing configuration..."
if [ -d "/opt/timecard/src" ]; then
    cp -r /opt/timecard/src/* "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d "/etc/timecard" ]; then
    cp -r /etc/timecard/* "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "Step 6: Copying files..."
# ソースファイルのコピー
cp "$SCRIPT_DIR/src"/* /opt/timecard/src/

# 設定ファイルのコピー
cp "$SCRIPT_DIR/config/config.yaml.template" /etc/timecard/config.yaml
cp "$SCRIPT_DIR/config/nfc.rules" /etc/udev/rules.d/99-nfc.rules

# 音声ファイルのコピー
cp "$SCRIPT_DIR/config/entrance.wav" /opt/timecard/sounds/
cp "$SCRIPT_DIR/config/exit.wav" /opt/timecard/sounds/

echo "Step 7: Creating Python wrapper script..."
cat > /opt/timecard/src/timecard_wrapper.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=/opt/timecard/src
source /opt/timecard/venv/bin/activate
exec python3 /opt/timecard/src/main.py "$@"
EOF

chmod +x /opt/timecard/src/timecard_wrapper.sh
chmod +x /opt/timecard/src/main.py

echo "Step 8: Setting up permissions..."
chown -R root:root /opt/timecard
chown -R root:root /etc/timecard
chown -R root:root /var/log/timecard
chmod 755 /opt/timecard
chmod 755 /etc/timecard
chmod 755 /var/log/timecard
chmod 755 /opt/timecard/sounds
chmod 644 /opt/timecard/sounds/*.wav
touch /var/log/timecard/timecard.log
chmod 644 /var/log/timecard/timecard.log
chmod 600 /etc/timecard/credentials.json || true
chmod 644 /etc/timecard/config.yaml

echo "Step 9: Setting up udev rules..."
udevadm control --reload-rules
udevadm trigger

echo "Step 10: Setting up systemd service..."
cat > /etc/systemd/system/timecard.service << 'EOF'
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

systemctl daemon-reload
systemctl enable timecard

echo "Installation completed successfully!"
echo "Backup of previous installation (if any) is stored in: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Place your Google API credentials in /etc/timecard/credentials.json"
echo "2. Update the configuration in /etc/timecard/config.yaml if needed"
echo "3. Start the service with: systemctl start timecard"