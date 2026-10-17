import { assemblyRequest } from "./api";
import { readSession, validSession, withJournal } from "./commands";
import type { JournalMeta } from "./journal";
import { readSaved } from "./savedCommands";
import type { SavedCommand } from "./savedCommands";
import type { AssemblyCredentials, Reconciliation, RecoveryRequestBody, RecoveryAuthorizeBody } from "./contracts";
function assert(value: boolean): asserts value { if (!value) throw new Error("Ответ не подтверждает исходную сверку. Команда сохранена для разбора."); }
export function validReconciliation(value: unknown, id: string): Reconciliation {
  const r = value as Reconciliation;
  assert(!!r && r.reconciliation_id === id && typeof r.session_id === "string" && !!r.session_id && typeof r.step_id === "string"
    && Number.isInteger(r.case_task_id) && r.case_task_id > 0 && ["REQUESTED","AUTHORIZED","COMPLETED","DISCREPANCY"].includes(r.state)
    && typeof r.requester_id === "string" && !!r.requester_id && (r.controller_id === null || typeof r.controller_id === "string")
    && typeof r.expected_weight_kg === "string" && Number.isInteger(r.expected_content_version));
  return r;
}
export async function readReconciliation(credentials: AssemblyCredentials, id: string, signal?: AbortSignal): Promise<Reconciliation> {
  return validReconciliation(await assemblyRequest<unknown>(`/reconciliations/${encodeURIComponent(id)}`, credentials, undefined, signal), id);
}
export function requestReconciliation(credentials: AssemblyCredentials, meta: JournalMeta, session: string, body: RecoveryRequestBody) {
  return withJournal("recovery_request", credentials, meta, session, body, async () => {
    const r = validReconciliation(await assemblyRequest<unknown>(`/sessions/${encodeURIComponent(session)}/reconciliations`, credentials, body), body.operation_id);
    assert(r.session_id === session && r.step_id === body.step_id && r.case_task_id === meta.task_id && r.requester_id === credentials.username
      && r.state === "REQUESTED" && r.controller_id === null && r.expected_content_version === body.expected_content_version);
    return r;
  });
}
export function authorizeReconciliation(credentials: AssemblyCredentials, meta: JournalMeta, current: Reconciliation, body: RecoveryAuthorizeBody) {
  assert(credentials.username !== current.requester_id && current.case_task_id === meta.task_id);
  const prior = readSaved("recovery_authorize", meta);
  const snapshot = prior?.context_snapshot ?? current;
  return withJournal("recovery_authorize", credentials, meta, current.session_id, body, async () => {
    const r = validReconciliation(await assemblyRequest<unknown>(`/reconciliations/${encodeURIComponent(current.reconciliation_id)}/authorize`, credentials, body), current.reconciliation_id);
    assert(r.session_id === current.session_id && r.step_id === current.step_id && r.case_task_id === current.case_task_id
      && r.requester_id === current.requester_id && r.controller_id === credentials.username && r.state === "AUTHORIZED" && r.operation_id === body.operation_id);
    return r;
  }, current.reconciliation_id, snapshot);
}
export async function retryRecoveryRequest(credentials: AssemblyCredentials, meta: JournalMeta, command: SavedCommand) {
  assert(command.kind === "recovery_request");
  await requestReconciliation(credentials, meta, command.target_session, command.body as RecoveryRequestBody);
  return validSession(await readSession(credentials, command.target_session), credentials, command.target_session, meta.task_id);
}


