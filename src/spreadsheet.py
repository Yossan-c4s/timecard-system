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
        
        # シートの取得または作成
        self.record_sheet = self._get_or_create_sheet('Records')
        self.user_sheet = self._get_or_create_sheet('Users')
        self.status_sheet = self._get_or_create_sheet('Status')
        
        self._initialize_sheets()

    def _get_or_create_sheet(self, sheet_name):
        """シートの取得、存在しない場合は作成"""
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            return self.spreadsheet.add_worksheet(sheet_name, 1000, 20)

    def _initialize_sheets(self):
        """シートの初期化とヘッダーの設定"""
        try:
            # Recordsシートのヘッダー
            records_headers = ['日付', '時刻', 'カードID', 'ユーザー名', '所属部署', '個人ID', '動作']
            if not self.record_sheet.row_values(1):
                self.record_sheet.append_row(records_headers)
            
            # Usersシートのヘッダー
            users_headers = ['カードID', 'ユーザー名', '所属部署', '個人ID']
            if not self.user_sheet.row_values(1):
                self.user_sheet.append_row(users_headers)
            
            # Statusシートのヘッダー
            status_headers = ['カードID', 'ユーザー名', '状態']
            if not self.status_sheet.row_values(1):
                self.status_sheet.append_row(status_headers)
                
        except Exception as e:
            logging.error(f"シートの初期化中にエラーが発生: {e}")
            raise

    def get_user_info(self, card_id):
        """カードIDに対応するユーザー情報を取得"""
        try:
            # ユーザー情報の検索
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

    def get_user_status(self, card_id):
        """ユーザーの現在の入退室状態を取得"""
        try:
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                return self.status_sheet.row_values(cell.row)[2]  # 状態
            return None
        except Exception as e:
            logging.error(f"ユーザー状態の取得中にエラーが発生: {e}")
            return None

    def update_user_status(self, card_id, action):
        """ユーザーの状態を更新"""
        try:
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                # 状態を更新
                self.status_sheet.update_cell(cell.row, 3, action)
            else:
                # 新規ユーザーの状態を追加
                user_info = self.get_user_info(card_id)
                user_name = user_info['user_name'] if user_info else '未登録'
                self.status_sheet.append_row([card_id, user_name, action])
        except Exception as e:
            logging.error(f"ユーザー状態の更新中にエラーが発生: {e}")
            raise

    def check_action_validity(self, card_id, action):
        """アクションの有効性をチェック"""
        current_status = self.get_user_status(card_id)
        
        if action == "入室":
            # 現在の状態が入室中の場合は、再度の入室を許可しない
            return current_status != "入室"
        elif action == "退室":
            # 現在の状態が退室中の場合は、再度の退室を許可しない
            # また、入室していない人の退室も許可しない
            return current_status == "入室"
        
        return False

    def append_record(self, card_id, action):
        """入退室記録の追加"""
        try:
            # アクションの有効性をチェック
            if not self.check_action_validity(card_id, action):
                logging.info(f"無効なアクション - カードID: {card_id}, アクション: {action}")
                return False
                
            now = datetime.now()
            user_info = self.get_user_info(card_id)
            
            # 記録の追加
            if user_info:
                self.record_sheet.append_row([
                    now.strftime('%Y-%m-%d'),
                    now.strftime('%H:%M:%S'),
                    card_id,
                    user_info['user_name'],
                    user_info['department'],
                    user_info['personal_id'],
                    action
                ])
                logging.info(f"記録完了: {user_info['user_name']} ({card_id}) - {action}")
            else:
                self.record_sheet.append_row([
                    now.strftime('%Y-%m-%d'),
                    now.strftime('%H:%M:%S'),
                    card_id,
                    '未登録',
                    '未登録',
                    '未登録',
                    action
                ])
                logging.warning(f"未登録のカード: {card_id}")
            
            # 状態の更新
            self.update_user_status(card_id, action)
            return True
            
        except Exception as e:
            logging.error(f"記録追加中にエラーが発生: {e}")
            return False
