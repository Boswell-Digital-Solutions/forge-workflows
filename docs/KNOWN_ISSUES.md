# Known Issues

## 2026-11-09 — `continue_on_test_failure` can turn a failed unit test into a green `CI Status`

**Status: open.** Recorded by forge BDS-FGITR-v0.1 (governance truth audit). Verified on `master` `7174e2fe`.

`tauri-ci-reusable.yml:48-50` declares the input `continue_on_test_failure` (default `false`). Line 176
sets `continue-on-error: ${{ inputs.continue_on_test_failure }}` on `cargo test --lib`. When a caller sets
it to `true`, a failed test step leaves the job result `success`. The `CI Status` job (lines 232-245)
checks only `needs.quick-checks.result`, so it passes. A caller can make `CI Status` a required check, so
a required check can report green over a failed test.

No caller sets the input to `true` today: forge-smithy (pin `d815c296`) omits it, and cortex_bds (pin
`cc189163`) sets `false`. The risk is latent.

**Fix:** none applied. Options: remove the input, or make `CI Status` fail when the test step outcome is
`failure`, the pattern forge-smithy's `analysis-suite.yml` uses with its "Enforce Gates" step.

## 2026-11-09 — A green `CI Status` does not prove a frontend build or a Tauri bundle

**Status: open.** Recorded by forge BDS-FGITR-v0.1. Verified on `master` `7174e2fe`.

`build_frontend` and `run_tauri_build` both default to `false` (`tauri-ci-reusable.yml:37-44`). With the
defaults, the workflow places a frontend placeholder (lines 129 and 137) and builds no bundle. `CI Status`
then reports the same green result as a full build. cortex_bds calls it with both inputs `false`. A
caller's required `CI Status` check is therefore Rust lint and unit-test evidence only, unless the caller
sets both inputs. Nothing in the result says which scope ran.

**Fix:** none applied.

## 2026-11-09 — The release workflow publishes on build success, with no operator release decision

**Status: open.** Recorded by forge BDS-FGITR-v0.1. Verified on `master` `7174e2fe`.

`tauri-release-reusable.yml:26-28` defaults `create_github_release` to `true`. The publication job runs on
`inputs.create_github_release && success()` (line 215). No step obtains or checks an operator release
decision. Build qualification, release authorization and publication are not separate, verifiable
transitions.

**Fix:** none applied. One option is a GitHub environment with required reviewers on the publication job.
For a single operator, a recorded release decision that the job verifies may fit better.

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
