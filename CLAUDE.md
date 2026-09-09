# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

forge-workflows provides reusable GitHub Actions workflows for the BDS Tauri ecosystem — the single
source of truth for CI/CD across `cortex_bds`, `VibeForge_BDS`, and future Tauri applications. This
repo contains no application code; it contains two reusable workflow definitions that other repos call
via `uses:`.

## Common Commands

There is no local build/test — this repo's "output" is the two workflow YAML files under
`.github/workflows/`. Changes are verified by testing in a calling repo before merge:

```bash
# tag a release once a change is merged to main
git tag v1.1.0
git push origin v1.1.0
```

```bash
# in a calling repo, point at a branch to test before it's tagged
uses: Boswecw/forge-workflows/.github/workflows/tauri-ci-reusable.yml@your-branch
```

## Architecture

- `.github/workflows/tauri-ci-reusable.yml` — reusable CI: Rust `cargo fmt`/`clippy`/`cargo test --lib`,
  optional SvelteKit/Vite frontend build, optional Tauri bundle build. Runs on Linux and Windows.
- `.github/workflows/tauri-release-reusable.yml` — reusable release: builds Tauri bundles (MSI/NSIS on
  Windows, AppImage/DEB on Linux), creates a GitHub Release, uploads artifacts. Triggered on version
  tags.
- Calling repos keep a ~10-line `ci.yml`/`release.yml` that just calls these with their own inputs
  (`tauri_workdir`, `frontend_dir`, `build_frontend`, `run_tauri_build`, etc. — see
  `forge-workflows-README.md` for the full input tables).

## Notes

- This repo is Tauri-specific and generic on purpose — it is not a place for app-specific CI logic
  (that belongs in the calling repo), and not for frontend-only or backend-only frameworks.
- Never merge a workflow change without testing it in a calling repo first (point that repo's `uses:`
  at your branch, confirm its CI is green, then merge here and tag a release). See
  `forge-workflows-CONTRIBUTING.md` for the full test-then-tag-then-notify workflow and versioning
  rules (patch/minor/major, migration guides for breaking changes).
- Repo docs are named `forge-workflows-README.md` / `forge-workflows-CONTRIBUTING.md` rather than the
  usual `README.md`/`CONTRIBUTING.md`.
