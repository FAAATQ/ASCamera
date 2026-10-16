# 项目工作约定

- 范围仅 ascii-photo-booth；不要把此处初始化扩展到父工作区或其他课程项目。
- 先读 CURRENT.md、TODO.md 与 docs/INDEX.md，再读目标源码；PROCESS 是历史，不是现行规格。
- 这是原生 HTML/CSS/JS 本地 ASCII 相机，不是游戏；不创建武器/战斗等无关模板。
- 规则见 docs/gameplay/interaction-system.md，标签/参数见 content/controls.md；技术与架构分开维护。
- 用户已确认方向：暖白硬件、轻微整体凸 CRT、四键单行、左侧电源/旋钮横排、屏内英文状态、可操作旋钮。
- 冻结不释放流；电源 OFF、隐藏页、pagehide 或中断关闭会话。不得把旧 stop-on-capture 说明带回实现。
- 所有图像本地处理，不自动启动相机、不录音/上传/持久化；不得伪造单摄像头翻转。
- PNG 为平面 ASCII，署名 ASCamera - FATQ，文件名带本地日期与毫秒；crt.js 仅历史/测试工具。
- 历史测试通过不代表当前通过；当前存在旧文件名断言，不得声称整套已验证。命令与边界见 docs/technical/verification.md。
- 不伪造同伴试用、硬件测试、视觉验收或课程合规；早期 demo PNG 不是当前截图证据。
- 本次授权仅文档。后续代码、测试或样式修改须另获授权；删除、外部发布、Git 提交/推送须先确认具体范围。
- GitHub 私有开发意向待确认；课程交付公开要求须在发布前核对。
