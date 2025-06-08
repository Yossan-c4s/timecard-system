#!/usr/bin/env python3
import time
import yaml
import logging
from nfc_reader import NFCReader
from spreadsheet import SpreadsheetManager
from audio_player import AudioPlayer
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/timecard/timecard.log'),
        logging.StreamHandler()
    ]
)

class TimecardSystem:
    def __init__(self):
        with open('/etc/timecard/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.spreadsheet = SpreadsheetManager(
            self.config['spreadsheet']['credentials_path'],
            self.config['spreadsheet']['sheet_name']
        )
        
        # NFCリーダーの初期化（最小間隔を1.5秒に設定）
        self.reader = NFCReader(
            self.config['nfc']['port'],
            'timecard',
            min_interval=1.5
        )
        
        # 音声プレーヤーの初期化
        self.audio = AudioPlayer(self.config['audio'])

    def run(self):
        logging.info("Starting Timecard System")
        
        while True:
            try:
                # カードの読み取り
                card_id = self.reader.read_card()
                if card_id:
                    # スプレッドシートの処理
                    result = self.spreadsheet.process_card(card_id)
                    if result:
                        action = result.get('action')
                        if action:
                            # 音声の再生
                            self.audio.play(action)
                            logging.info(f"処理完了: {card_id} - {action}")
                    else:
                        logging.warning(f"処理失敗: {card_id}")

                time.sleep(0.1)  # CPU負荷軽減

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                time.sleep(1)

if __name__ == "__main__":
    system = TimecardSystem()
    system.run()
