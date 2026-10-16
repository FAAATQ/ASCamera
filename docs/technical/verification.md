# 验证边界

## Runtime Responsibilities
- 本文区分历史报告、静态源码事实与真正执行过的验证；不将文档初始化当作验收。

## Key Components
- tests/ascii.test.js：纯转换/历史几何；tests/browser.py：Chrome 合成流与页面交互；tests/launcher.py：启动器。
- demo-1200.png、demo-400.png 为早期示例，不代表当前界面，也未在本轮视觉认证。

## Data Flow
- 历史 PROCESS 保存阶段测试记录；最近交接报告为 86 项通过，但其后源码发生变化，不能推导当前通过。
- 静态核对：browser.py 仍断言 `phosphor-portrait.png`；app.js 已输出带时间戳的 ascamera 文件名。当前整套测试未确认，存在明确的预期不匹配，预计相关断言会失败。
- 本轮未执行任何测试或启动浏览器；未修复测试或运行时。

## Performance Considerations
- 历史约 15 FPS 测量仅为本地合成 Canvas/DOM 更新，不是相机延迟、GPU 曲率质量或手机基准。

## Debug Notes
- 后续获开发授权后执行：
  - `node --test tests/ascii.test.js`
  - `uv run tests/browser.py`
  - `uv run tests/launcher.py`
  - `zsh -n Run.command`
- 先核对并批准过时断言的更新，不能为通过而掩盖功能回归。
- 真实相机、单/双设备、拒绝/迟到权限、冻结仍活跃、隐藏页释放、复制失败、带时间戳平面 PNG、40/96/160 密度、400px 布局需验证。
- Safari/iOS、Finder 启动、曲面截图与真实同伴试用尚待执行；不编造参与者、评价或课程合规结论。
