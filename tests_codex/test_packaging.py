"""Observable full-edition discovery and archive contracts."""

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('codex_port_tests', BASE / 'tools/codex_port.py')
port = importlib.util.module_from_spec(spec)
spec.loader.exec_module(port)


class FullPackageTests(unittest.TestCase):
    def test_all_source_resources_and_unique_workflows_are_present(self):
        result = port.validate()
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['source_files'], 505)
        self.assertEqual(result['missing_source_files'], 0)
        self.assertEqual(result['core_skills'], 26)
        self.assertEqual(result['specialist_prompts'], 19)
        self.assertEqual(len(result['extension_names']), 9)
        self.assertEqual(result['unique_discoverable_skills'], 33)

    def test_codex_manifests_agree_and_do_not_autotrust_hooks(self):
        root = json.loads((port.ROOT / 'plugin.json').read_text(encoding='utf-8'))
        overlay = json.loads((port.ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(root['name'], overlay['name'])
        self.assertEqual(root['version'], overlay['version'])
        self.assertEqual(root['extensions']['com.openai']['hooks'], [])
        self.assertEqual(overlay['hooks'], [])
        self.assertEqual(overlay['skills'], './codex-skills/')

    def test_archive_is_reproducible_complete_and_has_no_runtime_state(self):
        with tempfile.TemporaryDirectory(dir=BASE / '.runtime') as temporary:
            first = port.build(Path(temporary) / 'one')
            second = port.build(Path(temporary) / 'two')
            self.assertEqual(first['sha256'], second['sha256'])
            with zipfile.ZipFile(first['archive']) as archive:
                names = archive.namelist()
                for required in ('plugin.json', '.codex-plugin/plugin.json', 'scripts/codex_seo.py',
                                 'requirements.txt', 'extensions/codex-integrations.json', 'NOTICE.md'):
                    self.assertIn(required, names)
                self.assertEqual(len([name for name in names if name.startswith('codex-skills/') and
                                      name.endswith('/SKILL.md')]), 33)
                for name in names:
                    self.assertNotIn('..', Path(name).parts)
                    self.assertFalse(name.startswith('/'))
                    self.assertFalse(any(part in {'.venv', '__pycache__', '.runtime', '.git'}
                                         for part in Path(name).parts))
                self.assertIsNone(archive.testzip())


if __name__ == '__main__':
    unittest.main()
