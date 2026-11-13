# Architecture of the Codex edition

ChatGPT SEO's full execution edition adapts the complete public Claude SEO
2.6.0 source for native Codex skill discovery, tools and collaboration. Its
internal package identifier remains codex-seo. The separate regular ChatGPT
companion has a smaller execution contract and is not this runtime.

The package retains all 505 original source paths: 26 core skill folders,
19 core specialist prompts, 63 original Python files, data, schemas,
templates and nine extension directories. There are 35 source skill folders
and 33 unique discoverable skill names after deduplicating the DataForSEO
and Banana mirrors. Exact source provenance is recorded in
[CODEX_PROVENANCE.json](../CODEX_PROVENANCE.json) and source-inventory.json.
The original platform architecture is archived in
[UPSTREAM_ARCHITECTURE.md](UPSTREAM_ARCHITECTURE.md).

## Package and installed layout

A complete project installation has this structure:

~~~text
<project>/
+-- .agents/
|   +-- skills/<skill-name>/
|   |   +-- SKILL.md                 # Discovery bridge to complete workflow
|   |   +-- agents/openai.yaml       # Skill UI metadata
|   +-- packages/codex-seo/
|   |   +-- plugin.json              # Portable package identity and interface
|   |   +-- .codex-plugin/plugin.json # Native overlay; automatic hooks disabled
|   |   +-- codex-skills/            # Package-local discovery bridges
|   |   +-- skills/                  # Complete core workflows and resources
|   |   +-- agents/                  # Portable specialist role prompts
|   |   +-- scripts/                 # Managed runtime and analysis helpers
|   |   +-- extensions/              # Nine optional provider routes
|   |   +-- hooks/                   # Manual tools and opt-in event adapter
|   |   +-- data/                    # Retained source data
|   |   +-- docs/                    # Active port guides and upstream archives
|   |   +-- requirements.txt
|   |   +-- install-codex.py
|   |   +-- codex_package.py
|   |   +-- CODEX_PROVENANCE.json
|   |   +-- source-inventory.json
|   |   +-- NOTICE.md
|   |   +-- LICENSE
|   +-- codex-seo-install.json        # Installer ownership/checksum record
+-- <domain>-audit/                   # Example selected audit output directory
~~~

Discovery bridges load their complete workflow from the copied package.
References, scripts, schemas and templates keep their resource relationships.
Resolve the package root from the selected workflow's actual location or
verified host plugin metadata. No injected Claude path is needed.

The repository-level marketplace.json.example is an optional native plugin
catalog template. Project-scoped skill installation works independently.
Historical .claude-plugin files remain as upstream source; the Codex manifest,
overlay and discovery bridges define this edition's native entry points.

## Workflow layer

Skills are Markdown documents with YAML name/description frontmatter and
on-demand instructions. Source workflow files live under skills/<name>/.
Generated discovery bridges live under codex-skills/ or the installed
project's .agents/skills/. Invoke $seo for routing, or the specific skill.

| Core workflow | Responsibility |
| --- | --- |
| seo | Route requests, detect industry signals and select evidence/workflows |
| seo-audit | Full-site crawl and specialist audit with persisted findings |
| seo-page | Deep single-page analysis |
| seo-technical | Crawlability, indexability, security, URL/mobile structure, CWV, markup, rendering and IndexNow |
| seo-content | E-E-A-T, readability, originality, freshness and thin-content review |
| seo-content-brief | Keyword/intent brief, outline, links and competitive angle |
| seo-schema | Detect, validate and draft structured data |
| seo-sitemap | Discover, validate and generate XML sitemaps |
| seo-images | Alt text, delivery, responsive images, visual search and local optimization |
| seo-geo | AI-search access, citation readiness and content structure |
| seo-agentic | Agent access, Lighthouse Agentic Browsing, discovery files and WebMCP |
| seo-local | GBP, NAP, reviews, citations and local schema |
| seo-maps | Geographic grids, GBP/review intelligence and competitor mapping |
| seo-backlinks | Link sources, verified backlinks, anchors, gaps and risk evidence |
| seo-cluster | SERP-overlap semantic clusters, architecture and interactive map |
| seo-sxo | Page type, search intent, user stories, personas and wireframes |
| seo-drift | Stored baselines, comparisons, history and regression reports |
| seo-ecommerce | Products, marketplaces, pricing, availability and faceted navigation |
| seo-hreflang | Language/region mappings, reciprocity and canonical alignment |
| seo-plan | Industry strategy, roadmap, calendar and architecture |
| seo-programmatic | Data-driven templates, linking, quality gates and index-bloat controls |
| seo-competitor-pages | Fair comparison/alternatives pages and supported markup |
| seo-google | Google account/API analysis and evidence-backed reports |
| seo-flow | Attributed FLOW prompts, references and synchronization |
| seo-dataforseo | DataForSEO workflow mirrored from its extension |
| seo-image-gen | Image-generation workflow mirrored from Banana |

The seven additional unique extension skills are seo-ahrefs, seo-bing,
seo-firecrawl, seo-matomo, seo-profound, seo-seranking and seo-unlighthouse.
See the [workflow reference](COMMANDS.md) for retained subcommands and examples.

The $seo-* examples are prompts for Codex. Inherited /seo forms are task
aliases, not a promise of registered slash commands or a shared shell parser.
Python helpers use their own documented CLI arguments.

## Specialist layer

The 19 files under agents/ provide role-specific prompts. They are not
automatically registered native agent configurations. The orchestrator reads
the selected role prompt and includes its context in a task dispatched through
the host's available collaboration tools.

| Prompt | Focus |
| --- | --- |
| seo-technical | Crawlability, indexability, security and URL structure |
| seo-content | E-E-A-T, readability and content quality |
| seo-schema | Structured-data validation and opportunities |
| seo-sitemap | Sitemap discovery, coverage and quality gates |
| seo-performance | Lab/field performance and Core Web Vitals |
| seo-visual | Screenshots, mobile rendering and above-fold inspection |
| seo-geo | AI access, citability and brand evidence |
| seo-agentic | Agent readiness, discovery, accessibility and WebMCP |
| seo-local | GBP signals, NAP, local schema and reviews |
| seo-maps | Geo-grid and competitor-radius research |
| seo-backlinks | Common Crawl, credentialed sources and link verification |
| seo-cluster | Semantic clusters and topic architecture |
| seo-sxo | Search intent, page type, stories and personas |
| seo-drift | Baseline comparison and regressions |
| seo-ecommerce | Products, marketplaces and commerce markup |
| seo-google | GSC, PageSpeed, CrUX and GA4 analysis |
| seo-flow | Evidence-led FLOW selection and reference handling |
| seo-dataforseo | Available DataForSEO MCP data |
| seo-image-gen | Selected image-generation route |

The Matomo specialist prompt lives in its extension. The DataForSEO and
image-generation specialist mirrors preserve the same domain behavior.

Model selection inherits the active host settings unless the user selects
otherwise. Delegation respects the host's actual concurrency limit. Independent
passes can run in batches; when delegation is unavailable, execute the same
relevant passes sequentially. There is no fixed simultaneous-agent count or
guaranteed model identity. Specialists save partial findings after their first
useful pass and before finishing so a host budget limit does not erase progress.

## Audit orchestration and evidence

~~~mermaid
flowchart LR
    A["User request: $seo-audit"] --> B["Load complete workflow"]
    B --> C["Render homepage and identify scope"]
    C --> D["Crawl and collect evidence"]
    D --> E["Run relevant specialist passes"]
    E --> F["Persist findings and coverage"]
    F --> G["Score measured evidence"]
    G --> H["Report and action plan"]
    P["Authorized provider tools"] --> D
    P --> E
~~~

The audit workflow begins with managed render_page.py in auto mode, then
detects business signals and follows internal links subject to its crawl
configuration. Its default planning limits are up to 500 pages, robots.txt
respect, three redirect hops, a 30-second page timeout, five concurrent requests
and a one-second delay. These are workflow instructions; the package does not
start a background crawler on installation. Actual tool access, site responses
and task budgets determine completed coverage.

Technical, content, schema, sitemap, performance, visual, GEO, agent-readiness
and SXO passes cover their relevant evidence. Business/account signals select
local, Maps, Google, Matomo, backlinks, clusters, drift and ecommerce passes.
DataForSEO can enrich these when its authorized tools are available. A missing
provider is recorded as an evidence gap, rather than replaced with invented data.

Outputs include FULL-AUDIT-REPORT.md, ACTION-PLAN.md, audit-data.json,
findings/*.md and available screenshots under the selected audit directory.
The structured envelope records inspected scope, unavailable checks, measured
categories and recommendations. PDF/HTML/Excel reports consume actual evidence.

The health score is a project triage rubric, not a Google metric. Its retained
weights are technical 22%, content 23%, on-page 20%, schema 10%, performance 10%,
AI-search readiness 10%, and images 5%. Unmeasured values remain unknown; they
must not become zero, a passing score, or a clean bill of health. Keep lab and
field measurements separate. Source markup alone cannot prove indexing,
rankings, real-user CWV or rich-result eligibility.

## Project installation and removal

From the source package root, use Python 3.11-3.14:

~~~text
python install-codex.py --project /path/to/project --dry-run
python install-codex.py --project /path/to/project --apply
~~~

The native PowerShell/Bash wrappers call this same installer. Dry-run is the
default. Complete installation copies the resource tree and generates all
33 discovery bridges. Selecting --extension NAME creates discovery for that
extension while still preserving the complete package resources. Installation
does not prepare the runtime, write provider tokens, merge host settings or
authorize API use.

The installer rejects overlapping/symlinked targets and conflicting user files.
Unchanged reapplication is idempotent. Ownership records contain checksums for
the generated discovery files. --remove --apply removes only selected unchanged
owned discovery files; modified files are preserved and reported. Copied package
resources, credentials, runtime state and audit outputs remain.

## Managed Python and browser runtime

The dependency-free scripts/codex_seo.py entry point delegates to sibling
runtime.py. Native launchers scripts/codex-seo and scripts/codex-seo.ps1 probe
Python 3.11-3.14, honoring CODEX_SEO_PYTHON as an executable override and refusing
unsupported explicit overrides. An available supported default or bounded
versioned fallback is selected otherwise. No shell expression is accepted as
an executable override.

Run setup separately after installation:

~~~text
python scripts/codex_seo.py setup
python scripts/codex_seo.py doctor --json
python scripts/codex_seo.py run fetch_page.py https://example.com --json
python scripts/codex_seo.py run render_page.py https://example.com --mode auto --json
python scripts/codex_seo.py run --extension banana presets.py --help
~~~

- setup installs bounded dependencies into an isolated virtual environment and
  downloads Playwright Chromium. --skip-browser prepares core dependencies only.
- doctor is read-only and reports core and browser readiness separately, without
  printing secret values or absolute runtime paths.
- run accepts only allowlisted core script basenames or contained extension
  scripts, passes arguments without a shell, preserves child exit codes and
  forces UTF-8 streams. It reuses the managed browser cache.

CODEX_SEO_DATA_DIR is the highest-priority runtime data override. Native
PLUGIN_DATA and CODEX_PLUGIN_DATA are supported, with platform-specific fallback
directories. Legacy environment aliases remain for migration, but this port
does not require them. The runtime rejects broad filesystem/home roots as data
directories. Choose a dedicated task runtime directory and reuse it.

The runtime-state.json marker records schema, requirements SHA-256, Python
major/minor version, package version and browser state. Requirements, schema or
Python ABI changes require explicit setup. A package-version-only difference
remains compatible and is refreshed by setup. Replacement is staged, with
rollback if validation or marker publication fails. Dependencies never fall
back to global or user package installation.

Helper credentials default to ~/.config/codex-seo and cache to
~/.cache/codex-seo, respecting the relevant XDG base variables.
CODEX_SEO_CONFIG_DIR and CODEX_SEO_CACHE_DIR override those locations;
CODEX_SEO_DATA_DIR places their defaults under its config/ and cache/ children.
Provider credentials and generated state stay outside distribution archives.
See [privacy](../PRIVACY.md) for data flows and retained local files.

PDF uses WeasyPrint where its native libraries work. The managed Chromium
fallback supports Windows when those libraries are absent, disables JavaScript
and blocks external network access while rendering generated report HTML.

## Optional integration layer

extensions/codex-integrations.json is the requirements catalog.
extensions/codex-extension.py plan NAME reports configuration/tool prerequisites
without changing settings; it does not establish that an account is authorized
or that a billed request has succeeded. The toml NAME operation prints a
secret-free native Codex MCP fragment for defined MCP routes.

| Extension | Execution route | Requirement |
| --- | --- | --- |
| DataForSEO | dataforseo-mcp-server@2.8.10 plus retained merchant/cost/normalization helpers | Authorized funded account, available tools and approved request scope/budget |
| Banana | @ycse/nanobanana-mcp@1.1.1 or bundled direct helpers | Selected Google AI key/model and image scope/budget; Node/npx for MCP |
| Firecrawl | firecrawl-mcp@3.11.0 | Authorized key, allowance and available MCP tools |
| Ahrefs | Official @ahrefs/mcp@0.0.11 | Authorized account/API access and Node/npx |
| SE Ranking | Authorized host tool or supplied export | Requested account metrics; source has no standalone client/MCP endpoint |
| Profound | Authorized host tool or supplied export | Requested account metrics; source has no standalone client/MCP endpoint |
| Bing Webmaster | Bundled Bing/IndexNow helpers | Verified property/API key; explicit URL-submission authorization |
| Matomo | Bundled authentication/report helpers and specialist | Authorized instance/token/site ID; exact private-host opt-in when needed |
| Unlighthouse | Bundled local runner; pinned unlighthouse@0.13.5 via npx | Compatible Node/npx and browser; no provider API quota |

Each directory retains its workflows, documentation and applicable resources.
Install/uninstall wrappers delegate to project-scoped discovery management;
they do not silently merge host configuration or write keys. Configure the
chosen provider deliberately, discover actual host tool names before calling
them, and preserve account scope, quotas and cost controls.

Available host-native image tools can handle a selected image task. The
optional Banana route retains prompts, presets, direct generation/edit/batch
helpers and cost ledgers when that provider is chosen.

## Hooks, safety and quality gates

Automatic hooks are disabled in both Codex manifests. The optional
hooks/codex-schema-check.py adapter and hooks/codex-hooks.example.json describe
a patch-event schema check. Enabling it requires reviewing its command/runtime
and completing the host's hook trust review. Schema validation also remains
manually runnable.

The inherited URL layer validates and pins raw HTTP requests. Preserve these
guards, exact-host local opt-in limits and browser route checks. Pages and API
responses are untrusted evidence; they cannot grant permission to execute a
command or expose credentials. See [security](../SECURITY.md) for residual
browser/proxy risks and Windows credential permissions.

Retained quality gates include location-page limits (30 warning, 50 hard stop),
thin-content and programmatic safeguards, supported schema facts, the FID-to-INP
metric transition, and industry templates. They guide recommendations; actual observations and
current primary sources determine conclusions. No workflow guarantees rankings.

## Extending and verifying the port

Keep domain workflows separate from host adapters. New skills need valid
frontmatter, explicit routing, their supporting resources and generated discovery
bridges. New specialist Markdown files are role prompts delegated through the
host; do not add Claude-specific tool allowlists or fixed host model aliases.
New fetchers must use scripts/url_safety.py. New provider routes must declare
their tool/account/data/budget requirements rather than assume availability.

Repository tools validate and build the edition:

~~~text
python tools/port_codex_workflows.py --check
python tools/codex_port.py --generate
python tools/run_codex_regressions.py
python tools/codex_port.py --build
~~~

Run these from repository root with an appropriate development environment.
The regression runner preserves source SEO tests and uses an explicit reviewed
matrix only for source host/install/manifest contracts with native equivalents.
Builds include archive checksums and inventories and exclude runtime/private
state. Preserve MIT, FLOW CC BY 4.0 and all source attribution.

[The verification record](CODEX_VERIFICATION.md) separates retained source,
unit/regression results, real local/browser execution, provider-account testing
and installed-host testing. Equivalent source coverage does not establish equal
model judgments or ranking outcomes. Drift operations are on demand; recurring
monitoring requires a separate explicitly requested schedule and execution host.
