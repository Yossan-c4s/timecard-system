import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import time
from typing import Dict, Optional

class SpreadsheetManager:
    def __init__(self, credentials_path: str, sheet_name: str):
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

    def _initialize_sheets(self) -> None:
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
            status_headers = ['カードID', 'ユーザー名', '現在の状態', '最終更新時刻']
            if not self.status_sheet.row_values(1):
                self.status_sheet.append_row(status_headers)
                
        except Exception as e:
            logging.error(f"シートの初期化中にエラーが発生: {e}")
            raise

    def get_user_info(self, card_id: str) -> Optional[Dict[str, str]]:
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

    def get_current_status(self, card_id: str) -> str:
        """カードIDの現在の状態を取得"""
        try:
            # Statusシートから直接状態を取得
            cell = self.status_sheet.find(card_id)
            if cell and cell.col == 1:
                status = self.status_sheet.cell(cell.row, 3).value  # 現在の状態
                return status
            return "退室"  # 初期状態は退室
        except Exception as e:
            logging.error(f"状態取得中にエラーが発生: {e}")
            return "退室"  # エラー時も退室扱い

    def update_status(self, card_id: str, user_name: str, action: str) -> bool:
        """ユーザーの状態を更新"""
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cell = self.status_sheet.find(card_id)
            
            if cell and cell.col == 1:
                # 既存の状態を更新
                self.status_sheet.update_cell(cell.row, 3, action)
                self.status_sheet.update_cell(cell.row, 4, now)
            else:
                # 新規の状態を追加
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

    def validate_action(self, card_id: str, action: str) -> bool:
        """アクションの有効性をチェック"""
        current_status = self.get_current_status(card_id)
        
        if action == "入室":
            return current_status == "退室"
        elif action == "退室":
            return current_status == "入室"
        
        return False

    def append_record(self, card_id: str, action: str) -> bool:
        """入退室記録の追加"""
        try:
            # アクションの有効性をチェック
            if not self.validate_action(card_id, action):
                current_status = self.get_current_status(card_id)
                logging.info(f"無効なアクション: カードID {card_id} の現在の状態は {current_status} です")
                return False
            
            now = datetime.now()
            user_info = self.get_user_info(card_id)
            
            # 記録の追加
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
            
            # 状態を更新
            user_name = user_info['user_name'] if user_info else '未登録'
            success = self.update_status(card_id, user_name, action)
            
            if success:
                logging.info(f"記録完了: {user_name} ({card_id}) - {action}")
            else:
                logging.error(f"状態更新失敗: {user_name} ({card_id}) - {action}")
            
            return success
            
        except Exception as e:
            logging.error(f"記録追加中にエラーが発生: {e}")
            return False
