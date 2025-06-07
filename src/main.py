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
        logging.FileHandler('/var/log/timecard.log'),
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
                    self.record_time(card_id, "入室")

                # 退室リーダーの監視
                card_id = self.exit_reader.read_card()
                if card_id:
                    self.record_time(card_id, "退室")

                time.sleep(0.1)

            except Exception as e:
                logging.error(f"Error occurred: {e}")
                time.sleep(1)

    def record_time(self, card_id, action):
        now = datetime.now()
        logging.info(f"Card {card_id} detected: {action} at {now}")
        self.spreadsheet.append_record([
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            card_id,
            action
        ])

if __name__ == "__main__":
    system = TimecardSystem()
    system.run()