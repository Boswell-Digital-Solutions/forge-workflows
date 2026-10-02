# forge-workflows

Reusable GitHub Actions workflows for the BDS Tauri ecosystem.

Single source of truth for CI/CD across cortex_bds, VibeForge_BDS, and future Tauri applications.

---

## ðŸ“‹ Workflows Included

### `tauri-ci-reusable.yml`
Runs on every PR and push. Performs:
- Rust formatting check (`cargo fmt`)
- Clippy linting (`cargo clippy`)
- Unit tests (`cargo test --lib`)
- Optional: SvelteKit/Vite frontend build
- Optional: Tauri bundle build (creates installers)

**Supported Platforms:** Linux (ubuntu-latest), Windows (windows-latest). The `runner_os` input selects the runners. The default runs both.

### `tauri-release-reusable.yml`
Runs on version tags (`v1.0.0`, `v0.5.0-beta`, etc.). Performs:
- Frontend build (if enabled)
- Tauri bundle build (MSI, NSIS for Windows; AppImage, DEB for Linux)
- Creates GitHub Release
- Uploads artifacts for download

**Supported Platforms:** Linux (ubuntu-latest), Windows (windows-latest)

---

## ðŸš€ Quick Start

### For cortex_bds (Rust-only, no frontend)

**`.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  tauri-ci:
    uses: Boswecw/forge-workflows/.github/workflows/tauri-ci-reusable.yml@v1.0.0
    with:
      tauri_workdir: src-tauri
      build_frontend: false
      run_tauri_build: false
```

**`.github/workflows/release.yml`:**
```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  tauri-release:
    uses: Boswecw/forge-workflows/.github/workflows/tauri-release-reusable.yml@v1.0.0
    with:
      tauri_workdir: src-tauri
      create_github_release: true
```

### For VibeForge_BDS (Tauri + SvelteKit frontend)

**`.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:

jobs:
  tauri-ci:
    uses: Boswecw/forge-workflows/.github/workflows/tauri-ci-reusable.yml@v1.0.0
    with:
      tauri_workdir: src-tauri
      frontend_dir: .
      build_frontend: true
      run_tauri_build: false
```

**`.github/workflows/release.yml`:**
```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  tauri-release:
    uses: Boswecw/forge-workflows/.github/workflows/tauri-release-reusable.yml@v1.0.0
    with:
      tauri_workdir: src-tauri
      frontend_dir: .
      build_frontend: true
      create_github_release: true
```

---

## ðŸ”§ Workflow Inputs (Customization)

### `tauri-ci-reusable.yml` Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `runner_os` | string | `["ubuntu-latest","windows-latest"]` | JSON array of runner labels for the CI matrix. Pass `["ubuntu-latest"]` for Linux only. Supported labels: `ubuntu-latest`, `windows-latest` (not checked) |
| `rust_target_windows` | string | `x86_64-pc-windows-msvc` | Rust target for the Windows runner |
| `tauri_workdir` | string | `src-tauri` | Path to Tauri src-tauri directory |
| `frontend_dir` | string | `.` | Path to frontend (SvelteKit) directory |
| `build_frontend` | boolean | `false` | Whether to build frontend (required if using SvelteKit) |
| `frontend_build_dir` | string | `dist` | Output directory of frontend build |
| `run_tauri_build` | boolean | `false` | Whether to build Tauri bundles (slow, only on release tags) |
| `rust_version` | string | `stable` | Rust toolchain version (`stable`, `nightly`, `1.70.0`, etc.) |
| `continue_on_test_failure` | boolean | `false` | Continue to next job even if tests fail |

### `tauri-release-reusable.yml` Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tauri_workdir` | string | `src-tauri` | Path to Tauri src-tauri directory |
| `frontend_dir` | string | `.` | Path to frontend directory |
| `build_frontend` | boolean | `false` | Whether to build frontend before Tauri bundle |
| `frontend_build_dir` | string | `dist` | Output directory of frontend build |
| `create_github_release` | boolean | `true` | Whether to create GitHub Release with artifacts |
| `rust_version` | string | `stable` | Rust toolchain version |
| `artifact_retention_days` | number | `30` | How long to keep artifacts before deletion |

---

## ðŸ“¦ Artifact Downloads

### After PR/Push (via tauri-ci-reusable.yml)
- Workflow runs but artifacts are only uploaded if `run_tauri_build: true`
- Go to Actions â†’ Run â†’ Artifacts â†’ download

### After Release Tag (via tauri-release-reusable.yml)
- Push tag: `git tag v0.1.0 && git push origin v0.1.0`
- Workflow builds bundles automatically
- Go to Releases â†’ v0.1.0 â†’ download .msi/.exe/.deb/.AppImage
- Or: Actions â†’ Run â†’ Artifacts â†’ download

---

## ðŸ” Secrets Management

If you need to sign artifacts (Windows code signing, etc.):

**In calling repo (`cortex_bds/.github/workflows/release.yml`):**
```yaml
jobs:
  tauri-release:
    uses: Boswecw/forge-workflows/.github/workflows/tauri-release-reusable.yml@v1.0.0
    with:
      tauri_workdir: src-tauri
      create_github_release: true
    secrets:
      TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
      TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
```

Set these secrets in your calling repo (Settings â†’ Secrets and variables).

---

## ðŸ”„ Versioning Strategy

### Semantic Versioning
- **v1.0.0** â€” Stable. All repos should use this.
- **v1.1.0** â€” Minor update (new feature). Backward compatible.
- **v2.0.0** â€” Major update (breaking change). Requires migration.

### How to Update
1. **In forge-workflows:**
   ```bash
   git checkout main
   git pull origin main
   vim .github/workflows/tauri-ci-reusable.yml  # Make changes
   git add -A
   git commit -m "feat: add new feature"
   git tag v1.1.0
   git push origin main --tags
   ```

2. **In calling repos** (at their own pace):
   ```bash
   # Update .github/workflows/ci.yml and release.yml
   # Change: uses: ...@v1.0.0  â†’  ...@v1.1.0
   git add .github/workflows/
   git commit -m "ci: update to shared workflows v1.1.0"
   git push origin main
   ```

---

## ðŸ› Troubleshooting

### Workflow not found
**Error:** `Error: Can't find 'tauri-ci-reusable.yml'`  
**Fix:** Ensure tag exists in forge-workflows:
```bash
cd forge-workflows
git tag v1.0.0
git push origin v1.0.0
```

### Frontend build fails
**Error:** `Cannot find dist/` or similar  
**Fix:** Verify `frontendDist` in `tauri.conf.json` matches your build output:
```bash
# In calling repo
pnpm build                # Check output location
grep frontendDist src-tauri/tauri.conf.json
# Should point to where your frontend build outputs
```

### Tests fail on Windows
**Common:** Path separators (use `/` in Rust, not `\`)  
**Fix:** Use `std::path::Path` or constants instead of string literals.

### Slow builds
**Issue:** No caching or first-run cold build  
**Solution:** Already in workflows (uses `actions/cache@v4` and `Swatinem/rust-cache@v2`)  
First run = slow (15-20 min), subsequent = fast (5-10 min)

---

## ðŸ“Š Architecture

```
forge-workflows (this repo)
â”œâ”€â”€ .github/workflows/
â”‚   â”œâ”€â”€ tauri-ci-reusable.yml      # Reusable CI workflow
â”‚   â””â”€â”€ tauri-release-reusable.yml # Reusable release workflow
â”œâ”€â”€ README.md (this file)
â”œâ”€â”€ CONTRIBUTING.md
â””â”€â”€ LICENSE

Calling repos (cortex_bds, VibeForge_BDS, etc.)
â”œâ”€â”€ .github/workflows/
â”‚   â”œâ”€â”€ ci.yml       (10 lines - calls tauri-ci-reusable.yml)
â”‚   â””â”€â”€ release.yml  (10 lines - calls tauri-release-reusable.yml)
â””â”€â”€ [rest of repo]
```

---

## ðŸ“ Contributing

To improve these workflows:

1. **Test locally first** in a calling repo
2. **Open PR** to forge-workflows with description of change
3. **Tag release** (v1.1.0, v2.0.0, etc.) once merged
4. **Notify teams** if it's a breaking change

See `CONTRIBUTING.md` for detailed guidelines.

---

## ðŸ“š Related Documentation

- **GITHUB_ACTIONS_REUSABLE_WORKFLOW_PLAN.md** â€” Full implementation guide
- **REFERENCE_CARD.md** â€” Quick commands and troubleshooting
- **CORTEX_BDS_FIX_LOG.md** â€” What was fixed before this strategy

---

## ðŸ“„ License

[Your license here]

---

## â“ Support

**Issues during setup?**

1. Check troubleshooting section above
2. Verify `uses:` path is correct (check tag exists)
3. Run workflows locally first (`pnpm build && pnpm tauri build`)
4. Open an issue in this repo with workflow run logs

---

**Last Updated:** December 12, 2025  
**Maintainer:** BDS Team
