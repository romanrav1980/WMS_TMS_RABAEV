// Поля существующих API волны/исполнения (проверены живыми ответами 15.10.2026). Отсутствие поля — «нет данных», не ноль.
export type WaveBlocker = { blocker_type: string; severity: string; status: string | null; count: number; qty?: number; message: string };
export type WaveReadiness = { pick_wave_id: number; wave_code: string; wave_status: string; is_ready: boolean; status: string;
  summary: { open_replenishment_count: number; open_staging_count: number; open_case_pick_count: number; sync_error_count: number; shortage_count: number; shortage_qty: number };
  blockers: WaveBlocker[] };
export type PickReadinessTask = { pick_task_id: number; wave_task_id: number; article: string; task_type: string; status: string; cell: string | null;
  required_base: string; covered_base: string; missing_base: string; base_uom: string | null };
export type PickReadiness = { wave_id: number; warehouse: number; status: string; released_at: string | null; released_by: string | null;
  release_operation_id: string | null; ready: boolean; tasks: PickReadinessTask[]; open_replenishments: unknown[] };
// APPROVED несёт утверждённые моменты с поясом (RRL_WAVE_TIME_API.context); без утверждения сроков нет.
export type TimeContext = { wave_id: number; warehouse_id: number; wave_status: string; version: number; plan_status: string;
  time_zone?: string; start_at?: string; finish_at?: string };
export type ReplenishmentRow = { pick_wave_replenish_task_id: number; pick_wave_id: number; articul: string; target_cell_code: string | null; source_cell_code: string | null;
  status: string; wait_reason: string | null; planned_base: string | null; demand_base: string | null; confirmed_base: string | null; demand_remaining_base: string | null };
export type CaseShort = { case_pick_short_id: number; pick_wave_id: number; case_pick_task_id: number; articul: string; cell_code: string | null;
  short_qty: number; reason_code: string | null; status: string; created_at: string | null };

/** Детали волны из пяти независимых чтений; ошибка одного не скрывает остальные. */
export type WaveDetail = {
  wave_id: number;
  observed_at?: string;  // часы сервера снимка обзора этой волны (C-0159): сроки сравниваются с ними, не с браузером
  readiness: { data: WaveReadiness | null; error: string };
  pick: { data: PickReadiness | null; error: string };
  time: { data: TimeContext | null; error: string };
  replenishment: { data: ReplenishmentRow[] | null; error: string };
};

/** Риск — только с доказуемым основанием из источника. Проценты и сроки не рассчитываются (нормативы не утверждены). */
export type Risk = { key: string; wave_id: number | null; task_id: number | null; basis: string; source: string;
  impact: string; owner: string | null; action: { label: string; page: string; params?: Record<string, string | number> } | null; severity: "BLOCKER" | "WARNING" };
