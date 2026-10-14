# NI08.1: непрерывное вождение между рейсами

636–638 extends the existing approved driver-day read and existing evaluate_driver_rest rule. No parallel statutory rule engine, no Oracle DDL or quantity writes.

Previously driver-day summed total driving across trips, while continuous driving was evaluated only inside one trip. The same driver's approved operations now form one chronological chain. A new trip, unloading/work, or midnight does not reset observed continuity. Only the existing explicit REST of at least15 minutes resets the existing120-minute project parameter. Day540-minute budget remains the previous clipped planned_day_drive calculation.

Observed operations before local midnight are retained as known carry-in; operation ends beyond day finish are clipped so tomorrow's driving cannot cause today's false violation. Duplicate operation IDs are not counted twice. Missing/invalid intervals, gaps/overlaps and unproven driver changes stay unknown. Initial duty/outside-WMS history and applicable legal rules remain unverified, never converted into admission by this calculation.

Existing driver-day result includes continuity per day, existing Gantt card displays limits/violations/gaps. Shared coordination emits specific chain violation code/operation/day alongside the separate daily budget blocker; incomplete recorded chain marks recorded_plan_coverage_complete=false. Current actor/WARE/approved source/version and one READ ONLY cursor retain their previous boundaries.

637 targeted domain case PASS: two trips90+40 separated by unloading10 produce130; explicit REST15 resets; midnight120+30 produces150; a22:00–00:30 interval is120 for preceding day; duplicate ID unchanged. No real driver duty or legal compliance claimed. Architecture676/0cycles/76debt and changed frontend TypeScript PASS. Existing queries unchanged/bounded7day200trips2000operations; no extra per-operation SQL introduced. Previous driver-source SQL13.891ms decision remains bounded owner/date read; live expanded preview case and SQL profiling remain pending, not claimed.
