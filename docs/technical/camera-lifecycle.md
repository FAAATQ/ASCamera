# 摄像头生命周期

## Runtime Responsibilities
- app.js 持有 sessionPower、state、stream、image、epoch 与 RAF。
- 默认不访问媒体；video-only、audio:false。所有媒体数据留在本地内存。

## Key Components
- start：安全上下文检查、请求视频、枚举设备、播放与建立 preview。
- capture/result：冻结完整帧并暂停 RAF；保留 stream，第二次拍照复用流恢复。
- reset/fail/cleanup：使异步令牌过期、取消 RAF、停止 tracks、解除 video 源并清空会话图像。

## Data Flow
- 电源 → start → getUserMedia → 实际 track settings → enumerateDevices → video → render。
- switch 先停止旧流，再请求另一设备/朝向；失败且非权限拒绝时尝试恢复原设备。
- 不以切换请求推断镜像；比较真实 deviceId，缺失 ID 时才以明确 facing 变化作验证。

## Performance Considerations
- 冻结不是摄像头关闭，仍占用设备；必须如实保留 CAMERA ACTIVE 提示。
- 单设备不重复申请，不制造翻转效果。

## Debug Notes
- 电源 OFF、隐藏标签、pagehide 或流中断会关闭会话；返回页面不自动重启。
- epoch 阻止迟到的权限结果附着，过期流会停止；浏览器权限弹窗本身不能由脚本取消。
- requesting、preview、result、idle/error 的控制守卫需分别验证。
- Close/Stop 旧文案与实际电源操作不一致，暂只记录待修复。
- 本轮未使用真实摄像头或执行生命周期测试。
