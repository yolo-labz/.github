# Colour

Dark is the default. Catppuccin Mocha for neutrals, Latte for the light theme, emerald for the one action.
Use the semantic names (`surface`, `text`, `accent`, `link`, `role`, `signal`). The Mocha and Latte names exist so
a palette can be checked, not so pages can reach for them.

| Role | Dark | Light | Used for |
|---|---|---|---|
| `surface.base` | `#1e1e2e` | `#eff1f5` | page ground |
| `surface.raised` | `#181825` | `#e6e9ef` | the one raised band |
| `text.default` / `text.muted` | `#cdd6f4` / `#a6adc8` | `#4c4f69` / `#5c5f77` | body, secondary |
| `accent.default` | `#00c77a` | `#007045` | the one action |
| `link.default` | `#89b4fa` | `#154fc3` | links that leave the page |
| `role.audit` / `role.compliance` | peach / yellow | peach / yellow | audit trail, compliance badges |
| `role.mark` | mauve | mauve | the gremlin's pupils and glyphs |

**Rules**
- Colour carries meaning and nothing else. Emerald means act. Peach means audit. Yellow means compliance only.
- Text is 4.5:1 or better on its ground, in both themes. Control borders and the focus ring are 3:1. `test_tokens.py` checks it.
- Mauve stays inside the gremlin. It is not a UI colour.
- Rules between rows are `border.default`; a control's own edge is `border.strong`.

**Right:** `color: var(--yl-color-text-muted)` on a caption.
**Wrong:** `color: #a6adc8`. The value is right today and wrong after the next palette change. A raw hex in CSS fails the blog gate.

**Right:** a green "Send a brief" button using `accent.default` with `accent.on` text.
**Wrong:** a second purple button next to it because the page "needed an accent".
