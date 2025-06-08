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
        self.spreadsheet = self.client.open(sheet_name)
        
        # シートの取得
        self.record_sheet = self.spreadsheet.worksheet('Records')
        self.user_sheet = self.spreadsheet.worksheet('Users')
        self.status_sheet = self.spreadsheet.worksheet('Status')
        
        # シートの初期化
        self._initialize_sheets()

    def _initialize_sheets(self):
        """シートの初期化とヘッダーの設定"""
        try:
            # Recordsシートのヘッダー確認
            if not self.record_sheet.row_values(1):
                self.record_sheet.append_row([
                    '日付', '時刻', 'カードID', 'ユーザー名', 
                    '所属部署', '個人ID', '動作'
                ])
            
            # Usersシートのヘッダー確認
            if not self.user_sheet.row_values(1):
                self.user_sheet.append_row([
                    'カードID', 'ユーザー名', '所属部署', '個人ID'
                ])
            
            # Statusシートのヘッダー確認
            if not self.status_sheet.row_values(1):
                self.status_sheet.append_row([
                    'カードID', 'ユーザー名', '現在の状態', '最終更新時刻'
                ])
                
        except Exception as e:
            logging.error(f"シートの初期化中にエラーが発生: {e}")
            raise

    def get_user_info(self, card_id):
        """カードIDに対応するユーザー情報を取得"""
        try:
            cell = self.user_sheet.find(card_id)
            if cell and cell.col == 1:  # カードIDは1列目
                row_values = self.user_sheet.row_values(cell.row)
                return {
                    'card_id': row_values[0],
                    'user_name': row_values[1],
                    'department': row_values[2],
                    'personal_id': row_values[3]
                }
            return None
        except Exception as e:
            logging.error(f"ユーザー情報の取得中にエラーが発生: {e}")
            return None

    def get_status(self, card_id):
        """カードIDの現在の入退室状態を取得"""
        try:
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                row_values = self.status_sheet.row_values(cell.row)
                return row_values[2]  # 現在の状態
            # Status未登録の場合は退室状態とみなす
            return "退室"
        except Exception as e:
            logging.error(f"状態取得中にエラーが発生: {e}")
            return "退室"  # エラー時は退室状態とみなす

    def process_entrance(self, card_id):
        """入室処理"""
        try:
            current_status = self.get_status(card_id)
            if current_status == "入室":
                logging.info(f"既に入室済み: カードID {card_id}")
                return False
            
            # 入室記録と状態更新
            return self._record_and_update_status(card_id, "入室")
            
        except Exception as e:
            logging.error(f"入室処理中にエラーが発生: {e}")
            return False

    def process_exit(self, card_id):
        """退室処理"""
        try:
            current_status = self.get_status(card_id)
            if current_status == "退室":
                logging.info(f"既に退室済み: カードID {card_id}")
                return False
            
            # 退室記録と状態更新
            return self._record_and_update_status(card_id, "退室")
            
        except Exception as e:
            logging.error(f"退室処理中にエラーが発生: {e}")
            return False

    def _record_and_update_status(self, card_id, action):
        """記録の追加と状態の更新"""
        try:
            now = datetime.now()
            user_info = self.get_user_info(card_id)
            
            # 記録用データの準備
            record_data = [
                now.strftime('%Y-%m-%d'),
                now.strftime('%H:%M:%S'),
                card_id,
                user_info['user_name'] if user_info else '未登録',
                user_info['department'] if user_info else '未登録',
                user_info['personal_id'] if user_info else '未登録',
                action
            ]
            
            # Recordsシートに記録を追加
            self.record_sheet.append_row(record_data)
            
            # Statusシートの更新
            cell = self.status_sheet.find(card_id)
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            if cell and cell.col == 1:
                # 既存のステータスを更新
                self.status_sheet.update(f'C{cell.row}:D{cell.row}', 
                                       [[action, now_str]])
            else:
                # 新規ステータスを追加
                self.status_sheet.append_row([
                    card_id,
                    user_info['user_name'] if user_info else '未登録',
                    action,
                    now_str
                ])
            
            logging.info(f"記録完了: {record_data[3]} ({card_id}) - {action}")
            return True
            
        except Exception as e:
            logging.error(f"記録と状態更新中にエラーが発生: {e}")
            return False
