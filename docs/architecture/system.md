# 系统架构

## System Relationships
- index.html：语义结构、四键/电源/range、CRT SVG 定义。
- styles.css：外壳、实体控件、响应式与屏幕效果；存在历史级联，最终规则优先。
- app.js：DOM 协调、状态机、摄像头、旋钮、显示、复制和导出。
- ascii.js：无 DOM 的转换函数；crt.js 为历史测试工具，不被 app 导入。
- start.py / Run.command：本机启动入口，与浏览器媒体生命周期分离。

## Signal/Event Flow
- 按钮/范围输入 → app 状态守卫 → 媒体或转换操作 → CRT 状态反馈。
- video ready/resize、RAF → render/fit；ResizeObserver → 斜面与玻璃边界对齐。
- hidden/pagehide/track ended → reset 或 fail → cleanup。

## Ownership
- 浏览器拥有权限提示与媒体设备；app 拥有流引用、临时图像、取消令牌与 RAF。
- ascii.js 拥有转换算法；样式/DOM 拥有外观，不承担设备身份判断。
- 用户决定是否开相机、复制或保存；没有远端图像服务或账户系统。

## Lifecycle
- localhost 页面载入不申请权限 → 显式电源启动 → 实时/冻结往返 → 电源或页面生命周期关闭。
- Python 服务绑定 127.0.0.1，默认 8765；浏览器关闭不等于服务进程结束，终端 Ctrl-C 关闭服务器。

## Dependencies
- 运行时：浏览器原生 ES modules、Canvas、MediaDevices、Clipboard、SVG、ResizeObserver；Python 标准库。
- uv 为启动工具；Node 与 Playwright/Chrome 为开发验证工具，无前端构建或第三方运行库。
- 数据不写 localStorage，无上传、录音或自动照片历史。
