import os
os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'  # ここをalsa→pulseaudioに
import pygame
import logging
from pathlib import Path

class AudioPlayer:
    def __init__(self, audio_config):
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0)
            self.sounds = {}
            for action in ['entrance', 'exit']:
                sound_path = audio_config.get(f'{action}_sound')
                if sound_path and Path(sound_path).exists():
                    self.sounds[action] = pygame.mixer.Sound(sound_path)
                else:
                    logging.warning(f"音声ファイルが見つかりません: {sound_path}")
        except Exception as e:
            logging.error(f"音声プレーヤーの初期化中にエラーが発生: {e}")
            self.sounds = {}

    def play(self, action):
        try:
            sound_key = 'entrance' if action == "入室" else 'exit'
            if sound_key in self.sounds:
                self.sounds[sound_key].play()
        except Exception as e:
            logging.error(f"音声再生中にエラーが発生: {e}")
