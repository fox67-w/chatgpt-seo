# Bing Webmaster Tools + IndexNow extension setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension bing-webmaster --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan bing-webmaster
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

## What this gives you

1. **Bing Webmaster Tools API**: inbound links, crawl stats, search
   keywords, and competitor link comparison via
   `python "<resolved-plugin-root>/scripts/codex_seo.py" run bing_webmaster.py` (already shipped with claude-seo).
2. **IndexNow URL submission** for Amazon, Bing, Naver, Seznam.cz,
   Yandex, and Yep via `python "<resolved-plugin-root>/scripts/codex_seo.py" run indexnow_submit.py`.
3. A unified `seo-bing` skill that routes the right command at the
   right script.

## IndexNow setup checklist

1. Generate a key: `openssl rand -hex 32`
2. Save the key to a file at the **root** of your site, named `<key>.txt`,
   served at `https://example.com/<key>.txt`. The file body is the key.
3. Run:
   ```
   /seo bing verify-indexnow
   ```
   The verifier fetches your keyLocation URL and confirms the body
   matches the key, the #1 onboarding mistake.

## Microsoft Copilot citation

Microsoft Copilot pulls citations from the Bing index. Pages that
aren't in Bing aren't citable. IndexNow notifies participating
engines about changed URLs and can speed discovery, but it does not
guarantee indexing speed.
