###############################################################################
#  Copyright (C) 2024 LiveTalking@lipku https://github.com/lipku/LiveTalking
#  email: lipku@foxmail.com
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
#
#  Avatar 基类 — 合并自 basereal.py，集成到 Async Pipeline
#

import math
from numpy.typing import NDArray
import torch
import numpy as np
import subprocess
import os
import time
import cv2
import glob
import resampy
import queue
from queue import Queue
from threading import Thread, Event
from io import BytesIO
import soundfile as sf
import asyncio
import threading
from datetime import datetime, timezone
from enum import Enum
import json
import importlib
import registry

import torch.multiprocessing as mp
from dataclasses import dataclass, field

from av import AudioFrame, VideoFrame
from fractions import Fraction

from utils.logger import logger
from utils.image import read_imgs,mirror_index

# class State(Enum):
#     INIT=0
#     WAIT=1
#     QUESTION=2
#     ANSWER=3

@dataclass
class AudioFrameData:
    data: NDArray[np.float32]
    type: int = 0  # 默认值
    userdata: dict = field(default_factory=dict)

class BaseAvatar:
    def __init__(self, opt):
        self.opt = opt
        self.sample_rate = 16000
        self.chunk = self.sample_rate // (opt.fps*2) # 320 samples per chunk (20ms)
        self.sessionid = self.opt.sessionid

        self.speaking = False
        self.rendering_speech = False
        self._speech_lock = threading.RLock()
        self._speech_id = None
        self._speech_updated_at = self._utc_now()
        self._speech_event_publisher = None
        self._custom_lock = threading.RLock()
        self.recording = False
        self._record_video_pipe = None
        self._record_audio_pipe = None
        self.width = self.height = 0

        self.custom_audiotype = 0 # 0: normal, 1: sinlence, >1: custom audio
        self.custom_img_cycle = {}
        self.custom_audio_cycle = {}
        self.custom_audio_index = {}
        self.custom_index = {}
        self.custom_loop_modes = {}
        self.custom_action_types = {}
        self.active_action = 'NEUTRAL'
        # self.custom_opt = {}
        self.__loadcustom()

        self.batch_size = opt.batch_size
        self.res_frame_queue = Queue(self.batch_size*2)
        self.render_event = Event()

        _tts_modules = {
            'edgetts': 'tts.edge',
            'voxcpmgradio': 'tts.voxcpmgradio',
            'gpt-sovits': 'tts.sovits',
            'xtts': 'tts.xtts',
            'cosyvoice': 'tts.cosyvoice',
            'fishtts': 'tts.fish',
            'tencent': 'tts.tencent',
            'doubao': 'tts.doubao',
            'indextts2': 'tts.indextts2',
            'azuretts': 'tts.azure',
            'qwentts': 'tts.qwentts'
        }

        if opt.tts in _tts_modules:
            importlib.import_module(_tts_modules[opt.tts])
            self.tts = registry.create("tts", opt.tts, opt=opt, parent=self)
        else:
            logger.error(f"TTS module {opt.tts} not found.")

        _output_modules = {
            'webrtc': 'streamout.webrtc',
            'rtcpush': 'streamout.webrtc',
            'rtmp': 'streamout.rtmp',
            'virtualcam': 'streamout.virtualcam'
        }

        # 初始化 Output 模块
        if opt.transport in _output_modules:
            try:
                importlib.import_module(_output_modules[opt.transport])
                self.output = registry.create("streamout", opt.transport, opt=opt, parent=self)
            except ModuleNotFoundError:
                logger.error(f"Output transport module {_output_modules[opt.transport]} not found.")
        else:
            logger.error(f"Output transport {opt.transport} not found in map.")

    # 如果系统没有使用 pipeline，或者为了向后兼容原来的 ttsreal.py
    @staticmethod
    def _utc_now():
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def set_speech_event_publisher(self, publisher):
        """设置 WebRTC 生命周期事件发布器；publisher 可从媒体线程调用。"""
        with self._speech_lock:
            self._speech_event_publisher = publisher

    def register_speech(self, speech_id: str):
        """在 TTS 入队前登记当前播报，使旧任务的迟到事件可被识别。"""
        with self._speech_lock:
            self._speech_id = speech_id
            self.speaking = False
            self._speech_updated_at = self._utc_now()

    def get_speech_status(self):
        with self._speech_lock:
            return {
                'speaking': bool(self.speaking),
                'speechId': self._speech_id,
                'updatedAt': self._speech_updated_at,
            }

    def put_msg_txt(self, msg, datainfo=None):
        datainfo = dict(datainfo or {})
        if hasattr(self, 'tts'):
            self.tts.put_msg_txt(msg, datainfo)
    
    def put_audio_frame(self, audio_chunk:NDArray[np.float32], datainfo:dict={}): # 16khz 20ms pcm
        if hasattr(self, 'asr'):
            self.asr.put_audio_frame(audio_chunk, datainfo)

    def put_audio_file(self, filebyte, datainfo:dict={}): 
        input_stream = BytesIO(filebyte)
        stream = self.__create_bytes_stream(input_stream)
        streamlen = stream.shape[0]
        idx = 0
        first = True
        while streamlen >= self.chunk:
            eventpoint = {}
            if first:
                eventpoint = {'status': 'start'}
                first = False
            if streamlen - self.chunk < self.chunk:
                eventpoint = {'status': 'end'}
            eventpoint.update(**datainfo) 
            self.put_audio_frame(stream[idx:idx+self.chunk], eventpoint)
            streamlen -= self.chunk
            idx += self.chunk

    def put_audio_filepath(self, filepath, datainfo:dict={}): 
        stream = self.__create_bytes_stream(filepath)
        streamlen = stream.shape[0]
        idx = 0
        first = True
        while streamlen >= self.chunk:
            eventpoint = {}
            if first:
                eventpoint = {'status': 'start'}
                first = False
            if streamlen - self.chunk < self.chunk:
                eventpoint = {'status': 'end'}
            eventpoint.update(**datainfo) 
            self.put_audio_frame(stream[idx:idx+self.chunk], eventpoint)
            streamlen -= self.chunk
            idx += self.chunk
    
    def __create_bytes_stream(self, byte_stream):
        stream, sample_rate = sf.read(byte_stream) # [T*sample_rate,] float64
        logger.info(f'[INFO]put audio stream {sample_rate}: {stream.shape}')
        stream = stream.astype(np.float32)

        if stream.ndim > 1:
            logger.info(f'[WARN] audio has {stream.shape[1]} channels, only use the first.')
            stream = stream[:, 0]
    
        if sample_rate != self.sample_rate and stream.shape[0] > 0:
            logger.info(f'[WARN] audio sample rate is {sample_rate}, resampling into {self.sample_rate}.')
            stream = resampy.resample(x=stream, sr_orig=sample_rate, sr_new=self.sample_rate)

        return stream

    def flush_talk(self):
        if hasattr(self, 'tts') and hasattr(self.tts, 'flush_talk'):
            self.tts.flush_talk()
        if hasattr(self, 'asr') and hasattr(self.asr, 'flush_talk'):
            self.asr.flush_talk()
        with self._custom_lock:
            self.custom_audiotype = 0
            self.active_action = 'NEUTRAL'

    # def flush(self):
    #     self.flush_talk()

    def is_speaking(self) -> bool:
        return self.get_speech_status()['speaking']
    
    def __loadcustom(self):
        if not hasattr(self.opt, 'customopt') or not self.opt.customopt:
            return
        for item in self.opt.customopt:
            logger.info(item)
            review_status = str(item.get('reviewStatus', 'pending')).strip().lower()
            if review_status != 'approved':
                logger.info(
                    'custom action not loaded; reviewStatus=%s action=%s',
                    review_status, item.get('action'))
                continue
            input_img_list = glob.glob(os.path.join(item['imgpath'], '*.[jpJP][pnPN]*[gG]'))
            input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            if not input_img_list:
                logger.warning('custom action skipped; no image frames: %s', item.get('imgpath'))
                continue
            try:
                start_frame = int(item.get('startFrame', 0))
                end_frame = int(item.get('endFrame', len(input_img_list) - 1))
            except (TypeError, ValueError):
                logger.warning('custom action skipped; frame range must be integers: %s', item)
                continue
            if not 0 <= start_frame <= end_frame < len(input_img_list):
                logger.warning(
                    'custom action skipped; invalid frame range %s-%s for %s frames',
                    start_frame, end_frame, len(input_img_list))
                continue
            input_img_list = input_img_list[start_frame:end_frame + 1]
            loop_mode = str(item.get('loopMode', 'ping-pong')).strip().lower()
            if loop_mode not in ('loop', 'ping-pong'):
                logger.warning('custom action skipped; unsupported loopMode: %s', loop_mode)
                continue
            self.custom_img_cycle[item['audiotype']] = read_imgs(input_img_list)
            self.custom_loop_modes[item['audiotype']] = loop_mode
            if item.get('audiopath'):
                if os.path.isfile(item['audiopath']):
                    audio, sample_rate = sf.read(item['audiopath'], dtype='float32')
                    if audio.ndim > 1:
                        audio = audio.mean(axis=1)
                    if sample_rate != self.sample_rate:
                        logger.info('resampling custom action audio: %sHz -> %sHz', sample_rate, self.sample_rate)
                        audio = resampy.resample(audio, sample_rate, self.sample_rate)
                    self.custom_audio_cycle[item['audiotype']] = np.asarray(audio, dtype=np.float32)
                    self.custom_audio_index[item['audiotype']] = 0
                else:
                    logger.warning('custom action audio missing; loading as silent loop: %s', item['audiopath'])
            self.custom_index[item['audiotype']] = 0
            action = str(item.get('action') or '').strip().upper()
            if action:
                self.custom_action_types[action] = item['audiotype']
            # self.custom_opt[item['audiotype']] = item

    def init_customindex(self):
        with self._custom_lock:
            self.custom_audiotype = 0
            self.active_action = 'NEUTRAL'
            for key in self.custom_audio_index:
                self.custom_audio_index[key] = 0
            for key in self.custom_index:
                self.custom_index[key] = 0

    def notify(self, eventpoint:dict):
        if not eventpoint or eventpoint.get('status') not in ('start', 'end', 'error', 'interrupted'):
            return

        status = eventpoint['status']
        speech_id = eventpoint.get('speechId')
        timestamp = self._utc_now()
        with self._speech_lock:
            # A lifecycle event belongs only to the speech registered before TTS
            # enqueue. Terminal events arriving after that context was cleared are stale.
            stale = bool(speech_id and speech_id != self._speech_id)
            if not stale:
                if speech_id:
                    self._speech_id = speech_id
                self.speaking = status == 'start'
                self._speech_updated_at = timestamp
                if status in ('end', 'error', 'interrupted'):
                    self.speaking = False
                    self._speech_id = None
            publisher = self._speech_event_publisher

        lifecycle_event = {
            'event': {
                'start': 'speech-started',
                'end': 'speech-ended',
                'error': 'speech-error',
                'interrupted': 'speech-interrupted',
            }[status],
            'speechId': speech_id,
            'timestamp': timestamp,
            'stale': stale,
        }
        if eventpoint.get('error'):
            lifecycle_event['error'] = str(eventpoint['error'])
        logger.info("notify:%s", lifecycle_event)
        if publisher:
            try:
                publisher(lifecycle_event)
            except Exception:
                logger.exception('speech lifecycle publisher failed:')

    def notify_speech_error(self, speech_id, error):
        self.notify({'status': 'error', 'speechId': speech_id, 'error': error})

    def interrupt_speech(self, expected_speech_id=None):
        """Stop only the currently registered speech and publish a confirmed lifecycle event."""
        with self._speech_lock:
            active_speech_id = self._speech_id
            if not active_speech_id:
                return {
                    'interrupted': False,
                    'speechId': None,
                    'reason': 'no-active-speech',
                }
            if expected_speech_id and expected_speech_id != active_speech_id:
                return {
                    'interrupted': False,
                    'speechId': active_speech_id,
                    'reason': 'speech-id-mismatch',
                }
            self.flush_talk()
            self.notify({'status': 'interrupted', 'speechId': active_speech_id})
            return {
                'interrupted': True,
                'speechId': active_speech_id,
                'reason': 'output-pipeline-flushed',
            }

    def start_recording(self):
        if self.recording:
            return
        command = ['ffmpeg',
                    '-y', '-an',
                    '-f', 'rawvideo',
                    '-vcodec','rawvideo',
                    '-pix_fmt', 'bgr24',
                    '-s', "{}x{}".format(self.width, self.height),
                    '-r', str(25),
                    '-i', '-',
                    '-pix_fmt', 'yuv420p', 
                    '-vcodec', "h264",
                    f'temp{self.opt.sessionid}.mp4']
        self._record_video_pipe = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE)

        acommand = ['ffmpeg',
                    '-y', '-vn',
                    '-f', 's16le',
                    '-ac', '1',
                    '-ar', '16000',
                    '-i', '-',
                    '-acodec', 'aac',
                    f'temp{self.opt.sessionid}.aac']
        self._record_audio_pipe = subprocess.Popen(acommand, shell=False, stdin=subprocess.PIPE)

        self.recording = True
    
    def record_video_data(self, image):
        if self.width == 0:
            self.height, self.width, _ = image.shape
        if self.recording:
            self._record_video_pipe.stdin.write(image.tostring())

    def record_audio_data(self, frame):
        if self.recording:
            self._record_audio_pipe.stdin.write(frame.tostring())
		
    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False 
        self._record_video_pipe.stdin.close()
        self._record_video_pipe.wait()
        self._record_audio_pipe.stdin.close()
        self._record_audio_pipe.wait()
        cmd_combine_audio = f"ffmpeg -y -i temp{self.opt.sessionid}.aac -i temp{self.opt.sessionid}.mp4 -c:v copy -c:a copy data/record.mp4"
        os.system(cmd_combine_audio)

    # def mirror_index(self, size, index):
    #     turn = index // size
    #     res = index % size
    #     if turn % 2 == 0:
    #         return res
    #     else:
    #         return size - res - 1 
    
    def get_custom_audio_stream(self, audiotype):
        with self._custom_lock:
            if audiotype not in self.custom_audio_cycle:
                return np.zeros(self.chunk, dtype=np.float32)
            idx = self.custom_audio_index[audiotype]
            stream = self.custom_audio_cycle[audiotype][idx:idx+self.chunk]
            self.custom_audio_index[audiotype] += self.chunk
            if self.custom_audio_index[audiotype] >= self.custom_audio_cycle[audiotype].shape[0]:
                self.custom_audiotype = 1
                self.active_action = 'NEUTRAL'
            if stream.shape[0] < self.chunk:
                stream = np.pad(stream, (0, self.chunk - stream.shape[0]))
            return stream
    
    def set_custom_state(self, audiotype, reinit=True):
        logger.info('set_custom_state: %s', audiotype)
        try:
            audiotype = int(audiotype)
        except (TypeError, ValueError):
            return False
        with self._custom_lock:
            if audiotype not in (0, 1) and audiotype not in self.custom_img_cycle:
                return False
            self.custom_audiotype = audiotype
            if reinit:
                if audiotype in self.custom_audio_index:
                    self.custom_audio_index[audiotype] = 0
                if audiotype in self.custom_index:
                    self.custom_index[audiotype] = 0
            return True

    def get_action_capabilities(self):
        with self._custom_lock:
            return sorted({'NEUTRAL', 'SPEAKING', *self.custom_action_types.keys()})

    def set_action_state(self, action):
        requested = str(action or 'NEUTRAL').strip().upper()
        capabilities = self.get_action_capabilities()
        with self._speech_lock:
            speech_in_flight = bool(self._speech_id)

        if requested == 'SPEAKING':
            self.set_custom_state(0)
            with self._custom_lock:
                self.active_action = 'SPEAKING'
            return {
                'applied': True,
                'appliedAction': 'SPEAKING',
                'reason': 'tts-lipsync-controls-speaking',
                'capabilities': capabilities,
            }
        if requested == 'ERROR':
            self.set_custom_state(0)
            with self._custom_lock:
                self.active_action = 'NEUTRAL'
            return {
                'applied': False,
                'appliedAction': 'NEUTRAL',
                'reason': 'error-safe-neutral',
                'capabilities': capabilities,
            }
        if speech_in_flight:
            return {
                'applied': False,
                'appliedAction': 'SPEAKING',
                'reason': 'speech-in-flight-protected',
                'capabilities': capabilities,
            }

        audiotype = self.custom_action_types.get(requested)
        if audiotype is not None and self.set_custom_state(audiotype):
            with self._custom_lock:
                self.active_action = requested
            return {
                'applied': True,
                'appliedAction': requested,
                'reason': 'custom-action-loaded',
                'capabilities': capabilities,
            }
        if requested == 'NEUTRAL':
            self.set_custom_state(0)
            with self._custom_lock:
                self.active_action = 'NEUTRAL'
            return {
                'applied': True,
                'appliedAction': 'NEUTRAL',
                'reason': 'base-idle-cycle',
                'capabilities': capabilities,
            }
        self.set_custom_state(0)
        with self._custom_lock:
            self.active_action = 'NEUTRAL'
        return {
            'applied': False,
            'appliedAction': 'NEUTRAL',
            'reason': 'action-resource-unavailable',
            'capabilities': capabilities,
        }

    # ========================== 核心渲染及 Pipeline 桥接 ==========================
    def get_avatar_length(self):
        if hasattr(self, 'frame_list_cycle'):
            return len(self.frame_list_cycle)
        return 1
        
    def inference(self, quit_event):
        length = self.get_avatar_length()
        index = 0
        count = 0
        counttime = 0
        last_speaking = False

        # syncnet_T = 12  # 时间步
        # weight_dtype = torch.float16  # 数据类型
        # infernum = 0
        logger.info('start inference')
        while not quit_event.is_set():
            starttime = time.perf_counter()
            audiofeat_batch = []
            try:
                audiofeat_batch = self.asr.feat_queue.get(block=True, timeout=1)
            except queue.Empty:
                continue
                
            is_all_silence = True
            audio_frames: list[AudioFrameData] = []
            for _ in range(self.batch_size * 2):
                audioframe:AudioFrameData = self.asr.output_queue.get()
                if audioframe.type == 0:
                    is_all_silence = False               
                audio_frames.append(audioframe)

             # 检测状态变化
            current_speaking = not is_all_silence

            if is_all_silence: #全为静音数据，只需要取fullimg，不需要推理
                for i in range(self.batch_size):
                    idx = mirror_index(length, index)
                    self.res_frame_queue.put((None, audio_frames[i*2:i*2+2], idx))
                    index = index + 1
            else:
                if current_speaking and not last_speaking and self.custom_index.get(1) is not None: #从静音到说话切换,并且有自定义静态视频
                    index = 0
                t = time.perf_counter()

                pred = self.inference_batch(index, audiofeat_batch)

                counttime += (time.perf_counter() - t)
                count += self.batch_size
                if count >= 100:
                    logger.info(f"------actual avg infer fps:{count/counttime:.4f}")
                    count = 0
                    counttime = 0
                for i, res_frame in enumerate(pred):
                    self.res_frame_queue.put((res_frame, audio_frames[i*2:i*2+2], mirror_index(length, index)))
                    index = index + 1
                    
            if current_speaking != last_speaking:
                logger.info(f"inference 状态切换：{'说话' if last_speaking else '静音'} → {'说话' if current_speaking else '静音'}")
                last_speaking = current_speaking         
        logger.info('baseavatar inference thread stop')

    def process_frames(self,quit_event):
        enable_transition = False  # 设置为False禁用过渡效果，True启用
        smooth_state_transition = True
        state_transition_duration = 0.12
        state_transition_started_at = 0.0
        state_transition_source = None
        last_output_frame = None
        last_output_type = None
        
        _last_speaking = False
        _transition_start = time.time()
        if enable_transition:
            _transition_duration = 0.1  # 过渡时间
            _last_silent_frame = None  # 静音帧缓存
            _last_speaking_frame = None  # 说话帧缓存

        self.output.start()
        
        while not quit_event.is_set():
            try:
                audio_frames: list[AudioFrameData]
                res_frame,audio_frames,idx = self.res_frame_queue.get(block=True, timeout=1)
            except queue.Empty:
                continue
            
            # 检测状态变化
            current_speaking = not (audio_frames[0].type!=0 and audio_frames[1].type!=0)
            output_type = 0 if current_speaking else audio_frames[0].type
            if output_type != last_output_type:
                state_transition_started_at = time.time()
                state_transition_source = last_output_frame.copy() if last_output_frame is not None else None
                last_output_type = output_type
            if current_speaking != _last_speaking:
                logger.info(f"状态切换：{'说话' if _last_speaking else '静音'} → {'说话' if current_speaking else '静音'}")
                _transition_start = time.time()
            _last_speaking = current_speaking

            if audio_frames[0].type!=0 and audio_frames[1].type!=0: #全为静音数据，只需要取fullimg
                self.rendering_speech = False
                audiotype = audio_frames[0].type
                if self.custom_index.get(audiotype) is not None: #有自定义视频
                    frame_count = len(self.custom_img_cycle[audiotype])
                    if self.custom_loop_modes.get(audiotype) == 'loop':
                        frame_index = self.custom_index[audiotype] % frame_count
                    else:
                        frame_index = mirror_index(frame_count, self.custom_index[audiotype])
                    target_frame = self.custom_img_cycle[audiotype][frame_index]
                    self.custom_index[audiotype] += 1
                else:
                    target_frame = self.frame_list_cycle[idx]
                
                if enable_transition:
                    # 说话→静音过渡
                    if time.time() - _transition_start < _transition_duration and _last_speaking_frame is not None:
                        alpha = min(1.0, (time.time() - _transition_start) / _transition_duration)
                        combine_frame = cv2.addWeighted(_last_speaking_frame, 1-alpha, target_frame, alpha, 0)
                    else:
                        combine_frame = target_frame
                    # 缓存静音帧
                    _last_silent_frame = combine_frame.copy()
                else:
                    combine_frame = target_frame
            else:
                self.rendering_speech = True
                try:
                    current_frame = self.paste_back_frame(res_frame,idx)
                except Exception as e:
                    logger.warning(f"paste_back_frame error: {e}")
                    continue
                if enable_transition:
                    # 静音→说话过渡
                    if time.time() - _transition_start < _transition_duration and _last_silent_frame is not None:
                        alpha = min(1.0, (time.time() - _transition_start) / _transition_duration)
                        combine_frame = cv2.addWeighted(_last_silent_frame, 1-alpha, current_frame, alpha, 0)
                    else:
                        combine_frame = current_frame
                    # 缓存说话帧
                    _last_speaking_frame = combine_frame.copy()
                else:
                    combine_frame = current_frame

            if smooth_state_transition and state_transition_source is not None:
                elapsed = time.time() - state_transition_started_at
                if elapsed < state_transition_duration and state_transition_source.shape == combine_frame.shape:
                    alpha = min(1.0, elapsed / state_transition_duration)
                    combine_frame = cv2.addWeighted(state_transition_source, 1 - alpha, combine_frame, alpha, 0)
                else:
                    state_transition_source = None
            last_output_frame = combine_frame.copy()

            cv2.putText(combine_frame, "LiveTalking", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (128,128,128), 1)
            
            # 使用统一输出接口推送视频帧
            self.output.push_video_frame(combine_frame)
            self.record_video_data(combine_frame)

            for audio_frame in audio_frames:
                #frame,type,eventpoint = audio_frame
                frame = (audio_frame.data * 32767).astype(np.int16)

                # 使用统一输出接口推送音频帧
                self.output.push_audio_frame(frame, audio_frame.userdata)
                self.record_audio_data(frame)
                
            # if self.opt.transport == 'virtualcam' and hasattr(self.output, '_cam') and self.output._cam:
            #     self.output._cam.sleep_until_next_frame()

        self.output.stop()
        logger.info('baseavatar process_frames thread stop') 

    def render(self,quit_event):
        self.quit_event = quit_event
        
        self.init_customindex()
        self.tts.render(quit_event)

        infer_quit_event = mp.Event()
        infer_thread = Thread(target=self.inference, args=(infer_quit_event,))
        infer_thread.start()
        
        process_quit_event = Event()
        process_thread = Thread(target=self.process_frames, args=(process_quit_event,))
        process_thread.start()

        count=0
        totaltime=0
        _starttime=time.perf_counter()
        _totalframe=0
        while not quit_event.is_set(): 
            t = time.perf_counter()
            self.asr.run_step()

            buffer_size = self.output.get_buffer_size() if hasattr(self.output, 'get_buffer_size') else 0
            if buffer_size >= 5:
                logger.debug('sleep qsize=%d', buffer_size)
                time.sleep(0.04 * buffer_size * 0.8)
        logger.info('baseavatar render thread stop')

        infer_quit_event.set()
        infer_thread.join()

        process_quit_event.set()
        process_thread.join()
