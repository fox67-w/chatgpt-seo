# DataForSEO Account Setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension dataforseo --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan dataforseo
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

For a Codex MCP connection fragment, run:

```text
python "<resolved-plugin-root>/extensions/codex-extension.py" toml dataforseo
```

Review the fragment and merge it through the host's MCP configuration flow. It names credential environment variables without embedding their values. Check the connection's actual available tools before running this workflow.

Step-by-step guide to getting DataForSEO API credentials for the Claude SEO extension.

## 1. Create Account

1. Go to [app.dataforseo.com/register](https://app.dataforseo.com/register)
2. Sign up with your email address
3. Verify your email

New accounts include a free trial balance for testing.

## 2. Find API Credentials

1. Log in to [app.dataforseo.com](https://app.dataforseo.com)
2. Go to **API Access** in the left sidebar
3. Your credentials are:
   - **Username**: Your registered email address
   - **Password**: Your API password (set during registration)

Provide these through the credential environment variables listed by the Codex integration plan.

## 3. Understanding Credits

DataForSEO uses a credit-based system:

- Each API call costs a small number of credits
- Different endpoints have different costs
- Credits are purchased in advance
- Monitor usage at [app.dataforseo.com/dashboard](https://app.dataforseo.com/dashboard)

**Typical costs per call, verified as of 2026-07-10:**

| Endpoint Type | Approximate Cost |
|--------------|-----------------|
| SERP (single query) | $0.001-0.003 |
| Keyword volume (per keyword) | $0.0005-0.002 |
| Backlink summary | $0.002-0.005 |
| Backlink list | $0.005-0.01 |
| On-page crawl (per page) | $0.01-0.05 |
| AI optimization (per call) | $0.05 |

## 5. Verify Installation

After installing, start Codex and run:

```
/seo dataforseo serp test query
```

If you see search results, the extension is working correctly.
