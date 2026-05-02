# Getting Started

This guide uses the tracked `cupboard` case as the shortest path through the repository.

## Requirements

- Windows with PowerShell
- Python managed through `uv`
- Node.js and npm for JSCAD, ForgeCAD CLI, and docs tooling
- Git for cloning and reviewing changes

## 1. Sync Python Dependencies

```powershell
cd <repo-root>
uv sync --python 3.11
```

The root `pyproject.toml` pins the Python range to `>=3.11,<3.12`.

## 2. Install Case Node Dependencies

```powershell
cd cases\cupboard
npm install
```

Each case owns its own `package.json` because Node CAD dependencies are case-local.

## 3. Install Portable OpenSCAD

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_openscad.ps1
```

The script installs OpenSCAD under the case-local `tools\` directory. That directory is ignored because it can be regenerated.

## 4. Run the Benchmark

```powershell
uv run scripts\run_all.py
```

Successful runs refresh lightweight reports and screenshots. CAD files under `outputs\` remain ignored.

## 5. Build the Docs

```powershell
cd <repo-root>
npm install
npm run docs:build
```

The root npm scripts delegate to the VitePress project under `docs/`.

## Next Steps

- Review [Cases](./cases.md) to choose another benchmark.
- Review [Verification](./verification.md) before publishing documentation or report changes.
