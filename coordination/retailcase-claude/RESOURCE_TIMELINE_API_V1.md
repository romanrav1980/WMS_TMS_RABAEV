# Resource timeline API v1 · 15.10.2026

GET /api/resources/timeline?warehouse_id=<int>&start_at=<ISO8601 offset>&finish_at=<ISO8601 offset>. Positive interval<=7days. Current authenticated actor; native resource_gantt_view on actual WAREHOUSE. Separate sources require resource_management_view / resource_shift_view / warehouse_task_view / transport_dispatch_view for same warehouse. No flattened new rights. Mixed-warehouse task/trip requires native view on all source members; otherwise omitted. 401/403/404/409(bound)/422(window)/503 unavailable.

Response: warehouse_id,start_at,finish_at,observed_at,access_revision,warehouse_time_zone(null if not established),resources[],events[],unscheduled[],assignments[],sources[],overlap_candidates[],overlap_limit200,time_policy,commands_executed=false.

resources: resource_id opaque stable (RESOURCE:n / EQUIPMENT:n / DOCK:warehouse:code / VEHICLE:normalizedplate),kind (CASE_PICKER/REACHTRUCK/DOCK/VEHICLE and existing other types),label,warehouse_id,source_state,availability=UNKNOWN. No current lane is not evidence of a free historical resource. Stable plate identity is available even if no unambiguous vehicle master ID. Use all returned lanes, no client permission inference.

events/unscheduled: event_id,kind,label,source,source_id,plan_start_at/plan_finish_at/fact_start_at/fact_finish_at(aware/null),time_status; optional status,trip_id,legacy_time,blocking_reason. ATTENDANCE is a planned presence interval, not task occupancy. One event has multiple assignments {event_id,resource_id}; count event once across lanes. events intersect aware window; unresolved legacy times go to unscheduled and MUST NOT be parsed as browser timezone or plotted as UTC. Legacy transport candidate window deliberately enlarged±1day; unscheduled is a candidate queue, not precise period total. AWARE_FACT can have unresolved legacy plan: show no plan bar.

sources: source_id,status READY/FORBIDDEN,permission,limit,observed_at(success only). Bound excess409 rather than falsely complete truncated result. Max500perregistry+equipment/attendance,2000tasks/transport. If whole request fails, keep prior data with prior observed time/error; do not claim fresh. No-data != zero availability.

overlap_candidates: resource_id,phase plan/fact,event_ids[2],status OVERLAP_REVIEW. Candidate for inspection, not universally illegal parallel work. Attendance excluded; one event's plan/fact not compared to itself; no open fact projected past observed_at. At most200 candidates.

First live admin read200 on warehouse1;6interval tests PASS. Limited actor/foreignwarehouse/revoke verification underway. Known gap: legacy local plans not yet supplied with verified native source timezone, and resource sessions are not an attendance-duration plan. Do not synthesize bars to conceal this. ShiftSupervisorDesk composes existing wave/execution/workload APIs; native launch source remains original.

## Дополнение CASE / проверка

source case_tasks требует case_pick_view WAREHOUSE; event kind CASE_PICK_TASK,source_id=CASE_PICK_TASK_ID,wave_id,total_lines,picked_lines. Единицы количества разных SKU не складываются. Warehouse event содержит task_source/source_task_id/wave_id при наличии исходной связи PICK_WAVE. CASE legacy finish не имеет достоверного instant: fact_finish_status=UNRESOLVED. Терминальные/после-сборочные состояния с неизвестным finish не продлевают занятость до now.

6live HTTP/native checks PASS,fixtures cleaned,stockNONE;7interval checks PASS. READY для первого UI адаптера, не означает завершения timezone/всего AK06.

## Zone/qualification/session additive fields

Resource has zone_code,qualifications,last_signal. Qualification: source_resource_id,task_type,current_by_native_policy=true,legacy_valid_from/legacy_valid_until,time_status=UNRESOLVED_SERVER_LOCAL. Existing installed native current predicate is retained; timestamp columns have no offset. null vs [] mean unavailable/not applicable vs empty current set. Qualificationbound2000.

sessions source separately requires resource_session_view WAREHOUSE,limit500. Last signal: session_id,aware_at=null,legacy_at,time_status=UNRESOLVED_SERVER_LOCAL,recent_by_native_server_clock.5min recency is not occupancy or attendance plan. No offset may be manufactured from the current server/session timezone. Availability remains UNKNOWN; limit excess409.
