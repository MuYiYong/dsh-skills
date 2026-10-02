# DSH Skills

让 AI agent 帮你创建、维护和升级 **DeepSeek Harness（DSH）独立插件**。安装 [dsh-plugin](dsh-plugin/SKILL.md) 后，直接描述需求即可；技能提供 Host 工具、Web UI、本体应用分层及安装验证的开发指导和脚手架。

## 1. 安装技能

通过 **cc-switch** 安装并同步到你使用的 AI 工具：

1. 打开 **Skills → 发现技能**，进入 GitHub 仓库管理，添加 `https://github.com/MuYiYong/dsh-skills`，分支选择 `main`。
2. 若界面分字段填写，owner 为 `MuYiYong`，repo 为 `dsh-skills`。
3. 刷新技能列表，安装 **dsh-plugin**，为 Codex / Claude Code 等工具启用同步。
4. 新建或重开 agent 会话，输入 `$dsh-plugin`；不支持该选择器的工具可输入“使用 dsh-plugin 技能”。

不同 cc-switch 版本的界面名称可能略有差异。技能入口为 `dsh-plugin/SKILL.md`，脚本、模板和参考资料均在同一目录内，可独立安装。

## 2. 直接描述你的需求

提供 **DSH 源码路径、插件目录和要实现的操作**。涉及业务数据时补充数据源与访问方式；排错时附上错误信息和复现步骤。以下路径均为占位示例，请替换为自己的路径。

### 创建插件

```text
$dsh-plugin 基于 /path/to/deepseek-harness，在 ./my-plugin 创建独立设备本体插件。
从我的数据源查询设备、故障和维修记录，提供实体检索、关系与证据查看。
UI 与 agent 工具共用业务操作，实现后验证打包、隔离安装和真实 DSH 页面。
```

如果只需要工具，可说明“仅实现 Host 工具，无需 UI”；只需要界面时可说明“仅接入 Web UI”。

### 排查已有插件

```text
$dsh-plugin 检查 ./my-plugin 安装后为什么没有显示。
DSH 位于 /path/to/deepseek-harness。请核实激活状态、依赖、Client 模块和 slot，
结合实际错误修复，并验证关闭、重新开启后功能正常。
```

### 适配新版本

```text
$dsh-plugin 把 ./my-plugin 适配到 /path/to/new-dsh。
对照旧版本记录检查实际接口变化，验证生命周期和 UI，更新兼容记录与回滚说明。
```

交付时应包含插件目录、安装/启动命令、已验证的 DSH 版本、测试结果和待验证项。脚手架中的数据和面板是接入示例；业务应用还需要接入真实数据和完成用户流程。

## 3. 手动生成和验证（可选）

通常由 agent 执行这些步骤，也可以在本仓库根目录手动运行。需要 Python 3.10+、Git 和 npm；当前 DSH 基线要求 Node 22.19+，安装插件时 pnpm 需在 PATH 中可用。探测和生成不需要额外 Python 包；探测会调用 Git 记录版本，运行 smoke 需要目标 DSH 已构建并安装依赖。

```bash
git clone https://github.com/MuYiYong/dsh-skills.git
cd dsh-skills

# 先核实你的 DSH 版本；输出文件必须尚不存在
python3 dsh-plugin/scripts/probe_dsh.py \
  --dsh /path/to/deepseek-harness --output ./dsh-baseline.json

# 本例使用已验证基线；其他版本需先核验实际接口
python3 dsh-plugin/scripts/scaffold.py --name @acme/ontology-workbench \
  --out ./my-plugin --kind full --dsh-version 0.2.0-rc.2

node --test ./my-plugin/domain.test.js
node dsh-plugin/scripts/smoke.mjs \
  --dsh /path/to/deepseek-harness --plugin ./my-plugin

cd my-plugin
npm pack
```

`--kind` 可选 `host`、`ui`、`full`；生成器拒绝覆盖已有目录。`ui` 模式的测试文件为 `entry.test.js`，也可进入生成目录统一执行 `node --test`。从已安装技能运行脚本时，将 `dsh-plugin/` 替换为实际技能目录。

使用独立测试 home 安装生成的 tarball。下面命令在同一终端执行，将 tarball 路径替换为 `npm pack` 输出文件的绝对路径；`dsh` 应指向你的目标宿主 CLI。

```bash
plugin_test_home=$(mktemp -d)
export DSH_HOME="$plugin_test_home"
dsh --profile ontology-test --from-default-profile web --dump-config
dsh plugin --profile ontology-test add /absolute/path/to/package.tgz
dsh --profile ontology-test --dump-config
dsh --profile ontology-test --no-open --port 3089
```

端口需可用。启动后，在 **Plugins → 自己的插件详情页** 查看示例面板，检查启用/关闭、中英文、浅深主题和窄屏显示。示例面板默认注册到 `plugins.detail.section`；Host-only 模式没有面板。安装态代码更新后需重启宿主并刷新页面。测试结束后停止测试宿主，执行 `unset DSH_HOME` 恢复终端环境。

更多安装、生命周期和回滚检查见 [维护与验证指南](dsh-plugin/references/maintenance.md)。当前实测基线为 DSH `0.2.0-rc.2`，详细证据见 [验证记录](docs/validation.md)。

## 4. 更新技能

在 cc-switch 的 Skills 页执行 **检查更新**，更新 `dsh-plugin`，然后重新打开 agent 会话。刷新“发现技能”与更新已安装副本是不同操作。

技能更新提供新的开发指导和脚手架，已有 DSH 插件仍按自身仓库和版本流程维护。个人改动请保存在开发仓库中；cc-switch 管理安装副本及同步，不要直接修改受管副本或数据库。

## 参与维护

在本仓库的 `dsh-plugin/` 下修改技能资源，并运行：

```bash
python3 scripts/check_skill.py
python3 -m unittest discover -s dsh-plugin/tests -v
```

涉及模板或 DSH 接入时，按 [仓库说明](AGENTS.md) 补充真实宿主验证。
