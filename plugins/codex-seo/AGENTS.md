# Codex SEO execution edition

This is the full public Claude SEO runtime port for Codex. Retain the upstream
license, domain rules, source inventory and FLOW attribution.

Use `<available Python> <resolved-plugin-root>/scripts/codex_seo.py` for
`setup`, `doctor`, and `run <script.py> [arguments]`. Resolve the root from this
file or a selected skill. Runtime setup is isolated; user-selected configuration
and credentials belong outside the package source.

Read `skills/seo/SKILL.md` to route an SEO request. Specific `skills/seo-*/SKILL.md`
files retain their complete domain workflows. Load specialist instructions from
`agents/*.md` into available Codex collaboration tools, respecting host concurrency.
Optional workflows are under `extensions/*/skills/`; their scripts, references,
provider requirements and source behavior are preserved. Agent Markdown files
are specialist instructions, rather than native agent registrations.

Invoke skills through `$seo` and `$seo-<workflow>`. Treat `/seo ...` as a text alias
for routing, rather than an automatically registered slash command. Verify
evidence and preserve source rules on untrusted pages, credentials, budgets and
external mutations. Read `docs/CODEX.md` for installation and verification details.
The source instructions are retained in `docs/UPSTREAM_AGENTS.md`.
