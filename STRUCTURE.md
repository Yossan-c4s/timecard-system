# Timecard System - Project Structure

```bash
timecard-system/
├── .github/                        # GitHub関連ファイル
│   └── workflows/                  # GitHub Actions ワークフロー
│       └── pytest.yml             # テスト自動化設定
├── src/                           # ソースコード
│   ├── __init__.py
│   ├── main.py                    # メインアプリケーション
│   ├── nfc_reader.py             # NFCリーダー制御
│   ├── spreadsheet.py            # スプレッドシート操作
│   └── utils.py                  # ユーティリティ関数
├── config/                        # 設定ファイル
│   ├── config.yaml.template      # 設定テンプレート
│   └── nfc.rules                # NFCデバイスルール
├── systemd/                       # Systemd関連
│   └── timecard.service         # サービス定義
├── tests/                        # テストコード
│   ├── __init__.py
│   ├── test_nfc_reader.py
│   ├── test_spreadsheet.py
│   └── test_utils.py
├── docs/                         # ドキュメント
│   ├── images/                   # 画像ファイル
│   │   ├── system_overview.png
│   │   └── spreadsheet_structure.png
│   ├── API.md                    # API仕様
│   ├── DEVELOPMENT.md           # 開発者向けガイド
│   └── TROUBLESHOOTING.md      # トラブルシューティング
├── .gitignore                    # Git除外設定
├── LICENSE                       # ライセンス
├── README.md                    # メインドキュメント
├── STRUCTURE.md                 # プロジェクト構造説明
├── install.sh                   # インストールスクリプト
├── requirements.txt            # Python依存パッケージ
└── setup.py                    # パッケージング設定