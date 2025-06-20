# Timecard System (SPI版 SSD1306 OLED対応)

NFCカードリーダー＋Google Spreadsheet＋SSD1306 OLED（SPI接続）による入退室管理システム

---

## 機能概要

- NFCカードタッチで入退室判定・Google Spreadsheet記録
- 入退室音再生（PulseAudio経由）
- OLED（SSD1306 SPI接続）に「ユーザー名＆入退室状態」表示
- 電源ONで自動起動（systemdサービス）

---

## ディレクトリ構成

```
timecard-system/
├── README.md
├── install.sh
├── requirements.txt
├── tree.txt
├── src/
│   ├── main.py
│   ├── audio_player.py
│   └── oled_display.py
├── config/
│   ├── config.yaml.template
│   ├── entrance.wav
│   ├── exit.wav
│   └── nfc.rules
└── .gitignore
```

---

## ハードウェア構成

- Raspberry Pi 4/5
- SONY RC-S380/S NFCリーダー
- SSD1306 OLEDディスプレイ（SPIモデル 128x64など）
- スピーカー（USB/HDMI/3.5mm）
- 必要に応じてジャンパワイヤ

---

### SSD1306 SPI接続例（Raspberry Pi 40ピン）

| OLED端子      | Raspberry Pi端子名 | ピン番号 | GPIO番号 |
|:-------------:|:------------------:|:--------:|:--------:|
| VCC           | 3.3V               | 1        |          |
| GND           | GND                | 6        |          |
| DIN (MOSI)    | MOSI               | 19       | GPIO10   |
| CLK           | SCLK               | 23       | GPIO11   |
| CS            | CE0                | 24       | GPIO8    |
| DC            | GPIO25             | 22       | GPIO25   |
| RES (RST)     | GPIO24             | 18       | GPIO24   |

- DC（D/C）: GPIO25ピン（22番）
- RES（RST）: GPIO24ピン（18番）
- CS: CE0(GPIO8)推奨

---

## セットアップ手順

### 1. システム準備

```bash
sudo apt update
sudo apt upgrade -y
sudo raspi-config   # → Interface Options > SPI → 有効 (Enable)
sudo reboot
```

### 2. Google Cloud Platform設定

（略：サービスアカウント・API有効化・credentials.json用意）

### 3. リポジトリクローン＆インストール

```bash
git clone https://github.com/Yossan-c4s/timecard-system.git
cd timecard-system
sudo ./install.sh
```

### 4. Google認証情報の配置

```bash
sudo cp ~/Downloads/credentials.json /etc/timecard/credentials.json
sudo chmod 600 /etc/timecard/credentials.json
```

### 5. 設定ファイル編集

```bash
sudo cp config/config.yaml.template /etc/timecard/config.yaml
sudo nano /etc/timecard/config.yaml
```
例：
```yaml
nfc:
  port: "usb:1:3"
  min_interval: 1.5

spreadsheet:
  credentials_path: "/etc/timecard/credentials.json"
  sheet_name: "Timecard Records"

audio:
  entrance_sound: "/opt/timecard/sounds/entrance.wav"
  exit_sound: "/opt/timecard/sounds/exit.wav"

oled:
  spi_port: 0
  spi_device: 0
  gpio_dc: 25
  gpio_rst: 24
```

### 6. systemdサービスによる自動起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable timecard
sudo systemctl start timecard
```

---

## OLED表示内容

- カードタッチ時「ユーザー名」と「[on work]/[off work]」をOLEDに表示

---

## トラブルシューティング

- OLEDが映らない場合：配線、SPI有効化、configのgpio番号やSPI番号を再確認
- 音声が出ない場合：`paplay`で鳴るかテスト、pulseaudio経由での再生
- サービスが起動しない：`journalctl -u timecard -f`でログ確認

---

## ライセンス

MIT License

---