"""Codex optional integration plans and opt-in schema adapter behavior."""

import contextlib
import errno
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import Mock, patch

PACKAGE = Path(__file__).resolve().parents[1] / 'plugins/codex-seo'
EXTENSIONS = PACKAGE / 'extensions'


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CodexExtensionPlans(unittest.TestCase):
    def setUp(self):
        self.tools = load_file('codex_extension_test_tools', EXTENSIONS / 'codex-extension.py')

    def test_catalog_retains_every_public_optional_extension(self):
        providers = self.tools.load_catalog()
        self.assertEqual(set(providers), {'ahrefs', 'banana', 'bing-webmaster', 'dataforseo',
                                         'firecrawl', 'matomo', 'profound', 'seranking', 'unlighthouse'})
        for name, provider in providers.items():
            with self.subTest(extension=name):
                self.assertTrue((EXTENSIONS / name / 'skills' / provider['skill'] / 'SKILL.md').is_file())
                self.assertTrue((PACKAGE / provider['source']).is_file())

    def test_mcp_fragments_are_valid_toml_with_environment_name_allowlists(self):
        for name in ('ahrefs', 'banana', 'dataforseo', 'firecrawl'):
            with self.subTest(extension=name):
                provider = self.tools.load_catalog()[name]
                servers = tomllib.loads(self.tools.mcp_toml(name))['mcp_servers']
                self.assertEqual(servers[provider['mcp']['name']],
                                 {key: provider['mcp'][key] for key in ('command', 'args', 'env_vars')})

    def test_plan_never_serializes_credential_values_or_claims_connection(self):
        sentinel = 'synthetic-secret-that-must-not-be-emitted'
        with patch.dict(os.environ, {'FIRECRAWL_API_KEY': sentinel}):
            plan = self.tools.integration_plan('firecrawl')
            self.assertTrue(plan['environment_present']['FIRECRAWL_API_KEY'])
            self.assertEqual(plan['connected'], 'not_checked')
            self.assertFalse(plan['writes'])
            self.assertNotIn(sentinel, json.dumps(plan) + self.tools.mcp_toml('firecrawl'))

    def test_local_runner_or_workflow_cannot_be_misrepresented_as_bundled_mcp(self):
        for name in ('bing-webmaster', 'matomo', 'profound', 'seranking', 'unlighthouse'):
            with self.subTest(extension=name), self.assertRaisesRegex(ValueError, 'no bundled MCP'):
                self.tools.mcp_toml(name)

    def test_planning_creates_no_home_or_project_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            env = {**os.environ, 'HOME': temporary, 'USERPROFILE': temporary,
                   'CODEX_SEO_DATA_DIR': str(root / 'runtime')}
            result = subprocess.run([sys.executable, str(EXTENSIONS / 'codex-extension.py'), 'plan', 'banana'],
                                    cwd=root, env=env, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)['connected'], 'not_checked')
            self.assertEqual(list(root.iterdir()), [])

    def test_output_fragment_does_not_overwrite_existing_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'selected.toml'
            target.write_text('existing = true\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(EXTENSIONS / 'codex-extension.py'),
                                     'toml', 'ahrefs', '--output', str(target)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(target.read_text(encoding='utf-8'), 'existing = true\n')

    def test_banana_fragment_does_not_persist_compatibility_key(self):
        setup = load_file('codex_banana_setup_test', EXTENSIONS / 'banana/scripts/setup_mcp.py')
        sentinel = 'synthetic-banana-key-value'
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'banana.toml'
            with contextlib.redirect_stdout(io.StringIO()) as output:
                setup.setup_mcp(sentinel, output=target)
            self.assertNotIn(sentinel, target.read_text(encoding='utf-8') + output.getvalue())
            self.assertIn('GOOGLE_AI_API_KEY', tomllib.loads(target.read_text())['mcp_servers']['nanobanana-mcp']['env_vars'])

    def test_activation_wrappers_delegate_scoped_parent_installer(self):
        for extension in EXTENSIONS.iterdir():
            if not extension.is_dir() or extension.name == '__pycache__':
                continue
            for wrapper in list(extension.glob('*.sh')) + list(extension.glob('*.ps1')):
                with self.subTest(wrapper=wrapper):
                    text = wrapper.read_text(encoding='utf-8')
                    self.assertIn('install-codex.py', text)
                    self.assertIn(extension.name, text)
                    self.assertNotIn('.claude', text)
                    self.assertNotIn('Read-Host', text)
                    self.assertNotIn('rm -rf', text)


class BananaLedgerLocks(unittest.TestCase):
    def setUp(self):
        self.module = load_file('codex_banana_cost_lock_test', EXTENSIONS / 'banana/scripts/cost_tracker.py')

    def test_windows_contention_retries_without_falling_back_to_an_unlocked_write(self):
        windows = Mock(LK_NBLCK=2)
        windows.locking.side_effect = [OSError(errno.EACCES, 'locked'),
                                       OSError(errno.EDEADLK, 'contended'), None]
        handle = Mock()
        with patch.object(self.module, 'fcntl', None), patch.object(self.module, 'msvcrt', windows), \
             patch.object(self.module.time, 'sleep') as sleep:
            self.module._lock(handle, exclusive=True)
        self.assertEqual(windows.locking.call_count, 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertTrue(all(call.args[1] == windows.LK_NBLCK for call in windows.locking.call_args_list))

    def test_windows_lock_timeout_fails_closed(self):
        windows = Mock(LK_NBLCK=2)
        windows.locking.side_effect = OSError(errno.EACCES, 'locked')
        with patch.object(self.module, 'fcntl', None), patch.object(self.module, 'msvcrt', windows), \
             patch.object(self.module.time, 'monotonic', side_effect=[0.0, 31.0]), \
             self.assertRaisesRegex(self.module.LedgerError, 'Refusing to update it unlocked'):
            self.module._lock(Mock(), exclusive=True)


class CodexSchemaAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter_path = PACKAGE / 'hooks/codex-schema-check.py'
        self.adapter = load_file('codex_schema_adapter_test', self.adapter_path)

    def test_default_hook_discovery_is_inactive_and_opt_in_template_is_available(self):
        default = json.loads((PACKAGE / 'hooks/hooks.json').read_text(encoding='utf-8'))
        example = json.loads((PACKAGE / 'hooks/codex-hooks.example.json').read_text(encoding='utf-8'))
        self.assertEqual(default['hooks'], {})
        self.assertIn('apply_patch', example['hooks']['PostToolUse'][0]['matcher'])

    def test_event_extracts_multiple_apply_patch_paths_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('a.html', 'moved.tsx', 'notes.md'):
                (root / name).write_text('synthetic', encoding='utf-8')
            event = {'cwd': str(root), 'tool_input': {'command': '*** Begin Patch\n*** Update File: a.html\n'
                     '*** Move to: moved.tsx\n*** Update File: a.html\n*** Add File: notes.md\n*** End Patch'}}
            self.assertEqual(self.adapter.event_paths(event), [root / 'a.html', root / 'moved.tsx'])

    def test_event_cannot_read_a_path_outside_session_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'workspace'
            root.mkdir()
            outside = root.parent / 'outside.html'
            outside.write_text('synthetic', encoding='utf-8')
            event = {'cwd': str(root), 'tool_input': {'file_path': str(outside)}}
            self.assertEqual(self.adapter.event_paths(event), [])

    def test_native_event_reports_placeholder_as_blocking_review_feedback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'page.html').write_text('<script type="application/ld+json">'
                '{"@context":"https://schema.org","@type":"Organization","name":"[Business Name]"}'
                '</script>', encoding='utf-8')
            event = {'cwd': str(root), 'tool_name': 'apply_patch', 'tool_input': {'command':
                     '*** Begin Patch\n*** Update File: page.html\n*** End Patch'}}
            result = subprocess.run([sys.executable, str(self.adapter_path)], input=json.dumps(event),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            feedback = json.loads(result.stdout)
            self.assertEqual(feedback['decision'], 'block')
            self.assertIn('placeholder', feedback['reason'].lower())
            self.assertEqual(feedback['hookSpecificOutput']['hookEventName'], 'PostToolUse')

    def test_node_launcher_accepts_explicit_codex_python_and_preserves_exit_code(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js is unavailable')
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / 'result.py'
            script.write_text('raise SystemExit(2)\n', encoding='utf-8')
            env = {**os.environ, 'CODEX_SEO_PYTHON': sys.executable}
            result = subprocess.run([node, str(PACKAGE / 'hooks/run-python-hook.js'), str(script)],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)


if __name__ == '__main__':
    unittest.main()
