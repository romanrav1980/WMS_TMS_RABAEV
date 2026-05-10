# Branch: External Integrations

## Role

This branch covers data exchange with systems outside the WMS core.

It includes historical ERP integration with `SUPERMAG` / `Sfera` and other non-core import/export boundaries.

SAP/SAP_INTEGRATION projects are intentionally excluded from this GitHub publication.

## What Lives Here

Integration concerns belong here:

- external ERP source contracts
- staging tables
- file import/export formats
- mapping external fields into WMS concepts
- integration runbooks and operational evidence

## Main Current Locations

- [`../../EXTERNAL_INTEGRATION.MD`](../../EXTERNAL_INTEGRATION.MD)
- [`../../SQL/SUPERMAG/`](../../SQL/SUPERMAG/)
- [`../../imports/`](../../imports/)

## Current Integration Lines

1. `SUPERMAG` / `Sfera`
   - external ERP/source schema
   - source of articles, documents, document lines, palletization, store/client data

## What It Depends On

- [[oracle_plsql_core]] for staging/current tables and WMS-side consumption.
- external system availability and agreed field contracts.

## Boundaries

- Do not put WMS core business rules inside integration scripts unless the rule is purely a mapping rule.
- Do not treat `SUPERMAG` objects as owned WMS tables.
- Do not publish SAP/SAP_INTEGRATION project files or runbooks to GitHub.

## Primary Sources

- [`../../EXTERNAL_INTEGRATION.MD`](../../EXTERNAL_INTEGRATION.MD)
- [`../concepts/external_integration_supermag.md`](../concepts/external_integration_supermag.md)
