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
            
            # Statusシートのヘッダー（状態管理用）
            status_headers = ['カードID', 'ユーザー名', '現在の状態', '最終更新時刻']
            if not self.status_sheet.row_values(1):
                self.status_sheet.append_row(status_headers)
            
            # 既存のカードIDをすべて「退室」状態に初期化
            self._initialize_all_status()
                
        except Exception as e:
            logging.error(f"シートの初期化中にエラーが発生: {e}")
            raise

    def _initialize_all_status(self):
        """すべてのユーザーの状態を「退室」に初期化"""
        try:
            # すべてのユーザー情報を取得
            all_users = self.user_sheet.get_all_records()
            
            # Status シートをクリア（ヘッダーを除く）
            status_data = self.status_sheet.get_all_values()
            if len(status_data) > 1:
                self.status_sheet.delete_rows(2, len(status_data))
            
            # 登録済みユーザーの状態を初期化
            for user in all_users:
                self.status_sheet.append_row([
                    user['カードID'],
                    user['ユーザー名'],
                    '退室',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])
            
        except Exception as e:
            logging.error(f"状態の初期化中にエラーが発生: {e}")
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

    def get_current_status(self, card_id):
        """カードIDの現在の状態を取得"""
        try:
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                row_values = self.status_sheet.row_values(cell.row)
                return row_values[2]  # 現在の状態
            return None
        except Exception as e:
            logging.error(f"状態取得中にエラーが発生: {e}")
            return None

    def update_status(self, card_id, user_name, action):
        """ユーザーの状態を更新"""
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cell = self.status_sheet.find(card_id)
            
            if cell and cell.col == 1:
                # 既存のユーザーの状態を更新
                self.status_sheet.update_cell(cell.row, 3, action)  # 状態
                self.status_sheet.update_cell(cell.row, 4, now)     # 更新時刻
            else:
                # 新規ユーザー（未登録含む）の状態を追加
                self.status_sheet.append_row([
                    card_id,
                    user_name,
                    action,
                    now
                ])
            return True
        except Exception as e:
            logging.error(f"状態更新中にエラーが発生: {e}")
            return False

    def validate_action(self, card_id, action):
        """アクションの有効性をチェック"""
        current_status = self.get_current_status(card_id)
        
        # 初めて使用するカードの場合
        if current_status is None:
            if action == "入室":
                return True
            return False
        
        # 入室の場合：現在の状態が退室であることを確認
        if action == "入室":
            return current_status == "退室"
            
        # 退室の場合：現在の状態が入室であることを確認
        if action == "退室":
            return current_status == "入室"
            
        return False

    def append_record(self, card_id, action):
        """入退室記録の追加"""
        try:
            # アクションの有効性をチェック
            if not self.validate_action(card_id, action):
                logging.info(f"無効なアクション: カードID {card_id} は既に {action} 状態です")
                return False
            
            now = datetime.now()
            user_info = self.get_user_info(card_id)
            
            # 記録用の情報を準備
            record_time = now.strftime('%H:%M:%S')
            record_date = now.strftime('%Y-%m-%d')
            
            if user_info:
                # 登録ユーザーの記録
                self.record_sheet.append_row([
                    record_date,
                    record_time,
                    card_id,
                    user_info['user_name'],
                    user_info['department'],
                    user_info['personal_id'],
                    action
                ])
                # 状態の更新
                self.update_status(card_id, user_info['user_name'], action)
                logging.info(f"記録完了: {user_info['user_name']} ({card_id}) - {action}")
            else:
                # 未登録ユーザーの記録
                self.record_sheet.append_row([
                    record_date,
                    record_time,
                    card_id,
                    '未登録',
                    '未登録',
                    '未登録',
                    action
                ])
                # 状態の更新
                self.update_status(card_id, '未登録', action)
                logging.warning(f"未登録のカード {card_id} を記録: {action}")
            
            return True
            
        except Exception as e:
            logging.error(f"記録追加中にエラーが発生: {e}")
            return False
