# Profound extension setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension profound --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan profound
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

This source extension supplies workflow guidance rather than a bundled provider API client. Use an independently authorized provider tool or a supplied export. A token by itself does not create a callable tool, and tool endpoints must not be invented.

Profound (https://tryprofound.com) tracks brand mentions across LLMs as
a time-series: the complement to SE Ranking's on-demand sampling.

## Verify

```
/seo profound citations "Claude SEO"
```

## When to use Profound vs. SE Ranking

| Use Profound | Use SE Ranking |
|---|---|
| Trend analysis (week-over-week brand mention drift) | Single-shot SoV measurement |
| ChatGPT + Perplexity deep coverage | All 5 platforms in one call |
| Alerts on citation rate change | Competitor-keyword gap analysis |

The two are complementary, not redundant. Install both for full AI
visibility coverage; install one if budget-constrained.
