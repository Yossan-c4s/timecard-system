import logging
from datetime import datetime

def setup_logging():
    """ログ設定の初期化"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/var/log/timecard/timecard.log'),
            logging.StreamHandler()
        ]
    )

def format_datetime(dt=None):
    """日時フォーマットの統一"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')