# Served hero and avatar

The files every surface serves, per the decision adopted on 08/11/2026
(`../hero-decision/README.md`):

| Slot | File | Source |
|---|---|---|
| Org profile README (shown at 640 px) | `gremlin-hero-gpt-887x640.webp` | GPT master `../rollout/gremlin-wide-hero.png` |
| Portfolio hero, desktop / phone | `gremlin-hero-gpt-{804x770,402x385}.{avif,webp}`, `804x770.png` fallback | same GPT master, same crop window |
| Avatar, 96 px | `gremlin-avatar-96.{png,webp}` | vector kit `../mascot/gremlin-avatar.svg` |
| GitHub org avatar upload | `gremlin-avatar-460.png` | same vector kit |

Crops and encoder settings are the ones the decision sheet was judged on
(`../hero-decision/build_sheet.py`). Alt text for every surface is in
`manifest.json` → `alt`; copy it verbatim.

```sh
python3 profile/assets/brand/hero/publish.py            # re-cut + rewrite manifest.json
python3 profile/assets/brand/hero/publish.py --verify   # committed bytes vs manifest.json
```

Consumers copy these files byte-for-byte; never re-encode them downstream.
