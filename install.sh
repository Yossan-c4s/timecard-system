#!/bin/bash

set -e

echo "Timecard System Installer (SSD1306 SPI版)"
echo "========================"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Step 1: Installing system packages..."
apt-get update
apt-get install -y \
    python3-pip \
    python3-venv \
    python3-yaml \
    libusb-1.0-0-dev \
    python3-dev \
    build-essential \
    python3-pygame \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    python3-pil \
    python3-setuptools \
    python3-spidev \
    i2c-tools \
    fonts-noto-cjk

echo "Step 2: Creating Python virtual environment..."
VENV_DIR="/opt/timecard/venv"
python3 -m venv "$VENV_DIR"

echo "Step 3: Installing Python packages..."
source "$VENV_DIR/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Step 4: Creating application directories..."
mkdir -p /opt/timecard/{src,sounds}
mkdir -p /etc/timecard
mkdir -p /var/log/timecard

echo "Step 5: Copying config and sound files..."
cp -n "$SCRIPT_DIR/config/config.yaml.template" /etc/timecard/config.yaml || true
cp -n "$SCRIPT_DIR/config/entrance.wav" /opt/timecard/sounds/ || true
cp -n "$SCRIPT_DIR/config/exit.wav" /opt/timecard/sounds/ || true
cp "$SCRIPT_DIR/config/nfc.rules" /etc/udev/rules.d/99-nfc.rules

echo "Step 6: Installing sources..."
cp "$SCRIPT_DIR/src/"*.py /opt/timecard/src/

echo "Step 7: Creating Python wrapper script..."
cat > /opt/timecard/src/timecard_wrapper.sh << 'EOF'
#!/bin/bash
export PYTHONPATH=/opt/timecard/src
source /opt/timecard/venv/bin/activate
exec python3 /opt/timecard/src/main.py "$@"
EOF

chmod +x /opt/timecard/src/timecard_wrapper.sh
chmod +x /opt/timecard/src/main.py

echo "Step 8: Setting up systemd service..."
cat > /etc/systemd/system/timecard.service << 'EOF'
[Unit]
Description=Timecard System Service
After=network.target

[Service]
ExecStart=/opt/timecard/src/timecard_wrapper.sh
WorkingDirectory=/opt/timecard
User=pi
Group=pi
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable timecard

echo "Step 9: Setting up audio..."
aplay -l

echo "Installation completed successfully!"
echo "1. Place your Google API credentials in /etc/timecard/credentials.json"
echo "2. Update config in /etc/timecard/config.yaml"
echo "3. Enable SPI (raspi-config), then reboot if not yet done."
echo "4. Test audio: paplay /opt/timecard/sounds/entrance.wav"
echo "5. Start service: sudo systemctl start timecard"