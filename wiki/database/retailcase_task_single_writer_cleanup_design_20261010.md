# NI03.2 / NI08.1 — единственное завершение и SAP metadata scope,146

Reuse144 native task access. Receiving.replan/cancel use their existing metadata transaction/document-task locks; native current actor scope before replay/document lookup and again after locked task identity. PermissionError becomes403 at old API boundaries. No nested warehouse-task UOW introduced.

Remove WarehouseTaskService._complete_task_locked PREPARED branch and exclusively-called Python scan/resource fallback helpers. All live complete callers already use inventory public native command. Native scan/qty/resource/splitting logic remains authoritative. Preserve live assign/start/cancel sync methods and original domain sync engine.

Replan identifier accepts legacy/internal up to150 characters and exact stored identifier first; SSCC normalization only when exact comparison fails. No SSCC-only field imposed on pallets. Original metadata cancellation/outbox effect retained, no stock writer added.
