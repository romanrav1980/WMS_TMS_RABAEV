import type { AssemblyCredentials } from "../assembly/contracts";
import { assemblyAuthHeader } from "../assembly/api";
import type { ControlBody, OriginalIntent } from "./contracts";
export class RecoveryError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function recoveryRequest(path: string, credentials: AssemblyCredentials, signal: AbortSignal, wire?: string): Promise<unknown> {
 const timeout = new AbortController(), abort = () => timeout.abort();
 signal.addEventListener("abort", abort, { once: true }); if (signal.aborted) abort();
 const timer = window.setTimeout(abort, 30000);
 try {
  const response = await fetch("/api/resources/metadata-intents" + path, { method: wire ? "POST" : "GET", body: wire,
   signal: timeout.signal, cache: "no-store", headers: { Authorization: assemblyAuthHeader(credentials), ...(wire ? { "Content-Type": "application/json" } : {}) } });
  if (!response.ok) throw new RecoveryError(response.status === 404 ? "Квитанция пока не найдена. Это не разрешение удалить запрос или создать новый."
   : response.status === 401 || response.status === 403 ? "Нет текущего доступа. Оба исходных запроса остаются сохранены."
   : `Восстановление не подтверждено (HTTP ${response.status}). Прочитайте результат; новый operation_id не создаётся.`, response.status);
  return await response.json();
 } catch (error) { if (error instanceof RecoveryError) throw error; throw new RecoveryError("Нет точного ответа восстановления. Сохранённый запрос прекращения можно только прочитать или повторить неизменно.", 0); }
 finally { window.clearTimeout(timer); signal.removeEventListener("abort", abort); }
}
export function resolutionPath(original: OriginalIntent): string {
 return "/resolution?" + new URLSearchParams({ domain: original.domain, task_id: String(original.task_id), original_operation_id: original.operation_id,
  action: original.action, target: original.target, original_request_sha256: original.request_sha256 }).toString();
}
export type { ControlBody };
