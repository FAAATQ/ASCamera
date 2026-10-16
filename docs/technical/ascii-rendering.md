# ASCII 渲染

## Runtime Responsibilities
- ascii.js：纯尺寸计算、加权亮度与字符映射；app.js：采样、文字栅格化、预览与导出。
- 保留完整源画面比例；不是裁切相机照片或直接导出原图。

## Key Components
- Ramp：` .:-=+*#%@`；亮度权重 R/G/B 为 0.2126/0.7152/0.0722，乘 alpha。
- 使用 16px monospace 实测 M 的 advance；行数按 advance/20 校正，实际 lineHeight 保持源比例。
- `sample` 为低分辨率采样 Canvas；`flat` 为文字栅格；`crt` 为显示 Canvas；pre 保留原始字符。

## Data Flow
- 视频/冻结 Canvas → 网格采样 → toAscii → pre → flat → 显示 Canvas。
- 屏幕整体 screen-content 经单个 SVG displacement（scale 12），包含标题、状态和图像；实体控件不受影响。
- PNG 使用 flat，不经过屏幕曲面；页脚 `ASCamera - FATQ` 在照片区域外。
- 文件名 `ascamera-portrait-YYYYMMDD-HHMMSS-mmm.png`，采用本地时间；Copy 是含空白的纯文本。
- crt.js 是历史网格工具，仅遗留/测试用途，不是当前 app 的渲染依赖。

## Performance Considerations
- 复用采样缓冲；单 RAF 链、同步转换，不排队补帧；转换间隔至少 55ms。
- 目标 FPS 与历史合成测量不能视为真实相机/手机性能。

## Debug Notes
- 镜像由实际相机身份决定；冻结采样已镜像，不再次翻转。
- 文本换行、字体度量、完整边缘、屏幕曲面与平面 PNG 应分别验证。
- 当前导出命名已改变，旧浏览器断言未同步，见 [verification](verification.md)。
