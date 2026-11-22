# Project detail

Source: `apps/web/src/components/project/project-detail.tsx` (portfolio).

## Purpose

Full page for one project. Gives the story: problem, solution, overview, the decision record, metrics, stack and links, and previous/next navigation.

## Anatomy

- Back link (`min-h-11`, `text-text-muted`) to the work index.
- Heading (`text-step-5`, `tracking-display`) and summary (`text-step-1`).
- Two-column grid (`lg:grid-cols-12`): main column with sections (`aria-labelledby`: problem, solution, overview, decision record); side column `dl` with metrics, stack (`font-mono text-xs`) and link list (`min-h-11`).
- Decision record: `dl` of constraint / decision / outcome, each coloured by kind (`warn`, `link`, `accent`).
- Walk nav: two `min-h-20` links, previous and next, with `aria-label` from translation. Hover turns the name to `text-accent`.

## Tokens used

- `text-step-5`, `text-step-2`, `text-step-1`, `text-sm`, `text-xs`, `font-mono`.
- `text-text`, `text-text-muted`, `text-link`, `text-warn`, `text-accent`, `border-border`.
- `max-w-measure` for prose.

## States

- Link hover, link focus, walk link hover (name to accent).
- No loading or empty state in this file.

## Accessibility notes

- Heading order: one `h1`, section `h2`s with ids that match `aria-labelledby`.
- Walk nav has an `aria-label`.
- Kind labels are text, not colour alone.
- Links and back link are 44 px tall.

## Open

- Metric labels (`text-xs text-text-muted`) are small. Check against the 14 px minimum (`--yl-text-min-text`).
