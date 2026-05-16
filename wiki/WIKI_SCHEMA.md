# Wiki Schema

This is the root knowledge layer for the TMS repository. It follows the Karpathy LLM wiki pattern:

- raw sources stay untouched
- the wiki stores maintained synthesis
- schema files teach future agents how to maintain the system

## Scope

The root wiki covers the whole repository:

- legacy WinForms WMS/TMS application
- Oracle schema reconstruction
- external ERP integration with `SUPERMAG` / `Sfera`
- operational runbooks and project decisions

SAP/SAP_INTEGRATION projects are intentionally out of scope for GitHub publication unless the user explicitly changes that rule.

## Directory Layout

- [`index.md`](index.md): table of contents and first entry point
- [`overview.md`](overview.md): project map and current boundaries
- [`log.md`](log.md): append-only wiki maintenance log
- `branches/`: four top-level architectural branches of the project
- `subprojects/`: one page per major project area
- `database/`: local wiki mirror of the Oracle schema and Oracle change protocol
- `requirements/`: technical assignments and durable product requirements
- `roadmap/`: strategic and tactical implementation plans
- `../db/migrations/`: versioned Oracle migration scripts with apply, rollback, and verify files
- `components/`: pages for concrete code or SQL modules
- `concepts/`: cross-cutting architecture and data concepts
- `runbooks/`: operator and developer procedures
- `incidents/`: regressions and failure analyses
- `sources/`: source catalogs and provenance notes

## Logical Branches

The root project is divided into four logical branches:

1. Oracle / PL/SQL Core
2. C# Desktop Client
3. Terminal Contour
4. External Integrations

Every major source file, runbook, or incident should be associated with one of these branches unless it is purely wiki maintenance.

## Page Contract

Each synthesis page should answer:

- what this thing is
- why it matters
- where the evidence lives
- what can safely change
- what must not be broken

## Workflows

### Ingest

1. Read new source material.
2. Update or create the relevant synthesis pages.
3. Add source links to [`sources/index.md`](sources/index.md).
4. Update [`index.md`](index.md) when navigation changes.
5. Append [`log.md`](log.md).

### Query

1. Read [`index.md`](index.md).
2. Open the minimum relevant wiki pages.
3. Use raw sources only to verify or fill gaps.
4. If the answer creates durable knowledge, file it back into the wiki.

### Lint

Periodically check for:

- stale claims
- missing source links
- orphan pages
- duplicated synthesis
- contradictions between old manifests and current code
- pages that should be marked superseded

## Link Style

- Use `[[wikilinks]]` for conceptual links inside prose.
- Use markdown links for actual repository paths.
- Use relative links when linking wiki pages.
- Use explicit source links for evidence.
