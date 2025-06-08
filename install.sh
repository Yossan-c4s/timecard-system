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
    "$VENV_DIR/bin/pip3" install --break-system-packages nfcpy gspread oauth2client pyyaml
else
    echo "Installing packages in virtual environment..."
    "$VENV_DIR/bin/pip3" install nfcpy gspread oauth2client pyyaml
fi

echo "Step 4: Creating application directories..."
mkdir -p /opt/timecard/src
mkdir -p /etc/timecard
mkdir -p /var/log/timecard

echo "Step 5: Backing up existing configuration..."
if [ -d "/opt/timecard/src" ]; then
    cp -r /opt/timecard/src/* "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -d "/etc/timecard" ]; then
    cp -r /etc/timecard/* "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "Step 6: Copying new files..."
cp src/* /opt/timecard/src/
cp config/config.yaml.template /etc/timecard/config.yaml
cp config/nfc.rules /etc/udev/rules.d/99-nfc.rules

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
touch /var/log/timecard/timecard.log
chmod 644 /var/log/timecard/timecard.log
chmod 600 /etc/timecard/credentials.json || true
chmod 644 /etc/timecard/config.yaml

echo "Step 9: Setting up udev rules..."
udevadm control --reload-rules
udevadm trigger

echo "Step 10: Setting up systemd service..."
cp systemd/timecard.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable timecard

echo "Installation completed successfully!"
echo "Backup of previous installation (if any) is stored in: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Follow the README.md instructions to set up Google Cloud Platform"
echo "2. Place your Google API credentials in /etc/timecard/credentials.json"
echo "3. Set up the Google Spreadsheet with required sheets (Records, Users, Status)"
echo "4. Update the configuration in /etc/timecard/config.yaml"
echo "5. Start the service with: systemctl start timecard"