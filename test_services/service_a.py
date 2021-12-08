import constants
import service
import voice
import typing
import json

VOICE_OPTIONS = {
    'pitch': {
        'default': 0.0, 'max': 20.0, 'min': -20.0, 'type': 'number'}, 
    'speaking_rate': {
        'default': 1.0, 'max': 4.0, 'min': 0.25, 'type': 'number'}
}

class ServiceA(service.ServiceBase):
    def __init__(self):
        pass

    def voice_list(self):
        return [
            voice.Voice('voice_a_1', constants.Gender.Male, constants.AudioLanguage.fr_FR, self, {'name': 'voice_1'}, VOICE_OPTIONS),
            voice.Voice('voice_a_2', constants.Gender.Female, constants.AudioLanguage.en_US, self, {'name': 'voice_2'}, VOICE_OPTIONS),
            voice.Voice('voice_a_3', constants.Gender.Female, constants.AudioLanguage.ja_JP, self, {'name': 'voice_3'}, VOICE_OPTIONS),
        ]

    def get_tts_audio(self, source_text, voice: voice.VoiceBase):
        self.requested_audio = {
            'source_text': source_text,
            'voice_key': voice.voice_key,
            'language': voice.language.name
        }
        encoded_dict = json.dumps(self.requested_audio, indent=2).encode('utf-8')
        return encoded_dict    

    def configuration_options(self):
        return {
            'api_key': str,
            'region': ['us', 'europe'],
            'delay': int
        }