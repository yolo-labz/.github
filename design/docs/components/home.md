# Home sections

Source: `apps/web/src/components/home/` (portfolio): `work-index.tsx`, `case-files.tsx`, `fleet-cases.tsx`.

## Purpose

The home page body. `WorkIndex` is the hero and the ordered list of work. `CaseFiles` and `FleetCases` are the two case lists below it.

## Anatomy

- `WorkIndex`: hero heading (`text-step-4`, `font-semibold`, `tracking-heading`), image with `alt`, lead paragraph, proof link, ordered work rows (`ol` > `li.work-row`), each row a link with title, summary and kind label (`text-warn` for case file, `text-link` otherwise), plus an arrow icon and a bottom rule that scales in on hover.
- `CaseFiles`: section with `aria-labelledby`, heading, intro, and `ol` of entries (title `text-step-2`, metric, `dl` of constraint / decision / outcome).
- `FleetCases`: like `CaseFiles` with a smaller title (`text-step-1`) and a link below each entry.

## Tokens used

- Type: `text-step-1` to `text-step-4`, `text-base`, `text-sm`, `text-xs`, `leading-body`, `leading-tight`, `tracking-heading`.
- Colour: `text-text`, `text-text-muted`, `text-accent` (keyword, hover), `text-warn` (case file label, constraint), `text-link` (other label, decision), `border-border`, `bg-accent` (rule).
- Motion: `duration-200 ease-out` (arrow), `duration-300` (rule).

## States

- Row: default, hover (title to `text-accent`), focus-visible (same colour plus focus ring).
- Proof link: hover to `text-accent`, focus-visible.
- Motion: arrow shift and rule scale. Under reduced motion the `globals.css` rule removes transitions.

## Accessibility notes

- Each section has `aria-labelledby` pointing at its heading.
- Hero image has `alt` from translation (`renderAlt`).
- Work rows use `min-h-11` (44 px). The inline link in case lists is `min-h-11`.
- Kind is shown in text (case file, other), not by colour alone.

## Open

- `text-warn` and `text-link` on `bg` need a contrast check in light theme (not run here).
