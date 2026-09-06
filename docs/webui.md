# Web UI / UX Design

## 1. Design principles

- **Transparency over automation.** Every AI-generated output (score, match, draft) should show *why* — the underlying reasoning or evidence — not just a number or a paragraph.
- **Review, don't surprise.** Nothing gets sent or submitted without an explicit, visible approval step. The approval screen should feel like a natural checkpoint, not a speed bump.
- **Progressive disclosure.** Don't show the full agent pipeline complexity up front — the user should feel like they're using a career assistant, not operating a multi-agent control panel.

## 2. Tech choices

- **Next.js** (matches existing stack) for the frontend, with server-side rendering for the dashboard.
- **Tailwind CSS** for styling; **shadcn/ui** for form components, dialogs, and the approval modal — fast to build with and consistent out of the box.
- **Recharts** for the progress-report charts (application volume, skill-gap trend over time).

## 3. Core screens

### 3.1 Onboarding / resume upload
- Drag-and-drop resume upload (PDF/DOCX)
- Target role input (autocomplete against a seeded role list, freeform allowed)
- After upload: show the *parsed* resume structure (name, skills, experience) for the user to confirm or correct before anything downstream uses it — catches parsing errors early.

### 3.2 Skill gap dashboard
- "Have" vs "need" skills for the target role, visually separated (e.g. two columns or a Venn-style layout)
- Each missing skill links to 1–2 recommended projects/resources
- ATS score for the resume with specific, actionable flags (not just a number)

### 3.3 Job matches
- Ranked list of jobs, each showing: match score, the 2–3 reasons it matched (retrieved evidence, not just a black-box score), and the specific skill gaps for *that* job
- Filter/sort by location, seniority, match score
- Clicking a job opens the detail view with the full structured requirements

### 3.4 Application review (the approval checkpoint)
- Side-by-side: original resume vs. the agent's reordered/tailored version, with changes highlighted
- Editable cover letter draft (plain textarea, not a black box — the user can rewrite freely)
- Explicit "Approve & continue" action — this is the one screen in the product that should never feel rushed; no auto-advance, no pre-checked boxes
- After approval: a clear next step (open the job posting to submit, or confirm submission if a compliant submit API is used)

### 3.5 Application tracker
- Table/kanban view: drafted → approved → applied → response received
- Quick filters by status and by role
- Manual status update (user can mark responses/interviews since most job sites won't report this back automatically)

### 3.6 Weekly progress report
- Auto-generated summary card: applications sent, response rate, top closing skill gaps, suggested focus for next week
- Delivered on the dashboard and optionally via email (see `deployment.md` for the scheduling mechanism)

## 4. Interaction patterns

- **Loading states matter more here than in a typical CRUD app** — agent calls take seconds, not milliseconds. Use skeleton loaders with a short, honest status label (e.g. "Matching against job requirements…") rather than a generic spinner, since the user should understand something substantive is happening.
- **Every AI output has a visible source.** Job match reasons, skill-gap items, and resume flags should be traceable to the underlying data, not presented as unexplained assertions.
- **Undo, not just approve.** The application review screen should let the user regenerate a section (e.g. "rewrite this cover letter paragraph") rather than only accept-or-discard the whole draft.

## 5. Accessibility

- All approval actions must be reachable via keyboard, not just mouse click (this is the highest-stakes screen in the product).
- Color is never the only signal for match quality or status — pair it with text labels/icons.
- Sufficient contrast on all status badges (drafted/approved/applied/response) in both light and dark mode.

## 6. Mobile

- The upload, dashboard, and tracker views should be usable on mobile (React Native app is a natural extension given the existing mobile stack), but the application review/approval screen benefits from a larger viewport — flag this as a "best on desktop" screen if mobile layout gets cramped, rather than compressing the side-by-side comparison into something unreadable.
