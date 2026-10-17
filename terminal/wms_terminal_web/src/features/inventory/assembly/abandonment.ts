import { assemblyRequest } from "./api";
import { clearIntent, readIntent, saveIntent } from "./journal";
import type { JournalMeta } from "./journal";
import { commandBodyValid, readSaved } from "./savedCommands";
import type { SavedCommand } from "./savedCommands";
import type { AssemblyCredentials, OpenSessionBody, OpenStepBody } from "./contracts";

type AbandonableKind = "open_session" | "open_step";
export type AbandonableCommand = SavedCommand & { kind: AbandonableKind };
export type AbandonBody = { operation_id: string; reason: string } & (
  { kind: "OPEN_SESSION"; original: OpenSessionBody } |
  { kind: "OPEN_STEP"; session_id: string; original: OpenStepBody });
export type AbandonControl = { version: 1; original: AbandonableCommand; request: AbandonBody };
const CONTROL = "abandonment";
const record = (value: unknown): value is Record<string, unknown> => !!value && typeof value === "object" && !Array.isArray(value);
function requireMatch(value: boolean): asserts value { if (!value) throw new Error("Отмена не подтверждает исходное намерение. Обе записи сохранены для сверки."); }
function ordered(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(ordered);
  if (record(value)) return Object.fromEntries(Object.keys(value).sort().map(key => [key, ordered(value[key])]));
  return value;
}
const same = (left: unknown, right: unknown) => JSON.stringify(ordered(left)) === JSON.stringify(ordered(right));
export function canAbandon(command: SavedCommand): command is AbandonableCommand {
  return command.kind === "open_session" || command.kind === "open_step";
}
export function readAbandonment(meta: JournalMeta): AbandonControl | null {
  const entry = readIntent<unknown>(CONTROL, meta);
  if (!entry) return null;
  const value = entry.body;
  requireMatch(record(value) && value.version === 1 && record(value.original) && record(value.request));
  const original = value.original as unknown as AbandonableCommand, request = value.request as unknown as AbandonBody;
  requireMatch(canAbandon(original) && original.version === 1 && typeof original.target_session === "string" && !!original.target_session
    && commandBodyValid(original.kind, original.body));
  requireMatch(request.kind === (original.kind === "open_session" ? "OPEN_SESSION" : "OPEN_STEP")
    && typeof request.operation_id === "string" && /^[A-Za-z0-9_.:-]{1,100}$/.test(request.operation_id)
    && typeof request.reason === "string" && request.reason.length >= 8 && request.reason.length <= 500 && same(request.original, original.body));
  if (request.kind === "OPEN_SESSION") requireMatch(request.original.task_id === meta.task_id && request.original.session_id === original.target_session);
  else requireMatch(request.session_id === original.target_session);
  const current = readSaved(original.kind, meta);
  requireMatch(current === null || same(current, original)); // Null is allowed only for crash after the original removal.
  return value as unknown as AbandonControl;
}
export function originalMatches(control: AbandonControl, command: SavedCommand): boolean { return same(control.original, command); }
export function createAbandonment(command: AbandonableCommand, reason: string): AbandonControl {
  requireMatch(reason.trim().length >= 8 && reason.trim().length <= 500);
  const common = { operation_id: `ASM.ABANDON:${crypto.randomUUID()}`, reason: reason.trim() };
  const request: AbandonBody = command.kind === "open_session"
    ? { ...common, kind: "OPEN_SESSION", original: command.body as OpenSessionBody }
    : { ...common, kind: "OPEN_STEP", session_id: command.target_session, original: command.body as OpenStepBody };
  return { version: 1, original: command, request };
}
export function validateAbandoned(value: unknown, control: AbandonControl, meta: JournalMeta): void {
  requireMatch(record(value));
  const original = control.original, request = control.request;
  requireMatch(value.operation_id === request.operation_id && value.status === "ABANDONED" && value.kind === request.kind
    && value.task_id === meta.task_id && value.session_id === original.target_session && value.stock_posted === false
    && same(value.original, request.original));
  if (request.kind === "OPEN_STEP") requireMatch(value.step_id === request.original.step_id && value.original_operation_id === request.original.operation_id);
  else requireMatch(value.step_id === null && value.original_operation_id === null);
}
export async function resolveAbandonment(credentials: AssemblyCredentials, meta: JournalMeta,
  control: AbandonControl, readOnly = false): Promise<void> {
  requireMatch(meta.actor === credentials.username && meta.server === location.origin);
  if (!navigator.locks) throw new Error("Нет безопасной блокировки журнала. Отмена не отправлена.");
  await navigator.locks.request(`assembly-command:${meta.server}:${meta.actor}:${meta.task_id}`, async () => {
    const prior = readAbandonment(meta);
    if (prior) requireMatch(same(prior, control));
    else {
      requireMatch(!readOnly && same(readSaved(control.original.kind, meta), control.original));
      saveIntent(CONTROL, meta, control); // Persist control BEFORE its first HTTP request.
    }
    const result = readOnly
      ? await assemblyRequest<unknown>(`/abandonments/${encodeURIComponent(control.request.operation_id)}`, credentials)
      : await assemblyRequest<unknown>("/abandonments", credentials, control.request);
    validateAbandoned(result, control, meta);
    // Keep control until original removal succeeds. Reload can resolve the same ACK again.
    clearIntent(control.original.kind, meta);
    clearIntent(CONTROL, meta);
  });
}

