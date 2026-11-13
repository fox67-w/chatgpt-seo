# Getting started with ChatGPT SEO

The full edition runs in Codex with local execution tools. Use the
[regular ChatGPT setup](../LOCAL_SETUP.md) if you only want the SEO-pro companion
instructions for a ChatGPT Project.

## 1. Get the repository

Install Git and Python 3.11-3.14, then run:

```sh
git clone https://github.com/fox67-w/chatgpt-seo.git
cd chatgpt-seo
```

You can also extract the repository ZIP and open a terminal in its root directory.
The commands below start from that directory. Replace the example project path
with the existing project you want to open in Codex.

## 2. Install into your project

The installer previews changes by default. The explicit apply command copies the
complete package into `<project>/.agents/packages/codex-seo` and adds skill
discovery bridges under `<project>/.agents/skills`. It preserves conflicting
existing files and reports them. All 33 unique workflows are selected by default.

### Windows PowerShell

```powershell
$seoProject = "C:\Projects\my-site"
.\plugins\codex-seo\install.ps1 -Project $seoProject -DryRun
.\plugins\codex-seo\install.ps1 -Project $seoProject -Apply

$env:CODEX_SEO_DATA_DIR = Join-Path $seoProject ".runtime\codex-seo"
$seoRunner = Join-Path $seoProject ".agents\packages\codex-seo\scripts\codex-seo.ps1"
& $seoRunner setup
& $seoRunner doctor --json
```

The PowerShell launchers select a supported Python interpreter. If your shell
does not allow PowerShell scripts, use an installed supported Python directly.
For example, if Python 3.12 is installed:

```powershell
py -3.12 .\plugins\codex-seo\install-codex.py --project $seoProject --dry-run
py -3.12 .\plugins\codex-seo\install-codex.py --project $seoProject --apply
$env:CODEX_SEO_DATA_DIR = Join-Path $seoProject ".runtime\codex-seo"
$seoRuntime = Join-Path $seoProject ".agents\packages\codex-seo\scripts\codex_seo.py"
py -3.12 $seoRuntime setup
py -3.12 $seoRuntime doctor --json
```

### macOS or Linux

```sh
seo_project="/absolute/path/to/my-site"
bash plugins/codex-seo/install.sh --project "$seo_project" --dry-run
bash plugins/codex-seo/install.sh --project "$seo_project" --apply

export CODEX_SEO_DATA_DIR="$seo_project/.runtime/codex-seo"
seo_runner="$seo_project/.agents/packages/codex-seo/scripts/codex-seo"
bash "$seo_runner" setup
bash "$seo_runner" doctor --json
```

Setup downloads dependencies into an isolated environment and installs Chromium.
It requires network access and disk space. `setup --skip-browser` omits Chromium
for an HTTP-only setup; rendering and screenshots then remain unavailable.
The selected data directory holds the managed runtime and its state. Set the same
`CODEX_SEO_DATA_DIR` before later runtime commands so they reuse it. This variable
is scoped to the terminal session shown above; no global Codex or Claude settings
are required.

If doctor reports a missing dependency, resolve it before running the affected
workflow. The [full guide](../plugins/codex-seo/docs/CODEX.md) covers runtime
locations, interpreter selection, PDF support and troubleshooting.

## 3. Check fetching and rendering

Keep the variables from your platform's setup commands. On Windows PowerShell:

```powershell
& $seoRunner run fetch_page.py https://example.com
& $seoRunner run render_page.py https://example.com --mode auto --json
```

If you used the direct Python alternative instead:

```powershell
py -3.12 $seoRuntime run fetch_page.py https://example.com
py -3.12 $seoRuntime run render_page.py https://example.com --mode auto --json
```

On macOS or Linux:

```sh
bash "$seo_runner" run fetch_page.py https://example.com
bash "$seo_runner" run render_page.py https://example.com --mode auto --json
```

Use the managed launcher for analysis scripts; it selects the isolated environment
created during setup. A successful check verifies those local operations, not any
private Google account or paid provider connection.

## 4. Run your first audit in Codex

Open the target project in Codex and start a chat. If skills do not appear,
reopen the project or restart Codex after installation. Try:

```text
$seo-audit Audit https://example.com. Use the installed codex-seo runtime,
save a report in this project, and identify missing evidence and required accounts.
```

Tell Codex the absolute runtime data directory selected above, so it can set
`CODEX_SEO_DATA_DIR` for its tool commands. You can also invoke `$seo` for routing
or another installed skill for a narrower task. `/seo ...` wording is a textual
alias, rather than a registered native slash command.

The workflow uses available Codex tools and native collaboration. The host's
permissions, tool availability and concurrency settings still apply. Automatic
schema hooks are disabled by default; enabling them is an optional setup step in
the [full guide](../plugins/codex-seo/docs/CODEX.md).

## 5. Connect only the data sources you need

Public-page fetching and local analysis work without a paid SEO-data provider.
Account-dependent workflows need additional setup:

| Data or feature | Requirement |
| --- | --- |
| Search Console, GA4 and Google Ads | Authorized Google access, enabled APIs and the permissions required by the specific workflow. |
| Ahrefs, DataForSEO, Firecrawl, Banana, Bing Webmaster and Matomo | The relevant service/tool, credentials and available quota. Paid operations need an authorized budget. |
| Profound and SE Ranking | Available provider tools or exported data; no standalone API client is bundled. |
| Unlighthouse | Its local CLI/runtime prerequisites. |

All nine extension directories and their workflows are included. Source inclusion
does not mean a service is connected or a live account has been verified. Use the
extension planning and configuration commands in the
[full guide](../plugins/codex-seo/docs/CODEX.md) before adding a provider.
Store credentials outside source control and exclude runtime state and reports
containing private account data from published archives.

## More information

- [Feature overview](../README.md) and [complete Codex guide](../plugins/codex-seo/docs/CODEX.md).
- [Verification results and limits](CODEX_VERIFICATION.md).
- [Exact source revision](../plugins/codex-seo/CODEX_PROVENANCE.json) and [imported source inventory](claude-source-inventory.json).
- [MIT license](../LICENSE), [project notices](../NOTICE.md) and [FLOW/asset notices](../plugins/codex-seo/NOTICE.md).

To remove installed discovery bridges, use the package's uninstall launcher or
`install-codex.py --project TARGET --remove --apply`. Only tracked, unchanged
bridges are removed; the copied package and runtime data are retained. See the
full guide before removing those separately.
