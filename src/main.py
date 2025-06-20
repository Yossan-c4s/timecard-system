import logging
import yaml
import time
from audio_player import AudioPlayer
from oled_display import OLEDDisplay

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def mock_read_card():
    # ダミー: 本来はNFCリーダーから取得
    import random
    users = [
        {"card_id": "123", "username": "山田太郎"},
        {"card_id": "456", "username": "佐藤花子"},
    ]
    return random.choice(users)

def mock_process_card(card_id):
    # ダミー: 本来はspreadsheet連携
    import random
    action = random.choice(["入室", "退室"])
    username = "山田太郎" if card_id == "123" else "佐藤花子"
    return {"action": action, "username": username}

def main():
    logging.basicConfig(filename="/var/log/timecard/timecard.log", level=logging.INFO)
    config = load_config("/etc/timecard/config.yaml")
    audio = AudioPlayer(config["audio"])
    oled_conf = config.get("oled", {})
    oled = OLEDDisplay(
        oled_conf.get("spi_port", 0),
        oled_conf.get("spi_device", 0),
        oled_conf.get("gpio_dc", 25),
        oled_conf.get("gpio_rst", 24),
    )

    while True:
        card = mock_read_card()
        result = mock_process_card(card["card_id"])

        if result:
            action = result["action"]
            username = result["username"]
            status = "[on work]" if action == "入室" else "[off work]"
            audio.play(action)
            oled.show_status(username, status)
            logging.info(f"{username} {action}")

        time.sleep(5)  # デモ用

if __name__ == "__main__":
    main()