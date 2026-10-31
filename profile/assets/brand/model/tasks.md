# S1 tasks — 31/10/2026

- [x] Inspect source SVGs, prior anchor, current effects and canonical GPT workflow.
- [x] Create requested 013 worktree from freshly fetched origin/main 6488088.
- [x] Fix parsed Mocha/Latte palette and head-unit proportions; label depth assumptions.
- [x] Expose absolute SPEC.md handoff path to wT:p6 in report and draft PR #12.
      The lead relays it; no message to or interruption of another pane is claimed.
- [x] Prepare source/anchor references, seven PNG provenance sidecars and five hashed prompts.
- [x] Reconcile readiness: chatgpt-c ready/headed on the server fleet, CDP forward
      verified before every send; no local browser, API or restart.
- [x] Generate orthographic front/3/4/side/back sheet (`turnaround.png`).
- [x] Generate six-expression sheet (`expressions.png`).
- [x] Generate typing/thinking/celebrating/asleep sheet (`poses.png`).
- [x] Generate hands/claws/keyboard sheet (`hands-keyboard.png`).
- [x] Generate colour/material sheet — delivered on the second attempt after the
      account quota reset (send 6/8).
- [x] Inspect all four delivered sheets and record per-sheet drift in SPEC.md and sidecars.
- [x] Re-derive SPEC geometry from merged `model/params.json` (PR #14, main `ff1abc0`);
      gate fails on upstream drift (unit test mutates the 3D eye radius).
- [x] Run spec-only gate: exit 0; not full sheet acceptance.
- [x] Run full gate: exit 0 on all five sheets and their provenance.
- [x] Run bad-palette fixture: exit 1; four offline tests pass.
- [x] Preserve reproducibility instructions, typed hold and draft delivery evidence.

All five sheets exist, the default gate exits 0, and the drift register records
what each render actually shows. No merge was attempted by this row.
