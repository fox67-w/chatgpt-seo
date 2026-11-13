# Full Codex SEO edition

This edition ports the complete public Claude SEO 2.6.0 source to Codex.
It includes all 26 core workflows, 19 core specialist prompts, 63 original
Python files, schemas, templates, data and nine extension directories.
There are 33 unique skill names after deduplicating the two extension mirrors.
See [provenance](../CODEX_PROVENANCE.json) and [attribution](../NOTICE.md).

## Install in a project

Use Python 3.11 through 3.14. Replace python below with your available executable,
such as python3, py -3, or a host-provided Python path.

    python install-codex.py --project /path/to/project --dry-run
    python install-codex.py --project /path/to/project --apply

The installer copies the complete package into .agents/packages/codex-seo in
the selected project. Discovery files under .agents/skills load the complete
workflow files from that package, retaining the original resource layout.
All unique workflows are discoverable by default. Existing conflicting files
are preserved and reported. Installation does not connect provider accounts.
Open that project in Codex and invoke $seo, $seo-audit, or a specific skill.

For one optional extension:

    python install-codex.py --extension firecrawl --project /path/to/project --apply
    python extensions/codex-extension.py plan firecrawl
    python extensions/codex-extension.py toml firecrawl

The final command prints a Codex MCP fragment containing environment variable
names, rather than secret values. Review it in the intended configuration.
The catalog records all nine providers' requirements. Configuration does not
grant provider permissions or a budget.

The install.ps1 and install.sh wrappers call the same installer and default to a
dry run. The uninstall wrappers, or install-codex.py --remove, remove only owned,
unchanged discovery files. Copied package resources and credential data remain.

The repository also supplies marketplace.json.example. For native plugin
discovery, copy that catalog into the repository's .agents/plugins/marketplace.json,
then restart Codex and select the local marketplace. This is an optional
distribution path; the project skill installer works independently.

## Prepare and check the runtime

From the installed package:

    python scripts/codex_seo.py doctor --json
    python scripts/codex_seo.py setup
    python scripts/codex_seo.py run fetch_page.py https://example.com
    python scripts/codex_seo.py run render_page.py https://example.com --mode auto --json

Setup installs bounded dependencies in an isolated virtual environment and
downloads Chromium for Playwright. Core and browser readiness are reported
separately. The setup --skip-browser option prepares the core only.
Run analysis through the managed entrypoint to select the right dependencies
and browser cache. Bash and PowerShell launchers are also included.

PDF reports use WeasyPrint where its native libraries are available. Otherwise
the managed Chromium browser provides a Windows-compatible fallback. That
fallback disables JavaScript and external network access while rendering the
generated report HTML.

Set CODEX_SEO_DATA_DIR before setup and tool execution to choose a dedicated
workspace runtime. In PowerShell:

    $env:CODEX_SEO_DATA_DIR = Join-Path (Get-Location) '.runtime/codex-seo'
    python scripts/codex_seo.py setup
    python scripts/codex_seo.py doctor --json

Config/cache paths also support CODEX_SEO_CONFIG_DIR and CODEX_SEO_CACHE_DIR.
Default credential stores are Codex-specific. Readiness checks avoid printing
secret values; provider authorization must be completed by the user.

## Included feature families

| Feature | Execution path | Requirement |
| --- | --- | --- |
| Full and page audits | All source workflows and specialist prompts | Site access and Codex tools |
| Crawl and HTTP checks | Safe fetch, sitemap discovery, page and transport tools | Network access |
| JavaScript and screenshots | Playwright renderer and screenshot tools | Installed Chromium |
| Technical SEO | Source canonicals, robots, redirect and sitemap checks | Pages or supplied evidence |
| Content and E-E-A-T | Quality, humanization, verification and briefs | Content evidence |
| Schema and ecommerce markup | Generators, validators, templates and optional hook | Verified business facts |
| Performance | PageSpeed, CrUX and source performance scripts | Applicable APIs and data |
| Google data | GSC, GA4, Google Ads, auth and property scripts | Authorized account/API access |
| Backlinks | Common Crawl, Moz, Bing and verification tools | Applicable sources or exports |
| Local, Maps, international and commerce | Full source workflows and references | Applicable observations/data |
| AI search and agent access | GEO, llms.txt, WebMCP and agentic tools | Site/browser evidence |
| Strategy | Clusters, programmatic SEO, comparisons and SXO | Research and evidence |
| FLOW | All reference and source-lock files retained | Selected FLOW workflow |
| Drift | Baseline, comparison, history and reports | Comparable snapshots |
| PDF and Excel | Original reporting implementation | Runtime dependencies/system support |
| Ahrefs, DataForSEO, Firecrawl | Workflows and Codex MCP fragments | Authorized providers and MCP tools |
| Banana images | Direct helpers and optional MCP | Selected key/model and budget |
| Bing, Matomo, Unlighthouse | Source API or CLI routes | Account, allowlist or local CLI |
| Profound and SE Ranking | Full source workflows | Available provider tool; source has no standalone client |

Specialist Markdown files supply prompts to native Codex collaboration.
The host concurrency limit determines batching. Model selection inherits
the current host settings. The /seo forms remain readable task aliases;
$seo is the native skill invocation. Available native image tools can be used,
and the optional Banana route remains available when selected.

## Schema validation hook

The schema tools remain manually runnable. The Codex event adapter and opt-in
definition are hooks/codex-schema-check.py and hooks/codex-hooks.example.json.
They handle patch events and enforce workspace boundaries. Manifests disable
automatic hooks. To enable the example, review its command/Python environment,
select its definition in the plugin manifest and complete Codex hook trust review.

## Verification

Repository tool tools/codex_port.py validates every source path, discovery bridge,
workflow count and Python syntax. tools/port_codex_workflows.py --check verifies
workflow conversion and retained FLOW material. Builds include checksums and
inventories. Source preservation, unit tests, browser execution, authenticated
provider checks and installed-host audits are distinct verification states.

For development regressions, install requirements-dev.txt into an isolated
development/runtime environment and run the repository's
tools/run_codex_regressions.py with that Python executable. It retains all
upstream SEO analysis tests and uses an explicit reviewed matrix for old
Claude-only host contracts, alongside their native Codex equivalents.

Consult [the verification record](CODEX_VERIFICATION.md) for completed checks.
Matching source coverage does not establish equal model judgments or ranking
results without comparative audits.
