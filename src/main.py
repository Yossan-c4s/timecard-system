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
        
        self.entrance_reader = NFCReader(
            self.config['nfc']['entrance_port'],
            'entrance'
        )
        self.exit_reader = NFCReader(
            self.config['nfc']['exit_port'],
            'exit'
        )

    def run(self):
        logging.info("Starting Timecard System")
        
        while True:
            try:
                # 入室リーダーの監視
                card_id = self.entrance_reader.read_card()
                if card_id:
                    if self.spreadsheet.process_entrance(card_id):
                        logging.info(f"入室処理完了: {card_id}")
                    else:
                        logging.warning(f"入室処理失敗: {card_id}")

                # 退室リーダーの監視
                card_id = self.exit_reader.read_card()
                if card_id:
                    if self.spreadsheet.process_exit(card_id):
                        logging.info(f"退室処理完了: {card_id}")
                    else:
                        logging.warning(f"退室処理失敗: {card_id}")

                time.sleep(0.1)

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                time.sleep(1)

if __name__ == "__main__":
    system = TimecardSystem()
    system.run()
