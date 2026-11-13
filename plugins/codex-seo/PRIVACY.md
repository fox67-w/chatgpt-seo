# Privacy for ChatGPT SEO's Codex edition

This statement covers the independent Codex adaptation in this package. The
original Claude SEO statement is preserved in
[UPSTREAM_PRIVACY.md](docs/UPSTREAM_PRIVACY.md) for attribution and history.
The regular ChatGPT companion has its own
[privacy statement](../ai-marketing-hub-seo/legal/PRIVACY.md).

## Processing and network requests

The Python analysis helpers run on the machine or execution environment that
launches them. Reports, screenshots, caches and drift databases are written
there. Codex may send prompts, supplied files and tool results to its model
service under the host's account settings and policies. Local helper execution
does not mean that the whole AI conversation stays on the device.

Audits fetch the URLs you select. Rendering can request scripts, images and
other resources from the target site and its public dependencies. Sites and
API providers receive ordinary network request information. Managed setup
downloads Python dependencies and Chromium. FLOW synchronization fetches public
references from GitHub. The package does not bundle a publisher-operated
task-data receiver or telemetry service.

Use only the site data and account access needed for the task. Avoid including
credentials, unrelated personal data or confidential client exports in prompts,
reports, screenshots, public issues or source commits.

## Optional external services

Selecting a provider route can transmit the corresponding task data:

| Route | Typical data transmitted |
| --- | --- |
| Google Search Console, GA4 and Google Ads | Authorized property/account queries, URLs, dates and keyword seeds |
| PageSpeed, CrUX, YouTube and Cloud Natural Language | Analyzed URLs/origins, search queries or supplied text |
| Backlink sources, Ahrefs, DataForSEO and Bing | Domains, URLs, keywords, products and requested metrics |
| Firecrawl | Requested URLs and crawl/scrape parameters |
| Banana / Gemini image tools | Image prompts and any reference images supplied for the operation |
| Matomo | The selected instance, site ID, report parameters and API authorization |
| Profound and SE Ranking | Brands, domains, keywords and queries sent through the selected provider tool |
| IndexNow and Google's Indexing API | Submitted URLs and required authorization or verification data |
| Unlighthouse | Requests from the local CLI/browser to the target site and its page resources |

Provider routes require the applicable service, permissions, credentials, quota
and budget. Provider and host policies govern their handling and retention.
Account authorization is not supplied by installing these workflows.

## Credentials and local files

The default helper credential directory is ~/.config/codex-seo, respecting
XDG_CONFIG_HOME. CODEX_SEO_CONFIG_DIR selects a different directory.
CODEX_SEO_DATA_DIR places configuration and cache data under a selected runtime
directory when the more specific overrides are absent. CODEX_SEO_CACHE_DIR
overrides cache placement. Legacy configuration environment aliases remain
supported for migration; do not point them at unrelated credential stores.

OAuth and provider helpers can save authorization material locally. Protect
these directories with your operating system's access controls. POSIX file
modes do not provide Windows ACL guarantees. Local reports and caches remain
until you remove them; uninstalling discovery files does not erase copied
package resources, credentials or analysis outputs.

Repository and archive filters exclude common credential and runtime files,
but filters cannot identify every private file. Review changes before sharing.
Do not place secrets inside package source or public test fixtures.

For questions, use the project's [support guidance](../../SUPPORT.md).
