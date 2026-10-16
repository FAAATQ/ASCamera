# 交互系统

## Summary
- 本地摄像头转绿色 ASCII，允许冻结、调密度、复制与导出；无公共 demo 按钮。

## Core Rules
- 仅 Camera power 从关闭状态发起初次视频权限请求；不请求音频。
- 四个操作键始终可见可点；不可用时解释原因，而非隐藏或禁用。
- 冻结保留摄像头流与电源 ON；再按拍照恢复实时预览。
- 关闭电源清空图像并释放流；不自动持久化照片。

## State Flow
- `idle/error → requesting → preview → result → preview`。
- 电源关闭、页面隐藏、pagehide：回到 idle；中断/失败：error。
- 切换摄像头仅在 preview 有效；单摄像头不发起伪切换、不翻转同一设备。

## Timing
- 无倒计时；拍照同步采集就绪帧。
- 实时循环以 55ms 最小转换间隔限速，目标约 18 FPS，不保证实际帧率。

## Feedback
- 状态与密度数字位于 CRT 内，运行时文案为英文。
- 冻结时明确提示摄像头仍活跃；外部 LED 区分 live/captured/off。

## Edge Cases
- 请求中电源可取消；迟到的流会被停止。
- 关闭状态操作不会请求摄像头；密度可预设。
- Copy 在实时/冻结有效；Save 仅冻结有效；拒绝剪贴板权限时提供手动复制反馈。
- 当前源码仍含 Close/Stop 等旧提示，列为待办，不作为实际控件。

## Future Expansion
- 先完成真实设备与同伴试用，再决定扩展；不默认增加录制、上传或历史库。
- 标签及参数见 [controls](content/controls.md)。
