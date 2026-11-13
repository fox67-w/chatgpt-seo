"""Full-port workflow coverage, discovery and retained source artifacts."""

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'tools'))

import port_codex_workflows as port


class CodexWorkflowTests(unittest.TestCase):
    def test_all_source_workflows_and_optional_integrations_are_present(self):
        result = port.check(port.DEFAULT_ROOT)
        self.assertTrue(result['valid'], result['errors'])
        self.assertEqual(result['core_skills'], 26)
        self.assertEqual(result['core_agents'], 19)
        self.assertEqual(result['extensions'], 9)
        self.assertEqual(result['unique_skills'], 33)

    def test_codex_skill_metadata_is_specific_and_invocable(self):
        paths = [*port.DEFAULT_ROOT.joinpath('skills').glob('*/SKILL.md'),
                 *port.DEFAULT_ROOT.joinpath('extensions').glob('*/skills/*/SKILL.md')]
        for path in paths:
            with self.subTest(skill=path.relative_to(port.DEFAULT_ROOT).as_posix()):
                header, _ = port.split_frontmatter(path.read_text(encoding='utf-8'))
                name = port.scalar(header, 'name')
                ui = (path.parent / 'agents/openai.yaml').read_text(encoding='utf-8')
                prompt = json.loads(re.search(r'^  default_prompt: (.+)$', ui, re.M).group(1))
                short = json.loads(re.search(r'^  short_description: (.+)$', ui, re.M).group(1))
                self.assertIn('$' + name, prompt)
                self.assertTrue(25 <= len(short) <= 64)

    def test_documented_managed_script_targets_exist(self):
        found = set()
        for path in port.documents(port.DEFAULT_ROOT):
            text = path.read_text(encoding='utf-8')
            for extension, name in re.findall(
                    r'codex_seo\.py["\x27]?\s+run\s+(?:--extension\s+([a-z-]+)\s+)?([a-z][a-z0-9_]*\.py)',
                    text):
                target = (port.DEFAULT_ROOT / f'extensions/{extension}/scripts/{name}'
                          if extension else port.DEFAULT_ROOT / 'scripts' / name)
                with self.subTest(document=path.relative_to(port.DEFAULT_ROOT).as_posix(), target=name):
                    self.assertTrue(target.is_file(), str(target))
                found.add((extension, name))
        self.assertGreaterEqual(len(found), 40)

    def test_attributed_flow_reference_snapshots_keep_source_bytes(self):
        evidence = json.loads((BASE / 'tests/fixtures/codex-flow-source.json').read_text(encoding='utf-8'))
        self.assertEqual(evidence['commit'], 'cca7e4a267991aca880efade1fd12e8498caf2ce')
        for entry in evidence['files']:
            data = (port.DEFAULT_ROOT / entry['path']).read_bytes()
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            with self.subTest(path=entry['path']):
                self.assertEqual(hashlib.sha1(blob).hexdigest(), entry['git_blob_sha'])

    def test_audit_example_does_not_score_unavailable_evidence_as_zero(self):
        text = (port.DEFAULT_ROOT / 'skills/seo-audit/SKILL.md').read_text(encoding='utf-8')
        block = re.search(r'```json\n(.*?)\n```', text, re.S).group(1)
        example = json.loads(block)
        self.assertIsNone(example['summary']['health_score'])
        self.assertIsNone(example['summary']['coverage']['total_pages'])
        self.assertIsNone(example['categories'][0]['score'])
        self.assertEqual(example['categories'][0]['evidence_status'], 'unmeasured')

    def test_conversion_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ('skills', 'agents', 'extensions'):
                shutil.copytree(port.DEFAULT_ROOT / directory, root / directory,
                                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            port.apply(root)
            before = {path.relative_to(root): path.read_bytes()
                      for path in root.rglob('*') if path.is_file()}
            self.assertEqual(port.apply(root), [])
            after = {path.relative_to(root): path.read_bytes()
                     for path in root.rglob('*') if path.is_file()}
            self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
