---
name: nicora-operations
description: Prepare NICORA environment passports, reproducible deployment, load capacity, monitoring, recovery and pilots. Use for operational readiness, release gates and backup restoration.
---

# NICORA operations

Read wiki/index.md, wiki/architecture/nikora_technology_stack_20261007.md, procurement decisions and relevant NS00/NS06/NS11/NS12/NS61–NS67 cards. Use repository runbooks and root scripts for Windows development.

- Inventory versions, hardware, Oracle target and runtime processes before changing configuration. MCP smoke is not NS00 isolation or application readiness.
- Reuse chosen Linux API/background deployment shape, pin tested dependencies and capture build provenance. New Kubernetes, Kafka or second operational DB require measured need.
- Separate tms-docker-routing availability from OSRM/Valhalla health: a responding MCP can report stopped services. Route acceptance verifies payload semantics as well as HTTP status.
- Bound API workers, per-process pools, total connections, batches and retention. Measure waits, locks, commit delays, event-loop stalls and queue drain.
- Five-million-operation and peak figures remain preliminary until approved. Short independent INSERT tests are not mixed warehouse-shift evidence. Isolate load generation and Oracle/API from local-inference contention; record hardware/history/mix and p95/p99 with correctness.
- Agree RPO/RTO and actually restore Oracle plus linked files/photos. Verify interruption without double effects. Code rollback does not reverse committed warehouse facts.
- NICORA purchases production Oracle licensing before launch; dev 19c Enterprise Edition does not establish licensed production options. This skill authorizes no purchases.
- NS50 is a rehearsal, NS63 uses actual equipment, NS64/NS65 are observed pilots. Live-operation authorization and site limitations remain explicit; tooling setup does not authorize rollout.
- Preserve sandbox protection. For setup refresh errors use the diagnostic owner-repair account in wiki/runbooks/tms_mcp_servers.md rather than disabling protection.

Use versioned configuration, evidence and mandatory slow-SQL decisions; release against actual accepted gates.
