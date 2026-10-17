import type { AssemblyCredentials } from "../assembly/contracts";
import { assemblyAuthHeader } from "../assembly/api";
import type { Intent } from "./contracts";
import { record } from "./contracts";

export class CaseWorkError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function request(path: string, credentials: AssemblyCredentials, signal: AbortSignal, intent?: Intent): Promise<unknown> {
  const timeout = new AbortController(), abort = () => timeout.abort();
  signal.addEventListener("abort", abort, { once: true });
  if (signal.aborted) abort();
  const timer = window.setTimeout(abort, 30000);
  try {
  const response = await fetch(path, { method: intent ? "POST" : "GET", cache: "no-store", signal: timeout.signal,
    headers: { Authorization: assemblyAuthHeader(credentials), ...(intent ? { "Content-Type": "application/json" } : {}) },
    body: intent?.wire });
  let value: unknown;
  try { value = await response.json(); } catch { throw new CaseWorkError("Сервер вернул неполный ответ. Сохранённая операция остаётся в журнале.", response.status); }
  if (!intent && response.status === 200) return value;
  if (intent && ((response.status === 200 && record(value) && value.outcome === "APPLIED")
    || (response.status === 409 && record(value) && value.outcome === "REJECTED"))) return value;
  if (response.ok || response.status === 409) throw new CaseWorkError("Ответ сервера не соответствует контракту операции. Исходный запрос сохранён.", response.status);
  throw new CaseWorkError(response.status === 404 ? "Результат пока не найден. Исходный запрос сохранён; доступен только его точный повтор."
    : response.status === 401 || response.status === 403 ? "Нет действующего доступа. Операция сохранена; проверьте учётную запись и права."
    : `Связь с сервером не подтверждена (HTTP ${response.status}). Исходный запрос сохранён.`, response.status);
  } catch (error) {
    if (error instanceof CaseWorkError) throw error;
    throw new CaseWorkError("Нет подтверждённого ответа сервера. Сохранённая операция остаётся в журнале; прочитайте её результат.", 0);
  } finally { window.clearTimeout(timer); signal.removeEventListener("abort", abort); }
}
