#!/bin/bash

# プロジェクトディレクトリの作成
mkdir -p timecard-system/{src,config,systemd}

# 必要なファイルを作成
touch timecard-system/src/{main.py,nfc_reader.py,spreadsheet.py,utils.py}
touch timecard-system/config/{config.yaml.template,nfc.rules}
touch timecard-system/systemd/timecard.service
touch timecard-system/{install.sh,README.md}

# 実行権限の付与
chmod +x timecard-system/install.sh