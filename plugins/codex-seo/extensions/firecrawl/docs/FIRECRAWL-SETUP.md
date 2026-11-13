# Firecrawl Setup Guide

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension firecrawl --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan firecrawl
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

For a Codex MCP connection fragment, run:

```text
python "<resolved-plugin-root>/extensions/codex-extension.py" toml firecrawl
```

Review the fragment and merge it through the host's MCP configuration flow. It names credential environment variables without embedding their values. Check the connection's actual available tools before running this workflow.

## 1. Get Your API Key

1. Go to [firecrawl.dev/app/sign-up](https://www.firecrawl.dev/signup)
2. Create a free account (500 credits/month included)
3. Navigate to **API Keys** in the dashboard
4. Copy your API key (starts with `fc-`)

## 4. Verify Installation

Start Codex and try:

```
/seo firecrawl map https://example.com
```

You should see a list of discovered URLs. If you get a "tool not available" error, restart Codex to reload MCP servers.

## 5. Understanding Credits

| Operation | Credits Used |
|-----------|-------------|
| `crawl` | 1 per page crawled |
| `scrape` | 1 per page |
| `map` | 0.5 per URL discovered |
| `search` | 1 per result returned |

**Free tier**: 500 credits/month resets on your billing date.

**Tip**: Use `map` first (cheap) to see how many pages a site has, then decide how many to `crawl` (more expensive).
