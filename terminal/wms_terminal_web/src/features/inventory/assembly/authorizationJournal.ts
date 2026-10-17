import { readSaved } from "./savedCommands";
import type { SavedCommand } from "./savedCommands";
import { validReconciliation } from "./recoveryCommands";
import type { AssemblyCredentials, Reconciliation } from "./contracts";
export function savedAuthorization(credentials: AssemblyCredentials, id: string): SavedCommand | null {
  const prefix = `assembly-scale:recovery_authorize:${location.origin}:${credentials.username}:`;
  let saved: SavedCommand | null = null;
  for (let index = 0; index < localStorage.length; index += 1) {
    const key = localStorage.key(index);
    if (!key?.startsWith(prefix)) continue;
    const task = Number(key.slice(prefix.length));
    if (!Number.isSafeInteger(task) || task <= 0) throw new Error("Повреждена область сохранённого подтверждения.");
    const candidate = readSaved("recovery_authorize", { server: location.origin, actor: credentials.username, task_id: task });
    if (candidate?.target_reconciliation !== id) continue;
    if (saved) throw new Error("Найдены противоречивые сохранённые подтверждения. Нужна сверка.");
    validReconciliation(candidate.context_snapshot, id);
    saved = candidate;
  }
  return saved;
}
export function authorizationSnapshot(command: SavedCommand | null): Reconciliation | null {
  return command?.context_snapshot ?? null;
}
