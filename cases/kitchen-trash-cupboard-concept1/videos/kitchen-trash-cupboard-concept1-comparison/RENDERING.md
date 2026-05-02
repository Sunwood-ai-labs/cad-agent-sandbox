# Kitchen Trash Cupboard Concept 1 Video Rendering

This HyperFrames project regenerates the concept1 comparison video with the corrected strict scoring and the attached concept sheet image included as visible evidence.

## Source Scope

- Video project: `cases\kitchen-trash-cupboard-concept1\videos\kitchen-trash-cupboard-concept1-comparison`
- Working case: `cases\kitchen-trash-cupboard-concept1`
- Reference-only case: `cases\kitchen-trash-cupboard`
- Concept image included: `assets\concept\concept_sheet_01_family_unit.png`
- Strict score data: `assets\video-data.json`

## Render Commands

```powershell
cd <repo-root>\cases\kitchen-trash-cupboard-concept1\videos\kitchen-trash-cupboard-concept1-comparison
npx hyperframes lint
npx hyperframes validate
npx hyperframes inspect --samples 14
npx hyperframes render --output renders\kitchen-trash-cupboard-concept1-comparison.mp4 --quality standard --fps 30
```

## 2026-05-02 Render Result

- MP4: `renders\kitchen-trash-cupboard-concept1-comparison.mp4`
- Duration: `64.000000` seconds
- Frames: `1920`
- Resolution: `1920 x 1080`
- Frame rate: `30 fps`
- Size: `9536236` bytes
- SHA256: `23B748EA6A0438099160EA9D62B49F11BC19D294FFC6ACFEBE44E0370F06309D`
- Validation: `npx hyperframes validate` passed with no console errors and 74 text elements passing WCAG AA.
- Layout inspection: `npx hyperframes inspect --samples 14` passed with 0 layout issues.
- Lint: 0 errors, 1 warning for single-file composition size.

## QA Frames

```powershell
ffmpeg -y -ss 0 -i renders\kitchen-trash-cupboard-concept1-comparison.mp4 -frames:v 1 -update 1 qa_frames\audit_first_frame.png
ffmpeg -y -i renders\kitchen-trash-cupboard-concept1-comparison.mp4 -vf "fps=1/8,scale=384:-1,tile=4x2" -frames:v 1 -update 1 qa_frames\contact_sheet.png
ffmpeg -y -i renders\kitchen-trash-cupboard-concept1-comparison.mp4 -vf "select='eq(n,60)+eq(n,300)+eq(n,600)+eq(n,810)+eq(n,1050)+eq(n,1290)+eq(n,1530)+eq(n,1740)',scale=384:-1,tile=4x2" -frames:v 1 -update 1 qa_frames\scene_start_sheet.png
ffmpeg -y -i renders\kitchen-trash-cupboard-concept1-comparison.mp4 -vf "select='eq(n,201)+eq(n,213)+eq(n,471)+eq(n,483)+eq(n,711)+eq(n,723)+eq(n,951)+eq(n,963)+eq(n,1191)+eq(n,1203)+eq(n,1431)+eq(n,1443)+eq(n,1641)+eq(n,1653)',scale=320:-1,tile=4x4" -frames:v 1 -update 1 qa_frames\transition_boundary_sheet.png
```

Generated QA frames:

- `qa_frames\audit_first_frame.png`
- `qa_frames\contact_sheet.png`
- `qa_frames\scene_start_sheet.png`
- `qa_frames\transition_boundary_sheet.png`

## Render Policy

`renders\`, `qa_frames\`, and `.hyperframes\` are generated local artifacts and are ignored by Git according to the repository policy.
