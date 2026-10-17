import { readIntent } from "./journal";
import type { JournalMeta } from "./journal";
import type { Reconciliation, RecoveryRequestBody, RecoveryAuthorizeBody, CaseCloseBody, FinishBody, OpenSessionBody, OpenStepBody } from "./contracts";

export type CommandKind = "open_session" | "open_step" | "finish" | "case_close" | "recovery_request" | "recovery_authorize";
export type CommandBody = OpenSessionBody | OpenStepBody | FinishBody | CaseCloseBody | RecoveryRequestBody | RecoveryAuthorizeBody;
export type SavedCommand = { version: 1; kind: CommandKind; target_session: string; body: CommandBody; target_reconciliation?: string; context_snapshot?: Reconciliation };
export const COMMAND_KINDS: CommandKind[] = ["open_session", "open_step", "finish", "case_close", "recovery_request", "recovery_authorize"];
const object = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const text = (v: unknown): v is string => typeof v === "string" && v.length > 0;
export function commandBodyValid(kind: CommandKind, value: unknown): value is CommandBody {
  if (!object(value)) return false;
  if (kind === "recovery_request") return text(value.operation_id) && text(value.step_id) && Number.isInteger(value.expected_content_version) && text(value.reason) && value.reason.length >= 8 && value.reason.length <= 500;
  if (kind === "recovery_authorize") return text(value.operation_id) && text(value.reason) && value.reason.length >= 8 && value.reason.length <= 500 && value.unaccepted_goods_removed === true;
  if (kind === "case_close") return text(value.operation_id) && Number.isInteger(value.expected_content_version);
  if (kind === "finish") return text(value.final_capture_key) && /^[A-F0-9]{64}$/.test(value.final_capture_key);
  if (kind === "open_session") return text(value.session_id) && text(value.device_id) && text(value.tare_capture_key)
    && text(value.scan_container) && Number.isInteger(value.task_id) && Number.isInteger(value.expected_content_version);
  return text(value.step_id) && text(value.operation_id) && Number.isInteger(value.case_line_id)
    && text(value.quantity) && /^[1-9][0-9]*$/.test(value.quantity) && text(value.scan_source_cell)
    && text(value.scan_product) && text(value.scan_container) && Number.isInteger(value.expected_content_version)
    && typeof value.consent_to_auto === "boolean";
}
export function savedCommand(kind: CommandKind, session: string, body: CommandBody, reconciliation?: string, snapshot?: Reconciliation): SavedCommand {
  if (!text(session) || !commandBodyValid(kind, body)) throw new Error("Команда не содержит исходный контекст или пригодное тело.");
  if (kind === "recovery_authorize" && !text(reconciliation)) throw new Error("В команде отсутствует исходная сверка.");
  return { version: 1, kind, target_session: session, body, ...(reconciliation ? { target_reconciliation: reconciliation, context_snapshot: snapshot } : {}) };
}
export function readSaved(kind: CommandKind, meta: JournalMeta): SavedCommand | null {
  const entry = readIntent<unknown>(kind, meta);
  if (!entry) return null;
  const value = entry.body;
  if (object(value) && value.version === 1 && value.kind === kind && text(value.target_session) && commandBodyValid(kind, value.body)) {
    if (kind === "open_session" && (value.body as OpenSessionBody).session_id !== value.target_session) throw new Error("Сохранённая сессия не совпадает с адресом команды.");
    if (kind === "recovery_authorize" && !text(value.target_reconciliation)) throw new Error("Сохранённая команда потеряла исходный адрес сверки.");
    if (kind === "recovery_authorize") {
      const context = value.context_snapshot;
      if (!object(context) || context.reconciliation_id !== value.target_reconciliation || context.session_id !== value.target_session || context.case_task_id !== meta.task_id || !text(context.step_id) || !text(context.requester_id)) throw new Error("Сохранённое подтверждение потеряло исходный контекст сверки.");
    }
    return value as SavedCommand;
  }
  // C0112 entries already contain the complete original session URL in the body.
  if (kind === "open_session" && commandBodyValid(kind, value)) {
    const body = value as OpenSessionBody;
    return savedCommand(kind, body.session_id, body);
  }
  throw new Error("Сохранённая команда не содержит доказанный исходный адрес сессии или повреждена. Требуется сверка; новый запрос заблокирован.");
}
export function pendingCommands(meta: JournalMeta): SavedCommand[] {
  return COMMAND_KINDS.flatMap(kind => { const value = readSaved(kind, meta); return value ? [value] : []; });
}



