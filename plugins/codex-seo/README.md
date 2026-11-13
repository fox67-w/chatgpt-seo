# ChatGPT SEO - Codex execution package

Complete public Claude SEO execution workflows adapted for Codex.

This is the full execution package of
[ChatGPT SEO](https://github.com/fox67-w/chatgpt-seo). Its internal package and
command name is `codex-seo`.

- 26 core skills and 19 core specialist prompts.
- All 63 original Python files, source data, schemas and reporting templates.
- All nine optional extension directories, yielding 33 unique discoverable skills.
- Isolated Python/Chromium setup, real HTTP checks, rendering and drift snapshots.
- Native Codex discovery, project-scoped install, provider configuration and opt-in hooks.

Read [the Codex guide](docs/CODEX.md) for setup, features and requirements.
Original attribution is in [NOTICE.md](NOTICE.md) and the source revision is
recorded in [CODEX_PROVENANCE.json](CODEX_PROVENANCE.json).

    python install-codex.py --project /path/to/project --dry-run
    python install-codex.py --project /path/to/project --apply
    python scripts/codex_seo.py setup
    python scripts/codex_seo.py doctor --json

Invoke $seo or a specific workflow in the installed Codex project. The complete
package layout is retained, including optional integrations. Provider-dependent
features need their actual accounts, credentials and any applicable budget.
Native image tools can be used when available; the optional Banana route remains.

The original public README is retained in docs/UPSTREAM_README.md for provenance;
its Claude installation instructions describe the source platform.
