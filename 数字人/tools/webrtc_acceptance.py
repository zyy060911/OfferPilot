"""Local WebRTC/DataChannel acceptance probe for the digital-human service."""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid

import aiohttp
from aiortc import RTCPeerConnection, RTCSessionDescription


async def wait_for_ice_gathering(pc, timeout=15):
    if pc.iceGatheringState == 'complete':
        return
    completed = asyncio.Event()

    @pc.on('icegatheringstatechange')
    def on_state_change():
        if pc.iceGatheringState == 'complete':
            completed.set()

    await asyncio.wait_for(completed.wait(), timeout)


async def consume_track(track):
    try:
        while True:
            await track.recv()
    except Exception:
        return


async def post_json(session, base_url, path, payload):
    async with session.post(f'{base_url}{path}', json=payload) as response:
        body = await response.json()
        if response.status >= 400 or body.get('code', 0) != 0:
            raise RuntimeError(f'{path} failed: HTTP {response.status} {body}')
        return body


async def run(base_url, tts_timeout):
    pc = RTCPeerConnection()
    channel = pc.createDataChannel('offerpilot.lifecycle', ordered=True)
    channel_open = asyncio.Event()
    lifecycle_events = asyncio.Queue()
    consumers = []
    session_id = None

    @channel.on('open')
    def on_open():
        channel_open.set()

    @channel.on('message')
    def on_message(message):
        lifecycle_events.put_nowait(json.loads(message))

    @pc.on('track')
    def on_track(track):
        consumers.append(asyncio.create_task(consume_track(track)))

    pc.addTransceiver('video', direction='recvonly')
    pc.addTransceiver('audio', direction='recvonly')
    try:
        await pc.setLocalDescription(await pc.createOffer())
        await wait_for_ice_gathering(pc)
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{base_url}/offer', json={
                'sdp': pc.localDescription.sdp,
                'type': pc.localDescription.type,
            }) as response:
                answer = await response.json()
                if response.status >= 400 or not answer.get('sessionid'):
                    raise RuntimeError(f'/offer failed: HTTP {response.status} {answer}')
            session_id = answer['sessionid']
            await pc.setRemoteDescription(RTCSessionDescription(sdp=answer['sdp'], type=answer['type']))
            await asyncio.wait_for(channel_open.wait(), 15)

            neutral = await post_json(session, base_url, '/set_audiotype', {
                'sessionid': session_id,
                'action': 'NEUTRAL',
                'requestId': 'acceptance-neutral',
            })
            thinking = await post_json(session, base_url, '/set_audiotype', {
                'sessionid': session_id,
                'action': 'THINKING',
                'requestId': 'acceptance-thinking',
            })

            speech_id = f'acceptance-{uuid.uuid4()}'
            accepted = await post_json(session, base_url, '/human', {
                'sessionid': session_id,
                'type': 'echo',
                'text': '这是本地数字人链路验收。',
                'speechId': speech_id,
                'interrupt': True,
            })
            observed = []
            while not any(item.get('event') in ('speech-ended', 'speech-error') for item in observed):
                event = await asyncio.wait_for(lifecycle_events.get(), tts_timeout)
                if event.get('speechId') == speech_id:
                    observed.append(event)

            interrupt_speech_id = f'interrupt-{uuid.uuid4()}'
            await post_json(session, base_url, '/human', {
                'sessionid': session_id,
                'type': 'echo',
                'text': '这是一段用于验证受控语音打断的较长播报。数字人应当先开始输出，然后只接受匹配播报标识的停止请求。',
                'speechId': interrupt_speech_id,
                'interrupt': True,
            })
            interrupt_events = []
            while not any(item.get('event') == 'speech-started' for item in interrupt_events):
                event = await asyncio.wait_for(lifecycle_events.get(), tts_timeout)
                if event.get('speechId') == interrupt_speech_id:
                    interrupt_events.append(event)
            stale_interrupt_response = await post_json(session, base_url, '/interrupt_talk', {
                'sessionid': session_id,
                'speechId': 'stale-speech-id',
            })
            interrupt_response = await post_json(session, base_url, '/interrupt_talk', {
                'sessionid': session_id,
                'speechId': interrupt_speech_id,
            })
            while not any(item.get('event') in ('speech-interrupted', 'speech-error') for item in interrupt_events):
                event = await asyncio.wait_for(lifecycle_events.get(), tts_timeout)
                if event.get('speechId') == interrupt_speech_id:
                    interrupt_events.append(event)

            return {
                'sessionId': session_id,
                'dataChannel': channel.readyState,
                'neutralAction': neutral.get('data'),
                'thinkingFallback': thinking.get('data'),
                'acceptedSpeechId': accepted.get('data', {}).get('speechId'),
                'lifecycle': [item.get('event') for item in observed],
                'speechIdsMatch': all(item.get('speechId') == speech_id for item in observed),
                'mediaConsumers': len(consumers),
                'interruptResponse': interrupt_response.get('data'),
                'staleInterruptResponse': stale_interrupt_response.get('data'),
                'interruptLifecycle': [item.get('event') for item in interrupt_events],
                'interruptSpeechIdsMatch': all(
                    item.get('speechId') == interrupt_speech_id for item in interrupt_events
                ),
            }
    finally:
        if session_id:
            try:
                async with aiohttp.ClientSession() as session:
                    await post_json(session, base_url, '/close_session', {'sessionid': session_id})
            except Exception:
                pass
        await pc.close()
        for task in consumers:
            task.cancel()
        await asyncio.gather(*consumers, return_exceptions=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8010')
    parser.add_argument('--tts-timeout', type=float, default=45)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.base_url.rstrip('/'), args.tts_timeout)), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
