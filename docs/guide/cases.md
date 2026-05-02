# Cases

Each tracked case is a self-contained benchmark workspace under `cases/<slug>/`.

## Case Matrix

| Case | Model | Main evidence | Notes |
|---|---|---|---|
| [cupboard](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/cupboard) | Basic 900 x 450 x 2000 mm cupboard | [Report](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/cupboard/reports/benchmark_report.md) | Baseline case for the shared workflow |
| [kitchen-trash-cupboard](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard) | 1680 x 650 x 1800 mm kitchen cupboard with three trash-bin bays | [Report](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/kitchen-trash-cupboard/reports/benchmark_report.md) | Production-style kitchen layout benchmark |
| [kitchen-trash-cupboard-concept1](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/tree/main/cases/kitchen-trash-cupboard-concept1) | Concept-image-driven kitchen cupboard variant | [Report](https://github.com/Sunwood-ai-labs/cad-agent-sandbox/blob/main/cases/kitchen-trash-cupboard-concept1/reports/benchmark_report.md) | Adds concept comparison and visual scoring evidence |

## What Belongs in a Case

```text
cases/<slug>/
  README.md
  docs/
  cupboard_benchmark/
  designs/
  outputs/
  reports/
  scripts/
  videos/
```

The case README should explain the model, toolchains, setup path, outputs, verification status, screenshots, and known limits.

## What Stays Out of Git

Generated CAD outputs, local OpenSCAD installs, dependency directories, rendered MP4 files, QA frames, and internal logs stay out of Git unless they are intentionally small public evidence files.

The canonical tracking rules live in [Case Layout](../CASE_LAYOUT.md).
