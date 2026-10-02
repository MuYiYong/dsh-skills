# UI 设计与实测

目标是与 DSH 协调、适合领域任务的成品界面。美化包括信息结构、交互状态和可访问性，不只是换颜色。

## 先确定真实渲染位置

在运行实例查询 Slots/Theme，或查同版本 slot 声明、props 与实际渲染方。页面/侧栏/聊天节点选择不同 slot；`conversation.composer.dock` 适合紧凑提示，不适合塞完整本体工作台。没有合适 slot 时说明实际限制并找已有扩展位置，不私改 DOM、替换根节点或用 iframe 假装接入。

脚手架默认使用 `plugins.detail.section`，仅在自己的 bundle 详情页渲染。当前 `composer.dock` 只在正式 session 的 composer 变体下渲染，欢迎页不显示；注册成功不能证明当前视图可见。

通过 `ctx.slots.inject(ownerKey, () => ctx.slots.register(options, Component))` 绑定 slot 生命周期。注册的 namespace/id 保持唯一。父 slot 关闭和重新出现时，贡献也应移除/恢复。Chat 节点需现有 Conversation definition 与 keyed renderer；专用工具 Web 卡片用 `tool.call.toolview` 等真实接口，Host 的 presentResult 本身不产生 Web 专用卡片。

## 小型视觉 brief

实现前记录受众、主任务、信息密度、一个主要操作、目标屏幕与宿主参考页。列表型插件参考 Plugin Manager，编辑器参考已有编辑页。领域特征用图关系、类型图例、证据链等承载，避免无关 hero、夸张渐变或一排假统计卡。

选择并记录：文本层级、间距尺度（可先 4/8/12/16/24）、内容最大宽度、表格密度、空白与分组、圆角与动效。普通界面继承系统字体/宿主字号；不默认引入外网字体。单一主强调色，状态色语义固定。

## 样式边界

以宿主实际 Theme 查询为准。当前基线可用：

| 语义 | Token |
|---|---|
| 基础面 | `--dsw-alias-bg-base` |
| 正文/次要文字 | `--dsw-alias-label-primary` / `--dsw-alias-label-secondary` |
| 轻边框 | `--dsw-alias-border-l1` |
| 主强调/键盘焦点 | `--dsw-alias-state-business-primary` |

CSS 使用插件前缀的类/属性选择器，禁止全局 `button`、`body`、`*` 重置。背景、文字、交互状态用 token，不为深色模式自行复制整套色值。示意图艺术内容可用独立颜色，但仍提供图例和文本。Tokens 比内部组件包稳定，仍应在升级测试中检查是否存在。

不 runtime require `@deepseek-ai/dsh-client-ui-primitives` 或其他 Harness Client 内部组件。外部插件自己拥有控件实现；参考宿主行为与布局，需要复制源码时保留所需许可证，重命名 CSS，复制最小部分。React 由宿主 factory require 取得，不安装/打包第二个 React。避免复杂自制模态，确实需要时完整处理焦点陷阱、Escape、关闭后焦点恢复。

## 文案与状态

用 `ctx.effect(() => ctx.locale.register(namespace, { zh, en }))` 注册字典，slot options 写 `locale: namespace`，组件使用注入的 `t`。包管理器展示元信息放在 `locale/zh.json` 与 `locale/en.json` 的 `meta`；与 UI 字典用途不同。

至少覆盖 loading、empty、error/retry、ready；有数据更新时补 stale、saving、conflict。错误说明失败操作和恢复动作，不能静默丢失败、显示假成功或固定的假在线状态。按钮名明确“查询实体”“预览变更”“保存关系”。权限不足与没有数据区分。危险操作有确认，但不把普通查看变成审批流程。

键盘可达、焦点可见、表单有 label、图标按钮有可访问名称；状态不只依赖颜色。一般文本对比目标 4.5:1，控件/大字 3:1。图谱提供列表/表格等价入口。支持 zoom 200%、长中文、320/375px 窄屏、空数据和长列表；减少动画偏好下关闭非必要动效。

## 验证方法

必须在实际 DSH 页面看插件，至少选择桌面和窄屏，以及浅/深主题、中/英文。浏览器检查：无 `slot entry crashed`、无布局遮挡/横向溢出、完整键盘路径、切换 locale/theme 即时响应、关闭/开启插件无重复节点。保存前/失败后 UI 状态正确，实际 Host 操作结果与工具路径一致。

先安装可用最小版本，再截图检查信息层级、对齐、文字可读性、密度与主操作。针对观察到的问题修改并复测。组件渲染测试是前置验证，不能替代真实页面检查；没有浏览器时明确写“尚未进行真实 UI 验证”，不能由 slot 注册成功推断视觉质量。
