# Known Issues

## 2026-10-18 — Shared Debian package check rollout

**Status: proposed.** Reusable bundle jobs uploaded Debian archives without a
required Lintian check. The proposed check blocks upload on missing tools,
runtime failure, archive mutation and error-level findings. Application package
errors require review in the owning repository; no suppression is added here.

**Open acceptance limit:** the contribution procedure requires a successful
calling-repository test before merge. This proposal has local command tests,
not a live caller qualification. No release/tag or caller ref was changed.

**Open documentation limit:** the builder ignores `--check`. Separate output
hash comparisons prove stable rebuilds but do not implement a strict stale guard.
The unresolved documentation structure class remains unchanged.
