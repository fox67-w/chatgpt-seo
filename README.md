# ChatGPT SEO

An independent adaptation of public [Claude SEO](https://github.com/AgriciDaniel/claude-seo)
for OpenAI Codex, with a smaller companion for regular ChatGPT.

**Use the Codex edition for the full execution workflow:** website fetching,
JavaScript rendering, specialist collaboration, analysis scripts and reports.
Its internal package name and directory remain `codex-seo`.

| Edition | Runs in | What it provides |
| --- | --- | --- |
| Full execution edition | Codex with local tools | The pinned public source workflows, Python runtime, browser support, specialist prompts, data, templates and optional provider extensions. |
| SEO-pro companion | Regular ChatGPT | Instructions and analysis of supplied content or exports. Website retrieval depends on the tools available in your ChatGPT session. It does not install a crawler or run the Codex runtime. |

## Get started

Follow the [installation and first-audit guide](docs/GETTING_STARTED.md) for
Windows PowerShell or macOS/Linux. It installs the complete package into a
project you choose, sets up an isolated Python runtime and installs Chromium.
Python 3.11-3.14 is supported.

Then open that project in Codex and invoke a skill:

```text
$seo-audit Audit https://example.com and save a report with evidence and priorities.
```

For regular ChatGPT, use the [companion setup guide](LOCAL_SETUP.md) and
[Project instructions](chatgpt-project/INSTRUCTIONS.md).

## Included features

- Site and page audits, HTTP fetching, sitemap discovery, JavaScript rendering and screenshots.
- Technical SEO, content and E-E-A-T, schema, images, performance, international SEO and ecommerce.
- Google Search Console, GA4, Google Ads, PageSpeed, CrUX, backlinks, local/Maps research and domain checks.
- GEO/AI access, agent readiness, `llms.txt`, WebMCP, clustering, programmatic SEO and SXO.
- FLOW workflows, drift baselines and comparisons, history, and PDF/HTML/Excel reports.
- Optional Ahrefs, DataForSEO, Firecrawl, Banana, Bing Webmaster, Matomo, Profound, SE Ranking and Unlighthouse routes.
- Native Codex skill discovery and collaboration, project-scoped installation, and opt-in schema hooks.

The full edition retains all 505 files from the pinned public Claude SEO source:
26 core skills, 19 core specialist prompts, 63 Python files and all nine optional
extension directories. Deduplicating mirrored extension skills gives 33 unique
discoverable workflows. The source is pinned to
[`cca7e4a267991aca880efade1fd12e8498caf2ce`](https://github.com/AgriciDaniel/claude-seo/tree/cca7e4a267991aca880efade1fd12e8498caf2ce).
See the [provenance record](plugins/codex-seo/CODEX_PROVENANCE.json) and
[source inventory](docs/claude-source-inventory.json).

## Accounts and costs

The source code is free to use under its licenses. Codex/ChatGPT access and
third-party services have their own plans, quotas and charges. Basic public-page
fetching and local browser analysis do not require a paid SEO-data provider.

Private Google data needs the appropriate authorized account and API setup.
Optional provider workflows need their respective tools or exports, credentials
and an authorized budget where charges apply. Profound and SE Ranking retain
their workflows but do not bundle standalone API clients. Installation does not
connect accounts or purchase data. See [provider setup and runtime details](plugins/codex-seo/docs/CODEX.md).

## Documentation and verification

- [Getting started](docs/GETTING_STARTED.md): installation, runtime setup and a first audit.
- [Full Codex guide](plugins/codex-seo/docs/CODEX.md): workflows, extensions, hooks, runtime and removal.
- [Verification record](docs/CODEX_VERIFICATION.md): regression results, browser checks and remaining limits.
- [Regular ChatGPT setup](LOCAL_SETUP.md): the narrower SEO-pro companion.

Local verification covers the analysis/runtime regressions, public-page fetching,
JavaScript rendering, screenshots, sitemap discovery, drift comparisons and
report generation. Live provider accounts and native host plugin installation
have not been tested. macOS/Linux runtime execution remains unverified locally;
the repository includes cross-platform CI. Included source coverage does not
establish identical judgments or results across AI models.

To check the port and build its archive from the repository root, use a supported
Python executable (replace `python` below if its command has a different name):

```sh
python tools/port_codex_workflows.py --check
python tools/codex_port.py --generate
python tools/codex_port.py --build
```

Build output, checksums and the inventory go under `dist/codex`. A packaged
[full edition ZIP](downloads/codex-seo-0.1.0.zip),
[SHA-256 checksum](downloads/codex-seo-0.1.0.sha256) and
[file inventory](downloads/codex-seo-0.1.0.inventory.json) are also included.
Use the project installer after extracting this ZIP; it is the Codex execution
package, with `codex-seo` as its internal name.

## Attribution and licenses

Original work by Daniel Agrici and the public project contributors. Preserve the
[MIT license](LICENSE), [project notices](NOTICE.md) and
[full-edition notices](plugins/codex-seo/NOTICE.md), including FLOW's CC BY 4.0
attribution and separate asset licenses. The earlier companion retains its
SEO-pro identity and [original README](docs/UPSTREAM_CHATGPT_README.md).
This independent project is not endorsed by OpenAI or Anthropic.
