import nfc
import logging
from threading import Lock

class NFCReader:
    def __init__(self, port, reader_type):
        self.clf = nfc.ContactlessFrontend(port)
        self.reader_type = reader_type
        self.lock = Lock()

    def read_card(self):
        with self.lock:
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False})
                if tag:
                    return self._get_id_from_tag(tag)
            except Exception as e:
                logging.error(f"Error reading card on {self.reader_type} reader: {e}")
        return None

    def _get_id_from_tag(self, tag):
        if isinstance(tag, nfc.tag.tt3.Type3Tag):
            return str(tag.identifier.hex().upper())
        return None