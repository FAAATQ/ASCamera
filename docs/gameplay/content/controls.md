# 控件与视觉内容

## Summary
- 数据来源：index.html、app.js 与 styles.css 的最终级联；行为规则见 [交互系统](../interaction-system.md)。

## Core Rules
- 四键标签依次为 `Take photo`、`Switch camera`、`Copy`、`Save`，保持单行；窄屏可让仪表组与键组换行，但不改四键顺序。
- 左侧电源与旋钮横向并列；不恢复 Retake、Stop/Clear 或公共 demo 键。
- 密度：40–160 列，step 8，默认 96；原生 range 提供键盘语义。
- 旋钮角度：-135° 至 +135°；刻度与旋钮使用同一角度范围。

## State Flow
- 所有操作键与密度始终 enabled；状态守卫决定反馈或动作。
- 电源 aria-checked 对应会话供电，不是是否正在更新 ASCII。

## Timing
- 拖动右/上增加密度，左/下减少；冻结立即重转换，关闭时更新预设。

## Feedback
- 用户确认的复古方向：虚构暖白仪器外壳、厚边框、四个斜面直接接玻璃、轻微凸 CRT、绿色字符与 ASCII 开机标题。
- 实体键有高度与凹面；拍照橙色，其余浅色；红色翻转电源，机壳签名 `ASCamera - FATQ`。
- 旋钮为真实可拖动控件；浅色 3px 指示点安装于凸起握柄，共享旋转，不是漂浮装饰。
- 状态、密度与 LOCAL ONLY 在 CRT 内；公共运行时文案为英文。

## Edge Cases
- 没有相机时四键仍能反馈；外观 enabled 不等于动作可执行。
- 视觉由源码静态核对，当前未做浏览器视觉认证。

## Future Expansion
- 保留用户认可的硬件方向；任何版式调整先确认，不擅自恢复旧 fader、两行键组或倒计时。
