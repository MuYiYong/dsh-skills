"""Generator behavior: non-destructive output and usable standalone artifacts."""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]


class ScaffoldTests(unittest.TestCase):
    def run_scaffold(self, out, *extra):
        return subprocess.run(['python3', str(SKILL / 'scripts/scaffold.py'),
            '--name', '@acme/ontology', '--out', str(out),
            '--dsh-version', '0.2.0-rc.2', *extra], capture_output=True, text=True)

    def test_modes_have_resolvable_exports_and_runnable_domain_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind in ('host', 'ui', 'full'):
                with self.subTest(kind=kind):
                    out = Path(tmp) / kind
                    result = self.run_scaffold(out, '--kind', kind)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    pkg = json.loads((out / 'package.json').read_text())
                    for target in pkg['exports'].values():
                        if '*' not in target:
                            self.assertTrue((out / target).is_file(), target)
                    self.assertEqual('./client' in pkg['exports'], kind != 'host')
                    self.assertEqual('dependencies' in pkg, False)
                    test = subprocess.run(['node', '--test'], cwd=out, capture_output=True, text=True)
                    self.assertEqual(test.returncode, 0, test.stderr + test.stdout)

    def test_existing_directory_is_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'keep.txt'
            path.write_text('user work')
            self.assertNotEqual(self.run_scaffold(Path(tmp)).returncode, 0)
            self.assertEqual(path.read_text(), 'user work')
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)

    def test_rejects_invalid_name_and_version_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            for flags in [('--name', '../../escape'), ('--dsh-version', '*'),
                          ('--name', '@a/x;echo injected'), ('--dsh-version', 'v1')]:
                out = Path(tmp) / 'output'
                self.assertNotEqual(self.run_scaffold(out, *flags).returncode, 0)
                self.assertFalse(out.exists())

    def test_rejects_invalid_semver_identifiers_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            for version in ('1.0.0-01', '1.0.0-rc.01', '1.0.0-00.a', '1\u0661.0.0'):
                with self.subTest(version=version):
                    out = Path(tmp) / version
                    result = self.run_scaffold(out, '--dsh-version', version)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(out.exists())

    def test_accepts_valid_semver_prerelease_and_build_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            for version in ('0.0.0', '1.0.0-0', '1.0.0-0a.01a', '1.0.0-rc.2+001'):
                with self.subTest(version=version):
                    out = Path(tmp) / version
                    result = self.run_scaffold(out, '--dsh-version', version)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    package = json.loads((out / 'package.json').read_text())
                    self.assertEqual(package['peerDependencies']['@deepseek-ai/dsh'], version)

    def test_distinct_packages_have_independent_stable_bounded_identities(self):
        names = ('@a/b', 'a-b', '@a.b/c', '@a/b-c', 'a' * 213 + 'b', 'a' * 213 + 'c')
        with tempfile.TemporaryDirectory() as tmp:
            identities = []
            for index, name in enumerate(names):
                out = Path(tmp) / str(index)
                result = self.run_scaffold(out, '--name', name)
                self.assertEqual(result.returncode, 0, result.stderr)
                row_id = re.search(r'^    - id: (.+)$',
                                   (out / 'cordis.patch.yml').read_text(), re.M).group(1)
                self.assertNotIn(row_id, identities, f'colliding identity for {name}')
                self.assertLessEqual(len(row_id), 64)
                self.assertRegex(row_id, r'^[a-z0-9][a-z0-9-]*$')
                identities.append(row_id)
                # Observe the generated Client's boundary calls and rendered element.
                client = subprocess.run(['node', '--input-type=module', '-', str(out / 'client.js')],
                    input="""
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
let registration, namespace, slot, panel;
vm.runInNewContext(readFileSync(process.argv[2], 'utf8'), {
  window: { __ModuleLoader__: { load(value) { registration = value; } } },
});
const plugin = registration.factory(() => ({
  createElement: (type, props, ...children) => ({ type, props, children }),
}));
plugin.apply({
  effect: callback => callback(),
  locale: { register(value) { namespace = value; } },
  slots: {
    inject: (_name, callback) => callback(),
    register(options, component) { slot = options; panel = component; },
  },
});
const tree = panel({ t: key => key, subject: { kind: 'bundle', pkg: { name: registration.id } } });
console.log(JSON.stringify({ namespace, id: slot.id, locale: slot.locale,
  attributes: Object.keys(tree.props).filter(key => key.startsWith('data-')),
  css: tree.children.find(child => child.type === 'style').children.join(''),
}));
""", capture_output=True, text=True)
                self.assertEqual(client.returncode, 0, client.stderr)
                values = json.loads(client.stdout)
                self.assertEqual((values['namespace'], values['id'], values['locale']), (row_id,) * 3)
                self.assertEqual(values['attributes'], ['data-' + row_id])
                self.assertIn('[data-' + row_id + ']', values['css'])
                again = Path(tmp) / (str(index) + '-again')
                repeated = self.run_scaffold(again, '--name', name, '--kind', 'host')
                self.assertEqual(repeated.returncode, 0, repeated.stderr)
                self.assertEqual((again / 'cordis.patch.yml').read_text(),
                                 (out / 'cordis.patch.yml').read_text())
                self.assertEqual(json.loads(repeated.stdout)['tool'], json.loads(result.stdout)['tool'])
                if name == '@a/b':
                    self.assertEqual(json.loads(result.stdout)['tool'], 'a_b_c93bbe63_inspect')
            self.assertEqual(len(set(identities)), len(names))


class ProbeTests(unittest.TestCase):
    def test_baseline_detects_changed_surface_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'apps/cli').mkdir(parents=True)
            (root / 'apps/cli/package.json').write_text(json.dumps({
                'name': '@deepseek-ai/dsh', 'version': '0.2.0-rc.2'}))
            surface = root / 'AGENTS.md'
            surface.write_text('old API')
            command = ['python3', str(SKILL / 'scripts/probe_dsh.py'), '--dsh', str(root)]
            first = json.loads(subprocess.check_output(command))
            surface.write_text('new API')
            second = json.loads(subprocess.check_output(command))
            self.assertNotEqual(first['surfaces']['AGENTS.md'], second['surfaces']['AGENTS.md'])
            self.assertIsNone(second['commit'])
            output = root / 'baseline.json'
            output.write_text('user evidence')
            result = subprocess.run([*command, '--output', str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), 'user evidence')


if __name__ == '__main__':
    unittest.main()
