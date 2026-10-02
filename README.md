# DSH Skills

用于创建和维护 **DeepSeek Harness 独立插件**，通过 **cc-switch** 安装、同步和更新。

当前技能：[dsh-plugin](dsh-plugin/SKILL.md)。涵盖 Cordis 生命周期、bundle/profile 接入、Host 工具、Web UI、本体智能应用分层、升级兼容与回滚。包含可执行的 Host / UI / Full 脚手架。当前基线为 DSH `0.2.0-rc.2`；未来版本需重新验证，不承诺接口永久稳定。

## 在 cc-switch 中使用

1. 打开 **Skills → 发现技能**，进入 GitHub 仓库管理/添加仓库（不同 cc-switch 版本文案可能略有差异）。
2. 添加 `https://github.com/MuYiYong/dsh-skills`，分支选 `main`。若分字段输入，owner 为 `MuYiYong`，repo 为 `dsh-skills`。
3. 刷新仓库技能列表，安装 **dsh-plugin**，并为 Codex / Claude Code 等需要的工具启用同步。
4. 新建或重开 agent 会话，输入 `$dsh-plugin`。若工具不支持 `$` 选择器，可说“使用 dsh-plugin 技能”。

仓库中的发现路径是 `dsh-plugin/SKILL.md`，其他资源都在同一目录内，安装时不会依赖仓库根目录或本机 DSH 的绝对路径。Codex 专用界面元数据位于 `agents/openai.yaml`，其他工具直接读 SKILL.md。

cc-switch 默认将技能安装到 `~/.cc-switch/skills/`（可配置为其他位置），再以软链接或复制同步到工具目录。**不要手动修改 cc-switch 的 SQLite 数据库，也不要把开发 clone 直接链接到其受管安装目录。** 通过仓库安装保留来源信息，才能正确检查远程更新。本仓库交付不等于已替你在 cc-switch 界面安装。

## 使用示例

```text
$dsh-plugin 基于 /home/vesoft/deepseek-harness，创建一个独立的设备本体插件。
从我的数据源查询设备、故障和维修记录，在 DSH 中提供实体检索、关系与证据查看；
UI 与 agent 工具共用业务操作。先做可运行版本并验证，不修改 DSH 核心。
```

```text
$dsh-plugin 检查 ./my-plugin 在升级后的 DSH 中为什么没有显示。
保留当前配置，核实 slot、Client 模块格式、依赖与激活状态，修复并验证。
```

```text
$dsh-plugin 把 ./my-plugin 适配到 /path/to/new-dsh。
对照旧版本记录检查实际接口变化，测试生命周期和 UI，更新兼容矩阵与回滚说明。
```

## 本地开发与更新

本机开发 clone：`/home/vesoft/dsh-skills`；远端：`https://github.com/MuYiYong/dsh-skills`。

```bash
cd /home/vesoft/dsh-skills
git pull --ff-only
# 修改 dsh-plugin/ 内的技能、参考或脚本
python3 scripts/check_skill.py
python3 -m unittest discover -s dsh-plugin/tests -v
git add <本次修改的文件>
git commit -m "fix(dsh-plugin): describe the actual change"
git push origin main
```

发布后，在 cc-switch 的 Skills 页执行 **检查更新**，更新 `dsh-plugin`，然后重新打开使用它的 agent 会话。仅刷新“发现技能”不一定替换已安装副本。不要直接编辑已安装副本：下一次更新会替换它。若在那里已有个人修改，先备份并移回本仓库，再更新。cc-switch 自带更新/卸载备份，具体位置和保留量以使用版本为准。

更新 skill 与更新应用插件是两件事：cc-switch 更新开发指导；生成的 DSH 插件有自己的仓库、版本、测试和发布流程，不随 skill 更新自动改动。

## 手动运行辅助脚本

```bash
python3 dsh-plugin/scripts/probe_dsh.py --dsh /path/to/deepseek-harness --output /tmp/dsh-baseline.json
python3 dsh-plugin/scripts/scaffold.py --name @acme/ontology-workbench \
  --out /tmp/ontology-workbench --kind full --dsh-version 0.2.0-rc.2
node --test /tmp/ontology-workbench/domain.test.js
node dsh-plugin/scripts/smoke.mjs --dsh /path/to/deepseek-harness --plugin /tmp/ontology-workbench
```

需要 Python 3.10+、Node 22.19+（此基线的 DSH 要求）；probe/scaffold 仅用 Python 标准库。smoke 需要 DSH **已构建产物及其依赖**，在临时目录运行，结束清理，不修改正常 profile。它检查生成模板，不是任意业务插件的完整测试器。安装验证使用独立 `DSH_HOME`，具体见 [维护指南](dsh-plugin/references/maintenance.md)。

脚手架的本体数据和 UI 都明确标为示例。生成后继续接入真实数据和业务流程，不能作为已完成的本体应用交付。验证范围见 [验证记录](docs/validation.md)。
