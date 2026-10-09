---
name: nicora-delivery
description: Plan and deliver NICORA increments from revision-55 requirements, GAP, sprint dependencies and evidence. Use for NICORA tickets, scope and acceptance tracking.
---

# NICORA delivery

Find the TMS repository from the working directory or MCP root. Read wiki/index.md, the relevant NSxx card under wiki/requirements/nikora_delivery_v55/ and the smallest relevant business process under wiki/requirements/nikora_business_processes/. Revision 55 and subsequent owner decisions govern; historical restart_context passages are not current instructions. The old AGENTS Sprint 1 pointer is not the actual implementation baseline.

- NS01 owns stable NK-Pxx-nnn/NK-Mxx-nnn IDs. Before the registry exists cite source paragraphs, rather than inventing IDs independently.
- NS02/NS03 establish actual coverage: ready, configuration, bounded change, new function or missing evidence. Existing code/old tests do not prove revision-55 compliance.
- Use task_template.md. Define input, rights, business effect, failures, fixture target and evidence before edits. One ticket covers one scenario or two closely related scenarios, usually 3–8 implementation files.
- Respect sprints.json dependencies; shared schemas/API contracts change sequentially. Use testing_and_ai.md author/reviewer assignments. Author tests do not count as independent review; report unavailable review without claiming acceptance.
- Read wiki/runbooks/evidence_driven_process_testing.md for demonstration and wiki/runbooks/slow_sql_review.md after meaningful functional/load gates. Update focused wiki pages, index and append log for durable findings.
- Preserve unrelated edits. GitHub publication needs a fresh direct instruction; exclude SAP material. Close tickets with requirement-linked results, environment, limits and actual acceptance. Re-estimate after GAP and five accepted changes; summed historical days are not calendar commitments.

Before functional NICORA changes read wiki/architecture/nicora_modular_development_contract.md and config/architecture/nicora-policy.json. Select the module owner, public dependencies, authoritative rule implementation and transaction owner. Run python scripts/nicora_quality_gate.py before acceptance. Do not grow oversized legacy units or raise debt/thresholds to hide failure. After extraction use --tighten-baseline; this gate complements real business and independent acceptance evidence.
