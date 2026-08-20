"""Analyze, preview, validate, and import real digital-human action frames.

This tool never synthesizes or geometrically transforms a person. Imported video
or frames must already be 544x960 at 25 FPS; previews only add diagnostic text.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import resampy
import soundfile as sf


EXPECTED_SIZE = (544, 960)
EXPECTED_FPS = 25.0
VALID_ACTIONS = {'NEUTRAL', 'LISTENING', 'LISTENING_PAUSE', 'THINKING'}
VALID_REVIEW_STATUSES = {'pending', 'approved', 'rejected'}


@dataclass
class Candidate:
    category: str
    start_frame: int
    end_frame: int
    duration_seconds: float
    mean_motion: float
    p90_motion: float
    face_motion: float
    upper_body_motion: float
    arm_motion: float
    mouth_motion: float
    seam_difference: float
    seam_score: float
    score: float


def numbered_images(frame_dir: Path) -> list[Path]:
    images = [path for path in frame_dir.iterdir() if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}]
    try:
        return sorted(images, key=lambda path: int(path.stem))
    except ValueError as error:
        raise ValueError('Frame filenames must be numeric so temporal order is unambiguous') from error


def read_image(path: Path) -> np.ndarray | None:
    """Read an image without relying on OpenCV's Windows Unicode path support."""
    try:
        payload = np.fromfile(path, dtype=np.uint8)
    except OSError:
        return None
    return cv2.imdecode(payload, cv2.IMREAD_COLOR)


def write_image(path: Path, image: np.ndarray) -> None:
    """Write an image to paths containing non-ASCII characters on Windows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    extension = path.suffix or '.png'
    success, payload = cv2.imencode(extension, image)
    if not success:
        raise RuntimeError(f'OpenCV cannot encode image as {extension}: {path}')
    payload.tofile(path)


def load_frames(frame_dir: Path) -> tuple[list[Path], list[np.ndarray]]:
    paths = numbered_images(frame_dir)
    if not paths:
        raise ValueError(f'No image frames found in {frame_dir}')
    frames = []
    shape = None
    for path in paths:
        frame = read_image(path)
        if frame is None:
            raise ValueError(f'Unreadable frame: {path}')
        if shape is None:
            shape = frame.shape
        if frame.shape != shape:
            raise ValueError(f'Frame resolution mismatch: {path} is {frame.shape}, expected {shape}')
        frames.append(frame)
    return paths, frames


def detect_face_box(frames: list[np.ndarray]) -> tuple[tuple[int, int, int, int], str]:
    height, width = frames[0].shape[:2]
    fallback = (int(width * .27), int(height * .16), int(width * .46), int(height * .32))
    if not hasattr(cv2, 'CascadeClassifier') or not hasattr(cv2, 'data'):
        return fallback, 'proportional-fallback'
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detections = []
    for index in np.linspace(0, len(frames) - 1, min(12, len(frames)), dtype=int):
        gray = cv2.cvtColor(frames[index], cv2.COLOR_BGR2GRAY)
        found = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(80, 80))
        if len(found):
            detections.append(max(found, key=lambda box: box[2] * box[3]))
    if not detections:
        return fallback, 'proportional-fallback'
    values = np.median(np.asarray(detections), axis=0).astype(int)
    return tuple(int(value) for value in values), 'haar-cascade-median'


def clipped_box(x1, y1, x2, y2, width, height):
    return max(0, x1), max(0, y1), min(width, x2), min(height, y2)


def build_regions(face_box, frame_shape, scale=.5):
    height, width = frame_shape[:2]
    x, y, w, h = face_box
    boxes = {
        'face': clipped_box(x, y, x + w, y + h, width, height),
        'head': clipped_box(x - int(.25*w), y - int(.2*h), x + int(1.25*w), y + int(1.3*h), width, height),
        'mouth': clipped_box(x + int(.2*w), y + int(.58*h), x + int(.8*w), y + int(.92*h), width, height),
        'upper_body': clipped_box(int(.12*width), y + h, int(.88*width), int(.86*height), width, height),
        'arms': None,
    }
    scaled = {}
    for name, box in boxes.items():
        if box is not None:
            scaled[name] = tuple(int(value * scale) for value in box)
    scaled['arms'] = [
        (0, int(.42*height*scale), int(.3*width*scale), int(.95*height*scale)),
        (int(.7*width*scale), int(.42*height*scale), int(width*scale), int(.95*height*scale)),
    ]
    return scaled


def roi_mean(array, box):
    x1, y1, x2, y2 = box
    roi = array[y1:y2, x1:x2]
    return float(np.mean(roi)) if roi.size else 0.0


def analyze_motion(frames: list[np.ndarray]):
    scale = .5
    grays = [cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), None, fx=scale, fy=scale) for frame in frames]
    face_box, face_region_method = detect_face_box(frames)
    regions = build_regions(face_box, frames[0].shape, scale)
    rows = []
    for index, gray in enumerate(grays):
        if index == 0:
            row = dict(frame=index, frame_difference=0, global_motion=0, face_motion=0,
                       head_motion=0, upper_body_motion=0, arm_motion=0, mouth_motion=0,
                       motion_intensity=0)
        else:
            previous = grays[index - 1]
            flow = cv2.calcOpticalFlowFarneback(previous, gray, None, .5, 3, 15, 3, 5, 1.2, 0)
            magnitude = cv2.magnitude(flow[..., 0], flow[..., 1])
            arms = np.mean([roi_mean(magnitude, box) for box in regions['arms']])
            metrics = {
                'global_motion': float(np.mean(magnitude)),
                'face_motion': roi_mean(magnitude, regions['face']),
                'head_motion': roi_mean(magnitude, regions['head']),
                'upper_body_motion': roi_mean(magnitude, regions['upper_body']),
                'arm_motion': float(arms),
                'mouth_motion': roi_mean(magnitude, regions['mouth']),
            }
            intensity = (.25 * metrics['global_motion'] + .25 * metrics['head_motion']
                         + .18 * metrics['upper_body_motion'] + .17 * metrics['arm_motion']
                         + .15 * metrics['mouth_motion'])
            row = dict(
                frame=index,
                frame_difference=float(np.mean(cv2.absdiff(previous, gray)) / 255.0),
                motion_intensity=float(intensity),
                **metrics,
            )
        rows.append(row)
    return rows, grays, face_box, regions, face_region_method


def contiguous_intervals(values, low_threshold, high_threshold, fps):
    labels = np.where(values <= low_threshold, 'low', np.where(values <= high_threshold, 'light', 'action'))
    intervals = []
    start = 0
    for index in range(1, len(labels) + 1):
        if index == len(labels) or labels[index] != labels[start]:
            if index - start >= 5:
                intervals.append({
                    'classification': str(labels[start]),
                    'startFrame': int(start),
                    'endFrame': int(index - 1),
                    'durationSeconds': round((index - start) / fps, 3),
                    'meanMotion': round(float(np.mean(values[start:index])), 6),
                })
            start = index
    return intervals


def seam_difference(grays, start, end, box):
    x1, y1, x2, y2 = box
    first = grays[start][y1:y2, x1:x2]
    last = grays[end][y1:y2, x1:x2]
    return float(np.mean(cv2.absdiff(first, last)) / 255.0)


def select_candidates(rows, grays, regions, fps):
    motion = np.asarray([row['motion_intensity'] for row in rows])
    positive = motion[1:]
    q20, q45, q70, q90 = np.quantile(positive, [.2, .45, .7, .9])
    raw = []
    max_seam = .08
    for length in (50, 75, 100, 125):
        for start in range(0, len(rows) - length + 1, 5):
            end = start + length - 1
            segment = rows[start:end + 1]
            values = motion[start:end + 1]
            seam = .55 * seam_difference(grays, start, end, regions['head']) \
                + .45 * seam_difference(grays, start, end, (0, 0, grays[0].shape[1], grays[0].shape[0]))
            seam_score = max(0.0, 1.0 - seam / max_seam)
            common = dict(
                start_frame=start,
                end_frame=end,
                duration_seconds=length / fps,
                mean_motion=float(np.mean(values)),
                p90_motion=float(np.quantile(values, .9)),
                face_motion=float(np.mean([item['face_motion'] for item in segment])),
                upper_body_motion=float(np.mean([item['upper_body_motion'] for item in segment])),
                arm_motion=float(np.mean([item['arm_motion'] for item in segment])),
                mouth_motion=float(np.mean([item['mouth_motion'] for item in segment])),
                seam_difference=seam,
                seam_score=seam_score,
            )
            neutral_motion = 1 - min(1.0, common['mean_motion'] / max(q45, 1e-6))
            neutral_score = .48 * seam_score + .34 * neutral_motion + .18 * (1 - min(1, common['p90_motion']/max(q90, 1e-6)))
            raw.append(Candidate('NEUTRAL', score=float(neutral_score), **common))

            target = (q45 + q70) / 2
            target_score = max(0.0, 1 - abs(common['mean_motion'] - target) / max(target, 1e-6))
            quiet_mouth = 1 - min(1.0, common['mouth_motion'] / max(q90, 1e-6))
            quiet_arms = 1 - min(1.0, common['arm_motion'] / max(q90 * 1.5, 1e-6))
            listening_score = .42 * seam_score + .3 * target_score + .16 * quiet_mouth + .12 * quiet_arms
            raw.append(Candidate('LISTENING', score=float(listening_score), **common))

            pause_target = q20
            pause_motion = max(0.0, 1 - abs(common['mean_motion'] - pause_target) / max(q45, 1e-6))
            pause_score = .5 * seam_score + .35 * pause_motion + .15 * quiet_mouth
            raw.append(Candidate('LISTENING_PAUSE', score=float(pause_score), **common))

    selected = {}
    for category in ('NEUTRAL', 'LISTENING', 'LISTENING_PAUSE'):
        choices = sorted((item for item in raw if item.category == category), key=lambda item: item.score, reverse=True)
        kept = []
        for choice in choices:
            if all(interval_iou(choice, other) < .6 for other in kept):
                kept.append(choice)
            if len(kept) == 3:
                break
        selected[category] = kept
    return selected, {'q20': q20, 'q45': q45, 'q70': q70, 'q90': q90}


def interval_iou(left, right):
    overlap = max(0, min(left.end_frame, right.end_frame) - max(left.start_frame, right.start_frame) + 1)
    union = max(left.end_frame, right.end_frame) - min(left.start_frame, right.start_frame) + 1
    return overlap / union


def open_writer(path: Path, size, fps):
    path.parent.mkdir(parents=True, exist_ok=True)
    # mp4v is broadly available in OpenCV wheels; try H.264 only as fallback.
    for codec in ('mp4v', 'avc1'):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*codec), fps, size)
        if writer.isOpened():
            return writer, codec
        writer.release()
    raise RuntimeError('OpenCV cannot create MP4 with avc1 or mp4v on this machine')


def labeled_frame(frame, label):
    output = frame.copy()
    cv2.rectangle(output, (8, 8), (min(output.shape[1] - 8, 510), 44), (0, 0, 0), -1)
    cv2.putText(output, label, (16, 33), cv2.FONT_HERSHEY_SIMPLEX, .55, (255, 255, 255), 1, cv2.LINE_AA)
    return output


def write_candidate_preview(frames, candidate, path, fps, cycles=3):
    height, width = frames[0].shape[:2]
    writer, codec = open_writer(path, (width, height), fps)
    label = (f'{candidate.category} {candidate.start_frame}-{candidate.end_frame} '
             f'seam={candidate.seam_score:.3f}')
    try:
        for _ in range(cycles):
            for index in range(candidate.start_frame, candidate.end_frame + 1):
                writer.write(labeled_frame(frames[index], label))
    finally:
        writer.release()
    return codec


def write_comparison(frames, candidates, path, fps, cycles=3):
    selected = [candidates[name][0] for name in ('NEUTRAL', 'LISTENING', 'LISTENING_PAUSE')]
    height, width = frames[0].shape[:2]
    panel_width = width // 2
    panel_height = height // 2
    writer, codec = open_writer(path, (panel_width * 3, panel_height), fps)
    sequences = [list(range(item.start_frame, item.end_frame + 1)) for item in selected]
    total = max(len(sequence) for sequence in sequences) * cycles
    try:
        for step in range(total):
            panels = []
            for candidate, sequence in zip(selected, sequences):
                frame = cv2.resize(frames[sequence[step % len(sequence)]], (panel_width, panel_height))
                panels.append(labeled_frame(frame, f'{candidate.category} {candidate.start_frame}-{candidate.end_frame} seam={candidate.seam_score:.3f}'))
            writer.write(np.hstack(panels))
    finally:
        writer.release()
    return codec


def write_contact_sheet(frames, candidates, path):
    rows = []
    for name in ('NEUTRAL', 'LISTENING', 'LISTENING_PAUSE'):
        candidate = candidates[name][0]
        indices = np.linspace(candidate.start_frame, candidate.end_frame, 5, dtype=int)
        tiles = []
        for index in indices:
            tile = cv2.resize(frames[index], (218, 384))
            tiles.append(labeled_frame(tile, f'{name} f{index}'))
        rows.append(np.hstack(tiles))
    write_image(path, np.vstack(rows))


def write_curve(rows, thresholds, output):
    frames = [row['frame'] for row in rows]
    plt.figure(figsize=(14, 7))
    for key, label in (
        ('motion_intensity', 'combined'), ('head_motion', 'head/face'),
        ('upper_body_motion', 'upper body'), ('arm_motion', 'arms'), ('mouth_motion', 'mouth')):
        plt.plot(frames, [row[key] for row in rows], label=label, linewidth=1)
    for key, color in (('q20', '#2f855a'), ('q45', '#3182ce'), ('q70', '#dd6b20')):
        plt.axhline(thresholds[key], linestyle='--', color=color, alpha=.6, label=key)
    plt.xlabel('Frame')
    plt.ylabel('Optical-flow magnitude (downsampled pixels/frame)')
    plt.title('Base idle motion intensity by region')
    plt.grid(alpha=.2)
    plt.legend(ncol=4)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def analyze_command(args):
    frame_dir = Path(args.frames).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths, frames = load_frames(frame_dir)
    height, width = frames[0].shape[:2]
    rows, grays, face_box, regions, face_region_method = analyze_motion(frames)
    motion = np.asarray([row['motion_intensity'] for row in rows])
    low, high = np.quantile(motion[1:], [.33, .75])
    intervals = contiguous_intervals(motion, low, high, args.fps)
    candidates, thresholds = select_candidates(rows, grays, regions, args.fps)

    with (output / 'frame_metrics.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    write_curve(rows, thresholds, output / 'motion_curve.png')
    codecs = {}
    preview_dir = output / 'previews'
    preview_dir.mkdir(exist_ok=True)
    for category, items in candidates.items():
        for rank, item in enumerate(items, 1):
            name = f'{category.lower()}_{rank}_{item.start_frame:03d}-{item.end_frame:03d}.mp4'
            codecs[name] = write_candidate_preview(frames, item, preview_dir / name, args.fps)
    codecs['comparison.mp4'] = write_comparison(frames, candidates, preview_dir / 'comparison.mp4', args.fps)
    write_contact_sheet(frames, candidates, output / 'candidate_contact_sheet.jpg')

    first_last = float(np.mean(cv2.absdiff(grays[0], grays[-1])) / 255.0)
    result = {
        'source': Path(args.frames).as_posix(),
        'frameCount': len(frames),
        'resolution': {'width': width, 'height': height},
        'fps': args.fps,
        'durationSeconds': len(frames) / args.fps,
        'faceBox': {'x': face_box[0], 'y': face_box[1], 'width': face_box[2], 'height': face_box[3]},
        'faceRegionMethod': face_region_method,
        'firstLastFrameDifference': first_last,
        'motionThresholds': {key: float(value) for key, value in thresholds.items()},
        'classifiedIntervals': intervals,
        'candidates': {name: [asdict(item) for item in items] for name, items in candidates.items()},
        'previewCodecs': codecs,
        'thinkingConfigured': False,
        'thinkingReason': 'Automated motion analysis cannot prove a real thinking pose; manual review is required.',
    }
    (output / 'analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    write_report(result, output / 'README.md')
    print(json.dumps(result, ensure_ascii=False, indent=2))


def write_report(result, path):
    lines = [
        '# 数字人基础待机帧动作分析', '',
        f"- 帧数：{result['frameCount']}",
        f"- 分辨率：{result['resolution']['width']}×{result['resolution']['height']}",
        f"- 帧率：{result['fps']} FPS", f"- 总时长：{result['durationSeconds']:.2f} 秒",
        f"- 首尾帧差异：{result['firstLastFrameDifference']:.6f}", '',
        '## 自动候选', '',
        '| 类别 | 帧范围 | 时长 | 平均运动 | 接缝评分 | 综合评分 |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for category, candidates in result['candidates'].items():
        for item in candidates:
            lines.append(
                f"| {category} | {item['start_frame']}–{item['end_frame']} | "
                f"{item['duration_seconds']:.2f}s | {item['mean_motion']:.4f} | "
                f"{item['seam_score']:.3f} | {item['score']:.3f} |"
            )
    lines += ['', '## 文件', '', '- `motion_curve.png`：逐帧区域运动曲线',
              '- `frame_metrics.csv`：逐帧原始指标', '- `candidate_contact_sheet.jpg`：候选关键帧',
              '- `previews/`：各候选三次循环及三栏对比视频', '',
              '> 自动评分只筛选候选，不能证明人物语义姿态。THINKING 必须人工确认后才能配置。', '']
    lines.insert(-1, '- `selection.md`：人工审核结论、最终运行区间和后续真实素材导入步骤')
    path.write_text('\n'.join(lines), encoding='utf-8')


def config_items(config_path):
    value = json.loads(Path(config_path).read_text(encoding='utf-8'))
    if not isinstance(value, list):
        raise ValueError('Action config must be a JSON array')
    return value


def validate_command(args):
    errors, warnings = [], []
    seen_actions, seen_types = set(), set()
    for item in config_items(args.config):
        action = str(item.get('action', '')).upper()
        audiotype = item.get('audiotype')
        review_status = str(item.get('reviewStatus', 'pending')).strip().lower()
        if action not in VALID_ACTIONS:
            errors.append(f'Unsupported action: {action or "<missing>"}')
        if action in seen_actions or audiotype in seen_types:
            errors.append(f'Duplicate action or audiotype: {action}/{audiotype}')
        seen_actions.add(action)
        seen_types.add(audiotype)
        if review_status not in VALID_REVIEW_STATUSES:
            errors.append(f'{action}: unsupported reviewStatus {review_status!r}')
        elif review_status == 'approved' and not item.get('approvedAt'):
            errors.append(f'{action}: approved action requires approvedAt')
        elif review_status != 'approved':
            warnings.append(f'{action}: reviewStatus={review_status}; runtime will use NEUTRAL fallback')
        frame_dir = Path(item.get('imgpath', ''))
        if not frame_dir.is_dir():
            errors.append(f'{action}: frame directory does not exist: {frame_dir}')
            continue
        paths, frames = load_frames(frame_dir)
        start = int(item.get('startFrame', 0))
        end = int(item.get('endFrame', len(frames) - 1))
        if not 0 <= start <= end < len(frames):
            errors.append(f'{action}: invalid frame range {start}-{end} for {len(frames)} frames')
        loop_mode = str(item.get('loopMode', 'ping-pong')).strip().lower()
        if loop_mode not in ('loop', 'ping-pong'):
            errors.append(f'{action}: unsupported loopMode {loop_mode!r}')
        configured_fps = float(item.get('fps', EXPECTED_FPS))
        if abs(configured_fps - EXPECTED_FPS) > .05:
            errors.append(f'{action}: configured FPS {configured_fps} is not 25')
        height, width = frames[0].shape[:2]
        if (width, height) != EXPECTED_SIZE:
            errors.append(f'{action}: resolution {width}x{height}, expected {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}')
        if item.get('audiopath'):
            audio_path = Path(item['audiopath'])
            if not audio_path.is_file():
                errors.append(f'{action}: audio does not exist: {audio_path}')
            else:
                audio, rate = sf.read(audio_path, always_2d=False)
                if rate != 16000 or audio.ndim != 1:
                    warnings.append(f'{action}: runtime will normalize audio to mono 16kHz')
    report = {'valid': not errors, 'errors': errors, 'warnings': warnings}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(2)


def import_command(args):
    action = args.action.upper()
    if action not in VALID_ACTIONS:
        raise ValueError(f'Unsupported action: {action}')
    source = Path(args.source).resolve()
    target = Path(args.target).resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError(f'Refusing to overwrite non-empty target: {target}')
    if source.is_dir():
        _, frames = load_frames(source)
        source_fps = args.fps
    else:
        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            raise ValueError(f'Cannot open video: {source}')
        source_fps = capture.get(cv2.CAP_PROP_FPS)
        frames = []
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frames.append(frame)
        capture.release()
    if abs(source_fps - EXPECTED_FPS) > .05:
        raise ValueError(f'FPS {source_fps} is not 25; re-export the real source without frame interpolation')
    if not frames:
        raise ValueError('No frames decoded')
    for index, frame in enumerate(frames):
        height, width = frame.shape[:2]
        if (width, height) != EXPECTED_SIZE:
            raise ValueError(f'Frame {index} is {width}x{height}; resizing is intentionally forbidden')
    audio_target = None
    normalized_audio = None
    if args.audio:
        audio, rate = sf.read(args.audio, dtype='float32')
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if rate != 16000:
            audio = resampy.resample(audio, rate, 16000)
        normalized_audio = audio
        audio_target = target.parent / f'{target.name}.wav'
    target.mkdir(parents=True, exist_ok=True)
    for index, frame in enumerate(frames):
        write_image(target / f'{index:08d}.png', frame)
    if normalized_audio is not None:
        sf.write(audio_target, normalized_audio, 16000, subtype='PCM_16')
    print(json.dumps({
        'action': action, 'frameCount': len(frames), 'fps': source_fps,
        'resolution': {'width': EXPECTED_SIZE[0], 'height': EXPECTED_SIZE[1]},
        'imgpath': str(target), 'audiopath': str(audio_target) if audio_target else None,
    }, ensure_ascii=False, indent=2))


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest='command', required=True)
    analyze = commands.add_parser('analyze', help='Analyze an existing numeric frame sequence read-only')
    analyze.add_argument('--frames', required=True)
    analyze.add_argument('--output', required=True)
    analyze.add_argument('--fps', type=float, default=EXPECTED_FPS)
    analyze.set_defaults(func=analyze_command)
    validate = commands.add_parser('validate', help='Validate an action JSON and all referenced real assets')
    validate.add_argument('--config', required=True)
    validate.set_defaults(func=validate_command)
    import_action = commands.add_parser('import', help='Import exact-size real video/frames without visual transforms')
    import_action.add_argument('--action', required=True)
    import_action.add_argument('--source', required=True)
    import_action.add_argument('--target', required=True)
    import_action.add_argument('--audio')
    import_action.add_argument('--fps', type=float, default=EXPECTED_FPS, help='FPS declaration for frame directories')
    import_action.set_defaults(func=import_command)
    return root


if __name__ == '__main__':
    arguments = parser().parse_args()
    arguments.func(arguments)
