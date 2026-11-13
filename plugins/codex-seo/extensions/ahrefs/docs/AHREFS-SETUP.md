# Ahrefs extension setup

<!-- codex-seo-extension -->
## Codex provider integration

This workflow is included with the full port. Review local activation and provider requirements with:

```text
python "<resolved-plugin-root>/install-codex.py" --extension ahrefs --project "<project-root>" --dry-run
python "<resolved-plugin-root>/extensions/codex-extension.py" plan ahrefs
```

Use `--apply` instead of `--dry-run` only when enabling local discovery is requested. Activation alone does not connect a provider or authorize a paid operation. Keep credentials in the supported environment/local store; never paste values into reports or tracked configuration.

For a Codex MCP connection fragment, run:

```text
python "<resolved-plugin-root>/extensions/codex-extension.py" toml ahrefs
```

Review the fragment and merge it through the host's MCP configuration flow. It names credential environment variables without embedding their values. Check the connection's actual available tools before running this workflow.

Wires the official [`@ahrefs/mcp@0.0.11`](https://www.npmjs.com/package/@ahrefs/mcp)
server into your Codex session so the `seo-ahrefs` skill can call
live Ahrefs data.

## Verify

Open a new Codex session and ask:

```
/seo ahrefs metrics https://example.com
```

If you see "Ahrefs MCP not connected", the npm package is not yet cached.
Re-run the installer to pre-warm or run `npx --yes --package=@ahrefs/mcp@0.0.11 mcp --help` manually.

## Cost model

Ahrefs charges per "unit". A unit covers most read endpoints (domain
metrics, backlink data) at 1 unit each; bulk endpoints cost more. The
`python "<resolved-plugin-root>/scripts/codex_seo.py" run dataforseo_costs.py` cost tracker shipped with claude-seo
generalises across vendors; see the DataForSEO extension's
`references/cost-tiers.md` for the budget-preset pattern to mirror when
wiring Ahrefs accounting.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Error: AHREFS_API_TOKEN is empty` | Credential environment is unavailable | Provide the token through the connection's required environment variable |
| `npx: package not found` | Offline run / fresh machine | Run with internet on; the installer pre-warms but the cache needs network |
| 401 from any `/seo ahrefs *` command | Token revoked / expired | Refresh the token at https://ahrefs.com/api and update the connection environment |
