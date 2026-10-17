import { ApiRequestError, apiFetch, apiOperationScope } from "../../../api";
import type { CommandReceipt } from "./types";

/** Общий отправитель команд метаданных (/api/access/commands, /api/knowledge/commands).
 *  Команда сохраняется в браузере ДО отправки и сверяется чтением; удаляется только после квитанции
 *  или подтверждённого сервером отказа (detail.outcome_confirmed === true). Сеть/5xx/непонятный ответ —
 *  «результат неизвестен»: повтор только тем же operation_id и тем же телом, новая команда заблокирована. */
export type MetadataDomain = "access" | "knowledge";
/** endpoint — отдельный маршрут с operation_id в теле (например импорт wiki): тело = {operation_id, ...payload}, квитанция — повтор того же тела. */
export type PendingCommand = { domain: MetadataDomain; operation_id: string; command_type: string; payload: Record<string, unknown>; label: string; created_at: string; endpoint?: string };
export type PendingState = { kind: "none" } | { kind: "valid"; command: PendingCommand; raw: string } | { kind: "damaged"; raw: string };
export type SendOutcome =
  | { kind: "done"; receipt: CommandReceipt }
  | { kind: "refused"; code: string; message: string; status: number }
  | { kind: "unknown"; message: string };

const key = (domain: MetadataDomain) => `retailcase.${domain}.pending:${apiOperationScope()}`;
const archiveKey = (domain: MetadataDomain) => `retailcase.${domain}.damaged:${apiOperationScope()}`;

function parse(raw: string, domain: MetadataDomain): PendingCommand | null {
  try {
    const value = JSON.parse(raw) as PendingCommand;
    const ok = value && value.domain === domain && typeof value.operation_id === "string" && typeof value.command_type === "string"
      && typeof value.payload === "object" && value.payload !== null && typeof value.label === "string"
      && (value.endpoint === undefined || (typeof value.endpoint === "string" && value.endpoint.startsWith("/api/knowledge/")));
    return ok ? value : null;
  } catch { return null; }
}

export function readPending(domain: MetadataDomain): PendingState {
  let raw: string | null;
  try { raw = localStorage.getItem(key(domain)); } catch { return { kind: "damaged", raw: "" }; }
  if (!raw) return { kind: "none" };
  const command = parse(raw, domain);
  return command ? { kind: "valid", command, raw } : { kind: "damaged", raw };
}

/** Запись с проверкой чтением: без подтверждённой записи команда не отправляется. */
export function savePending(command: PendingCommand): string {
  const raw = JSON.stringify(command);
  try {
    if (localStorage.getItem(key(command.domain))) throw new Error("Есть незавершённая команда — сначала проверьте её исход.");
    localStorage.setItem(key(command.domain), raw);
    if (localStorage.getItem(key(command.domain)) !== raw) throw new Error("Хранилище браузера не подтвердило запись.");
  } catch (error) { throw error instanceof Error ? error : new Error("Хранилище браузера недоступно."); }
  return raw;
}

/** Удаляет только ту же самую запись (другая вкладка могла записать новую). */
export function settlePending(domain: MetadataDomain, raw: string): boolean {
  try {
    if (localStorage.getItem(key(domain)) !== raw) return false;
    localStorage.removeItem(key(domain));
    return true;
  } catch { return false; }
}

export function archiveDamaged(domain: MetadataDomain, raw: string): boolean {
  try {
    if (localStorage.getItem(key(domain)) !== raw) return false;
    localStorage.setItem(archiveKey(domain) + ":" + Date.now(), raw);
    localStorage.removeItem(key(domain));
    return true;
  } catch { return false; }
}

export function newOperationId(prefix: string): string {
  return `UI.${prefix}:${crypto.randomUUID()}`;
}

function refusal(error: unknown): SendOutcome | null {
  if (!(error instanceof ApiRequestError)) return null;
  const detail = error.detail as { code?: unknown; message?: unknown; outcome_confirmed?: unknown } | null;
  if (detail && typeof detail === "object" && detail.outcome_confirmed === true && typeof detail.code === "string")
    return { kind: "refused", code: detail.code, message: typeof detail.message === "string" ? detail.message : detail.code, status: error.status };
  return null;
}

const base = (domain: MetadataDomain) => domain === "access" ? "/api/access/commands" : "/api/knowledge/commands";

/** Отправка сохранённой команды точным телом. */
export async function sendPending(command: PendingCommand, raw: string): Promise<SendOutcome> {
  let receipt: CommandReceipt;
  try {
    const body = command.endpoint ? { operation_id: command.operation_id, ...command.payload }
      : { operation_id: command.operation_id, command_type: command.command_type, payload: command.payload };
    receipt = await apiFetch<CommandReceipt>(command.endpoint ?? base(command.domain), { method: "POST", body: JSON.stringify(body) });
  } catch (error) {
    const refused = refusal(error);
    if (refused) { settlePending(command.domain, raw); return refused; }
    return { kind: "unknown", message: error instanceof ApiRequestError ? `HTTP ${error.status}: исход не подтверждён` : "Сервер не ответил" };
  }
  if (!receipt || (receipt.operation_id ?? (command.endpoint ? command.operation_id : undefined)) !== command.operation_id)
    return { kind: "unknown", message: "Ответ не подтверждает исходную команду" };
  settlePending(command.domain, raw);
  return { kind: "done", receipt };
}

/** Квитанция по operation_id. 404 RECEIPT_NOT_VISIBLE — квитанции не видно; это не разрешение менять команду. */
export async function readReceipt(command: PendingCommand, raw: string): Promise<SendOutcome> {
  if (command.endpoint) return sendPending(command, raw);
  try {
    const receipt = await apiFetch<CommandReceipt>(`${base(command.domain)}/${encodeURIComponent(command.operation_id)}`);
    if (receipt?.operation_id === command.operation_id) { settlePending(command.domain, raw); return { kind: "done", receipt }; }
    return { kind: "unknown", message: "Квитанция не совпадает с командой" };
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) return { kind: "unknown", message: "Квитанции нет: команда не зафиксирована или не видна. Повторите ту же команду." };
    return { kind: "unknown", message: "Квитанция не получена" };
  }
}

export function describeRefusal(outcome: Extract<SendOutcome, { kind: "refused" }>): string {
  const known: Record<string, string> = {
    VERSION_CONFLICT: "Объект уже изменён. Перечитайте его и создайте новую команду.",
    VERSION_REQUIRED: "Нужна текущая версия объекта: перечитайте и повторите новой командой.",
    OPERATION_CONFLICT: "Под этим operation_id уже сохранена другая команда — тело менять нельзя.",
    OBJECT_NOT_FOUND: "Объект не найден или удалён.",
    ROLE_NOT_FOUND: "Роль не найдена.",
    GROUP_NOT_FOUND: "Группа объектов не найдена.",
    USER_NOT_FOUND: "Пользователь не найден или удалён.",
    BRANCH_NOT_FOUND: "Ветвь организации не найдена.",
    SNAPSHOT_NOT_FOUND: "Снимок группы с такой версией не найден.",
    SNAPSHOT_REVISION_CONFLICT: "Снимок изменился — выберите актуальную версию.",
    GROUP_KIND_MISMATCH: "Состав группы должен быть одного вида объектов.",
    GROUP_MEMBER_LIMIT: "В группе не больше 200 объектов.",
    ROLE_RIGHTS_LIMIT: "В роли не больше 200 прав.",
    OBJECT_CYCLE: "Родитель создаёт цикл в иерархии.",
    SELF_REFERENCE: "Объект не может быть родителем самому себе.",
    GLOBAL_ADMIN_REQUIRED: "Это изменение пока доступно только глобальному администратору.",
    DELEGATION_OUTSIDE_MANDATE: "Назначение шире ваших собственных прав, области или срока.",
    REVOKE_OUTSIDE_MANDATE: "Отозвать это назначение можно только в пределах вашего мандата.",
    ACCESS_DENIED: "Нет полномочий для этого изменения.",
    INVALID_COMMAND: "Данные команды отклонены проверкой.",
    UNKNOWN_COMMAND: "Неизвестный тип команды.",
    ARTICLE_ACCESS_DENIED: "Нет права на эту статью или её пространство.",
    RELATED_NOT_FOUND: "Связанная статья не найдена — проверьте article_id в «Связанных».",
    RELATED_LIMIT: "Не больше 30 связанных статей.",
    AUDIENCE_LIMIT: "Не больше 30 прав чтения.",
  };  return `${known[outcome.code] ?? outcome.message} (${outcome.code}, HTTP ${outcome.status})`;
}
