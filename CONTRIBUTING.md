# Contributing to ChatGPT SEO

ChatGPT SEO contains two editions. The full Codex execution package is in
`plugins/codex-seo/`; the original instruction-first ChatGPT companion is in
`plugins/ai-marketing-hub-seo/`. State which edition a change affects. Preserve
the companion's SEO-pro identity, the upstream source inventory, original MIT
notices, and the FLOW reference attribution and byte hashes.

For the full edition, use Python 3.11-3.14. Install the runtime and development
dependencies in a virtual environment, then run these checks from the root:

```bash
python -m pip install -r plugins/codex-seo/requirements.txt -r plugins/codex-seo/requirements-dev.txt
python tools/port_codex_workflows.py --check
python tools/codex_port.py --generate
python tools/run_codex_regressions.py
python tools/codex_port.py --build
```

The regression runner uses loopback HTTP fixtures. It retains the source SEO
analysis tests and maps exact Claude host assumptions to reviewed Codex cases.
See [the verification record](docs/CODEX_VERIFICATION.md) and
`tests_codex/source_contract_replacements.json`. New replacements need a precise
host-contract reason and an active native equivalent. Do not waive analysis,
fetcher, parser, schema, quota or evidence checks.

Check the companion and shared tooling with:

```bash
python tools/validate_plugin.py
python -m unittest discover -s tests -v
python tools/package_plugin.py --check-downloads
```

The companion build must continue to reproduce its pinned release. Full-edition
builds are written to `dist/codex/`. Keep runtime environments, `.env` files,
provider tokens, generated client reports and private exports out of commits
and archives. Use synthetic or redacted fixtures. Provider routes must declare
their account, tool, authorization and cost requirements; missing evidence must
remain unknown.

Root `rollout/` and `tools/rollout.py` retain upstream companion migration
tooling. They are separate from normal installation and this repository's
publication. Do not use them to change another account or repository.

Describe the resulting behavior and relevant verification in a pull request.
For support and security reporting, see [Support](SUPPORT.md) and
[Security](SECURITY.md).
