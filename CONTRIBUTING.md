# Contributing

Thanks for improving CAD Agent Sandbox.

## Development Setup

Use Windows PowerShell and `uv` for Python commands:

```powershell
uv sync --python 3.11
npm install
```

Case-local Node dependencies still live inside each case:

```powershell
cd cases\cupboard
npm install
```

## Before Opening a Pull Request

Run the lightweight checks from the repository root:

```powershell
uv run cases\cupboard\scripts\verify_text_encoding.py
uv run scripts\verify_tracked_markdown_links.py
npm run docs:build
```

If you change CAD generation or scoring code, also run the relevant case's `uv run scripts\run_all.py`.

## Generated Files

Do not commit regenerated `outputs`, local `tools`, `node_modules`, rendered videos, QA frames, or internal logs unless a specific public evidence file is intentionally tracked.
