# timecard_felica_Rspi5
# Timecard System 導入手順書

## 1. 前提条件
- Raspberry Pi 5 (Raspberry Pi OS インストール済み)
- WiFi設定済み
- SONY RC-S380/S × 2台
- Google アカウント（Spreadsheetへのアクセス用）

## 2. Google API設定の詳細手順

### 2.1 Google Cloud Platform (GCP) プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 右上のプロジェクト選択ドロップダウン → 「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例：「Timecard System」）
4. 「作成」をクリック

### 2.2 Google Sheets APIの有効化
1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーで「Google Sheets API」を検索
3. Google Sheets APIを選択し、「有効にする」をクリック

### 2.3 サービスアカウントの作成
1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウントの詳細を入力：
   - サービスアカウント名（例：「timecard-service」）
   - サービスアカウントID（自動生成）
   - 説明（任意）
4. 「作成して続行」をクリック
5. 役割の選択：
   - 「基本」→「編集者」を選択
6. 「完了」をクリック

### 2.4 JSONキーの作成とダウンロード
1. 作成したサービスアカウントの一覧から、該当のアカウントをクリック
2. 「キー」タブを選択
3. 「キーを追加」→「新しいキーを作成」→「JSON」を選択
4. JSONキーファイルが自動的にダウンロードされます
5. このファイルを`credentials.json`としてリネーム

### 2.5 Google Spreadsheetの設定
1. [Google Spreadsheet](https://docs.google.com/spreadsheets)を開く
2. 新規スプレッドシートを作成
3. スプレッドシートの名前を設定（例：「Timecard Records」）
4. シートの構成：
   - A列: 日付
   - B列: 時刻
   - C列: カードID
   - D列: 動作（入室/退室）
5. 共有設定：
   - 右上の「共有」ボタンをクリック
   - サービスアカウントのメールアドレス（`[アカウント名]@[プロジェクトID].iam.gserviceaccount.com`）を追加
   - 権限を「編集者」に設定
   - 「完了」をクリック

### 2.6 config.yamlの設定
1. `/etc/timecard/config.yaml`を編集：
```yaml
nfc:
  entrance_port: "usb:0:0"  # 入室用リーダーのポート
  exit_port: "usb:1:0"     # 退室用リーダーのポート

spreadsheet:
  credentials_path: "/etc/timecard/credentials.json"
  sheet_name: "Timecard Records"  # 作成したスプレッドシートの名前
```

## 3. システムのインストール
1. ソースコードをダウンロード:
```bash
git clone https://github.com/Yossan-c4s/timecard-system
cd timecard-system
```

2. Google API認証情報の配置:
```bash
sudo mkdir -p /etc/timecard
sudo cp /path/to/credentials.json /etc/timecard/
sudo chmod 600 /etc/timecard/credentials.json
```

3. インストールの実行:
```bash
sudo ./install.sh
```

## 4. 設定の確認と調整
1. `/etc/timecard/config.yaml`の確認
   - NFCリーダーのポート設定の確認方法：
     ```bash
     lsusb
     ```
     で表示されるデバイスIDを確認し、必要に応じて設定を変更
   - Spreadsheetの名前が正しいことを確認

2. 動作確認
```bash
sudo systemctl status timecard
```

## 5. トラブルシューティング
- ログの確認:
```bash
sudo journalctl -u timecard
```

- NFCリーダーの認識確認:
```bash
lsusb
```

- Google API接続のテスト:
```bash
sudo python3 -c "
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('/etc/timecard/credentials.json', scope)
client = gspread.authorize(creds)
print('Connection successful!')
"
```

## 6. 運用管理
- Spreadsheetの確認
  - データが正しく記録されているか定期的に確認
  - バックアップを定期的に作成することを推奨
- 定期的なログの確認
  - システムの健全性確認
  - エラーの早期発見
- システムの再起動方法
```bash
sudo systemctl restart timecard
```

## サポート
問題が発生した場合は、以下のログを確認してください：
- システムログ: `/var/log/timecard.log`
- systemdログ: `journalctl -u timecard`

### よくある問題と解決方法
1. スプレッドシートに記録されない
   - credentials.jsonの権限を確認
   - スプレッドシートの共有設定を確認
   - インターネット接続を確認

2. NFCリーダーが認識されない
   - USBポートの接続を確認
   - `lsusb`コマンドでデバイスの認識を確認
   - config.yamlのポート設定を確認

3. サービスが起動しない
   - `systemctl status timecard`で状態確認
   - ログファイルでエラーメッセージを確認
   - 必要なパッケージが全てインストールされているか確認
