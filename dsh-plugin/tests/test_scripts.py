"""Generator behavior: non-destructive output and usable standalone artifacts."""
import json
from pathlib import Path
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
