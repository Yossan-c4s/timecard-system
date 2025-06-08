import nfc
import logging
import time
from threading import Lock

class NFCReader:
    def __init__(self, port, reader_type, min_interval=1.0):
        """
        NFCリーダーの初期化
        
        Parameters:
        port (str): NFCリーダーのポート
        reader_type (str): リーダーの種類を示す文字列
        min_interval (float): 連続読み取りの最小間隔（秒）
        """
        self.clf = nfc.ContactlessFrontend(port)
        self.reader_type = reader_type
        self.lock = Lock()
        self.min_interval = min_interval
        self.last_read_time = 0
        self.last_card_id = None

    def read_card(self):
        """
        カードの読み取り
        
        Returns:
        str or None: カードID、または読み取り失敗時/インターバル期間中はNone
        """
        current_time = time.time()
        
        # 最小間隔のチェック
        if current_time - self.last_read_time < self.min_interval:
            return None

        with self.lock:
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
                if tag:
                    card_id = self._get_id_from_tag(tag)
                    
                    # 同じカードの連続読み取り防止
                    if card_id == self.last_card_id:
                        if current_time - self.last_read_time < self.min_interval * 2:
                            return None
                    
                    self.last_read_time = current_time
                    self.last_card_id = card_id
                    return card_id
                    
            except Exception as e:
                logging.error(f"カード読み取り中にエラーが発生: {e}")
                
        return None

    def _get_id_from_tag(self, tag):
        """タグからIDを取得"""
        if isinstance(tag, nfc.tag.tt3.Type3Tag):
            return str(tag.identifier.hex().upper())
        return None