# SE Ranking extension setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension seranking --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan seranking
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

This source extension supplies workflow guidance rather than a bundled provider API client. Use an independently authorized provider tool or a supplied export. A token by itself does not create a callable tool, and tool endpoints must not be invented.

SE Ranking's API exposes traditional SEO data (SERP, backlinks,
competitors) plus AI Share-of-Voice across 5 AI platforms.

## Get an API key

https://seranking.com/api.html: pricing is unit-based; the AI visibility
endpoint costs ~5 units per query (1 per platform).

## Verify

```
/seo seranking ai-visibility "Claude SEO"
```

Expected output: percentages per platform (ChatGPT, Gemini, Perplexity,
AI Overviews, AI Mode) with sample-size confidence notes.
