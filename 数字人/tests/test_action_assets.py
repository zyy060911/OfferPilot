import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from avatars.base_avatar import BaseAvatar
from tools import avatar_action_pipeline


class ActionAssetLoadingTest(unittest.TestCase):
    def make_avatar(self, customopt):
        avatar = BaseAvatar.__new__(BaseAvatar)
        avatar.opt = SimpleNamespace(customopt=customopt)
        avatar.sample_rate = 16000
        avatar.custom_img_cycle = {}
        avatar.custom_audio_cycle = {}
        avatar.custom_audio_index = {}
        avatar.custom_index = {}
        avatar.custom_loop_modes = {}
        avatar.custom_action_types = {}
        avatar._custom_lock = threading.RLock()
        avatar._speech_lock = threading.RLock()
        avatar._speech_id = None
        avatar.active_action = 'NEUTRAL'
        return avatar

    @patch('avatars.base_avatar.read_imgs', side_effect=lambda paths: list(paths))
    @patch('avatars.base_avatar.glob.glob')
    def test_loader_uses_configured_real_frame_range(self, glob_mock, _read_mock):
        glob_mock.return_value = [f'frames/{index:08d}.png' for index in range(349)]
        avatar = self.make_avatar([{
            'action': 'LISTENING', 'audiotype': 3, 'imgpath': 'frames',
            'startFrame': 155, 'endFrame': 204, 'loopMode': 'loop',
            'reviewStatus': 'approved', 'approvedAt': '2026-08-09T00:00:00Z',
        }])

        avatar._BaseAvatar__loadcustom()

        self.assertEqual(len(avatar.custom_img_cycle[3]), 50)
        self.assertTrue(avatar.custom_img_cycle[3][0].endswith('00000155.png'))
        self.assertTrue(avatar.custom_img_cycle[3][-1].endswith('00000204.png'))
        self.assertEqual(avatar.custom_loop_modes[3], 'loop')
        self.assertEqual(avatar.custom_action_types['LISTENING'], 3)

    @patch('avatars.base_avatar.read_imgs')
    @patch('avatars.base_avatar.glob.glob')
    def test_pending_candidate_is_not_loaded(self, glob_mock, read_mock):
        glob_mock.return_value = [f'frames/{index:08d}.png' for index in range(349)]
        avatar = self.make_avatar([{
            'action': 'LISTENING', 'audiotype': 3, 'imgpath': 'frames',
            'startFrame': 155, 'endFrame': 204, 'loopMode': 'loop',
            'reviewStatus': 'pending',
        }])

        avatar._BaseAvatar__loadcustom()

        self.assertEqual(avatar.custom_img_cycle, {})
        self.assertEqual(avatar.custom_action_types, {})
        read_mock.assert_not_called()

    def test_configured_neutral_subloop_is_applied(self):
        avatar = self.make_avatar([])
        avatar.custom_img_cycle[2] = [np.zeros((1, 1, 3), dtype=np.uint8)]
        avatar.custom_index[2] = 0
        avatar.custom_action_types['NEUTRAL'] = 2

        result = avatar.set_action_state('NEUTRAL')

        self.assertTrue(result['applied'])
        self.assertEqual(result['appliedAction'], 'NEUTRAL')
        self.assertEqual(result['reason'], 'custom-action-loaded')
        self.assertEqual(avatar.custom_audiotype, 2)


class ActionPipelineTest(unittest.TestCase):
    def test_unicode_image_round_trip(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as directory:
            path = Path(directory) / '中文帧.png'
            expected = np.full((8, 6, 3), 127, dtype=np.uint8)
            avatar_action_pipeline.write_image(path, expected)
            actual = avatar_action_pipeline.read_image(path)
            self.assertTrue(np.array_equal(actual, expected))


if __name__ == '__main__':
    unittest.main()
