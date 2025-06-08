# Timecard System

入退室管理システムは、NFCカードリーダーとGoogle Spreadsheetを使用して入退室を記録・管理するシステムです。

## システム要件

### ハードウェア
- Raspberry Pi 5
- SONY RC-S380/S (NFCリーダー) × 1台
- NFCカード（FeliCa規格対応）

### ソフトウェア
- Raspberry Pi OS (最新版)
- Python 3.7以上
- インターネット接続
- Google アカウント

## セットアップ手順

### 1. システムの準備
1. Raspberry Pi OSのインストールと初期設定
2. ネットワーク設定
3. SSHの有効化（推奨）

### 2. Google Cloud Platform (GCP) の設定

#### 2.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新規プロジェクトを作成
   - プロジェクト名：任意（例：「Timecard System」）
   - 「作成」をクリック

#### 2.2 APIの有効化
1. 左側メニュー →「APIとサービス」→「ライブラリ」
2. 以下のAPIを検索し有効化：
   - Google Sheets API
   - Google Drive API（必須）

#### 2.3 サービスアカウントの作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウントの設定：
   - 名前：任意（例：「timecard-service」）
   - 役割：編集者
4. 認証情報（JSON）のダウンロード

### 3. Google Spreadsheetの準備

#### 3.1 スプレッドシートの作成
1. [Google Spreadsheet](https://docs.google.com/spreadsheets)を開く
2. 新規スプレッドシート作成
3. ファイル名を設定（例：「Timecard Records」）

#### 3.2 シートの設定
以下の3つのシートを作成：

1. Records（記録シート）
   ```
   日付, 時刻, カードID, ユーザー名, 所属部署, 個人ID, 動作
   ```

2. Users（ユーザー管理シート）
   ```
   カードID, ユーザー名, 所属部署, 個人ID
   ```

3. Status（状態管理シート）
   ```
   カードID, ユーザー名, 現在の状態, 最終更新時刻
   ```

#### 3.3 共有設定
1. 「共有」ボタンをクリック
2. サービスアカウントのメールアドレスを追加
3. 権限を「編集者」に設定

### 4. システムのインストール

#### 4.1 リポジトリのクローン
```bash
git clone https://github.com/Yossan-c4s/timecard-system.git
cd timecard-system
```

#### 4.2 インストールの実行
```bash
# 通常インストール
sudo ./install.sh

# または、パッケージの競合がある場合
sudo ./install.sh --break-system-packages
```

#### 4.3 認証情報の設定
```bash
# Google Cloud Platformからダウンロードした認証情報を配置
sudo cp /path/to/downloaded/credentials.json /etc/timecard/credentials.json
sudo chmod 600 /etc/timecard/credentials.json
```

#### 4.4 設定ファイルの編集
1. NFCリーダーのポート番号確認：
```bash
lsusb | grep "Sony"
# 出力例：Bus 001 Device 003: ID 054c:06c3 Sony Corp. RC-S380/S
# → ポート番号は "usb:1:3"
```

2. 設定ファイルの編集：
```bash
sudo nano /etc/timecard/config.yaml
```

```yaml
nfc:
  port: "usb:1:3"  # NFCリーダーのポート番号
  min_interval: 1.5  # 最小読み取り間隔（秒）

spreadsheet:
  credentials_path: "/etc/timecard/credentials.json"
  sheet_name: "Timecard Records"  # 作成したスプレッドシート名

audio:
  entrance_sound: "/opt/timecard/sounds/entrance.wav"
  exit_sound: "/opt/timecard/sounds/exit.wav"
```

### 5. ユーザー情報の登録
1. Usersシートを開く
2. 以下の形式でユーザー情報を入力：
   - カードID: NFCカードのID（16進数）
   - ユーザー名: 表示名
   - 所属部署: 部署名
   - 個人ID: 社員番号など

### 6. システムの起動
```bash
sudo systemctl start timecard
sudo systemctl status timecard
```

## 動作確認

### 1. ログの確認
```bash
# サービスのログ
sudo journalctl -u timecard -f

# アプリケーションログ
sudo tail -f /var/log/timecard/timecard.log
```

### 2. カードリーダーの動作確認
1. カードをリーダーにタッチ
2. ログを確認
3. スプレッドシートの確認
   - Recordsシートに記録が追加されているか
   - Statusシートの状態が更新されているか

### 3. 動作仕様
- カードタッチごとに入室/退室状態が切り替わる
- 入室/退室時に音声フィードバック
- カードの連続読み取りは1.5秒以上の間隔が必要
- 未登録カードも記録可能（「未登録」として記録）

## トラブルシューティング

### よくある問題と解決方法

1. サービスが起動しない
```bash
# ログ確認
sudo journalctl -u timecard -n 50

# 設定確認
sudo cat /etc/timecard/config.yaml

# 権限確認
ls -l /etc/timecard/credentials.json
```

2. NFCリーダーが認識されない
```bash
# デバイス確認
lsusb | grep "Sony"

# udevルール再読み込み
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. スプレッドシートに記録されない
- Google Drive APIが有効か確認
- 認証情報の確認
- スプレッドシートの共有設定確認
- インターネット接続確認

## メンテナンス

### 更新方法
```bash
cd /path/to/timecard-system
git pull
sudo ./install.sh
```

### バックアップ対象
- `/etc/timecard/` - 設定ファイル
- `/etc/timecard/credentials.json` - 認証情報
- `/var/log/timecard/` - ログファイル

## セキュリティ注意事項
1. credentials.jsonの権限は600に設定
2. 定期的なログ確認
3. アクセス権限の定期的見直し
4. システムアップデートの適用

## サポート
問題発生時は以下の情報を添えて報告してください：
1. エラーメッセージ
2. システムログ
3. 設定ファイルの内容（認証情報を除く）
4. 実行環境の詳細

## ライセンス
MIT License

## 作者
Yossan-c4s

## 最終更新
2025-06-08 11:04:43 (UTC)