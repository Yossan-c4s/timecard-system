# Timecard System 導入手順書

## 1. システム要件
- Raspberry Pi 5
- Raspberry Pi OS (最新版)
- SONY RC-S380/S × 2台
- インターネット接続
- Google アカウント

## 2. 事前準備

### 2.1 Raspberry Pi の準備
1. Raspberry Pi OSのインストールと初期設定
2. ネットワーク設定
3. SSHの有効化（推奨）

### 2.2 Google Cloud Platform (GCP) の設定

#### 2.2.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成
   - 右上の「プロジェクトの選択」→「新しいプロジェクト」
   - プロジェクト名：「Timecard System」など
   - 「作成」をクリック

#### 2.2.2 必要なAPIの有効化
1. 左側メニュー →「APIとサービス」→「ライブラリ」
2. 以下のAPIを検索し、それぞれ「有効にする」をクリック：
   - Google Sheets API
   - Google Drive API
   ※ Drive APIの有効化は必須です

#### 2.2.3 サービスアカウントの作成
1. 左側メニュー →「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. 必要事項を入力：
   - サービスアカウント名：「timecard-service」など
   - 説明：任意
4. 「作成して続行」をクリック
5. 役割の設定：
   - 「基本」→「編集者」を選択
6. 「完了」をクリック

#### 2.2.4 認証情報のダウンロード
1. 作成したサービスアカウントをクリック
2. 「キー」タブ →「キーを追加」→「新しいキーを作成」
3. 「JSON」を選択してダウンロード

### 2.3 Google Spreadsheetの準備
1. [Google Spreadsheet](https://docs.google.com/spreadsheets) を開く
2. 新規スプレッドシートを作成
3. ファイル名を「Timecard Records」に変更
4. 以下の3つのシートを作成：
   
   a. Records（記録用）
   - ヘッダー: 日付, 時刻, カードID, ユーザー名, 所属部署, 個人ID, 動作
   
   b. Users（ユーザー管理用）
   - ヘッダー: カードID, ユーザー名, 所属部署, 個人ID
   
   c. Status（状態管理用）
   - ヘッダー: カードID, ユーザー名, 最終動作, 最終更新時刻

5. 共有設定：
   - 「共有」ボタンをクリック
   - サービスアカウントのメールアドレスを追加
   - 権限を「編集者」に設定
   - 「完了」をクリック

## 3. システムのインストール

### 3.1 ソースコードの取得
```bash
git clone https://github.com/Yossan-c4s/timecard-system
cd timecard-system
```

### 3.2 インストールの実行
```bash
# 通常インストール
sudo ./install.sh

# または、パッケージの競合がある場合
sudo ./install.sh --break-system-packages
```

### 3.3 認証情報の設定
```bash
# Google Cloud Platformからダウンロードした認証情報を配置
sudo cp /path/to/downloaded/credentials.json /etc/timecard/credentials.json
sudo chmod 600 /etc/timecard/credentials.json
```

### 3.4 設定ファイルの編集
1. NFCリーダーのポート番号確認：
```bash
lsusb | grep "Sony"
# 出力例：
# Bus 001 Device 003: ID 054c:06c3 Sony Corp. RC-S380/S
# → この場合、ポート番号は "usb:1:3"
```

2. 設定ファイルの編集：
```bash
sudo nano /etc/timecard/config.yaml
```

```yaml
nfc:
  entrance_port: "usb:1:3"  # 1台目のリーダーのポート番号
  exit_port: "usb:1:4"     # 2台目のリーダーのポート番号

spreadsheet:
  credentials_path: "/etc/timecard/credentials.json"
  sheet_name: "Timecard Records"
```

### 3.5 ユーザー情報の登録
1. Usersシートを開く
2. 以下の形式でユーザー情報を入力：
   - カードID: NFCカードのID（16進数）
   - ユーザー名: 表示名
   - 所属部署: 部署名
   - 個人ID: 社員番号など

### 3.6 サービスの起動
```bash
sudo systemctl start timecard
sudo systemctl status timecard
```

## 4. 動作確認

### 4.1 ログの確認
```bash
# サービスのログを確認
sudo journalctl -u timecard -f

# アプリケーションログを確認
sudo tail -f /var/log/timecard/timecard.log
```

### 4.2 カードリーダーのテスト
1. 入室用リーダーにカードをタッチ
2. ログを確認
3. スプレッドシートの確認
   - Recordsシートに記録が追加されているか
   - Statusシートの状態が更新されているか
4. 退室用リーダーで同様のテストを実施

### 4.3 動作仕様の確認
- 異なるカードIDでの連続使用が可能
- 同一カードIDでの重複動作（連続入室/連続退室）は防止
- 未登録カードも記録可能（「未登録」として記録）

## 5. トラブルシューティング

### 5.1 一般的な問題と解決方法

1. サービスが起動しない場合：
```bash
# ログの確認
sudo journalctl -u timecard -n 50
# 設定ファイルの確認
sudo cat /etc/timecard/config.yaml
# 権限の確認
ls -l /etc/timecard/credentials.json
```

2. NFCリーダーが認識されない場合：
```bash
# デバイスの確認
lsusb | grep "Sony"
# udevルールの再読み込み
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. スプレッドシートに記録されない場合：
- Google Drive APIが有効化されているか確認
- 認証情報の正確性を確認
- スプレッドシートの共有設定を確認
- インターネット接続を確認

### 5.2 ログファイルの場所
- システムログ: `/var/log/timecard/timecard.log`
- Systemdログ: `journalctl -u timecard`

## 6. メンテナンス

### 6.1 定期的なチェック項目
1. ログファイルのローテーション
2. スプレッドシートのバックアップ
3. システムの動作確認
4. エラーログの確認

### 6.2 アップデート方法
```bash
cd /path/to/timecard-system
git pull
sudo ./install.sh
```

### 6.3 バックアップ
- 設定ファイル: `/etc/timecard/`
- 認証情報: `/etc/timecard/credentials.json`
- ログファイル: `/var/log/timecard/`

## 7. セキュリティ注意事項
1. credentials.jsonの権限は600に設定
2. 定期的なログの確認
3. アクセス権限の定期的な見直し
4. システムアップデートの適用

## サポート
問題が発生した場合は、以下の情報を確認の上、報告してください：
1. エラーメッセージ
2. システムのログ
3. 設定ファイルの内容（認証情報を除く）
4. 実行環境の詳細