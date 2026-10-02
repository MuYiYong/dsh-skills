# 维护、升级与验证

## 记录兼容性

每个插件维护：自身版本、DSH runtime 版本/commit、Node 版本、接口依赖（服务方法/事件及 mode/slot/token/模块格式）、数据版本、测试证据和日期。只将确实运行通过的组合记为 verified。脚手架 `compatibility.json` 初始为 unverified；不是宿主 `compatibility.json` 的版本豁免格式，不复制到 profile。

探测脚本的哈希变化只说明文件变化，不意味着破坏兼容；哈希相同也不证明行为兼容。探测覆盖主要接入文件，插件使用其他接口时将它们加入自身接口清单。兼容范围不应大于证据范围，尤其当前是预发布版本。避免为了安装通过使用 `*` 或取消 peer。

## 升级流程

1. 保存当前插件版本、lockfile、profile 导出配置及插件数据备份；明确旧版恢复方式。记录用户未提交修改。
2. 只读探测新/旧 DSH，比较当前插件实际依赖的 exports、签名、inject key、事件 mode、slot props、主题 token、loader/module 格式与配置语义。
3. 在独立 checkout/home/profile 测新宿主。先运行旧插件的同一套验证，得到具体失败后只改 adapter；领域代码不因宿主版本随意重写。
4. 若迁移插件数据，做版本化、事务/原子提交、幂等迁移和未来版本拒绝。备份验证可恢复；破坏性迁移不能声称只退 npm 版本就能回滚。
5. 运行下表适用项。至少验证当前受支持版本和候选版本，保留证据；只有一个版本可用时将另一个标记未验证。
6. 更新插件语义版本、peer 范围与迁移说明，再安装目标 profile。已安装代码更新要重启验证实际新版本，不用相同 slot id 证明已更新。

## 验证矩阵

| 范围 | 通过的可观察证据 |
|---|---|
| 领域 | 查询/规则/授权/分页/写入幂等的代表案例，错误和取消分支 |
| Cordis | apply→调用→dispose→不可调用→重新挂载，provider 缺失/恢复，双实例隔离，无遗留资源 |
| 工具 | 参数与结果 schema、真实注册执行、abort、输出可重放；涉及策略则经执行管线验证 |
| 配置 | 缺项/无效输入清晰失败；patch 覆盖符合预期；用户值重启仍在 |
| 发布 | tarball 实际含所有 exports/patch/locale/client，外部目录安装，无 workspace: 或 src 深导入 |
| profile | 独立 home 的 install、dump、启动、disable/enable、重启；没有 skipped bundle 或 required pending |
| UI | 真实 DSH 渲染、关键操作、中英/浅深/窄宽屏、console、slot owner 回收 |
| 数据 | 迁移前后查询、重启持久化、重复迁移、未来版本拒绝、恢复备份 |
| 升级 | 当前与候选 DSH 相同矩阵，插件独立升级、DSH 独立升级、回退演练 |

只运行改动相关检查。普通文案不需构建整个 DSH；Host/Client 改动分别类型检查，已验证后不反复全量跑测试。引用 DSH 仓库自带测试框架时以其规则为准，必要的 keyless 会话快照不要用简单单测替代。

## 安全的试运行命令

下面 shell 变量仅供这次测试，不修改正常 home。先将 `dsh` 替换为已确认的 CLI（本地 built bin 可用 `node /path/to/apps/cli/lib/bin.js`）。

```bash
plugin_test_home=$(mktemp -d)
DSH_HOME="$plugin_test_home" dsh --profile ontology-test --from-default-profile web --dump-config
DSH_HOME="$plugin_test_home" dsh plugin --profile ontology-test add /absolute/plugin.tgz
DSH_HOME="$plugin_test_home" dsh --profile ontology-test --dump-config
DSH_HOME="$plugin_test_home" dsh --profile ontology-test --no-open --port 3089
```

端口应先检查可用；Web 测试不需要调用付费模型。退出时只停止自己启动的进程，保留必要日志。`DSH_HOME` 只隔离产品文件，不将 Host 插件放进安全沙箱。

## 常见症状

| 症状 | 首先核实 |
|---|---|
| 安装成功但无功能 | `application`、warnings、skippedBundles、disabled/后层 patch、必需 inject pending |
| UI 空白 | 裸包名 row、dsh.client、./client 文件、factory id、console slot crash、slot 是否存在 |
| 改代码不生效 | 是否重启已安装包、浏览器是否获取新 revision；不要反复开关猜测 |
| 工具隐藏或不能执行 | agent scope/preset、restrict/guard/审批；不通过暴露额外接口绕过 |
| 关闭插件后仍工作 | 模块顶层副作用、跨 context disposer、异步清理是否被 await |
| 会话无法重开 | 是否写了未知 event type，数据/日志版本；先备份再修，禁止直接删除日志 |
| 两个 TS 声明冲突 | 是否将 Host 与 Client Context 放进同一个 ts.Program |
| 安装被版本拒绝 | 实际 runtime 与 peer，先适配或回退；豁免不是修复 |

若没有足够信息，报告明确的失败步骤、最小日志和下一项诊断，不假报通过。发布/迁移/正常 profile 安装的授权取自用户任务，不从测试成功推导授权。
