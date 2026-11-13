# Full Codex edition verification

Verified on Windows, 13 November 2026, using Python 3.12.14.

The complete public Claude SEO 2.6.0 source at commit
cca7e4a267991aca880efade1fd12e8498caf2ce was retained: 505 original paths,
26 core workflows, 19 core specialist prompts, 63 original Python files and
nine optional extensions. There are 33 unique discoverable skills across 35
source skill folders. All 35 skill frontmatters validated. All 45 retained
FLOW reference/lock files match their original Git hashes.

## Tests and execution

| Check | Result |
| --- | --- |
| Codex regression suite | 2,324 passed, 29 skipped, 78 reviewed host-contract translations; 387 subtests passed |
| Companion/shared unit suite | 155 run, 2 platform skips, no failures |
| Workflow adaptation and resource checks | Passed, with no pending document changes |
| Managed runtime and Chromium | Ready |
| Real runtime smoke checks | All 10 passed |
| Public desktop screenshot capture | Passed |
| Earlier ChatGPT package reproduction | Exact ZIP/checksum/inventory match retained |

The 78 deselections are exact old Claude host/install/manifest assertions with
reviewed native Codex equivalents. The source cases remain on disk. Four
original mirror invariants were repaired and remain active. The review also
covers eight explicit POSIX-only old installer-writer cases. No SEO analysis,
parser, fetcher, schema, quota or measurement invariant was waived. The detailed
matrix is in tests_codex/source_contract_replacements.json at repository root
and is also copied into the package's docs folder.

The runtime smoke used a controlled local HTTP site for fetch, sitemap discovery
and persisted drift, a public JavaScript test site for guarded browser rendering,
and an offline synthetic document for independent Chromium JavaScript execution.
At https://quotes.toscrape.com/js/ the renderer returned HTTP 200 and observed
13 raw words versus 265 rendered words. The separate inline JavaScript fixture
ran with no browser network requests. Real HTML, Excel and PDF files were written.
Schema/cost/auth/quota and account-data logic were exercised by the preserved
regression tests and Codex adapters, rather than billed provider calls.

## Fixes demonstrated during validation

- Native Codex paths, environment names, tool routing and specialist delegation.
- Complete project-scoped installation with 33 usable discovery bridges, conflict
  preservation and safe removal of unchanged installer-owned discovery files.
- Supported Python 3.11-3.14 selection, including Windows fallback from an
  unsupported default and refusal of an unsupported explicit override.
- Fail-closed Windows ledger retries, verified with 20 concurrent processes.
- Chromium PDF fallback when native WeasyPrint libraries are absent on Windows.
- Machine-readable report JSON when an optional native import fails.
- Missing report evidence remains unknown; it does not become a passing score,
  clean bill of health, invented roadmap or claimed Google API data source.

## Practical limits

All nine provider routes are retained. Their live behavior needs the relevant
account, authorization, quota, MCP/CLI capability and applicable budget. No live
paid-provider account was connected for these checks. Profound and SE Ranking
retain source workflows, whose original implementation requires an independent
provider tool rather than a bundled standalone API client.

The inherited URL policy permits opted-in local targets for raw HTTP but blocks
their browser navigation. That guard was preserved. Native plugin installation
in the user's app and Linux execution have not been verified locally.
Ubuntu/Windows CI is configured in the project; current hosted results are
available on the [Actions page](https://github.com/fox67-w/chatgpt-seo/actions).
Functional tests do not establish identical AI judgments
or ranking results compared with Claude without comparative site audits.

Detailed results are in CODEX_VERIFICATION.json. Runtime logs and sample outputs
remain under the ignored dist/verification directory and are excluded from builds.
