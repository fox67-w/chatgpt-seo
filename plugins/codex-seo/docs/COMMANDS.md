# Codex workflow and command reference

## Overview

Invoke the installed hub with $seo or a specific workflow such as $seo-audit.
The examples below are prompts to enter in Codex, not executable shell commands.
Subcommands express task intent that the workflow routes to its available tools.
The inherited /seo forms remain readable aliases; this port does not register a
native slash-command parser.

Python examples are executable commands run from the installed package root,
normally <project>/.agents/packages/codex-seo. Replace python with an available
Python 3.11-3.14 executable, and replace placeholder arguments before execution.
Use the package's actual path when running from another working directory.
See [setup](CODEX.md) and [architecture](ARCHITECTURE.md). The original platform reference is archived in [UPSTREAM_COMMANDS.md](UPSTREAM_COMMANDS.md).

Workflows that require accounts, paid requests, URL submissions, or publishing
need the corresponding tool, authorization, quota and budget. Installation does
not connect those services. Missing data remains unknown, and rubric scores
must identify their evidence and scope. Static markup cannot establish live
indexing, rankings, real-user performance or rich-result eligibility.

## Page-fetching script

Use `python scripts/codex_seo.py run fetch_page.py https://example.com --json` for structured
retrieval. Both the raw path (default, `--render never`) and the rendered path
(`--render auto` or `--render always`) emit JSON through the same
`render_page._json_summary` contract, so the two share one key set: `url`,
`status_code`, `content`, `raw_content`, `is_spa`, `extracted_text`,
`publication_date`, `accessibility_tree`, `accessibility_error`,
`accessibility_partial`, `headers`, `redirect_chain`, `console_errors`,
`render_diagnostics`, `render_engine`, `render_ms`, `mode_used`, `error`,
`structured_data`, and `truncation`. The raw path fills renderer-only fields
(`is_spa`, `extracted_text`, `render_engine`, ...) with `None`/empty defaults.
Fetch errors still emit JSON and exit 1; successful fetches exit 0. HTTP status
codes are reported without changing this behavior.

Pass `--max-text N` to cap the `content`, `raw_content`, and `extracted_text`
fields at N characters each; `truncation.fields` reports the original and
returned character counts per field. `--max-text 0` (default) keeps full text.

Combine `--json --output page.html` to save successful HTML while keeping JSON
on stdout. `output_written` indicates whether HTML was saved. On fetch errors,
the output file is left untouched. Without `--json`, existing text output is
unchanged.

## Command List

### `python scripts/codex_seo.py setup`

Explicitly create or refresh the isolated Python runtime and Playwright Chromium.
Run setup explicitly after project installation when the required runtime is
not ready. The project installer and its wrappers copy resources and discovery
files; they do not run setup or connect providers. Setup never installs packages
globally. Use setup --skip-browser when only core analysis is needed.

### `python scripts/codex_seo.py doctor --json`

Check runtime, dependency, and Chromium readiness without changing the system.
Diagnostic output omits absolute paths and environment values.

### `$seo-audit <url>`

Full website SEO audit with specialist analysis.

**Example:**
```
$seo-audit https://example.com
```

**What it does:**
1. Crawls up to 500 pages
2. Detects business type
3. Runs the relevant specialist passes in host-limited batches, or sequentially when delegation is unavailable
4. Applies the evidence-scoped SEO Health Score rubric (0-100), leaving unmeasured categories unknown
5. Creates prioritized action plan

**Output:**
- `FULL-AUDIT-REPORT.md`
- `ACTION-PLAN.md`
- `audit-data.json` and `findings/*.md`
- `screenshots/` (if Playwright available)

Outputs live under the selected `{domain}-audit/` directory.

---

### `$seo-page <url>`

Deep single-page analysis.

**Example:**
```
$seo-page https://example.com/about
```

**What it analyzes:**
- On-page SEO (title, meta, headings, URLs)
- Content quality (word count, readability, E-E-A-T)
- Technical elements (canonical, robots, Open Graph)
- Schema markup
- Images (alt text, sizes, formats)
- Core Web Vitals potential issues

---

### `$seo-technical <url>`

Technical SEO audit across 9 categories.

**Example:**
```
$seo-technical https://example.com
```

**Categories:**
1. Crawlability
2. Indexability
3. Security
4. URL Structure
5. Mobile Optimization
6. Core Web Vitals (LCP, INP, CLS)
7. Structured Data
8. JavaScript Rendering
9. IndexNow Protocol

---

### `$seo-content <url>`

E-E-A-T and content quality analysis.

**Example:**
```
$seo-content https://example.com/blog/post
```

**What it evaluates:**
- Experience signals (first-hand knowledge)
- Expertise (author credentials)
- Authoritativeness (external recognition)
- Trustworthiness (transparency, security)
- AI citation readiness
- Content freshness

---

### `$seo-content-brief <topic or url>`

Generate a detailed SEO content brief: target keywords, search intent, heading outline, internal link targets, and competitor angle.

**Example:**
```
$seo-content-brief "best running shoes for flat feet"
```

**What it produces:**
- Primary and secondary target keywords
- Search intent and audience
- Section-by-section heading outline
- Internal link recommendations
- Competitor content angles to beat

---

### `$seo-schema <url>`

Schema markup detection, validation, and generation.

**Example:**
```
$seo-schema https://example.com
```

**What it does:**
- Detects existing schema (JSON-LD, Microdata, RDFa)
- Validates against Google's requirements
- Identifies missing opportunities
- Generates ready-to-use JSON-LD

---

### `$seo-geo <url>`

AI Overviews / Generative Engine Optimization.

**Example:**
```
$seo-geo https://example.com/blog/guide
```

**What it analyzes:**
- Citability score (quotable facts, statistics)
- Structural readability (headings, lists, tables)
- Entity clarity (definitions, context)
- Authority signals (credentials, sources)
- Structured data support

---

### `$seo-agentic [audit|fix|lighthouse|refresh] <url>`

Agent readiness: how well AI agents that browse and act for people can read and use the site.

**Examples:**
```
$seo-agentic https://example.com
$seo-agentic lighthouse https://example.com
$seo-agentic fix https://example.com
```

**What it analyzes:**
- Lighthouse Agentic Browsing result as Lighthouse computes it (X of N, N/A and informative audits excluded)
- Accessibility tree for agents (the 33 axe rules Lighthouse uses, plus the local Agent-UX heuristic)
- robots.txt groups per AI purpose (training, search, user-triggered) and Content-Signal
- llms.txt, Markdown delivery (`Accept: text/markdown`, `.md` alternates), ai-catalog.json, `/.well-known` files
- WebMCP tools and form annotations, labelled as a W3C Community Group draft

`fix` drafts robots.txt Content-Signal lines, llms.txt, ai-catalog.json and WebMCP scaffolds for review; nothing is deployed.

---

### `$seo-images <url>`

Image optimization analysis. Subcommands: `serp <keyword>` (image SERP / visual-search analysis), `optimize <path>` (local file optimization + IPTC AI labeling).

**Examples:**
```
$seo-images https://example.com
$seo-images serp "running shoes"
$seo-images optimize ./hero.webp
```

**What it checks:**
- Alt text presence and quality
- File sizes (flag >200KB)
- Formats (WebP/AVIF recommendations)
- Responsive images (srcset, sizes)
- Lazy loading
- CLS prevention (dimensions)

---

### `$seo-sitemap <url>`

Analyze existing XML sitemap.

**Example:**
```
$seo-sitemap https://example.com/sitemap.xml
```

**What it validates:**
- XML format
- URL count (<50k per file)
- URL status codes
- lastmod accuracy
- Deprecated tags (priority, changefreq)
- Coverage vs crawled pages

---

### `$seo-sitemap generate`

Generate new sitemap with industry templates.

**Example:**
```
$seo-sitemap generate
```

**Process:**
1. Select or auto-detect business type
2. Interactive structure planning
3. Apply quality gates (30/50 location page limits)
4. Generate valid XML
5. Create documentation

---

### `$seo-plan <type>`

Strategic SEO planning.

**Types:** `saas`, `local`, `ecommerce`, `publisher`, `agency`

**Example:**
```
$seo-plan saas
```

**What it creates:**
- Complete SEO strategy
- Competitive analysis
- Content calendar
- Implementation roadmap (4 phases)
- Site architecture design

---

### `$seo-competitor-pages [url|generate]`

Competitor comparison page generation.

**Examples:**
```
$seo-competitor-pages https://example.com/vs/competitor
$seo-competitor-pages generate
```

**Capabilities:**
- Generate "X vs Y" comparison page layouts
- Create "Alternatives to X" page structures
- Build feature comparison matrices with scoring
- Generate Product + AggregateRating schema markup
- Apply conversion-optimized CTA placement
- Enforce fairness guidelines (accurate data, source citations)

---

### `$seo-hreflang [url]`

Hreflang and international SEO audit and generation. Subcommand: `audit <directory-or-url>` (audit hreflang across a local build directory or a live URL set).

**Examples:**
```
$seo-hreflang https://example.com
$seo-hreflang audit ./dist
```

**Capabilities:**
- Validate self-referencing hreflang tags
- Check return tag reciprocity (A -> B requires B -> A)
- Verify x-default tag presence
- Validate ISO 639-1 language and ISO 3166-1 region codes
- Check canonical URL alignment with hreflang
- Detect protocol mismatches (HTTP vs HTTPS)
- Generate correct hreflang link tags and sitemap XML

---

### `$seo-programmatic [url|plan]`

Programmatic SEO analysis and planning for pages generated at scale.

**Examples:**
```
$seo-programmatic https://example.com/tools/
$seo-programmatic plan
```

**Capabilities:**
- Assess data source quality (CSV, JSON, API, database)
- Plan template engines with unique content per page
- Design URL pattern strategies (`/tools/[tool-name]`, `/[city]/[service]`)
- Automate internal linking (hub/spoke, related items, breadcrumbs)
- Enforce thin content safeguards (quality gates, word count thresholds)
- Prevent index bloat (noindex low-value, pagination, faceted nav)

---

### `$seo-local <url>`

Local SEO analysis covering Google Business Profile, citations, reviews, and the map pack.

**Example:**
```
$seo-local https://example.com
```

**What it analyzes:**
- Google Business Profile signals (categories, hours, photos, posts)
- NAP (Name, Address, Phone) consistency across the page and external citations
- Review velocity, response rate, and sentiment
- Local schema markup (LocalBusiness, Restaurant, Service-specific types)
- Industry-specific local factors (brick-and-mortar, SAB, hybrid)
- Map pack visibility signals

---

### `$seo-maps [command] [args]`

Maps intelligence: geo-grid rank tracking, GBP profile audits, review intelligence, cross-platform NAP verification, competitor radius mapping.

**Examples:**
```
$seo-maps "Joe's Coffee" "austin tx"
$seo-maps grid "coffee shop" "austin tx"
$seo-maps gbp "Joe's Coffee" "austin tx"
$seo-maps reviews "Joe's Coffee" "austin tx"
$seo-maps competitors "auto repair" "denver"
$seo-maps nap "Joe's Coffee" "austin tx"
$seo-maps schema "Joe's Coffee" "austin tx"
```

**Capabilities:**
- Rank tracking on a geographic grid (typically 49 points)
- GBP profile audit with completeness scoring
- Review aggregation across Google, Yelp, Facebook, Bing
- Competitor discovery within a configurable radius

---

### `$seo-backlinks <url>`

Backlink profile analysis with a 3-tier data cascade: public Common Crawl data plus verification, credentialed Moz/Bing Webmaster sources, and DataForSEO. Current provider access, allowance and pricing depend on the selected account.

**Examples:**
```
$seo-backlinks https://example.com
$seo-backlinks gap https://example.com https://competitor.com
$seo-backlinks toxic https://example.com
$seo-backlinks new https://example.com
$seo-backlinks verify https://example.com --links known-links.txt
$seo-backlinks setup
```

**What it analyzes:**
- Domain Authority and Page Authority (Moz)
- Referring domain count and growth
- Anchor text distribution (branded, exact, partial, naked URL)
- Toxic / spammy backlink detection
- Lost backlinks
- Competitor link gap

---

### `$seo-cluster [command] <seed-keyword>`

SERP-based semantic topic clustering for content architecture planning. Built on the Pro Hub Challenge Semantic Cluster Engine. Subcommands: `plan <seed>` (full planning workflow; also `plan --from strategy` to import a `$seo-plan` output), `execute` (create content with an available, separately authorized writing workflow or output briefs), `map` (regenerate the interactive visualization). Bare `$seo-cluster <seed>` is shorthand for `plan`.

**Examples:**
```
$seo-cluster plan "codex seo skills"
$seo-cluster plan --from strategy
$seo-cluster execute
$seo-cluster map
```

**What it produces:**
- Keyword expansion from the seed (50-200 candidates)
- Pairwise SERP overlap comparison to detect semantic clusters
- Intent classification per cluster (informational, commercial, transactional, navigational)
- Hub-and-spoke content architecture proposal
- Internal link matrix between cluster pages
- Interactive `cluster-map.html` visualization

---

### `$seo-sxo <url>`

Search Experience Optimization: SERP backwards analysis, page-type mismatch detection, persona scoring. Subcommands: `<url> <keyword>` (analyze for a specific keyword), `wireframe <url>` (IST/SOLL wireframe), `personas <url>` (persona-only scoring, skips SERP).

**Examples:**
```
$seo-sxo https://example.com/blog/how-to-x
$seo-sxo https://example.com/page "target keyword"
$seo-sxo wireframe https://example.com/page
$seo-sxo personas https://example.com/page
```

**What it produces:**
- Page-type taxonomy classification (article, landing, product, tool, listing)
- SERP intent vs page-type alignment check
- User stories derived from SERP signals
- Multi-persona scoring (researcher, buyer, expert, casual visitor)
- Wireframe-level recommendations for fixing mismatches

---

### `$seo-drift baseline|compare|history <url>`

SEO drift monitoring. Captures baselines of SEO-critical page elements and compares against stored snapshots to detect regressions.

**Examples:**
```
$seo-drift baseline https://example.com
$seo-drift compare https://example.com
$seo-drift history https://example.com
```

**What it tracks:** title, meta description, canonical, hreflang, Open Graph, schema, headings, internal links, robots, sitemap entry, indexability, Core Web Vitals, response status, redirect chain.

**17 comparison rules** classify changes by severity (CRITICAL, HIGH, MEDIUM). SQLite-backed baselines. These are on-demand operations; no recurring monitor is installed or scheduled.

---

### `$seo-ecommerce <url>`

E-commerce SEO covering product schema, marketplace intelligence, and pricing gap analysis. Subcommands: `products <keyword>` (Google Shopping competitive analysis), `gaps <domain>` (organic-vs-Shopping visibility gap), `schema <url>` (product schema validation + enhancement).

**Examples:**
```
$seo-ecommerce https://shop.example.com/product/x
$seo-ecommerce products "running shoes"
$seo-ecommerce gaps shop.example.com
$seo-ecommerce schema https://shop.example.com/product/x
```

**What it analyzes:**
- Product schema (Product, Offer, AggregateRating, Review)
- Google Shopping visibility
- Amazon marketplace presence
- Pricing gap vs competitors
- Out-of-stock and availability signals
- Faceted navigation crawl traps

---

### `$seo-flow [stage] [url|topic]`

FLOW framework integration: evidence-led prompts for the Find, Leverage, Optimize, Win, and Local stages of a content campaign.

**Examples:**
```
$seo-flow find "topic"
$seo-flow leverage https://example.com
$seo-flow optimize https://example.com/page
$seo-flow win https://example.com/page
$seo-flow local https://example.com
$seo-flow prompts
$seo-flow sync
```

**41 prompts** sourced from FLOW (CC BY 4.0). Each prompt is grounded in a specific evidence source (SERP data, GSC, GA4, customer interviews) with attribution preserved.

---

### `$seo-google [command] [url]`

Google SEO APIs. 4-tier credential system covering PageSpeed Insights, CrUX, CrUX History, Search Console, URL Inspection, Indexing API, GA4, and Keyword Planner.

**Setup & reporting:**
```
$seo-google setup                      # Configure/check credentials
$seo-google quotas                     # Show per-API quota usage
$seo-google report full                # Generate full PDF/HTML report
$seo-google report cwv-audit           # CWV-focused report
$seo-google report gsc-performance     # Search performance report
$seo-google report indexation          # Indexation status report
```

**PageSpeed / CrUX (Tier 0):**
```
$seo-google pagespeed <url>            # PageSpeed Insights (lab) + CWV
$seo-google crux <url>                 # CrUX field data
$seo-google crux-history <url>         # 25-week CrUX history
```

**Search Console / Indexing (Tier 1):**
```
$seo-google gsc <property>             # Search Analytics (clicks/impressions/CTR/position)
$seo-google inspect <url>              # URL Inspection (indexation status)
$seo-google inspect-batch <file>       # Batch URL inspection
$seo-google sitemaps <property>        # List submitted sitemaps + status
$seo-google index <url>                # Indexing API notify
$seo-google index-batch <file>         # Batch indexing notify
```
Use Indexing API commands only for pages with JobPosting or BroadcastEvent embedded in VideoObject. Route ordinary URLs to URL Inspection or sitemaps; `URL_UPDATED` does not guarantee indexing.

**GA4 (Tier 2):**
```
$seo-google ga4 [property-id]          # Organic traffic report
$seo-google ga4-pages [property-id]    # Top organic landing pages
```

**NLP / Keywords / YouTube:**
```
$seo-google nlp <url-or-text>          # NLP content analysis
$seo-google entities <url-or-text>     # Entity extraction
$seo-google entity <query>             # Entity lookup
$seo-google keywords <seed>            # Keyword Planner ideas (Tier 3)
$seo-google volume <keywords>          # Keyword search volume (Tier 3)
$seo-google youtube <query>            # YouTube search
$seo-google youtube-video <video_id>   # YouTube video analysis
$seo-google safety <url>               # Safe Browsing check
```

**Tiers:**
- Tier 0 (API key only): PSI, CrUX, CrUX History
- Tier 1 (+ OAuth or Service Account): GSC, URL Inspection, Indexing API
- Tier 2 (+ GA4 property config): GA4 organic traffic
- Tier 3 (+ Google Ads developer token): Keyword Planner

PDF and HTML reports use the bundled reporting implementation and matplotlib. PDF uses WeasyPrint when its native libraries are available, or the managed Chromium fallback; HTML and Excel paths are also retained. Unavailable metrics remain unknown.

---

### `$seo-image-gen [use-case] <description>`

AI image generation for SEO assets. The optional Banana route uses Gemini via nanobanana-mcp or bundled direct helpers. An available host-native image tool can be used when selected for the task.

**Prerequisites for Banana:** Discoverable image workflow, authorized Google AI key, chosen model and applicable budget. MCP additionally needs Node.js/npx and the configured nanobanana-mcp server.

**Use Cases:**
```
$seo-image-gen og <description>          # OG/social preview image (16:9, 1K)
$seo-image-gen hero <description>        # Blog hero image (16:9, 2K)
$seo-image-gen product <description>     # Product photography (4:3, 2K)
$seo-image-gen infographic <description> # Infographic visual (2:3, 4K)
$seo-image-gen custom <description>      # Custom with full Creative Director pipeline
$seo-image-gen batch <description> [N]   # Generate N variations (default: 3)
```

**What it does:**
1. Maps SEO use case to optimized domain mode, aspect ratio, and resolution
2. Constructs 6-component Reasoning Brief (Creative Director pipeline)
3. Generates image via Gemini API
4. Provides SEO checklist (alt text, file naming, WebP, schema markup)

---

### `$seo-firecrawl [command] <url>`

Full-site crawling and URL discovery via Firecrawl MCP (extension).

**Prerequisites:** Discoverable Firecrawl workflow, authorized Firecrawl account/key, applicable crawl allowance, and a configured Firecrawl MCP tool.

**Examples:**
```
$seo-firecrawl crawl https://example.com
$seo-firecrawl map https://example.com
$seo-firecrawl scrape https://example.com/page
$seo-firecrawl search "query" https://example.com
```

**What it does:**
- `crawl` walks the site discovering URLs and capturing content
- `map` returns the full URL inventory for a domain
- `scrape` extracts a single page in a model-friendly format
- `search` searches within a crawled site for a query

---

### `$seo-dataforseo [command]`

Live SEO data via DataForSEO MCP server (extension). 23 data commands across 9 API modules, plus cost-tracking commands.

**Prerequisites:** Discoverable DataForSEO workflow, authorized funded account, configured DataForSEO MCP tools, and a confirmed request scope/budget.

**SERP Analysis:**
```
$seo-dataforseo serp <keyword>              # Google organic results (also Bing/Yahoo)
$seo-dataforseo serp-images <keyword>       # Image elements in the organic SERP (no Images tool on the pinned server)
$seo-dataforseo serp-youtube <keyword>      # YouTube search results
$seo-dataforseo youtube <video_id>          # YouTube video deep analysis
```

**Keyword Research:**
```
$seo-dataforseo keywords <seed>             # Keyword ideas and suggestions
$seo-dataforseo volume <keywords>           # Search volume metrics
$seo-dataforseo difficulty <keywords>       # Keyword difficulty scores
$seo-dataforseo intent <keywords>           # Search intent classification
$seo-dataforseo trends <keyword>            # Google Trends data
```

**Domain & Competitors:**
```
$seo-dataforseo backlinks <domain>          # Full backlink profile
$seo-dataforseo competitors <domain>        # Competitor analysis
$seo-dataforseo ranked <domain>             # Ranked keywords
$seo-dataforseo intersection <domains>      # Keyword/backlink overlap
$seo-dataforseo traffic <domains>           # Traffic estimation
$seo-dataforseo subdomains <domain>         # Subdomains with ranking data
$seo-dataforseo top-searches <domain>       # Top queries mentioning domain
```

**Technical / On-Page:**
```
$seo-dataforseo onpage <url>                # On-page analysis (Lighthouse)
$seo-dataforseo tech <domain>               # Technology detection
$seo-dataforseo whois <domain>              # WHOIS data
```

**Content & Business Data:**
```
$seo-dataforseo content <keyword/url>       # Content analysis and trends
$seo-dataforseo listings <keyword>          # Business listings search
```

**AI Visibility / GEO:**
```
$seo-dataforseo ai-scrape <query>           # ChatGPT web scraper for GEO
$seo-dataforseo ai-mentions <keyword>       # LLM mention tracking
```

**Cost Tracking:**
```
$seo-dataforseo costs today                            # Today's DataForSEO spend
$seo-dataforseo costs summary                          # Spend summary across periods
$seo-dataforseo costs config --mode threshold --threshold 0.50   # Set cost-control mode/threshold
```

---

### `$seo-ahrefs [command] <url|topic>`

Ahrefs API metrics (extension). **Prerequisites:** Discoverable Ahrefs workflow, authorized Ahrefs API access, Node.js/npx and the configured official Ahrefs MCP server.
```
$seo-ahrefs metrics <url>       # DR/UR, referring-domain count, organic traffic estimate
$seo-ahrefs backlinks <url>     # Top referring domains, anchor distribution, follow/nofollow ratio
$seo-ahrefs organic <url>       # Organic keywords, ranking distribution, traffic by country
$seo-ahrefs content <topic>     # Content Explorer top results, social shares, referring domains
```

---

### `$seo-bing [command]`

Bing Webmaster Tools + IndexNow (extension). **Prerequisites:** Authorized Bing Webmaster property/API key. IndexNow submissions additionally require the published verification key and explicit submission authorization.
```
$seo-bing links <url>                 # Inbound links from Bing Webmaster
$seo-bing compare <urlA> <urlB>       # Compare two URLs' Bing link profiles
$seo-bing submit <url> --host <host>                # IndexNow single-URL submit (requires key)
$seo-bing submit-batch <file> --host <host>         # IndexNow batch submit (requires key)
$seo-bing verify-indexnow --host <host>             # Verify the IndexNow key is published
```

---

### `$seo-matomo [command] [site-id]`

Matomo Reporting API (extension). **Prerequisites:** An authorized instance URL,
API token and site ID. Set MATOMO_URL, MATOMO_API_TOKEN and optionally
MATOMO_SITE_ID in the process environment, or configure the supported Matomo
credential file under the Codex configuration directory. The default is
~/.config/codex-seo/matomo.json; CODEX_SEO_CONFIG_DIR or CODEX_SEO_DATA_DIR
can change it. The extension installer only manages discovery/package files
and does not write tokens. For setup guidance run:

    python scripts/codex_seo.py run matomo_auth.py --setup

A self-hosted private instance must be explicitly named in
CODEX_SEO_LOCAL_TARGETS. See [security](../SECURITY.md) for the narrow scope
of that allowlist. Environment values override the credential file.

Use as a GA4 alternative or supplement when you want full data ownership, no Google dependency, or privacy-first analytics.
```
$seo-matomo check                  # Probe credentials and confirm Matomo version
$seo-matomo organic [site-id]      # Organic traffic trend (28d) + top landing pages
$seo-matomo top-pages              # Top organic landing pages only
$seo-matomo device                 # Visits by device type
$seo-matomo country                # Visits by country
$seo-matomo referrers              # Channel + search-engine breakdown
$seo-matomo keywords               # Organic search keywords (often "(not provided)")
```

All commands accept `--days` (default 28), `--limit` (default 50),
`--site-id`, and `--json`. The audit workflow includes a Matomo specialist pass when credential checks succeed and the requested scope calls for it. The specialist prompt lives in the Matomo extension; it is not an automatically registered Codex agent.

---

### `$seo-profound [command] <brand>`

LLM brand-citation tracking via Profound (extension). **Prerequisites:** An independently authorized provider tool or supplied export and a plan with the requested metrics. The preserved source includes the workflow, not a standalone Profound client or MCP endpoint.
```
$seo-profound citations <brand>     # Citation rate per LLM + 30-day trend
$seo-profound prompts <brand>       # Top prompts that surface (or miss) the brand
$seo-profound competitors <brand>   # Brands cited alongside yours for the same prompts
$seo-profound alerts <brand>        # Spike/drop alerts vs 7-day baseline
```

---

### `$seo-seranking [command] <brand|keyword|url>`

AI-visibility + SERP via SE Ranking (extension). **Prerequisites:** An independently authorized provider tool or supplied export and a plan with the requested metrics. The preserved source includes the workflow, not a standalone SE Ranking client or MCP endpoint.
```
$seo-seranking ai-visibility <brand>   # Share-of-voice across ChatGPT/Gemini/Perplexity/AI Overviews/AI Mode
$seo-seranking serp <keyword>          # Top 100 organic positions + SERP features
$seo-seranking backlinks <url>         # Backlink profile, subject to current account access
$seo-seranking competitors <url>       # Top 10 organic competitors + shared-keyword gaps
```

---

### `$seo-unlighthouse <url>`

Multi-page Lighthouse audit via the local Unlighthouse runner (extension, MIT, no provider API quota). **Prerequisites:** Compatible Node.js/npx and a supported browser. The bundled wrapper invokes the pinned unlighthouse package through npx, which can download it on first use.
```
$seo-unlighthouse https://example.com
$seo-unlighthouse https://example.com --device desktop
$seo-unlighthouse https://example.com --max-routes 50 --output-dir ./reports
```

---

## Quick Reference

| Command | Use Case |
|---------|----------|
| `$seo-audit <url>` | Full website audit with host-limited specialist passes |
| `$seo-page <url>` | Single page analysis |
| `$seo-technical <url>` | Technical SEO across 9 categories |
| `$seo-content <url>` | E-E-A-T and content quality |
| `$seo-content-brief <topic>` | Detailed content brief: keywords, outline, internal links |
| `$seo-schema <url>` | Schema markup detection, validation, generation |
| `$seo-sitemap <url>` | Sitemap validation |
| `$seo-sitemap generate` | Create new sitemap with industry templates |
| `$seo-images <url>` | Image optimization |
| `$seo-geo <url>` | AI search optimization (GEO) |
| `$seo-agentic <url>` | Agent readiness (Lighthouse Agentic Browsing, AI agent access, WebMCP) |
| `$seo-local <url>` | Local SEO (GBP, citations, reviews) |
| `$seo-maps [command]` | Maps intelligence (geo-grid, GBP audit, competitors) |
| `$seo-backlinks <url>` | Backlink profile analysis |
| `$seo-cluster <seed>` | SERP-based semantic clustering |
| `$seo-sxo <url>` | Search Experience Optimization |
| `$seo-drift baseline\|compare\|history <url>` | SEO drift monitoring |
| `$seo-ecommerce <url>` | E-commerce SEO |
| `$seo-hreflang [url]` | Hreflang and international SEO |
| `$seo-plan <type>` | Strategic planning by industry |
| `$seo-programmatic [url\|plan]` | Programmatic SEO analysis |
| `$seo-competitor-pages [url\|generate]` | Competitor comparison pages |
| `$seo-flow [stage] [url\|topic]` | FLOW framework prompts |
| `$seo-google [command] [url]` | Google SEO APIs (GSC, PSI, CrUX, GA4) |
| `$seo-dataforseo [command]` | Live SEO data (extension) |
| `$seo-image-gen [use-case] <desc>` | AI image generation (extension) |
| `$seo-firecrawl [command] <url>` | Full-site crawling (extension) |
| `$seo-ahrefs [command] <url>` | Backlinks, organic keywords, and content data via the official Ahrefs MCP (extension) |
| `$seo-seranking [command]` | AI Share-of-Voice across ChatGPT, Gemini, Perplexity, AI Overviews, AI Mode (extension) |
| `$seo-profound [command]` | LLM citation tracking with time-series data (extension) |
| `$seo-bing [command] <url>` | Bing Webmaster Tools + IndexNow URL submission (extension) |
| `$seo-matomo [command] [args]` | Matomo Reporting API: GA4 alternative or complement (extension) |
| `$seo-unlighthouse <url>` | Multi-page Lighthouse runner, runs locally (extension) |


## Provider activation and executable helpers

All 33 unique skill workflows are discoverable after a complete project install.
The nine extension directories remain optional provider routes: availability
does not mean that a paid service is connected. To select one extension or
inspect its connection requirements, run from the package root:

    python install-codex.py --extension firecrawl --project /path/to/project --dry-run
    python install-codex.py --extension firecrawl --project /path/to/project --apply
    python extensions/codex-extension.py plan firecrawl
    python extensions/codex-extension.py toml firecrawl

The plan reports readiness without writing settings. The TOML command prints a
secret-free Codex MCP fragment only for providers with a defined MCP route.
Review it in the intended host configuration; installing discovery files does
not merge settings or authorize API calls. Replace firecrawl with a provider
name from extensions/codex-integrations.json. Node.js/npx is needed for the
listed stdio MCP packages.

For exact Python helper arguments, use the helper's --help through the managed
runtime. A workflow prompt and a Python CLI do not share an argument parser:

    python scripts/codex_seo.py run fetch_page.py --help
    python scripts/codex_seo.py run render_page.py https://example.com --mode auto --json
    python scripts/codex_seo.py run google_auth.py --check
    python scripts/codex_seo.py run google_report.py --help
    python scripts/codex_seo.py run unlighthouse_run.py --help

The runtime only dispatches allowlisted core scripts or contained extension
scripts. Use doctor --json to check core and browser readiness separately.
See [the verification record](CODEX_VERIFICATION.md) for what has been tested;
provider-account availability and model judgments are separate from source
coverage.
