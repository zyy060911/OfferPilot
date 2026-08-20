import json
import os
import sys
import unittest
import threading
import numpy as np
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from server import routes
from avatars.base_avatar import BaseAvatar


class FakeRequest:
    def __init__(self, payload):
        self._payload = payload
        self.app = {}

    async def json(self):
        return self._payload


class FakeAvatar:
    def __init__(self):
        self.registered = None
        self.message = None
        self.actions = []

    def flush_talk(self):
        pass

    def register_speech(self, speech_id):
        self.registered = speech_id

    def put_msg_txt(self, text, datainfo):
        self.message = (text, datainfo)

    def get_speech_status(self):
        return {
            'speaking': True,
            'speechId': 'speech-1',
            'updatedAt': '2026-08-09T00:00:00Z',
        }

    def set_action_state(self, action):
        self.actions.append(action)
        return {
            'applied': action == 'SPEAKING',
            'appliedAction': action if action == 'SPEAKING' else 'NEUTRAL',
            'reason': 'test',
            'capabilities': ['NEUTRAL', 'SPEAKING'],
        }

    def interrupt_speech(self, speech_id):
        return {
            'interrupted': speech_id == 'speech-1',
            'speechId': 'speech-1',
            'reason': 'output-pipeline-flushed' if speech_id == 'speech-1' else 'speech-id-mismatch',
        }


class SpeechRoutesTest(unittest.IsolatedAsyncioTestCase):
    async def test_is_speaking_returns_stable_json_shape(self):
        avatar = FakeAvatar()
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.is_speaking(FakeRequest({'sessionid': 7}))

        body = json.loads(response.text)
        self.assertEqual(body['code'], 0)
        self.assertEqual(body['msg'], 'ok')
        self.assertEqual(body['data'], {
            'speaking': True,
            'speechId': 'speech-1',
            'updatedAt': '2026-08-09T00:00:00Z',
        })

    async def test_human_preserves_speech_id_into_tts_metadata(self):
        avatar = FakeAvatar()
        request = FakeRequest({
            'sessionid': 7,
            'type': 'echo',
            'text': '你好',
            'speechId': 'speech-42',
        })
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.human(request)

        body = json.loads(response.text)
        self.assertEqual(body['data']['speechId'], 'speech-42')
        self.assertEqual(avatar.registered, 'speech-42')
        self.assertEqual(avatar.message[1]['speechId'], 'speech-42')
        self.assertEqual(avatar.actions, ['SPEAKING'])

    async def test_action_route_returns_explicit_fallback_when_resource_is_missing(self):
        avatar = FakeAvatar()
        request = FakeRequest({
            'sessionid': 7,
            'action': 'THINKING',
            'requestId': 'action-1',
        })
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.set_audiotype(request)

        body = json.loads(response.text)
        self.assertEqual(body['code'], 0)
        self.assertEqual(body['data'], {
            'applied': False,
            'appliedAction': 'NEUTRAL',
            'reason': 'test',
            'capabilities': ['NEUTRAL', 'SPEAKING'],
            'requestId': 'action-1',
        })

    async def test_is_speaking_error_is_not_reported_as_false(self):
        avatar = FakeAvatar()
        avatar.get_speech_status = lambda: (_ for _ in ()).throw(RuntimeError('status failed'))
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.is_speaking(FakeRequest({'sessionid': 7}))

        body = json.loads(response.text)
        self.assertNotEqual(body['code'], 0)
        self.assertNotIn('data', body)

    async def test_human_failure_returns_error_instead_of_acceptance(self):
        avatar = FakeAvatar()
        avatar.put_msg_txt = lambda *_: (_ for _ in ()).throw(RuntimeError('queue unavailable'))
        request = FakeRequest({
            'sessionid': 7,
            'type': 'echo',
            'text': '你好',
            'speechId': 'speech-failed',
        })
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.human(request)

        body = json.loads(response.text)
        self.assertNotEqual(body['code'], 0)

    async def test_interrupt_route_preserves_speech_id_and_returns_confirmation(self):
        avatar = FakeAvatar()
        with patch.object(routes, 'get_session', return_value=avatar):
            response = await routes.interrupt_talk(FakeRequest({
                'sessionid': 7,
                'speechId': 'speech-1',
            }))

        body = json.loads(response.text)
        self.assertEqual(body['data'], {
            'interrupted': True,
            'speechId': 'speech-1',
            'reason': 'output-pipeline-flushed',
        })


class AvatarSpeechLifecycleTest(unittest.TestCase):
    def make_avatar(self):
        avatar = BaseAvatar.__new__(BaseAvatar)
        avatar.speaking = False
        avatar._speech_lock = threading.RLock()
        avatar._speech_id = None
        avatar._speech_updated_at = avatar._utc_now()
        avatar._speech_event_publisher = None
        return avatar

    def test_output_events_update_thread_safe_status_and_publish_same_id(self):
        avatar = self.make_avatar()
        events = []
        avatar.set_speech_event_publisher(events.append)
        avatar.register_speech('speech-1')

        avatar.notify({'status': 'start', 'speechId': 'speech-1'})
        self.assertTrue(avatar.get_speech_status()['speaking'])
        avatar.notify({'status': 'end', 'speechId': 'speech-1'})

        self.assertEqual([event['event'] for event in events], ['speech-started', 'speech-ended'])
        self.assertTrue(all(event['speechId'] == 'speech-1' for event in events))
        self.assertEqual(avatar.get_speech_status()['speaking'], False)
        self.assertIsNone(avatar.get_speech_status()['speechId'])

    def test_old_output_event_is_marked_stale_and_cannot_replace_new_status(self):
        avatar = self.make_avatar()
        events = []
        avatar.set_speech_event_publisher(events.append)
        avatar.register_speech('new')
        avatar.notify({'status': 'start', 'speechId': 'old'})

        self.assertFalse(avatar.get_speech_status()['speaking'])
        self.assertEqual(avatar.get_speech_status()['speechId'], 'new')
        self.assertTrue(events[-1]['stale'])

    def test_late_terminal_event_cannot_resurrect_a_completed_speech(self):
        avatar = self.make_avatar()
        events = []
        avatar.set_speech_event_publisher(events.append)
        avatar.register_speech('speech-1')
        avatar.notify({'status': 'start', 'speechId': 'speech-1'})
        avatar.notify({'status': 'end', 'speechId': 'speech-1'})

        avatar.notify({'status': 'end', 'speechId': 'speech-1'})

        self.assertTrue(events[-1]['stale'])
        self.assertIsNone(avatar.get_speech_status()['speechId'])
        self.assertFalse(avatar.get_speech_status()['speaking'])

    def test_interrupt_flushes_current_speech_and_publishes_same_id(self):
        avatar = self.make_avatar()
        avatar._custom_lock = threading.RLock()
        avatar.custom_audiotype = 0
        avatar.active_action = 'SPEAKING'
        avatar.tts = type('FakeTts', (), {'flush_talk': lambda self: None})()
        avatar.asr = type('FakeAsr', (), {'flush_talk': lambda self: None})()
        events = []
        avatar.set_speech_event_publisher(events.append)
        avatar.register_speech('speech-1')
        avatar.notify({'status': 'start', 'speechId': 'speech-1'})

        result = avatar.interrupt_speech('speech-1')

        self.assertTrue(result['interrupted'])
        self.assertEqual(result['speechId'], 'speech-1')
        self.assertEqual(events[-1]['event'], 'speech-interrupted')
        self.assertIsNone(avatar.get_speech_status()['speechId'])

    def test_interrupt_rejects_stale_speech_id_without_flushing(self):
        avatar = self.make_avatar()
        avatar.flush_talk = lambda: self.fail('stale interruption must not flush current speech')
        avatar.register_speech('new')
        result = avatar.interrupt_speech('old')
        self.assertFalse(result['interrupted'])
        self.assertEqual(result['reason'], 'speech-id-mismatch')

    def test_action_state_falls_back_without_assets_and_protects_speech(self):
        avatar = self.make_avatar()
        avatar._custom_lock = threading.RLock()
        avatar.custom_audiotype = 0
        avatar.custom_img_cycle = {}
        avatar.custom_audio_cycle = {}
        avatar.custom_audio_index = {}
        avatar.custom_index = {}
        avatar.custom_action_types = {}
        avatar.active_action = 'NEUTRAL'

        fallback = avatar.set_action_state('LISTENING')
        self.assertFalse(fallback['applied'])
        self.assertEqual(fallback['appliedAction'], 'NEUTRAL')

        avatar.register_speech('speech-1')
        protected = avatar.set_action_state('THINKING')
        self.assertFalse(protected['applied'])
        self.assertEqual(protected['appliedAction'], 'SPEAKING')
        speaking = avatar.set_action_state('SPEAKING')
        self.assertTrue(speaking['applied'])
        self.assertEqual(speaking['reason'], 'tts-lipsync-controls-speaking')

    def test_image_only_custom_action_produces_silent_loop_without_tts_audio(self):
        avatar = self.make_avatar()
        avatar._custom_lock = threading.RLock()
        avatar.chunk = 320
        avatar.custom_audiotype = 0
        avatar.custom_img_cycle = {2: [np.zeros((2, 2, 3), dtype=np.uint8)]}
        avatar.custom_audio_cycle = {}
        avatar.custom_audio_index = {}
        avatar.custom_index = {2: 0}
        avatar.custom_action_types = {'LISTENING': 2}
        avatar.active_action = 'NEUTRAL'

        result = avatar.set_action_state('LISTENING')
        self.assertTrue(result['applied'])
        self.assertEqual(avatar.custom_audiotype, 2)
        self.assertEqual(avatar.get_custom_audio_stream(2).shape[0], 320)
        self.assertTrue(np.all(avatar.get_custom_audio_stream(2) == 0))


if __name__ == '__main__':
    unittest.main()
