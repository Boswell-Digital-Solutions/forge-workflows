# Architecture

The repository provides reusable Tauri CI and release workflows. They run in the
calling repository and retain its source checkout. The repository structure class
remains unresolved; this change does not assign a class or change ecosystem metadata.

## Required Debian archive check

Both workflows provision Lintian on Linux. When the CI caller enables bundle
building, the workflow checks every final Debian archive before artifact upload.
The release workflow applies the same check before its platform uploads.
Windows and AppImage inspection are outside Lintian's Debian scope.

The reusable CI toolchain setup explicitly installs `rustfmt` and `clippy`,
which its mandatory formatting and strict lint steps require. A fresh pinned
toolchain does not necessarily include those components. Missing components
remain a failed caller run; neither check is skipped or made advisory.

The check requires a tool version and at least one regular `.deb` archive.
It clears `LINTIAN_` environment options, disables user configuration and uses
the Debian profile. Existing package overrides remain in effect. Missing tools,
tool runtime failure, archive mutation and error-level tags block the job.
Warnings remain visible. The step records full output, tool version and archive
SHA-256 in the job log. It does not install packages from the caller.

The supported archive directory is
`<tauri_workdir>/target/release/bundle/deb`. A caller that uses a custom Cargo
output layout must supply a compatible build path before adopting this workflow.
Inspection does not establish binary source provenance, native readiness or release acceptance.
Callers retain ownership of application-specific repackaging and package contents.

Run `python3 -m unittest discover -s scripts -p test_lintian_workflows.py -v`.
These tests execute the actual YAML shell blocks with controlled tool outcomes.
They cover errors, runtime failure, missing tools, empty output, warnings,
configuration isolation and upload ordering. They do not qualify a live caller.
The existing contribution rule requires a successful calling-repository test
before merge. No caller ref or release tag is changed by this proposal.

Canonical documentation is rebuilt with `bash doc/system/BUILD.sh`.
The current builder ignores `--check`; compare output hashes across rebuilds.

The repository PR regression workflow also rebuilds the reference and compares
`doc/FWRSYSTEM.md` with Git. This comparison detects stale committed output
without treating the unsupported builder flag as a strict check.
