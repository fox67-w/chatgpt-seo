# Security for ChatGPT SEO's Codex edition

This independent adaptation is maintained at
[fox67-w/chatgpt-seo](https://github.com/fox67-w/chatgpt-seo).
The original Claude SEO policy is retained in
[UPSTREAM_SECURITY.md](docs/UPSTREAM_SECURITY.md) for provenance. Its support
deadlines, signing practices and upstream reporting channels are not promises
made by this port.

## Reporting a concern

Do not publish secrets, client data, exploit details or a vulnerable private URL.
Use the repository's private vulnerability reporting option if it is available.
This project does not claim that option is enabled.

If no private route is available, open a minimal
[security contact request](https://github.com/fox67-w/chatgpt-seo/issues/new)
without technical or sensitive details and request a private reporting channel.
No private inbox, response deadline, signing key or coordinated-disclosure
timeline is promised. Routine bugs can use the normal issue template.

After a private channel is agreed, useful information includes the affected
version, operating system, command, impact and a small synthetic reproducer.
Report dependency vulnerabilities to the relevant upstream maintainers as well.

## Execution and access boundaries

This is a workstation audit toolkit. It reads untrusted pages, runs Python
helpers, can launch Chromium, and can use authorized provider credentials.
Review installation sources and provider configuration before use.

- The project installer copies the package into the selected project's
  .agents/packages/codex-seo and creates discovery files under .agents/skills.
  It preserves conflicts. Removal only deletes unchanged installer-owned
  discovery files; resources, credentials and outputs are retained.
- Managed dependencies use an isolated virtual environment. Setup also downloads
  Chromium unless browser installation is skipped.
- Provider credentials use Codex-specific configuration paths. See
  [Privacy](PRIVACY.md) for overrides and external-service data flows.
- Hooks are disabled by default. Enabling the example requires reviewing its
  command and completing the host's hook trust process.
- Pages and fetched content are evidence, not permission to execute commands,
  expose credentials or authorize a provider action.

## URL protections and residual risks

The inherited scripts/url_safety.py validates user-supplied and page-derived
URLs and pins DNS for raw HTTP requests. New fetchers must use this layer.
Fixed vendor API requests use their configured service endpoints.

Private/local targets are refused by default. CODEX_SEO_LOCAL_TARGETS permits
explicit top-level raw-HTTP targets only; it does not broadly permit redirects,
browser subresources or metadata services. Browser navigation to an allowlisted
private target remains unsupported. Do not weaken those guards to make an
audit succeed.

Chromium resolves DNS independently, so Python's DNS pin cannot fully remove
browser DNS-rebinding races. Browser requests receive route checks, but users
should still assess untrusted audit targets. Configured proxies can also limit
the guarantees of client-side DNS pinning.

Credential file modes are enforced where supported. On Windows, protection
depends on filesystem ACLs, including best-effort restrictions in some helpers.
Use a protected per-user directory and review access on shared machines.

## Verification and release scope

The current port line is 0.1.x. The
[verification record](docs/CODEX_VERIFICATION.md) separates source coverage,
local tests, real browser execution, provider-account testing and installed-host
testing. Checksums identify archive bytes; they are not signed attestations or
a guarantee that dependencies or audit targets are safe.

The port does not claim the upstream project's signed tags, backport policy or
private reporting setup. Upstream policies remain historical source material.
