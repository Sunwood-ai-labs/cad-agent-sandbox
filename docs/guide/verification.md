# Verification

Use lightweight checks before committing documentation or report changes. Run full CAD regeneration only when the case source or scoring logic changed.

## Documentation Checks

```powershell
cd D:\Prj\cad-agent-sandbox
uv run cases\cupboard\scripts\verify_text_encoding.py
uv run scripts\verify_tracked_markdown_links.py
npm run docs:build
```

The encoding check scans Markdown and HTML outside `.venv`, `node_modules`, and `tools`. The tracked link check avoids local untracked experiment cases while still covering tracked docs and root README files.

## Case Checks

From a case directory:

```powershell
uv run scripts\verify_step_imports.py
uv run scripts\verify_openscad_step_probe.py
uv run scripts\verify_report_images.py
uv run scripts\verify_markdown_links.py
```

Use `uv run scripts\run_all.py` when you need a full refresh of source generation, screenshots, scoring, and reports.

## Payload Review

Before committing, review the staged payload and exclude bulky regenerated files:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_commit_payload.ps1 -RepoPath .
```

Keep `node_modules`, `.venv`, `tools`, `outputs`, video renders, and QA frames out of commits.
