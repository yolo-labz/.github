# Sections

Source: `apps/web/src/components/sections/` (portfolio): `contact-cta.tsx`, `experience-timeline.tsx`, `organization-showcase.tsx`, `services-ladder.tsx`, `skills-matrix.tsx`.

## Purpose

Content blocks that the pages compose. `ContactCTA` closes a page. `ServicesLadder` lists services. `OrganizationShowcase` shows organisations and projects. `ExperienceTimeline` (role, dates, bullet list) and `SkillsMatrix` (definition list of skill groups) give the background.

## Anatomy

- Each block is a `section` with `aria-labelledby` (except where the heading is decorative), a heading (`text-step-4` to `text-step-6`), an intro (`max-w-measure`, `text-step-1`, `text-text-muted`), and a list or grid.
- `ContactCTA`: `scroll-mt-14`, large heading, email link (mono, `border-b-2 border-accent`), and GitHub and LinkedIn links.
- `ServicesLadder`: rows with a tracked email CTA per service (`contactEvent("services", ...)`).
- `OrganizationShowcase`: list of organisations; project links (`block py-4`).
- `ExperienceTimeline`: `ol` of roles, `h3` per role, bullet `ul` in `text-text-muted`. `SkillsMatrix`: `dl` of groups, rules between rows, `md` two-column grid.

## Tokens used

- `text-step-4` to `text-step-6`, `text-step-1`, `leading-body`, `leading-[1.05]`, `tracking-heading`, `tracking-[-0.03em]`.
- `text-text`, `text-text-muted`, `border-border`, `border-accent`, `text-accent`.
- Spacing: `px-6`, `py-20 sm:py-28`.

## States

- Link hover (underline to text colour), focus-visible, hover on project links.
- No empty state.

## Accessibility notes

- Headings are real `h2`/`h3` tied to their section.
- Every CTA and social link is 44 px tall (`min-h-11`).
- Analytics names come from `contactEvent`; the visible text is the accessible name.

## Open

- Five components in one doc. Split if one changes shape.
