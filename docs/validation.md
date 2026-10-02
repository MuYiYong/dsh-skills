# 验证记录

2026-10-02；DSH `0.2.0-rc.2` / `639ed015397290b3745d163aafe02ffee4aa3f84`，Node `22.23.0`，Linux。

## 技能与脚手架

- 标准 skill frontmatter 和 Codex metadata 校验。
- 按需参考覆盖创建、维护、升级、ontology 分层与 UI；资源全在技能目录内。
- host/ui/full 三种模式生成、exports 对应文件、领域测试；现有目录拒绝覆盖；非法名字/版本拒绝。
- 本机真实 Cordis 与 DSH tools 管线验证：示例工具执行、无效输入、预先取消、卸载注销、重挂无重复。
- Client factory 协议、共享 React、本地化渲染树、locale disposer 验证；该检查使用 slot adapter，不能证明真实 UI 或 slot 清理。

## 实际安装与浏览器

- full 模式 tarball 实际包含 9 个发布文件，以 `dsh plugin --profile ontology-test add <tarball>` 安装到临时 DSH_HOME；dump-config 中存在正确 row。
- 独立 Web profile 成功启动；更换代码包后重启，Plugin Manager 显示 1 个组件 Running。
- 实际浏览器中，在自己的 bundle 详情页渲染 `plugins.detail.section`。开关 bundle 后面板消失，再开启恢复，DOM 中仅 1 个面板。
- 英文浅色 1280×720、中文深色 375×812 已截图检查；375px 下 document scrollWidth=375，无页面水平溢出；本地化与主题随宿主切换。
- 示例的 disclosure 可通过键盘聚焦和 Enter 展开。没有 slot entry crashed；更换包时主动停止 Host 导致短暂 WebSocket connection refused，重启后恢复，未归为插件错误。
- 初版 composer.dock 在欢迎页不可见；实际源码表明该位置要求正式会话 composer。因此脚手架改为自身详情页，免于把“已注册但看不见”作为接入成功。

命令：`python3 scripts/check_skill.py`、`python3 -m unittest discover -s dsh-plugin/tests -v`（4 个测试，生成测试遍历 3 种模式）、system skill-creator 的 quick_validate，以及三种模式分别运行 smoke.mjs。浏览器验证为本次人工编排的 Playwright 会话，不是 CI 的自动 UI 回归；截图和临时 home 不入仓库。

## 需求审阅与使用场景

以下为主入口和参考的逐项审阅，不冒充独立 agent 评测：

| 请求 | 技能要求的行为与对应资源 |
|---|---|
| 新建独立本体插件 | 领域无 DSH 导入、Host 适配器、数据来源/证据/动作；ontology.md + 三模式 scaffold |
| 不修改 DSH 直接接 UI | 独立 bundle，lazy factory、slot、theme、locale；integration.md + ui.md，已实际安装验证 |
| 升级 DSH 或插件 | 重新取证、接口差异、精确 peer、隔离矩阵、数据迁移与回退；probe + maintenance.md |
| 安装成功但没界面 | 区分安装/激活/slot 的渲染条件，排查模块与依赖；本次实际发现并修正模板位置 |
| cc-switch 管理更新 | 标准 SKILL.md 目录、自包含资源、GitHub main 来源；README 的安装与检查更新流程 |

cc-switch 的发现/安装/更新路径依据其上游 `src-tauri/src/services/skill.rs` 与 README 核对，未修改本机数据库、未宣称已操作本机 cc-switch GUI。CI 只验证便携静态/生成检查，不声称覆盖真实 DSH。

不同 DSH 版本、Windows、真实本体数据库、生产数据迁移不在样例实测范围，需具体插件补齐。论文采用可访问摘要中的机制说明，不声称全文形式化审查。

## 恢复任务后的回归验证

2026-10-02 再次核验同一 DSH runtime/commit 与 Node 版本，保留宿主原有四处 UI 文件修改。独立源码审计发现并修复了两项生成器边界：不同包名归一后共享 row/locale/slot/CSS 标识，以及错误接受数字预发布标识含前导零的 SemVer。默认 UI 依赖与来源说明也已对齐 Plugin Manager 的实际 slot。

- `python3 scripts/check_skill.py`、system skill-creator 的 quick_validate 和 `git diff --check` 通过；`python3 -m unittest discover -s dsh-plugin/tests -v` 为 **7 个测试通过**。新回归在旧实现上失败，修复后通过，覆盖同形包名、长包名、稳定身份、合法和非法 SemVer。原工具名称算法保持不变。
- 新临时目录分别生成 host/ui/full，三种模式均通过真实 built DSH 的 `smoke.mjs`；工具执行、错误、取消、卸载/重挂以及 Client factory 检查通过，仍不把 adapter 检查当成浏览器证明。
- `@a/b` 与 `a-b` 分别打包，各含 9 个发布文件，在新的隔离 `DSH_HOME` 中通过 CLI 同时安装。dump 分别出现 `a-b-c93bbe639bd6`、`a-b-d44362d67d92`；真实页面两个包均可运行和渲染自身面板。
- 真实页面禁用 `a-b` 后其面板消失，`@a/b` 仍运行；重新启用后恢复且 DOM 中仅 1 个对应面板。英文浅色 1280×720 与中文深色 375×812 截图已检查，页面宽度分别为 1280/375，无横向溢出；Tab 可聚焦折叠项，Enter 可展开；认证后的页面 console 为 0 errors / 0 warnings。
- 终止并重启本次测试宿主后，两个包均为 1 个组件运行中，各自详情页正常渲染；中文、深色与启用状态保留。
- 独立代码审查未发现阻塞项。新身份仅用于新生成项目；已有插件 id 和用户覆盖的迁移说明见 integration.md，不自动改写既有项目。

测试环境处理：安装子进程的 PATH 显式加入目标 DSH 的 pnpm；两个包的 npm tarball 同名，因此分别放入独立打包目录，再在全新 home 验证。首次未带临时 token 的页面访问返回 401，使用宿主生成的认证入口后成功；预览/API key 引导通过页面“稍后配置”完成，未输入密钥或调用模型。这些不是插件运行失败。测试 profile、浏览器状态、认证信息和临时 tarball 均不入仓库。
