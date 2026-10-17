import { assertPhysicalClear } from "./physicalJournal";
import { assemblyRequest } from "./api";
import { originalMatches, readAbandonment } from "./abandonment";
import { clearIntent, saveIntent } from "./journal";
import type { JournalMeta } from "./journal";
import { pendingCommands, readSaved, savedCommand } from "./savedCommands";
import type { CommandBody, CommandKind, SavedCommand } from "./savedCommands";
import type { Reconciliation, AssemblyCredentials, AssemblySession, AssemblyStep, CaseCloseAck, CaseCloseBody, FinishBody, OpenSessionBody, OpenStepBody } from "./contracts";
export { JournalDamagedError, clearIntent, readIntent } from "./journal";

function identity(condition: boolean): asserts condition {
  if (!condition) throw new Error("Ответ сервера не соответствует исходной команде. Результат требует сверки.");
}
function scope(credentials: AssemblyCredentials, meta: JournalMeta) {
  identity(meta.server === location.origin && meta.actor === credentials.username);
}
export function validSession(value: unknown, credentials: AssemblyCredentials, session: string, task?: number): AssemblySession {
  const s = value as AssemblySession;
  identity(!!s && s.session_id === session && s.operator_id === credentials.username && (task === undefined || s.task_id === task)
    && ["OPEN", "BLOCKED", "FINALIZED"].includes(s.state) && Array.isArray(s.steps) && Number.isInteger(s.content_version));
  if (s.reconciliation) {
    identity(s.reconciliation.session_id === session && s.reconciliation.case_task_id === s.task_id);
    if (["REQUESTED", "AUTHORIZED"].includes(s.reconciliation.state)) identity(s.state === "BLOCKED" && s.reconciliation.expected_content_version === s.content_version);
  }
  for (const step of s.steps) validStep(step, step?.step_id, session);
  return s;
}
export function validStep(value: unknown, step: string, session?: string): AssemblyStep {
  const s = value as AssemblyStep;
  identity(!!s && s.step_id === step && typeof s.session_id === "string" && (session === undefined || s.session_id === session)
    && ["WAITING_BEFORE", "ARMED", "READY", "APPLIED", "DISCREPANCY", "CANCELLED"].includes(s.state) && typeof s.operation_id === "string");
  return s;
}
export async function readSession(credentials: AssemblyCredentials, sessionId: string, signal?: AbortSignal) {
  return validSession(await assemblyRequest<unknown>(`/sessions/${encodeURIComponent(sessionId)}`, credentials, undefined, signal), credentials, sessionId);
}
export async function readStep(credentials: AssemblyCredentials, stepId: string, signal?: AbortSignal) {
  return validStep(await assemblyRequest<unknown>(`/steps/${encodeURIComponent(stepId)}`, credentials, undefined, signal), stepId);
}
export async function withJournal<T>(kind: CommandKind, credentials: AssemblyCredentials, meta: JournalMeta,
  target: string, body: CommandBody, send: () => Promise<T>, reconciliation?: string, snapshot?: Reconciliation): Promise<T> {
  scope(credentials, meta);
  if (!navigator.locks) throw new Error("Браузер не поддерживает безопасную блокировку журнала между вкладками. Отправка заблокирована.");
  return navigator.locks.request(`assembly-command:${meta.server}:${meta.actor}:${meta.task_id}`, async () => {
    assertPhysicalClear(meta);
    const wanted = savedCommand(kind, target, body, reconciliation, snapshot), existing = readSaved(kind, meta);
    const control = readAbandonment(meta);
    if (control && !originalMatches(control, wanted)) throw new Error("Есть незавершённая отмена. Разрешены только исходный точный повтор или сверка этой отмены.");
    if (existing && JSON.stringify(existing) !== JSON.stringify(wanted)) throw new Error("Есть незавершённая команда. Сначала восстановите исходную отправку без изменений.");
    if (!existing && !control && pendingCommands(meta).length) throw new Error("Есть другая незавершённая команда этого задания. Сначала восстановите её исходную отправку.");
    if (!existing) saveIntent(kind, meta, wanted);
    const result = await send(); // Invalid identity/ACK never clears the journal.
    clearIntent(kind, meta);
    if (control) clearIntent("abandonment", meta); // Original successful ACK resolves creation; this is not ABANDONED.
    return result;
  });
}
export function openSession(credentials: AssemblyCredentials, meta: JournalMeta, body: OpenSessionBody): Promise<AssemblySession> {
  identity(body.task_id === meta.task_id);
  return withJournal("open_session", credentials, meta, body.session_id, body, async () => {
    const s = validSession(await assemblyRequest<unknown>("/sessions", credentials, body), credentials, body.session_id, meta.task_id);
    identity(s.device_id === body.device_id && s.scan_container === body.scan_container && s.tare_capture_key === body.tare_capture_key);
    return s;
  });
}
export function openStep(credentials: AssemblyCredentials, meta: JournalMeta, sessionId: string, body: OpenStepBody): Promise<AssemblyStep> {
  return withJournal("open_step", credentials, meta, sessionId, body, async () => {
    const s = validStep(await assemblyRequest<unknown>(`/sessions/${encodeURIComponent(sessionId)}/steps`, credentials, body), body.step_id, sessionId);
    identity(s.operation_id === body.operation_id && s.case_line_id === body.case_line_id && s.quantity === body.quantity);
    return s;
  });
}
export function finishSession(credentials: AssemblyCredentials, meta: JournalMeta, sessionId: string, body: FinishBody): Promise<AssemblySession> {
  return withJournal("finish", credentials, meta, sessionId, body, async () => {
    const s = validSession(await assemblyRequest<unknown>(`/sessions/${encodeURIComponent(sessionId)}/finish`, credentials, body), credentials, sessionId, meta.task_id);
    identity(s.state === "FINALIZED"); return s;
  });
}
export async function markPlaced(credentials: AssemblyCredentials, stepId: string, sessionId: string): Promise<AssemblyStep> {
  const result = await assemblyRequest<{ step?: unknown }>(`/steps/${encodeURIComponent(stepId)}/placed`, credentials, {});
  return validStep(result?.step, stepId, sessionId);
}
export function closeCaseSession(credentials: AssemblyCredentials, meta: JournalMeta, sessionId: string, body: CaseCloseBody): Promise<CaseCloseAck> {
  return withJournal("case_close", credentials, meta, sessionId, body, async () => {
    const result = await assemblyRequest<CaseCloseAck>(`/sessions/${encodeURIComponent(sessionId)}/close`, credentials, body);
    identity(!!result && result.session_id === sessionId && result.case_pick_task_id === meta.task_id
      && result.operation_id === body.operation_id && result.physical_stock_changed === false
      && result.content_version === body.expected_content_version
      && ["WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"].includes(result.status));
    return result;
  });
}
export async function retrySaved(credentials: AssemblyCredentials, meta: JournalMeta, command: SavedCommand): Promise<AssemblySession> {
  if (command.kind === "open_session") return openSession(credentials, meta, command.body as OpenSessionBody);
  if (command.kind === "finish") return finishSession(credentials, meta, command.target_session, command.body as FinishBody);
  if (command.kind === "case_close") await closeCaseSession(credentials, meta, command.target_session, command.body as CaseCloseBody);
  else await openStep(credentials, meta, command.target_session, command.body as OpenStepBody);
  const session = await readSession(credentials, command.target_session);
  return validSession(session, credentials, command.target_session, meta.task_id);
}








