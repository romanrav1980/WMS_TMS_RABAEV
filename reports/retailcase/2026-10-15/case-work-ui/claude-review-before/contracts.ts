export type Action = "CLAIM" | "START";
export interface Command {
  operation_id: string; action: Action; expected_assignment_version: number;
  resource_session_id: number; resource_id: number | null; equipment_id: number | null; reason: string;
}
export interface Context {
  task_id: number; warehouse_id: number; status: string | null; assignment_version: number;
  content_version: number | null; assigned_to: string | null; resource_id: number | null;
  resource_session_id: number | null; equipment_id: number | null;
  started_at_instant: string | null; started_shift_time_zone: string | null; current_actor: string;
}
export interface Session {
  resource_session_id: number; resource_id: number; equipment_id: number | null;
  resource_code: string; ready: boolean; reason: string | null;
}
export interface Sessions { task_id: number; warehouse_id: number; current_actor: string; action: Action; items: Session[]; command_revalidates: true }
export interface Ack extends Omit<Context, "current_actor"> {
  operation_id: string; action: Action; actor: string; outcome: "APPLIED" | "REJECTED";
  request_sha256: string; outcome_confirmed: true; may_create_corrected_operation: boolean;
  error_code: string | null; changed: boolean; stock_posted: false;
}
export interface Intent {
  server: string; actor: string; task_id: number; url: string; wire: string;
  request_sha256: string; body: Command; created_at: string;
}
export interface Journal { schema: 1; pending: Intent | null; last: { intent: Intent; ack: Ack } | null }

export function record(value: unknown): value is Record<string, unknown> { return !!value && typeof value === "object" && !Array.isArray(value); }
export function positive(value: unknown): value is number { return typeof value === "number" && Number.isSafeInteger(value) && value > 0; }
export function nonnegative(value: unknown): value is number { return typeof value === "number" && Number.isSafeInteger(value) && value >= 0; }
function nullableId(value: unknown): boolean { return value === null || positive(value); }
function nullableText(value: unknown): boolean { return value === null || typeof value === "string"; }
export function canonical(body: Command): string {
  return JSON.stringify(Object.fromEntries(Object.keys(body).sort().map(key => [key, body[key as keyof Command]])));
}
export async function sha256(wire: string): Promise<string> {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(wire));
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("").toUpperCase();
}
export function validCommand(value: unknown): value is Command {
  if (!record(value) || Object.keys(value).sort().join() !== "action,equipment_id,expected_assignment_version,operation_id,reason,resource_id,resource_session_id") return false;
  return typeof value.operation_id === "string" && /^[A-Za-z0-9_.:-]{1,100}$/.test(value.operation_id)
    && (value.action === "CLAIM" || value.action === "START") && nonnegative(value.expected_assignment_version)
    && positive(value.resource_session_id) && nullableId(value.resource_id) && nullableId(value.equipment_id)
    && typeof value.reason === "string" && Array.from(value.reason.trim()).length >= 8 && Array.from(value.reason).length <= 500;
}
export function validState(value: unknown): value is Record<string, unknown> & Omit<Context, "current_actor"> {
  if (!record(value)) return false;
  return positive(value.task_id) && positive(value.warehouse_id) && nonnegative(value.assignment_version)
    && (value.content_version === null || nonnegative(value.content_version)) && nullableText(value.status)
    && nullableText(value.assigned_to) && nullableId(value.resource_id) && nullableId(value.resource_session_id)
    && nullableId(value.equipment_id) && nullableText(value.started_shift_time_zone)
    && (value.started_at_instant === null || (typeof value.started_at_instant === "string"
      && /(?:Z|[+-]\d{2}:\d{2})$/.test(value.started_at_instant) && Number.isFinite(Date.parse(value.started_at_instant))));
}
export function validateContext(value: unknown, task: number, actor: string): Context {
  if (!validState(value) || !record(value) || value.task_id !== task || value.current_actor !== actor) throw new Error("Сервер вернул другое задание или оператора. Обновите данные.");
  return value as unknown as Context;
}
export function validateSessions(value: unknown, context: Context): Sessions {
  if (!record(value) || value.task_id !== context.task_id || value.warehouse_id !== context.warehouse_id
    || value.current_actor !== context.current_actor || value.command_revalidates !== true
    || value.action !== (context.status === "NEW" ? "CLAIM" : "START") || !Array.isArray(value.items) || value.items.length > 20) throw new Error("Не удалось подтвердить список собственных рабочих сессий.");
  const ids = new Set<number>();
  for (const item of value.items) {
    if (!record(item) || !positive(item.resource_session_id) || !positive(item.resource_id) || !nullableId(item.equipment_id)
      || typeof item.resource_code !== "string" || !item.resource_code || typeof item.ready !== "boolean"
      || !nullableText(item.reason) || ids.has(item.resource_session_id)) throw new Error("Список рабочих сессий повреждён.");
    ids.add(item.resource_session_id);
  }
  return value as unknown as Sessions;
}
export function validateAck(value: unknown, intent: Intent): Ack {
  if (!record(value) || !validState(value) || value.operation_id !== intent.body.operation_id || value.action !== intent.body.action
    || value.task_id !== intent.task_id || value.actor !== intent.actor || value.request_sha256 !== intent.request_sha256
    || value.outcome_confirmed !== true || value.stock_posted !== false || typeof value.changed !== "boolean") throw new Error("Ответ не подтверждает именно сохранённую операцию. Исходный запрос сохранён.");
  if (value.outcome === "APPLIED") {
    if (value.status === null || value.content_version === null || value.error_code !== null || value.may_create_corrected_operation !== false) throw new Error("Неполное подтверждение выполнения. Исходный запрос сохранён.");
    if (value.status !== (intent.body.action === "CLAIM" ? "ASSIGNED" : "IN_PROGRESS")
      || value.assigned_to !== intent.actor || value.resource_session_id !== intent.body.resource_session_id
      || (intent.body.resource_id !== null && value.resource_id !== intent.body.resource_id)
      || (intent.body.equipment_id !== null && value.equipment_id !== intent.body.equipment_id)
      || value.assignment_version !== intent.body.expected_assignment_version + (value.changed ? 1 : 0)
      || (intent.body.action === "START" && value.started_at_instant === null)) throw new Error("Подтверждённое назначение не совпадает с исходным действием. Запрос сохранён для проверки результата.");
  } else if (value.outcome === "REJECTED") {
    if (value.changed !== false || value.may_create_corrected_operation !== true || typeof value.error_code !== "string" || !value.error_code.trim()) throw new Error("Отказ не подтверждён. Исходный запрос сохранён.");
  } else throw new Error("Результат операции неизвестен. Исходный запрос сохранён.");
  return value as unknown as Ack;
}
