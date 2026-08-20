# 基础待机帧人工筛选结论

## 候选区间（尚未批准上线）

当前三个候选的 `reviewStatus` 均为 `pending`。此前的技术筛选不等同于用户上线批准；数字人运行时不会加载这些区间，而是保持基础 `NEUTRAL` fallback。只有用户明确批准后，才能把对应项改为 `approved` 并记录 `approvedAt` 时间。

| 动作 | 帧范围 | 时长 | 接缝评分 | 人工结论 |
|---|---:|---:|---:|---|
| `NEUTRAL` | 240–289 | 2.00 秒 | 0.909 | pending；全片最低运动段，正视、无明显点头，适合长时间待机。 |
| `LISTENING` | 155–204 | 2.00 秒 | 0.882 | pending；正视并包含轻微眼睑、头部和上半身运动；未观察到连续说话口型。 |
| `LISTENING_PAUSE` | 230–279 | 2.00 秒 | 0.888 | pending；比倾听段安静且保持正视；与中性待机差异较弱。 |
| `THINKING` | 未配置 | — | — | 349 帧内没有足够明确的视线偏移、头部偏转或准备开口姿态，继续降级为 `NEUTRAL`。 |

运行配置只引用原始目录和帧范围，不复制或改写原始人物帧。三段均按 25 FPS 直接循环；没有缩放、插帧、慢放或几何形变。

## 指标解释与限制

- `motion_curve.png` 展示全帧、脸/头、嘴部、上半身及手臂区域的近似光流强度。
- `frame_metrics.csv` 保存逐帧指标，便于复核自动候选。
- 接缝评分根据候选首尾帧差异归一化，越接近 1 越自然；它不能证明人物动作语义。
- 当前 OpenCV 构建没有 Haar 分类器，因此脸部区域使用对本素材人工核对过的固定比例框。该限制已记录在分析结果的 `faceBox` 中，不影响原始帧。

## 后续真实动作素材导入

在 `数字人` 目录执行：

```powershell
.\.venv\Scripts\python.exe tools\avatar_action_pipeline.py import `
  --action THINKING `
  --source <真实25FPS视频或数字编号帧目录> `
  --target data\actions\thinking
```

导入器要求 544×960、25 FPS，不允许自动缩放或插帧；可选音频会规范为单声道 16 kHz。随后把资源写入 `offerpilot_actions.json`，再执行：

```powershell
.\.venv\Scripts\python.exe tools\avatar_action_pipeline.py validate `
  --config offerpilot_actions.json
```

正式采用前必须人工检查人物身份、姿态语义、嘴部动作、循环接缝和素材授权。
