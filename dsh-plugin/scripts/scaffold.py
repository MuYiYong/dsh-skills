#!/usr/bin/env python3
"""Generate a standalone DSH bundle without installing or modifying the host."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ASSETS = Path(__file__).resolve().parents[1] / 'assets/starter'
NAME = re.compile(r'(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*\Z')
NUMBER = r'(?:0|[1-9][0-9]*)'
PRERELEASE = rf'(?:{NUMBER}|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)'
VERSION = re.compile(rf'{NUMBER}\.{NUMBER}\.{NUMBER}(?:-{PRERELEASE}(?:\.{PRERELEASE})*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z')


def generate(name, out, kind, version):
    if len(name) > 214 or not NAME.fullmatch(name):
        raise ValueError('Use a lowercase npm package name, optionally @scope/name')
    if not VERSION.fullmatch(version):
        raise ValueError('Supply an exact tested DSH version, not a range or wildcard')
    if out.exists() or out.is_symlink():
        raise ValueError(f'Refusing to replace existing destination: {out}')
    slug = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
    digest = hashlib.sha256(name.encode()).hexdigest()
    # Punctuation normalization loses package identity (@a/b and a-b collide).
    # Bound the readable part and use the full package name for every UI/row id.
    identifier = slug[:42].rstrip('-') + '-' + digest[:12]
    # Keep generated tool identifiers short and distinct across scoped package names.
    tool = slug.replace('-', '_')[:42] + '_' + digest[:8] + '_inspect'
    ui = kind in ('ui', 'full')
    host = kind in ('host', 'full')
    peers = {'@deepseek-ai/dsh': version}
    if host:
        peers['@deepseek-ai/dsh-tools'] = version
    manifest = {
        'name': name, 'version': '0.1.0', 'private': True, 'type': 'module',
        'description': 'Standalone DSH ontology integration starter',
        'exports': {'.': './index.js', './package.json': './package.json',
                    './locale/*.json': './locale/*.json'},
        'files': ['index.js', 'cordis.patch.yml', 'locale', 'compatibility.json', 'README.md'],
        'scripts': {'test': 'node --test'},
        'peerDependencies': peers,
        'peerDependenciesMeta': {key: {'optional': True} for key in peers},
        'dsh': {'bundle': {'patch': './cordis.patch.yml'}},
    }
    replacements = {'__PACKAGE__': name, '__ID__': identifier, '__TOOL__': tool}
    files = {}
    for target, source in ([('index.js', 'host.js'), ('domain.js', 'domain.js'),
                             ('domain.test.js', 'domain.test.js')] if host else []):
        content = (ASSETS / source).read_text()
        for key, value in replacements.items():
            content = content.replace(key, value)
        files[target] = content
    if not host:
        files['index.js'] = '/** Browser-only bundle Host registration. */\nexport function apply() {}\n'
        files['entry.test.js'] = "import test from 'node:test';\nimport assert from 'node:assert/strict';\nimport { apply } from './index.js';\ntest('host half is callable without browser globals', () => assert.doesNotThrow(() => apply()));\n"
    else:
        manifest['files'].append('domain.js')
    if ui:
        manifest['exports']['./client'] = './client.js'
        manifest['files'].append('client.js')
        manifest['dsh']['client'] = {
            'platform': 'web', 'immediately': True,
            'inject': ['@deepseek-ai/dsh-client-ui-plugin-manager', '@deepseek-ai/dsh-client-locale'],
        }
        content = (ASSETS / 'client.js').read_text()
        for key, value in replacements.items():
            content = content.replace(key, value)
        files['client.js'] = content
    files['package.json'] = json.dumps(manifest, indent=2) + '\n'
    files['cordis.patch.yml'] = f"- insert:\n    - id: {identifier}\n      name: '{name}'\n      config: {{}}\n"
    files['compatibility.json'] = json.dumps({
        'formatVersion': 1, 'pluginVersion': '0.1.0', 'dshVersion': version,
        'status': 'unverified', 'checks': [],
        'note': 'Project test record, not DSH profile version exemptions.',
    }, indent=2) + '\n'
    for language, title, description in [
        ('zh', '本体应用接入示例', '独立 DSH 插件脚手架，尚未连接业务数据。'),
        ('en', 'Ontology integration starter', 'Standalone DSH starter; no business data is connected.'),
    ]:
        files[f'locale/{language}.json'] = json.dumps(
            {'meta': {'title': title, 'description': description}}, ensure_ascii=False, indent=2) + '\n'
    files['README.md'] = f'''# {name}

由 dsh-plugin skill 生成的 {kind} 接入起点，不是完整本体应用。
目标 DSH：`{version}`；兼容记录初始为 unverified。Host 工具：{tool if host else '无'}。
UI 提示只是示例，不证明 Host 在线或数据库连接成功。

## 验证

```bash
node --test
node --check index.js
{'node --check client.js' if ui else '# Host-only bundle'}
npm pack --dry-run
npm pack
```

领域测试不需安装 DSH。Host 工具运行需要宿主提供匹配版本的 dsh-tools。
用 skill 的 `scripts/smoke.mjs --dsh /path/to/dsh --plugin /absolute/path` 验证真实 Cordis/工具注册与清理。
发布前保留依赖锁与适用测试，选定许可证，并按实际验证决定是否移除 private。

## 隔离安装

设置独立 DSH_HOME 后，使用宿主 CLI：

```bash
dsh --profile ontology-test --from-default-profile web --dump-config
dsh plugin --profile ontology-test add /absolute/path/to/packed-bundle.tgz
dsh --profile ontology-test --dump-config
dsh --profile ontology-test --no-open --port 3089
```

在 Plugins 中打开自己的包详情页查看 UI 提示；它不会出现在其他插件页。
检查 row `{identifier}`；工具输入可用 `{{"id":"example:equipment-1"}}`。
正常 profile 安装影响该 profile 所有会话。代码包更新后重启，UI 在实际页面验证中英/深浅/窄宽屏及卸载。

## 开发与回退

领域逻辑放 domain 或独立 src/domain；DSH 接入留在 adapters。不得导入宿主源码路径，
不得将 workspace: 依赖带入发布。UI 与工具共享真实业务用例；业务数据单独版本化。
升级前保存旧 tarball、配置与数据备份；回退旧包并恢复兼容数据，不能用版本豁免代替适配。
'''
    # Validate and read all templates before creating any destination.
    out.mkdir(parents=True, exist_ok=False)
    for relative, content in files.items():
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    return {'path': str(out), 'package': name, 'kind': kind, 'tool': tool if host else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--kind', choices=['host', 'ui', 'full'], default='full')
    parser.add_argument('--dsh-version', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.name, args.out.absolute(), args.kind, args.dsh_version)))
    except (ValueError, OSError) as error:
        parser.exit(1, f'scaffold failed: {error}\n')


if __name__ == '__main__':
    main()
