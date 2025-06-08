#!/usr/bin/env python3
import time
import yaml
import logging
from nfc_reader import NFCReader
from spreadsheet import SpreadsheetManager
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
        
        # 1台のNFCリーダーを使用
        self.reader = NFCReader(
            self.config['nfc']['port'],
            'timecard'
        )

    def run(self):
        logging.info("Starting Timecard System")
        
        while True:
            try:
                # カードの読み取り
                card_id = self.reader.read_card()
                if card_id:
                    if self.spreadsheet.process_card(card_id):
                        logging.info(f"処理完了: {card_id}")
                    else:
                        logging.warning(f"処理失敗: {card_id}")

                time.sleep(0.1)

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                time.sleep(1)

if __name__ == "__main__":
    system = TimecardSystem()
    system.run()
