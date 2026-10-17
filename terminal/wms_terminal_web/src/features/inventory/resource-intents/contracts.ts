/** Only metadata CLAIM/ASSIGN/START. Never a quantity cancellation or task cancellation. */
export interface OriginalIntent {
 domain: "CASE" | "TASK"; task_id: number; actor: string; server: string;
 operation_id: string; action: "CLAIM" | "ASSIGN" | "START"; target: string;
 wire: string; request_sha256: string; expected_assignment_version: number;
}
export interface ControlBody { domain: "CASE" | "TASK"; task_id: number; operation_id: string; reason: string; original_wire: string }
export interface Abandoned {
 status: "ABANDONED"; operation_id: string; domain: "CASE" | "TASK"; task_id: number; actor: string;
 action: "CLAIM" | "ASSIGN" | "START"; target: string; original_operation_id: string; original_wire: string;
 original_request_sha256: string; control_request_sha256: string;
 original_expected_assignment_version: number; assignment_version_at_abandon: number; outcome_confirmed: true; stock_posted: false;
}
/** RECORDED is transport identity proof; host must apply its strict domain ACK validator before persistence/unblocking. */
export type RecoveryProof = { status: "RECORDED"; original_receipt: Record<string, unknown> } | { status: "ABANDONED"; abandonment: Abandoned };
export function record(value: unknown): value is Record<string, unknown> { return !!value && typeof value === "object" && !Array.isArray(value); }
export function canonical(value: object): string { return JSON.stringify(Object.fromEntries(Object.entries(value).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0))); }
export async function hash(wire: string): Promise<string> {
 const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(wire));
 return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("").toUpperCase();
}
export async function validateOriginal(original: OriginalIntent): Promise<void> {
 if (!["CASE", "TASK"].includes(original.domain) || !Number.isSafeInteger(original.task_id) || original.task_id < 1
  || !original.actor || !original.server || !/^[A-Za-z0-9_.:-]{1,100}$/.test(original.operation_id)
  || original.request_sha256 !== await hash(original.wire) || new TextEncoder().encode(original.wire).length > 16384)
  throw new Error("Исходный metadata intent не подтверждён. Действия заблокированы.");
 if (!Number.isSafeInteger(original.expected_assignment_version) || original.expected_assignment_version < 0
  || typeof original.target !== "string" || !original.target || original.target.length > 100) throw new Error("Некорректная версия или цель исходного запроса.");
 const body: unknown = JSON.parse(original.wire);
 if (!record(body) || body.operation_id !== original.operation_id || body.action !== original.action
  || body.expected_assignment_version !== original.expected_assignment_version
  || original.target !== (original.domain === "CASE" ? original.actor : body.target)
  || (original.domain === "CASE" ? !["CLAIM", "START"].includes(original.action) : !["ASSIGN", "START"].includes(original.action)))
  throw new Error("Исходный запрос относится к другому действию или оператору.");
 const fields = original.domain === "CASE" ? "action,equipment_id,expected_assignment_version,operation_id,reason,resource_id,resource_session_id"
  : "action,equipment_id,expected_assignment_version,expected_task_signature,operation_id,resource_id,resource_session_id,target";
 if (Object.keys(body).sort().join() !== fields || canonical(body) !== original.wire
  || typeof body.resource_session_id !== "number" || !Number.isSafeInteger(body.resource_session_id) || body.resource_session_id < 1)
  throw new Error("Исходный запрос не соответствует каноническому контракту назначения.");
 for (const field of ["resource_id", "equipment_id"]) if (body[field] !== null
  && (typeof body[field] !== "number" || !Number.isSafeInteger(body[field]) || body[field] < 1)) throw new Error("Неизвестный ресурс исходного запроса.");
 if (original.domain === "CASE" ? typeof body.reason !== "string" || Array.from(body.reason.trim()).length < 8 || Array.from(body.reason).length > 500
  : typeof body.expected_task_signature !== "string" || !/^[A-Fa-f0-9]{64}$/.test(body.expected_task_signature)) throw new Error("Основание исходного запроса повреждено.");
}
export function validateAbandoned(value: unknown, original: OriginalIntent, control?: { body: ControlBody; sha256: string }): Abandoned {
 if (!record(value) || value.status !== "ABANDONED" || value.domain !== original.domain || value.task_id !== original.task_id
  || value.actor !== original.actor || value.action !== original.action || value.target !== original.target
  || value.original_operation_id !== original.operation_id || value.original_wire !== original.wire
  || value.original_request_sha256 !== original.request_sha256 || value.original_expected_assignment_version !== original.expected_assignment_version
  || value.outcome_confirmed !== true || value.stock_posted !== false || typeof value.operation_id !== "string"
  || !/^[A-Za-z0-9_.:-]{1,100}$/.test(value.operation_id) || value.operation_id === original.operation_id
  || typeof value.control_request_sha256 !== "string" || !/^[A-F0-9]{64}$/.test(value.control_request_sha256)
  || typeof value.assignment_version_at_abandon !== "number" || !Number.isSafeInteger(value.assignment_version_at_abandon) || value.assignment_version_at_abandon < 0
  || (control && (value.operation_id !== control.body.operation_id || value.control_request_sha256 !== control.sha256)))
  throw new Error("Ответ не подтверждает прекращение именно сохранённого запроса. Исходный intent остаётся заблокирован.");
 return value as unknown as Abandoned;
}
export function validateResolution(value: unknown, original: OriginalIntent): RecoveryProof {
 if (!record(value) || value.domain !== original.domain || value.task_id !== original.task_id || value.actor !== original.actor
  || value.original_operation_id !== original.operation_id || value.original_request_sha256 !== original.request_sha256)
  throw new Error("Результат восстановления относится к другой операции.");
 if (value.status === "ABANDONED" && value.original_receipt === null) return { status: "ABANDONED", abandonment: validateAbandoned(value.abandonment, original) };
 const ack = value.original_receipt;
 if (value.status !== "RECORDED" || value.abandonment !== null || !record(ack)
  || ack.operation_id !== original.operation_id || ack.task_id !== original.task_id || ack.actor !== original.actor
  || ack.action !== original.action || ack.request_sha256 !== original.request_sha256
  || (original.domain === "TASK" && ack.target !== original.target) || ack.outcome_confirmed !== true || ack.stock_posted !== false
  || !["APPLIED", "REJECTED"].includes(String(ack.outcome))) throw new Error("Нет точной исходной квитанции. Запрос сохранён.");
 return { status: "RECORDED", original_receipt: ack };
}
