# Unlighthouse extension setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension unlighthouse --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan unlighthouse
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

[Unlighthouse](https://unlighthouse.dev) is an MIT-licensed multi-page
Lighthouse runner that produces a single aggregate report. No API
quota, no credentials, no network egress beyond crawling the target.

## Verify

```
/seo unlighthouse https://example.com --max-routes 5
```

## When to use Unlighthouse vs. PageSpeed Insights

| Use Unlighthouse | Use PSI |
|---|---|
| Site has 100s of pages and you want every one audited | Single-URL focused audit |
| Offline / restricted environment | Field data from real Chrome users (CrUX) |
| CI-driven regression check post-deploy | Quick CLI/web-form check |
| Free / no quota concern | PSI quota OK for small sites |

PSI uses CrUX field data when available (real users); Unlighthouse
runs Lighthouse lab tests locally. For trustworthy CWV measurement
on production traffic, prefer PSI / CrUX.
