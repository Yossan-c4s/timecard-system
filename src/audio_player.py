import pygame
import logging
from pathlib import Path

class AudioPlayer:
    def __init__(self, audio_config):
        """
        音声プレーヤーの初期化
        
        Parameters:
        audio_config (dict): {
            'entrance_sound': '入室時の音声ファイルパス',
            'exit_sound': '退室時の音声ファイルパス'
        }
        """
        try:
            pygame.mixer.init()
            self.sounds = {}
            
            # 音声ファイルの読み込み
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
        """
        指定されたアクションの音声を再生
        
        Parameters:
        action (str): "入室" または "退室"
        """
        try:
            sound_key = 'entrance' if action == "入室" else 'exit'
            if sound_key in self.sounds:
                self.sounds[sound_key].play()
        except Exception as e:
            logging.error(f"音声再生中にエラーが発生: {e}")