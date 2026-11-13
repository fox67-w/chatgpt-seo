# Local verification

Verified on Windows with the bundled Python 3.12 runtime on 13 November 2026.
This record describes the local working copy; it is separate from the upstream
publisher's installation and acceptance records.

| Check | Result |
| --- | --- |
| Downloaded release identity | ZIP Git blob SHA matched the pinned public source |
| Package validation | Passed: 27 skills, 113 package files, no structural errors |
| Unit tests | 134 run: 132 passed, 2 environment-dependent skips |
| Reproducible package build | Passed; ZIP, checksum and inventory exactly match the imported release |
| Project instructions | 5,940 characters inside the copyable block; ASCII punctuation |
| Independent Project workflow check | Correctly analyzed the supplied GSC sample and withheld unsupported indexing conclusions |

Release archive SHA-256:

```text
671db95f83ce9634db700baada0fce5ed5b21e97eecaff7abeb2e0b3c7a651be
```

The Windows test skips cover literal backslash/colon filename fixtures that
require a POSIX filesystem and symbolic-link creation denied by Windows error
1314. The validator's rejection checks remain active where those fixtures can be
created. The GitHub Actions workflow now configures Ubuntu and Windows checks;
those hosted jobs have not run for this local working copy.

The source build comparison exposed host-dependent path ordering and sidecar
newlines. Local packaging now uses case-sensitive path-component ordering and
UTF-8 LF sidecars, preserving the upstream Linux release bytes. The test suite
also checks the actual versioned download, archive order and sidecar newlines.

The independent Project test used the provided `gsc.csv` fixture. It calculated
19 clicks / 1,000 impressions = 1.9% CTR for the supplied rows, treated the
zero-impression row's CTR as undefined, and requested indexing evidence separately.
This is a local instruction-following check, rather than an installed ChatGPT
plugin test.

The generic skill creator validator was also attempted, but its PyYAML dependency
is absent from this bundled Python runtime. The package's standard-library
validator successfully checked all included skill metadata and resources.

Actual installation in the user's ChatGPT account and public directory approval
remain unverified. Local logs and the rebuilt archive are under ignored `dist/`.
Source provenance is recorded in [UPSTREAM.json](../UPSTREAM.json).
