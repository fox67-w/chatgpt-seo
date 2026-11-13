"""Codex adapter regressions that require only the Python standard library."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_adapter(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runtime = load_adapter("codex_runtime_adapter_test", "runtime.py")
paths = load_adapter("codex_paths_adapter_test", "codex_paths.py")


def isolated_environment(**values):
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith(("CODEX_SEO_", "CLAUDE_SEO_", "CLAUDE_PLUGIN_", "CODEX_PLUGIN_")):
            del environment[name]
    for name in ("XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME"):
        environment.pop(name, None)
    for name in ("PLUGIN_ROOT", "PLUGIN_DATA"):
        environment.pop(name, None)
    environment.update(values)
    return environment


class CodexLocationTests(unittest.TestCase):
    def test_portable_directory_isolates_all_state(self):
        with tempfile.TemporaryDirectory(prefix="codex runtime ") as temporary:
            data = Path(temporary) / "isolated runtime"
            with patch.dict(os.environ, isolated_environment(CODEX_SEO_DATA_DIR=str(data)), clear=True):
                self.assertEqual(runtime._data_dir(ROOT), (data.resolve(), "override"))
                self.assertEqual(paths.config_dir(), data.resolve() / "config")
                self.assertEqual(paths.cache_dir(), data.resolve() / "cache")
                self.assertFalse(data.exists())

    def test_specific_configuration_and_cache_overrides_take_precedence(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment = isolated_environment(
                CODEX_SEO_DATA_DIR=str(base / "runtime"),
                CODEX_SEO_CONFIG_DIR=str(base / "credentials"),
                CODEX_SEO_CACHE_DIR=str(base / "snapshots"),
            )
            with patch.dict(os.environ, environment, clear=True):
                # Explicit paths are canonicalized, including DOS 8.3 temp aliases.
                self.assertEqual(paths.config_dir(), (base / "credentials").resolve())
                self.assertEqual(paths.cache_dir(), (base / "snapshots").resolve())

    def test_default_paths_are_distinct_from_claude_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            with patch.dict(os.environ, isolated_environment(), clear=True), \
                    patch.object(paths.Path, "home", return_value=home):
                self.assertEqual(paths.config_dir(), home / ".config" / "codex-seo")
                self.assertEqual(paths.cache_dir(), home / ".cache" / "codex-seo")

    def test_codex_override_wins_over_legacy_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment = isolated_environment(
                CODEX_SEO_DATA_DIR=str(base / "codex"),
                CLAUDE_SEO_DATA_DIR=str(base / "legacy"),
                CODEX_SEO_CONFIG_DIR=str(base / "codex-config"),
                CLAUDE_SEO_CONFIG_DIR=str(base / "legacy-config"),
            )
            with patch.dict(os.environ, environment, clear=True):
                self.assertEqual(runtime._data_dir(ROOT)[0], (base / "codex").resolve())
                self.assertEqual(paths.config_dir(), (base / "codex-config").resolve())

    def test_portable_manifest_version_precedes_legacy_source_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text('{"version":"2.6.0"}')
            (root / "plugin.json").write_text('{"version":"2.6.0-codex.1"}')
            self.assertEqual(runtime._plugin_version(root), "2.6.0-codex.1")

    def test_codex_plugin_data_is_supported_without_a_claude_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary) / "plugin-data"
            with patch.dict(os.environ, isolated_environment(CODEX_PLUGIN_DATA=str(data)), clear=True):
                self.assertEqual(runtime._data_dir(ROOT), (data.resolve(), "plugin"))

    def test_native_plugin_data_precedes_compatibility_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment = isolated_environment(PLUGIN_DATA=str(base / "native"),
                                               CODEX_PLUGIN_DATA=str(base / "custom"),
                                               CLAUDE_SEO_DATA_DIR=str(base / "legacy-override"),
                                               CLAUDE_PLUGIN_DATA=str(base / "legacy"))
            with patch.dict(os.environ, environment, clear=True):
                self.assertEqual(runtime._data_dir(ROOT), ((base / "native").resolve(), "plugin"))
                self.assertTrue(runtime._is_plugin(base))

    def test_explicit_data_override_precedes_native_plugin_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment = isolated_environment(PLUGIN_DATA=str(base / "native"),
                                               CODEX_SEO_DATA_DIR=str(base / "explicit"))
            with patch.dict(os.environ, environment, clear=True):
                self.assertEqual(runtime._data_dir(ROOT), ((base / "explicit").resolve(), "override"))

    def test_native_plugin_root_marks_an_archive_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.dict(os.environ, isolated_environment(PLUGIN_ROOT=str(root)), clear=True):
                self.assertTrue(runtime._is_plugin(root))


class CodexEntryTests(unittest.TestCase):
    def invoke(self, arguments, environment, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "codex_seo.py"), *arguments],
            env=environment, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )

    def test_doctor_from_an_unrelated_directory_is_read_only_and_redacted(self):
        with tempfile.TemporaryDirectory(prefix="codex doctor ") as temporary:
            data = Path(temporary) / "private person" / "runtime"
            result = self.invoke(["doctor", "--json"],
                                 isolated_environment(CODEX_SEO_DATA_DIR=str(data)), cwd=temporary)
            self.assertEqual(result.returncode, 3, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ready"])
            self.assertEqual(payload["mode"], "override")
            self.assertNotIn(str(data), result.stdout + result.stderr)
            self.assertFalse(data.exists())

    def test_run_requires_setup_instead_of_using_global_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary) / "runtime"
            result = self.invoke(["run", "parse_html.py", "https://example.test"],
                                 isolated_environment(CODEX_SEO_DATA_DIR=str(data)))
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertIn("codex_seo.py setup", result.stderr)
            self.assertFalse(data.exists())

    def test_cli_rejects_traversal_before_any_setup(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary) / "runtime"
            result = self.invoke(["run", "../runtime.py"],
                                 isolated_environment(CODEX_SEO_DATA_DIR=str(data)))
            self.assertEqual(result.returncode, 2)
            self.assertIn("basename", result.stderr)
            self.assertFalse(data.exists())

    def test_help_has_codex_identity(self):
        result = self.invoke(["--help"], isolated_environment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Codex SEO managed Python runtime", result.stdout)

    @unittest.skipUnless(os.name == "nt", "PowerShell wrapper is exercised on Windows")
    def test_powershell_wrapper_preserves_spaced_python_path_and_flags(self):
        executable = shutil.which("pwsh") or shutil.which("powershell")
        if not executable:
            self.skipTest("PowerShell is unavailable")
        with tempfile.TemporaryDirectory(prefix="codex ps doctor ") as temporary:
            data = Path(temporary) / "runtime with spaces"
            result = subprocess.run(
                [executable, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                 str(SCRIPTS / "codex-seo.ps1"), "doctor", "--json"],
                env=isolated_environment(CODEX_SEO_PYTHON=sys.executable, CODEX_SEO_DATA_DIR=str(data)),
                capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertFalse(json.loads(result.stdout)["ready"])
            self.assertFalse(data.exists())

    @unittest.skipUnless(os.name == "nt", "PowerShell wrapper is exercised on Windows")
    def test_powershell_python_override_is_an_executable_not_a_command(self):
        executable = shutil.which("pwsh") or shutil.which("powershell")
        if not executable:
            self.skipTest("PowerShell is unavailable")
        result = subprocess.run(
            [executable, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(SCRIPTS / "codex-seo.ps1"), "doctor", "--json"],
            env=isolated_environment(CODEX_SEO_PYTHON=sys.executable + "; echo injected-command"),
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("injected-command", result.stdout)


if __name__ == "__main__":
    unittest.main()
