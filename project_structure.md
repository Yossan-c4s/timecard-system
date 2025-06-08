timecard-system/
├── install.sh                    # インストールスクリプト
├── config/
│   ├── config.yaml.template     # 設定ファイルテンプレート
│   └── nfc.rules               # NFCリーダーのudevルール
├── src/
│   ├── main.py                 # メインプログラム
│   ├── nfc_reader.py          # NFCリーダー制御
│   ├── spreadsheet.py         # Spreadsheet操作
│   └── utils.py               # ユーティリティ関数
├── systemd/
│   └── timecard.service       # systemdサービス定義
└── README.md                  # 詳細な導入手順書