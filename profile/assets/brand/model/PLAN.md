# S1 execution plan and checkpoint

1. Inspect actual source SVGs, prior anchor provenance, branch effects, processes
   and the canonical server GPT pipeline before any send.
2. Fix source-derived palette and head-unit proportions first. Publish SPEC path
   in the report and draft PR for the lead to relay to S2, without waiting for art.
3. Prepare immutable local references and five explicit PRESERVE/CHANGE prompts.
   Keep imported/raster-composed references distinct from newly generated sheets.
4. Only when server discovery and the authenticated composer are verified, hold
   the existing fleet queue lock and call the installed gpt-image shim for one
   reference-anchored image at a time. Reconcile before every further send.
   Five planned sends, ceiling eight; stop at the first exact blocker.
5. Inspect each result, keep exact originals and sanitized provenance, record drift.
   Default check.py must validate all five actual sheets, not prepared references.
6. Run negative fixture, source-only and full acceptance separately. Keep the PR
   draft and assigned phsb5321; never merge, publish, reset a browser or use API/local
   fallbacks. Preserve the exact hold if generation is blocked.
7. Re-derive the 2D spec from the merged 3D single source (`model/params.json`,
   PR #14) so the two cannot drift apart silently; machine-check the parity.

Current checkpoint (31/10/2026): steps 1-3, 5 (for the four delivered sheets),
6 and 7 are complete. Step 4 stopped at the account image quota after five sends:
sheets 1-4 exist with provenance, `colour-material.png` does not. Default gate
exits 1 on the missing fifth sheet by design. Resume is one send after the quota
reset (~16:25 BRT) — see `reproduce.md`.
