# timecard_felica_Rspi5
# Timecard System 導入手順書

## 1. 前提条件
- Raspberry Pi 5 (Raspberry Pi OS インストール済み)
- WiFi設定済み
- SONY RC-S380/S × 2台
- Google アカウント（Spreadsheetへのアクセス用）

## 2. Google API設定
1. Google Cloud Platformにアクセス
2. 新規プロジェクトを作成
3. Google Sheets APIを有効化
4. サービスアカウントを作成
5. JSONキーをダウンロード
6. Google Spreadsheetを作成し、サービスアカウントとの共有設定を行う

## 3. システムのインストール
1. ソースコードをダウンロード:
```bash
git clone https://[repository-url]/timecard-system.git
cd timecard-system
```

2. Google API認証情報の配置:
- ダウンロードしたJSONキーを`config/credentials.json`として配置

3. インストールの実行:
```bash
sudo ./install.sh
```

## 4. 設定の確認と調整
1. `/etc/timecard/config.yaml`の確認
   - NFCリーダーのポート設定
   - Spreadsheetの名前

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

## 6. 運用管理
- Spreadsheetの確認
- 定期的なログの確認
- システムの再起動方法
```bash
sudo systemctl restart timecard
```

## サポート
問題が発生した場合は、以下のログを確認してください：
- システムログ: `/var/log/timecard.log`
- systemdログ: `journalctl -u timecard`
