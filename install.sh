#!/bin/bash

# エラーが発生した場合即座に終了
set -e

echo "Timecard System Installer"
echo "========================"

# 必要なパッケージのインストール
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-yaml libusb-1.0-0-dev

# Python パッケージのインストール
echo "Installing Python packages..."
sudo pip3 install nfcpy gspread oauth2client

# アプリケーションディレクトリの作成
sudo mkdir -p /opt/timecard/src
sudo mkdir -p /etc/timecard

# ソースファイルのコピー
sudo cp src/* /opt/timecard/src/
sudo cp config/* /etc/timecard/

# 実行権限の付与
sudo chmod +x /opt/timecard/src/main.py

# systemdサービスの設定
sudo cp systemd/timecard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable timecard
sudo systemctl start timecard

echo "Installation completed successfully!"
echo "Please make sure to:"
echo "1. Place your Google API credentials in /etc/timecard/credentials.json"
echo "2. Update the configuration in /etc/timecard/config.yaml if needed"
echo "3. Restart the system to ensure everything works properly"