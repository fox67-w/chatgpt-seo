"""Exercise project installs without touching the user's real discovery folder."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


WORKSPACE = Path(__file__).resolve().parents[1]
PACKAGE = WORKSPACE / 'plugins/codex-seo'
REVIEW = WORKSPACE / '.runtime/installer-review'
REVIEW.resolve().relative_to(WORKSPACE.resolve())
REVIEW.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PACKAGE))
import codex_package

SPEC = importlib.util.spec_from_file_location('codex_installer_review', PACKAGE / 'install-codex.py')
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def snapshot(root):
    return {path.relative_to(root).as_posix():
            (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
            for path in root.rglob('*') if path.is_file() and not path.is_symlink()}


def fixture_package(root):
    (root / 'skills/seo').mkdir(parents=True)
    (root / 'skills/seo/SKILL.md').write_text(
        '---\nname: seo\ndescription: "Review supplied SEO evidence."\n---\n# SEO\n', encoding='utf-8')
    (root / 'extensions/matomo/skills/seo-matomo').mkdir(parents=True)
    (root / 'extensions/matomo/skills/seo-matomo/SKILL.md').write_text(
        '---\nname: seo-matomo\ndescription: "Review supplied Matomo data."\n---\n# Matomo\n', encoding='utf-8')
    (root / 'plugin.json').write_text('{"name":"codex-seo","version":"9.8.7"}\n')
    return root


class FullInstallerIntegration(unittest.TestCase):
    def test_full_install_all_skills_reapply_remove_and_preserve_edits(self):
        with tempfile.TemporaryDirectory(dir=REVIEW, prefix='full-install-') as temporary:
            base = Path(temporary).resolve()
            base.relative_to(REVIEW.resolve())
            source = base / 'frozen source with spaces'
            source.mkdir()
            # Freeze the current package so other agents can keep authoring it.
            for path in codex_package.package_files(PACKAGE):
                target = source / path.relative_to(PACKAGE)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
            project = base / 'user project with spaces'

            def command(*arguments, expected=0):
                result = subprocess.run(
                    [sys.executable, str(source / 'install-codex.py'), '--project', str(project), *arguments],
                    cwd=base, capture_output=True, text=True, encoding='utf-8', timeout=60,
                )
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout)

            dry = command('--dry-run')
            self.assertFalse(dry['applied'])
            self.assertEqual(len(dry['skills']), 33)
            self.assertFalse(project.exists())
            applied = command('--apply')
            self.assertTrue(applied['applied'])
            package = project / '.agents/packages/codex-seo'
            self.assertTrue((package / 'scripts/codex_seo.py').is_file())
            names = set(applied['skills'])
            for name in names:
                bridge = project / '.agents/skills' / name / 'SKILL.md'
                self.assertTrue(bridge.is_file(), name)
                self.assertEqual(codex_package.metadata(bridge)[0], name)
                target = re.search(r'\[complete workflow\]\(([^)]+)\)', bridge.read_text(encoding='utf-8'))
                self.assertIsNotNone(target, name)
                complete = (bridge.parent / target.group(1)).resolve()
                complete.relative_to(package.resolve())
                self.assertTrue(complete.is_file(), name)
                self.assertTrue((bridge.parent / 'agents/openai.yaml').is_file(), name)

            resources = subprocess.run(
                [sys.executable, str(package / 'scripts/consistency_check.py'), '--json'],
                cwd=base, capture_output=True, text=True, encoding='utf-8', timeout=60,
            )
            self.assertEqual(resources.returncode, 0, resources.stdout + resources.stderr)
            self.assertEqual(json.loads(resources.stdout)['errors'], [])

            before = snapshot(project)
            command('--apply')
            self.assertEqual(snapshot(project), before, 'Reapply must preserve file contents and timestamps')

            removed_names = {'seo-matomo'}
            removal = command('--extension', 'matomo', '--remove', '--dry-run')
            self.assertEqual(set(removal['skills']), removed_names)
            self.assertEqual(snapshot(project), before)
            command('--extension', 'matomo', '--remove', '--apply')
            remaining = {path.parent.name for path in (project / '.agents/skills').glob('*/SKILL.md')}
            self.assertEqual(remaining, names - removed_names)
            self.assertTrue((package / 'extensions/matomo/scripts/matomo_report.py').exists()
                            or (package / 'scripts/matomo_report.py').exists())
            command('--extension', 'matomo', '--apply')
            self.assertEqual({path.parent.name for path in (project / '.agents/skills').glob('*/SKILL.md')}, names)

            edited = project / '.agents/skills/seo-audit/SKILL.md'
            edited.write_text(edited.read_text(encoding='utf-8') + '\nUser-authored note.\n', encoding='utf-8')
            preserved = snapshot(project)
            command('--apply', expected=2)
            self.assertEqual(snapshot(project), preserved)
            command('--remove', '--apply', expected=2)
            self.assertEqual(snapshot(project), preserved)


class InstallerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=REVIEW, prefix='boundary-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.base.relative_to(REVIEW.resolve())
        self.source = fixture_package(self.base / 'source')
        self.project = self.base / 'project'
        self.project.mkdir()
        self.root_patch = patch.object(installer, 'ROOT', self.source)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_ancestor_file_is_rejected_before_copying_package(self):
        agents = self.project / '.agents'
        agents.mkdir()
        (agents / 'skills').write_text('User data')
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.plan(self.project)
        self.assertEqual(snapshot(self.project), before)
        self.assertFalse((agents / 'packages').exists())

    def test_state_directory_is_rejected_before_copying_package(self):
        state = self.project / '.agents/codex-seo-install.json'
        state.mkdir(parents=True)
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.plan(self.project)
        self.assertEqual(snapshot(self.project), before)
        self.assertFalse((self.project / '.agents/packages').exists())

    def test_source_overlap_is_rejected_without_writes(self):
        before = snapshot(self.source)
        with self.assertRaises(ValueError):
            installer.plan(self.source)
        self.assertEqual(snapshot(self.source), before)
        self.assertFalse((self.source / '.agents').exists())

    def test_forged_removal_state_cannot_escape_skills(self):
        keep = self.base / 'keep.txt'
        keep.write_text('Keep this user file')
        state = self.project / '.agents/codex-seo-install.json'
        state.parent.mkdir()
        state.write_text(json.dumps({'files': {'../keep.txt': codex_package.digest(keep.read_bytes())}}))
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.plan(self.project, remove=True)
        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(keep.read_text(), 'Keep this user file')

    def test_state_created_after_planning_is_preserved_before_writes(self):
        result = installer.plan(self.project)
        state = self.project / '.agents/codex-seo-install.json'
        state.parent.mkdir()
        state.write_text(json.dumps({'files': {}, 'user_note': 'Preserve this new state'}))
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.execute(result)
        self.assertEqual(snapshot(self.project), before)
        self.assertFalse((self.project / '.agents/packages').exists())

    def test_conflict_created_after_plan_is_preserved_before_other_writes(self):
        result = installer.plan(self.project)
        edited = self.project / '.agents/skills/seo/SKILL.md'
        edited.parent.mkdir(parents=True)
        edited.write_text('A new unrelated user skill')
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.execute(result)
        self.assertEqual(snapshot(self.project), before)
        self.assertFalse((self.project / '.agents/packages').exists())

    def test_removal_rechecks_all_owned_files_before_deleting(self):
        installer.execute(installer.plan(self.project))
        result = installer.plan(self.project, remove=True)
        edited = self.project / '.agents/skills/seo/SKILL.md'
        edited.write_text(edited.read_text(encoding='utf-8') + '\nA later user change.\n', encoding='utf-8')
        before = snapshot(self.project)
        with self.assertRaises(ValueError):
            installer.execute(result)
        self.assertEqual(snapshot(self.project), before)

    def test_state_records_the_actual_source_version(self):
        installer.execute(installer.plan(self.project))
        state = json.loads((self.project / '.agents/codex-seo-install.json').read_text())
        self.assertEqual(state['version'], '9.8.7')

    def test_symlinked_agents_folder_cannot_redirect_installation(self):
        outside = self.base / 'outside'
        outside.mkdir()
        try:
            (self.project / '.agents').symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if getattr(error, 'winerror', None) == 1314:
                self.skipTest('Windows symlink creation requires an unavailable privilege')
            raise
        with self.assertRaises(ValueError):
            installer.plan(self.project)
        self.assertEqual(list(outside.iterdir()), [])

    def test_extension_options_ignore_python_cache_directories(self):
        (self.source / 'extensions/__pycache__').mkdir()
        self.assertEqual(codex_package.extension_names(self.source), ['matomo'])

    def test_dotenv_variants_stay_out_of_source_inventory(self):
        for name in ('.env', '.env.local', '.env.production'):
            (self.source / name).write_text('EXAMPLE_ONLY=fixture')
        included = {path.name for path in codex_package.package_files(self.source)}
        self.assertFalse({'.env', '.env.local', '.env.production'} & included)

    def test_generated_root_outputs_and_configuration_are_excluded(self):
        for folder in ('reports', 'output', 'config', 'credentials', 'ms-playwright'):
            path = self.source / folder / 'generated.json'
            path.parent.mkdir()
            path.write_text('Generated local data')
        fixture = self.source / 'tests/fixtures/reports/example.json'
        fixture.parent.mkdir(parents=True)
        fixture.write_text('Public source fixture')
        names = {path.relative_to(self.source).as_posix() for path in codex_package.package_files(self.source)}
        self.assertIn('tests/fixtures/reports/example.json', names)
        self.assertFalse(any(name.startswith(('reports/', 'output/', 'config/', 'credentials/', 'ms-playwright/'))
                             for name in names))


class InstallerLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=REVIEW, prefix='launchers-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / 'project with spaces'

    def environment(self, **updates):
        env = os.environ.copy()
        env.pop('CODEX_SEO_PYTHON', None)
        env.update(updates)
        return env

    def powershell(self, wrapper, arguments, env):
        shell = shutil.which('pwsh') or shutil.which('powershell')
        if not shell:
            self.skipTest('PowerShell is unavailable')
        return subprocess.run(
            [shell, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(PACKAGE / wrapper),
             '-Project', str(self.project), *arguments], env=env,
            capture_output=True, text=True, encoding='utf-8', timeout=30,
        )

    @unittest.skipUnless(os.name == 'nt', 'Native PowerShell launch test')
    def test_native_powershell_preserves_default_plan_and_remove_arguments(self):
        env = self.environment(CODEX_SEO_PYTHON=sys.executable)
        for wrapper, action in (('install.ps1', 'install'), ('uninstall.ps1', 'remove')):
            with self.subTest(wrapper=wrapper):
                result = self.powershell(wrapper, ['-Extension', 'matomo'], env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload['action'], action)
                self.assertFalse(payload['applied'])
                self.assertEqual(payload['skills'], ['seo-matomo'])
                self.assertEqual(Path(payload['project']), self.project)
                self.assertFalse(self.project.exists())

    @unittest.skipUnless(os.name == 'nt', 'Native PowerShell launch test')
    def test_native_powershell_rejects_explicit_unsupported_python(self):
        stub = self.base / 'python315.cmd'
        stub.write_text('@echo off\necho 3.15\nexit /b 0\n', newline='\r\n')
        env = self.environment(CODEX_SEO_PYTHON=str(stub))
        for wrapper in ('install.ps1', 'uninstall.ps1'):
            with self.subTest(wrapper=wrapper):
                result = self.powershell(wrapper, [], env)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('3.11 to 3.14', result.stderr)
                self.assertFalse(self.project.exists())

    @unittest.skipUnless(os.name == 'nt', 'Native PowerShell launch test')
    def test_native_powershell_skips_315_default_for_versioned_314(self):
        stub = self.base / 'py.cmd'
        stub.write_text('@echo off\nif "%~1"=="-3" goto unsupported\n'
                        'if "%~1"=="-3.14" goto supported\nexit /b 1\n'
                        ':unsupported\necho 3.15\nexit /b 0\n'
                        ':supported\nif "%~2"=="-c" goto supported_probe\n'
                        'echo picked-py-3.14\necho %~nx2\necho %~3\necho %~4\necho %~5\nexit /b 0\n'
                        ':supported_probe\necho 3.14\nexit /b 0\n', newline='\r\n')
        result = self.powershell('install.ps1', ['-DryRun'], self.environment(PATH=str(self.base)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(),
                         ['picked-py-3.14', 'install-codex.py', '--project', str(self.project), '--dry-run'])

    def posix_stubs(self):
        bin_dir = self.base / 'bin'
        bin_dir.mkdir()
        for tool in ('dirname', 'bash'):
            executable = shutil.which(tool)
            if not executable:
                self.skipTest(tool + ' is unavailable')
            (bin_dir / tool).symlink_to(executable)
        for name, version in (('python3', '3.15'), ('python3.14', '3.14')):
            stub = bin_dir / name
            stub.write_text('#!/bin/sh\nif [ "$1" = "-c" ]; then echo ' + version + '; exit 0; fi\n'
                            'printf "%s\\n" "picked-' + name + '" "${1##*/}"\nshift\nprintf "%s\\n" "$@"\n')
            stub.chmod(0o755)
        return bin_dir

    @unittest.skipUnless(os.name == 'posix', 'POSIX shell launch test')
    def test_posix_skips_315_default_and_preserves_arguments(self):
        bin_dir = self.posix_stubs()
        result = subprocess.run([str(bin_dir / 'bash'), str(PACKAGE / 'install.sh'), '--project',
                                 str(self.project), '--dry-run'], env=self.environment(PATH=str(bin_dir)),
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(),
                         ['picked-python3.14', 'install-codex.py', '--project', str(self.project), '--dry-run'])

    @unittest.skipUnless(os.name == 'posix', 'POSIX shell launch test')
    def test_posix_install_and_uninstall_refuse_unsupported_override(self):
        bin_dir = self.posix_stubs()
        for wrapper in ('install.sh', 'uninstall.sh'):
            with self.subTest(wrapper=wrapper):
                result = subprocess.run([str(bin_dir / 'bash'), str(PACKAGE / wrapper), '--project',
                                         str(self.project), '--dry-run'],
                                        env=self.environment(PATH=str(bin_dir), CODEX_SEO_PYTHON=str(bin_dir / 'python3')),
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 2)
                self.assertIn('3.11 to 3.14', result.stderr)
                self.assertFalse(self.project.exists())


if __name__ == '__main__':
    unittest.main()
