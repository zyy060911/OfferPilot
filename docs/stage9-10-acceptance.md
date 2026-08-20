# 第九、十阶段验收记录

## A：基线验收

- 动作候选仍为 `pending`，运行时只允许加载 `approved` 且具有 `approvedAt` 的资源。
- `THINKING` 没有真实素材，继续回退到基础 `NEUTRAL`。
- 启动参数加载 `offerpilot_actions.json`，待审批动作不会进入运行能力列表。
- 本地隔离端口 8011 已真实完成 WebRTC 协商，DataChannel 为 `open`，音频和视频两条接收轨道均工作。
- `/set_audiotype` 的 `NEUTRAL` 成功，`THINKING` 返回明确 fallback。
- TTS 生命周期按同一 `speechId` 收到 `speech-started → speech-ended`。
- 自动三题测试覆盖新 answerId、重复提交阻止、迟到 ASR 丢弃、500ms guard 和结束清理。

本机 8010 仍由较高权限的旧开发进程占用，系统拒绝由当前任务停止。新代码使用隔离端口 8011 完成验证；正式继续使用 8010 前，需由启动该进程的管理员终端重启。

## B：受控语音打断

开关：

```dotenv
VITE_BARGE_IN_ENABLED=false
```

默认关闭。检测器只接收数字人 `SPEAKING` 期间已被业务门控排除的 PCM 摘要，绝不把重叠音频放入普通回答 VAD、pre-roll、ASR 分段或回答聚合。

第一版保守策略：

- 播放开始后保留 450ms 回声基线预热。
- 开启 AEC 时最低 RMS 0.035、最低 peak 0.07。
- 未确认 AEC 时最低 RMS 0.05、最低 peak 0.10，并使用更高噪声倍数。
- 需要累计 700ms 持续高能量；允许最多 120ms 短缺口。
- 短促键盘声或碰撞声进入 `REJECTED_AS_NOISE`，不会停止 TTS。
- 确认后状态进入 `INTERRUPTING`，只向当前 `speechId` 发出一次中断。
- 服务端确认输出管线 flush 后发布 `speech-interrupted`，随后执行原有 500ms playback guard，再恢复 `LISTENING`。
- 错误 speechId 不会中断当前播报；8秒未确认会进入可恢复错误路径，不伪造正常结束。

## 必须人工完成

- 笔记本扬声器、有线耳机、蓝牙耳机下分别测试真实 AEC。
- 验证数字人声音本身不会触发打断。
- 验证连续讲话约 700ms 可以打断，单次咳嗽、键盘声和碰撞声不会打断。
- 验证第一句开头可能因 450ms 预热和 500ms guard 丢失；第一版不承诺保存重叠开头。
- 验证浏览器切换输入/输出设备后的阈值表现。
- 通过设备矩阵前不要在生产构建中将开关设为 `true`。
