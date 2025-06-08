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
            status_headers = ['カードID', 'ユーザー名', '最終動作', '最終更新時刻']
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

    def check_status(self, card_id, action):
        """ユーザーの現在の入退室状態をチェック"""
        try:
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                current_status = self.status_sheet.row_values(cell.row)[2]  # 最終動作
                # 同じ動作の重複を防ぐ
                if current_status == action:
                    return False
                # 状態を更新
                self.status_sheet.update_cell(cell.row, 3, action)
                self.status_sheet.update_cell(cell.row, 4, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                return True
            else:
                # 新規ユーザーの状態を追加
                user_info = self.get_user_info(card_id)
                if user_info:
                    self.status_sheet.append_row([
                        card_id,
                        user_info['user_name'],
                        action,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ])
                return True
        except Exception as e:
            logging.error(f"状態チェック中にエラーが発生: {e}")
            return True  # エラーの場合は記録を許可

    def append_record(self, card_id, action):
        """入退室記録の追加"""
        try:
            if not self.check_status(card_id, action):
                logging.info(f"重複する{action}のため記録をスキップ: {card_id}")
                return False
                
            now = datetime.now()
            user_info = self.get_user_info(card_id)
            
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
                return True
            else:
                # ユーザー情報が未登録の場合
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
                return True
        except Exception as e:
            logging.error(f"記録追加中にエラーが発生: {e}")
            return False