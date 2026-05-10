# TMS Agent Onramp

This repository uses a Karpathy-style LLM wiki pattern.

Before making non-trivial project decisions, start here:

1. Read [`wiki/index.md`](wiki/index.md).
2. Open the smallest relevant synthesis pages.
3. Drill into raw project sources only when the wiki does not settle the question.
4. After learning something durable, update the relevant wiki page and append [`wiki/log.md`](wiki/log.md).

## Three Layers

1. Raw sources
   - Existing code, SQL, project docs, logs, screenshots, exports, and files under `wiki-raw/`.
   - Treat these as evidence. Do not rewrite them as part of wiki maintenance.

2. Wiki
   - Files under `wiki/`.
   - These pages are maintained synthesis: project maps, runbooks, decisions, incidents, and source catalogs.
   - Prefer `[[wikilinks]]` for conceptual links and normal markdown links for file paths.

3. Schema
   - This file and [`wiki/WIKI_SCHEMA.md`](wiki/WIKI_SCHEMA.md).
   - These define how future sessions should ingest, query, and lint the wiki.

## Maintenance Rules

- Raw sources are source-of-truth evidence; wiki pages are summaries and cross-source synthesis.
- Do not silently merge contradictions. Record them on the relevant page.
- Keep pages small enough to scan in a fresh session.
- Use stable names: `subprojects/`, `components/`, `concepts/`, `runbooks/`, `incidents/`, `sources/`.
- Every meaningful wiki change updates `wiki/index.md`.
- Every meaningful wiki change appends `wiki/log.md`.
- Do not publish SAP/SAP_INTEGRATION projects to GitHub. Treat any local SAP material as out of scope for this repository publication unless the user explicitly changes that rule.
