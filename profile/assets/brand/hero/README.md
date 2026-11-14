# Served hero and avatar

The files every surface serves.

| Slot | File |
|---|---|
| Org profile README (shown at 640 px) | `gremlin-hero-887x640.webp` |
| Portfolio hero, desktop and phone | `gremlin-hero-{804x770,402x385}.{avif,webp}`, `804x770.png` fallback |
| Avatar, 96 px | `gremlin-avatar-96.{png,webp}` (from `../mascot/gremlin-avatar.svg`) |
| GitHub org avatar upload | `gremlin-avatar-460.png` (same source) |

`manifest.json` pins size and sha256 for each file and holds the alt text for
every surface. Copy the alt text verbatim.

Consumers copy these files byte for byte and never re-encode them downstream.
