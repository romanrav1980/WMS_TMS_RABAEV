// Поля существующих API (проверены живыми ответами 15.10.2026). Отсутствующее поле — «нет данных», не ноль.
export type Trip = {
  ID: number; TRANSPORT: string | null; TRANSTYPE: string | null; CONDITION: string | null; SHIPMENT_DATE: string | null; SHIPMENT_TIME: string | null;
  VODITEL_ID: number | null; VODITEL_NAME: string | null; VODITEL_TEL: string | null; TK_NAME: string | null; DOCK: string | null;
  PALLET_COUNT: number | null; ST_COUNT: number | null; VOLUME_M3: number | null; READY_PERC: number | null; UNREADY_COUNT: number | null;
};
export type GanttOperation = { op_id: number; tt_id: number; operation_code: string; ord: number; duration_min: number;
  plan_start: string | null; plan_end: string | null; fact_start: string | null; fact_end: string | null; delta_min: number | null; note: string | null };
export type GanttVehicle = { vehicle_id: number | null; vehicle_num: string; vehicle_type: string | null; operations: GanttOperation[] };
export type Wave = { pick_wave_id: number; wave_code: string; ware_id: number; ware_name: string; status: string; wave_kind: string;
  planned_start_at: string | null; planned_finish_at: string | null; order_count: number; task_count: number; launched_at: string | null };
export type Session = { session_id: number; resource_code: string; resource_name: string; resource_type: string; equipment_code: string | null;
  operator_user_id: string | null; status: string; current_task_id: number | null; last_heartbeat_at: string | null; zone_code: string | null; logout_at: string | null };
export type CaseTask = { case_pick_task_id: number; pick_wave_id: number; wave_code: string; customer_name: string; sscc: string; pallet_type_name: string;
  status: string; assigned_to: string | null; zone_code: string | null; total_lines: number; picked_lines: number; task_progress_pct: number;
  route_pallet_count: number; route_done_pallet_count: number; blocking_reason: string | null; blocking_cell_code: string | null; last_action: string | null; last_event_at: string | null };
export type SupplyOrder = { order_id: string; order_number: string; ware_id: number; condition: number; date_of_accept: string | null };

export type Selection = { kind: "trip"; id: number } | { kind: "wave"; id: number } | { kind: "session"; id: number } | null;

/** Цвет состояния рейса по фактическим значениям CONDITION; неизвестное показывается как есть, нейтрально. */
export function tripTone(condition: string | null): "plan" | "ship" | "closed" | "other" {
  if (condition === "Спланирован") return "plan";
  if (condition === "Отгружен") return "ship";
  if (condition === "Закрыт") return "closed";
  return "other";
}
