# SEO packages

The user has requested the complete public Claude SEO feature set for Codex.
The full execution edition lives in `plugins/codex-seo/`. It retains the public
source runtime, Python scripts, browser support, specialist prompts, data,
templates and all optional extensions. Preserve MIT and FLOW CC BY 4.0 notices.
Use only public source and record its exact upstream revision.

The earlier instruction-first ChatGPT package remains in
`plugins/ai-marketing-hub-seo/`. Its SEO-pro identity and offline-only
execution contract apply to that package, rather than to the new Codex edition.

Use available Codex tools and native collaboration for the full edition.
If this repository contains .runtime/codex-seo/runtime-state.json, reuse that
prepared runtime by setting CODEX_SEO_DATA_DIR to its absolute parent directory
in the tool command's environment. Keep that choice scoped to the task.
Resolve package paths from the selected skill or launcher. Do not depend on
Claude host variables, tool names, model aliases or global Claude settings.
Keep provider requirements explicit. Source availability, local verification,
live account testing and host installation are distinct states.

Run relevant runtime and analysis regressions and the full-port validation before
packaging the Codex edition. The existing ChatGPT package checks remain
`python tools/validate_plugin.py`, `python -m unittest discover -s tests -v`,
and `python tools/package_plugin.py --check-downloads`.

The user authorized publication as fox67-w/chatgpt-seo. Preserve other edits and
keep credentials, private reports and runtime state out of source archives.
Use ASCII punctuation in newly authored instructions.
