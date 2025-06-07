timecard-system/
├── install.sh                 # インストールスクリプト
├── config/
│   ├── config.yaml           # 設定ファイル
│   └── credentials.json      # Google API認証情報
├── src/
│   ├── main.py              # メインプログラム
│   ├── nfc_reader.py        # NFCリーダー制御
│   ├── spreadsheet.py       # Spreadsheet操作
│   └── utils.py             # ユーティリティ関数
├── systemd/
│   └── timecard.service     # systemdサービス定義
└── README.md                # 導入手順書