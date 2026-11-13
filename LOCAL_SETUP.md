# ChatGPT companion setup

For the complete execution edition, start with the
[full Codex guide](plugins/codex-seo/docs/CODEX.md).
The guide below describes the smaller regular-ChatGPT companion.

This workspace starts from Daniel Agrici's public
[ChatGPT SEO companion](https://github.com/AgriciDaniel/chatgpt-seo), which already
adapts Claude SEO for ChatGPT. The imported package is SEO-pro 0.2.16, with 27
workflows and nine optional offline helper commands. Its source revision and
download checksum are recorded in [UPSTREAM.json](UPSTREAM.json).

## Start in a regular ChatGPT Project

1. Create a ChatGPT Project for your website.
2. Open [chatgpt-project/INSTRUCTIONS.md](chatgpt-project/INSTRUCTIONS.md) and copy
   only the text inside the instruction block into the project's instructions.
3. Add your website context and relevant page HTML/text, Search Console exports,
   crawl reports, or drafts as needed. Keep account upload and usage limits in mind.
4. Ask for a concrete task, for example:

   > Review this page for SEO using the attached HTML. Prioritize the fixes and
   > draft a title and description using facts in the page. Explain how to verify
   > each change.

   > Analyze this Search Console export for the supplied date range. Calculate
   > CTR from clicks and impressions, identify pages worth reviewing, and state
   > what the export cannot establish.

This path uses project instructions and the tools your ChatGPT account exposes.
It needs no plugin archive or API key. Public URL inspection depends on available
browsing; supplied files or pasted text provide an alternative. The instruction
file is a local addition, and provides a smaller workflow than the complete plugin.

## Use the complete plugin

If your account supports plugin archive uploads, use
[downloads/ai-marketing-hub-seo-0.2.16.zip](downloads/ai-marketing-hub-seo-0.2.16.zip)
and follow [the upstream installation guide](docs/INSTALL.md).
The source folder is [plugins/ai-marketing-hub-seo](plugins/ai-marketing-hub-seo).
The archive's root contains `plugin.json`; uploading a source-code ZIP or attaching
the file in a chat is a different operation.

The open-source files have no license fee. ChatGPT usage, model access, tool
availability and plan limits still apply. Optional image generation likewise
depends on the account's available tools. Installation in this account has not
been tested.

## Coverage and source identity

See [the capability map](docs/CAPABILITIES.md) for included workflows and
[the runtime contract](plugins/ai-marketing-hub-seo/references/runtime-and-data.md)
for execution and data requirements. The included Python helpers inspect supplied
files. Whole-site crawling, live Google-account reads and measured third-party
SEO data require separately available tools or supplied exports. Coverage follows
the companion's recorded Claude SEO source revision; newer Claude runtime features
need separate adaptation and verification.

The original package identity, MIT copyright notices, FLOW CC BY 4.0 attribution,
and publisher assets are retained with their provenance. See [NOTICE.md](NOTICE.md)
and [the package notice](plugins/ai-marketing-hub-seo/NOTICE.md). A future separately
branded distribution should use its own publisher identity and assets while
retaining the required notices.

## Verify the source and build locally

The optional developer checks use Python 3.10 or newer and its standard library.
Use your available Python executable for these commands. On Windows, the Python
launcher is often `py -3`; on macOS/Linux it is often `python3`.

```sh
python -X utf8 tools/validate_plugin.py
python -X utf8 -m unittest discover -s tests -v
python -X utf8 tools/package_plugin.py --check-downloads
```

The build is written to `dist/`, which is ignored by Git. The final command compares
the generated ZIP, checksum and inventory with the imported release files.
Local validation establishes package structure and helper behavior; actual plugin
installation and behavior require a separate host check.
See [the local verification record](docs/LOCAL_VERIFICATION.md) for completed
checks and environment limitations.

The project repository is [ChatGPT SEO](https://github.com/fox67-w/chatgpt-seo).
For the complete execution edition, follow [Getting started](docs/GETTING_STARTED.md).

Official product references:
[ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)
and [building skills](https://learn.chatgpt.com/docs/build-skills).
