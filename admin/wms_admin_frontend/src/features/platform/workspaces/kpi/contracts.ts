export type Rates = Record<"lines_per_assembly_hour" | "boxes_per_assembly_hour" | "lines_per_shift_hour" | "boxes_per_shift_hour", string | null>;
export type PickFact = { operation_id: string; actor: string; at: string; task_id: number; line_id: number; article: string; base_uom: string; previous: string; cumulative: string; delta: string; boxes: string | null; pieces: string | null; packaging_reason: string | null };
export type QualityQuantity = { article: string; base_uom: string; quantity: string };
export type LineCompletion = { operation_id: string; task_id: number; line_id: number; actor: string; at: string; approved_at: string | null; kind: "FULL" | "ACCEPTED_SHORT"; quantity: string; shortage_quantity: string };
export type PickerRow = { operator_id: string; completed_lines: number; boxes: string | null; pieces: string | null; box_reasons: string[]; registered_assembly_hours: string | null; registered_shift_hours: string | null; rates: Rates; facts: PickFact[]; uncovered_work_operations: string[]; uncovered_shift_operations: string[]; shortage_completed_lines: number; shortage_quantities: QualityQuantity[]; return_events: number; returned_quantities: QualityQuantity[]; line_completions: LineCompletion[]; observed_pick_coverage: {total:number; covered_work:number; covered_shift:number; complete_for_observed_picks:boolean} };
export type PickerKpi = { warehouse_id: number; formula_version: "PICKER_KPI_V2"; scope: "REGISTERED_OBSERVATIONS"; work_coverage_certified: false; operators: PickerRow[]; source_limitations: string[]; as_of: string };
export type DeliveryRow = { load_operation_id: string; store_address: string; trip_id: number; load_status: string; window_start: string | null; window_finish: string | null; arrived_at: string | null; on_time_state: "ON_TIME" | "EARLY" | "LATE" | "NO_ARRIVAL" | "NO_PLAN"; receipt_operation_id: string | null; receipt_mode: string | null; received_at: string | null; full_state: "FULL" | "WITH_ISSUES" | "PENDING"; line_count: number; issue_count: number };
export type DeliveryKpi = { warehouse_id: number; formula_version: "DELIVERY_KPI_V1"; deliveries: DeliveryRow[]; timing: Record<"ON_TIME" | "EARLY" | "LATE" | "NO_ARRIVAL" | "NO_PLAN" | "observed_planned", number> & { on_time_percent_of_observed: string | null }; receipt: Record<"FULL" | "WITH_ISSUES" | "PENDING" | "received", number> & { full_percent_of_received: string | null }; source_limitations: string[] };

function record(value: unknown): asserts value is Record<string, unknown> { if (!value || typeof value !== "object" || Array.isArray(value)) throw Error("Объект KPI не получен"); }
function text(value: unknown): asserts value is string { if (typeof value !== "string") throw Error("Неверное текстовое поле KPI"); }
function count(value: unknown): asserts value is number { if (typeof value !== "number" || !Number.isSafeInteger(value) || value < 0) throw Error("Неверный счётчик KPI"); }
function decimal(value: unknown): void { if (value !== null && (typeof value !== "string" || !/^\d+(\.\d+)?([eE][+-]?\d+)?$/.test(value))) throw Error("Неверное числовое поле KPI"); }
function moment(value: unknown, nullable = false): void { if (nullable && value === null) return; if (typeof value !== "string" || !/(Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))) throw Error("Время KPI не подтверждено с часовым поясом"); }
function strings(value: unknown): void { if (!Array.isArray(value) || value.some(item => typeof item !== "string")) throw Error("Неверные сведения об источнике KPI"); }
function array(value: unknown, max: number): asserts value is unknown[] { if (!Array.isArray(value) || value.length > max) throw Error("Превышен размер ответа KPI"); }

export function parsePicker(value: unknown, warehouse: number): PickerKpi {
 record(value);
 if (value.warehouse_id !== warehouse || value.formula_version !== "PICKER_KPI_V2" || value.scope !== "REGISTERED_OBSERVATIONS" || value.work_coverage_certified !== false) throw Error("Неизвестная версия или область KPI выработки");
 array(value.operators, 500); strings(value.source_limitations); moment(value.as_of);
 let facts = 0;
 for (const row of value.operators) {
  record(row); text(row.operator_id); count(row.completed_lines); decimal(row.boxes); decimal(row.registered_assembly_hours); decimal(row.registered_shift_hours); strings(row.box_reasons); strings(row.uncovered_work_operations); strings(row.uncovered_shift_operations); record(row.rates);
  decimal(row.pieces); count(row.shortage_completed_lines); count(row.return_events);
  for (const quantities of [row.shortage_quantities,row.returned_quantities]) {
   array(quantities,5000);for(const item of quantities){record(item);text(item.article);text(item.base_uom);decimal(item.quantity);}
  }
  array(row.line_completions,5000);
  for(const item of row.line_completions){record(item);text(item.operation_id);text(item.actor);count(item.task_id);count(item.line_id);moment(item.at);moment(item.approved_at,true);decimal(item.quantity);decimal(item.shortage_quantity);if(!["FULL","ACCEPTED_SHORT"].includes(String(item.kind)))throw Error("Неизвестный факт завершения строки");}
  record(row.observed_pick_coverage);for(const key of ["total","covered_work","covered_shift"])count(row.observed_pick_coverage[key]);if(typeof row.observed_pick_coverage.complete_for_observed_picks!=="boolean")throw Error("Неверная полнота зарегистрированных отборов");
  for (const key of ["lines_per_assembly_hour", "boxes_per_assembly_hour", "lines_per_shift_hour", "boxes_per_shift_hour"]) decimal(row.rates[key]);
  array(row.facts, 5000); facts += row.facts.length; if (facts > 5000) throw Error("Превышен размер фактов KPI");
  for (const fact of row.facts) {
   record(fact); for (const key of ["operation_id", "actor", "article", "base_uom"]) text(fact[key]); count(fact.task_id); count(fact.line_id); moment(fact.at);
   for (const key of ["previous", "cumulative", "delta", "boxes", "pieces"]) decimal(fact[key]); if (fact.packaging_reason !== null) text(fact.packaging_reason);
  }
 }
 return value as unknown as PickerKpi;
}

export function parseDelivery(value: unknown, warehouse: number): DeliveryKpi {
 record(value);
 if (value.warehouse_id !== warehouse || value.formula_version !== "DELIVERY_KPI_V1") throw Error("Неизвестная версия или область KPI доставки");
 array(value.deliveries, 500); strings(value.source_limitations); record(value.timing); record(value.receipt);
 for (const key of ["ON_TIME", "EARLY", "LATE", "NO_ARRIVAL", "NO_PLAN", "observed_planned"]) count(value.timing[key]);
 for (const key of ["FULL", "WITH_ISSUES", "PENDING", "received"]) count(value.receipt[key]);
 decimal(value.timing.on_time_percent_of_observed); decimal(value.receipt.full_percent_of_received);
 for (const row of value.deliveries) {
  record(row); for (const key of ["load_operation_id", "store_address", "load_status"]) text(row[key]); count(row.trip_id); count(row.line_count); count(row.issue_count);
  for (const key of ["window_start", "window_finish", "arrived_at", "received_at"]) moment(row[key], true);
  for (const key of ["receipt_operation_id", "receipt_mode"]) if (row[key] !== null) text(row[key]);
  if (!["ON_TIME", "EARLY", "LATE", "NO_ARRIVAL", "NO_PLAN"].includes(String(row.on_time_state)) || !["FULL", "WITH_ISSUES", "PENDING"].includes(String(row.full_state))) throw Error("Неизвестное состояние доставки");
 }
 return value as unknown as DeliveryKpi;
}
