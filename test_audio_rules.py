import sys
import os
import re
import datetime
import unittest

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

import hypertts
import testing_utils
import constants
import languages
import config_models
import batch_status


logging_utils = __import__('logging_utils', globals(), locals(), [], sys._addon_import_level_base)
logger = logging_utils.get_test_child_logger(__name__)

class mock_progress_bar():
    def __init__(self):
        self.iteration = 0

    def callback_fn(self, iteration):
        self.iteration = iteration


class MockBatchStatusListener():
    def __init__(self, anki_utils):
        self.anki_utils = anki_utils
        self.callbacks_received = {}
        self.current_row = None

        self.batch_started = None
        self.batch_ended = None

    def batch_start(self):
        self.batch_started = True

    def batch_end(self, completed):
        self.batch_ended = True

    def batch_change(self, note_id, row, total_count, start_time, current_time):
        if note_id not in self.callbacks_received:
            self.anki_utils.tick_time()
        self.callbacks_received[note_id] = True
        self.current_row = row
        self.total_count = total_count
        self.start_time = start_time
        self.current_time = current_time

class AudioRulesTests(unittest.TestCase):
    def test_editor_process_single_rule(self):
        # initialize hypertts instance
        # ============================
        config_gen = testing_utils.TestConfigGenerator()
        hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

        # configure two presets
        # =====================

        voice_list = hypertts_instance.service_manager.full_voice_list()

        #  preset 1
        voice_a_1 = [x for x in voice_list if x.name == 'voice_a_1'][0]
        voice_selection = config_models.VoiceSelectionSingle()
        voice_selection.set_voice(config_models.VoiceWithOptions(voice_a_1, {}))

        batch_config = config_models.BatchConfig(hypertts_instance.anki_utils)
        source = config_models.BatchSourceSimple('Chinese')
        target = config_models.BatchTarget('Sound', False, True)
        text_processing = config_models.TextProcessing()

        batch_config.set_source(source)
        batch_config.set_target(target)
        batch_config.set_voice_selection(voice_selection)
        batch_config.set_text_processing(text_processing)

        # save the preset
        hypertts_instance.save_preset(batch_config)

        # configure preset rules
        # ======================

        rule_1 = config_models.MappingRule(preset_id=batch_config.uuid,
                                           rule_type = constants.MappingRuleType.DeckNoteType,
                                           model_id = config_gen.model_id,
                                           enabled = True,
                                           automatic = False,
                                           deck_id = config_gen.deck_id)

        # this is the target note
        target_note_id = config_gen.note_id_1

        # configure mock editor
        # =====================
        mock_editor = config_gen.get_mock_editor_with_note(target_note_id, config_gen.deck_id)

        # process rules
        # =============

        hypertts_instance.editor_note_process_rule(rule_1, mock_editor, None)


        # verify audio was added
        # ======================

        note_1 = mock_editor.note
        assert 'Sound' in note_1.set_values 

        sound_tag = note_1.set_values['Sound']
        audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
        audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)

        assert audio_data['source_text'] == '老人家'



    def test_process_two_rules(self):
        # initialize hypertts instance
        # ============================
        config_gen = testing_utils.TestConfigGenerator()
        hypertts_instance = config_gen.build_hypertts_instance_test_servicemanager('default')

        # configure two presets
        # =====================

        voice_list = hypertts_instance.service_manager.full_voice_list()

        #  preset 1
        voice_a_1 = [x for x in voice_list if x.name == 'voice_a_1'][0]
        voice_selection = config_models.VoiceSelectionSingle()
        voice_selection.set_voice(config_models.VoiceWithOptions(voice_a_1, {}))

        batch_config = config_models.BatchConfig(hypertts_instance.anki_utils)
        source = config_models.BatchSourceSimple('Chinese')
        target = config_models.BatchTarget('Sound', False, True)
        text_processing = config_models.TextProcessing()

        batch_config.set_source(source)
        batch_config.set_target(target)
        batch_config.set_voice_selection(voice_selection)
        batch_config.set_text_processing(text_processing)

        # save the preset
        hypertts_instance.save_preset(batch_config)
        preset_id_1 = batch_config.uuid

        # preset 2
        voice_b_1 = [x for x in voice_list if x.name == 'voice_a_2'][0]
        voice_selection = config_models.VoiceSelectionSingle()
        voice_selection.set_voice(config_models.VoiceWithOptions(voice_b_1, {}))

        batch_config = config_models.BatchConfig(hypertts_instance.anki_utils)
        source = config_models.BatchSourceSimple('English')
        target = config_models.BatchTarget('Sound English', False, True)
        text_processing = config_models.TextProcessing()

        batch_config.set_source(source)
        batch_config.set_target(target)
        batch_config.set_voice_selection(voice_selection)
        batch_config.set_text_processing(text_processing)

        # save the preset
        hypertts_instance.save_preset(batch_config)
        preset_id_2 = batch_config.uuid

        # configure preset rules
        # ======================

        preset_mapping_rules = config_models.PresetMappingRules()

        rule_1 = config_models.MappingRule(preset_id=preset_id_1,
                                           rule_type = constants.MappingRuleType.DeckNoteType,
                                           model_id = config_gen.model_id,
                                           enabled = True,
                                           automatic = False,
                                           deck_id = config_gen.deck_id)
        preset_mapping_rules.rules.append(rule_1)

        rule_2 = config_models.MappingRule(preset_id=preset_id_2,
                                             rule_type = constants.MappingRuleType.NoteType,
                                             model_id = config_gen.model_id,
                                             enabled = True,
                                             automatic = False)
        preset_mapping_rules.rules.append(rule_2)


        # this is the target note
        target_note_id = config_gen.note_id_1


        # configure mock editor
        # =====================
        mock_editor = config_gen.get_mock_editor_with_note(target_note_id, config_gen.deck_id, add_mode=False)

        # process rules
        # =============

        hypertts_instance.editor_note_process_rules(preset_mapping_rules, mock_editor, False, None)


        # verify audio was added
        # ======================

        note_1 = mock_editor.note
        # check preset 1
        assert 'Sound' in note_1.set_values 
        sound_tag = note_1.set_values['Sound']
        audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
        audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)
        assert audio_data['source_text'] == '老人家'

        # check preset 2
        assert 'Sound English' in note_1.set_values

        sound_tag = note_1.set_values['Sound English']
        audio_full_path = hypertts_instance.anki_utils.extract_sound_tag_audio_full_path(sound_tag)
        audio_data = hypertts_instance.anki_utils.extract_mock_tts_audio(audio_full_path)
        assert audio_data['source_text'] == 'old people'        
        

