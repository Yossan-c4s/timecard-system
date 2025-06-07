import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

class SpreadsheetManager:
    def __init__(self, credentials_path, sheet_name):
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, 
            scope
        )
        
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open(sheet_name).sheet1

    def append_record(self, row_data):
        try:
            self.sheet.append_row(row_data)
            logging.info(f"Successfully recorded: {row_data}")
        except Exception as e:
            logging.error(f"Error recording to spreadsheet: {e}")