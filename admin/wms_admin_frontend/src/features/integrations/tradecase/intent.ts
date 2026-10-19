import { API_BASE, ApiRequestError } from "../../../api";

/** Общий долговечный журнал команд TRADECASE (bind, buyout, sort): тело с operation_id сохраняется ДО отправки и не
 *  меняется до доказанного исхода. Ключ — сервер API + пользователь + склад: чужое намерение не воспроизводится.
 *  sent=true — отправка уже была, исход мог дойти до сервера. Повреждённая запись не перезаписывается. Пароль не хранится. */
export type Intent<B> = { body: B; sent: boolean };
export type Stored<B> = { kind: "none" } | { kind: "ok"; intent: Intent<B> } | { kind: "damaged"; raw: string };

export function journal<B extends { operation_id: string }>(kind: string, prefix: string, valid: (body: B) => boolean, what: string) {
  const key = (user: string, wh: string) => `tradecase.${kind}:${API_BASE}:${user}:${wh}`;
  const ok = (v: unknown): v is Intent<B> => {
    const i = v as Intent<B>;
    return Boolean(i && typeof i.sent === "boolean" && i.body && new RegExp("^" + prefix.replace(/\./g, "\\.") + ":[A-Za-z0-9-]{8,80}$").test(i.body.operation_id) && valid(i.body));
  };
  function read(user: string, wh: string): Stored<B> {
    if (!user || !wh) return { kind: "none" };
    let raw: string | null;
    try { raw = localStorage.getItem(key(user, wh)); } catch { return { kind: "damaged", raw: "Хранилище браузера недоступно. Отправка заблокирована." }; }
    if (raw === null) return { kind: "none" };
    try { const v = JSON.parse(raw); return ok(v) ? { kind: "ok", intent: v } : { kind: "damaged", raw }; } catch { return { kind: "damaged", raw }; }
  }
  function write(user: string, wh: string, intent: Intent<B>) {
    const raw = JSON.stringify(intent);
    localStorage.setItem(key(user, wh), raw);
    if (localStorage.getItem(key(user, wh)) !== raw) throw new Error("Команда не сохранена в браузере — запись не отправлена.");
  }
  /** Новое намерение: только если сохранённого нет. operation_id генерируется здесь один раз. */
  function create(user: string, wh: string, body: Omit<B, "operation_id">): Intent<B> {
    if (read(user, wh).kind !== "none") throw new Error(`Сначала завершите сохранённую команду (${what}) на этом складе.`);
    const intent = { body: { ...body, operation_id: prefix + ":" + crypto.randomUUID() } as B, sent: false };
    write(user, wh, intent); return intent;
  }
  return { read, create, markSent: (user: string, wh: string, intent: Intent<B>) => write(user, wh, { ...intent, sent: true }),
    clear: (user: string, wh: string) => localStorage.removeItem(key(user, wh)) };
}

export const codeOf = (e: ApiRequestError) => typeof e.detail === "object" && e.detail ? String((e.detail as { code?: string }).code ?? "") : String(e.detail ?? "");
const KEEP_CODES = ["OPERATION_CONFLICT", "OPERATION_CONTENT_CONFLICT"];

/** Исход ошибки POST. unknown — ответ не получен (сеть/5xx); kept — отказ при повторе после неизвестной отправки,
 *  команда остаётся при любом4xx: ранняя проверка текущих прав/политики не опровергает первый эффект; refused — отказ первой отправки. */
export function classify(e: unknown, prior: boolean): { outcome: "unknown" | "auth" | "kept" | "refused"; code: string } {
  if (!(e instanceof ApiRequestError) || e.status >= 500) return { outcome: "unknown", code: "" };
  const code = codeOf(e);
  if (e.status === 401) return { outcome: "auth", code };
  if (KEEP_CODES.includes(code) || prior) return { outcome: "kept", code };
  return { outcome: "refused", code };
}
