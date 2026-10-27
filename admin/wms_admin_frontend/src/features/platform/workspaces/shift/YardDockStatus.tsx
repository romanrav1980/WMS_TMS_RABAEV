import { useMemo, useState } from "react";
import { ApiRequestError, apiFetch, apiOperationScope } from "../../../../api";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { fmtTime } from "../resources/timelineModel";
import { shiftHelp } from "./help";

// Неисправность ворот (C-0180). Как и прочие команды двора: тело с operation_id сохраняется в браузере ДО отправки, повтор — те же байты;
// запись снимается только квитанцией своей операции и своих ворот или подтверждённым отказом. 401/403/503/сеть — запись остаётся.
type Dock = { dock: string; blocked: boolean | null; ambiguous?: boolean; status_error?: string | null; reason?: string | null; updated_by?: string | null; updated_at?: string | null };
type Action = "BLOCK" | "UNBLOCK";
type Intent = { ware: string; dock: string; action: Action; path: string; wire: string; operation_id: string; scope: string };
type Sent = { kind: "ack" } | { kind: "refused"; code: string } | { kind: "unknown"; message: string };

const key = (ware: string) => `retailcase.yard.dock-status.pending.v1:${apiOperationScope()}:${ware}`;
const pathOf = (ware: string, dock: string) => `/api/tradecase/warehouses/${encodeURIComponent(ware)}/yard/docks/${encodeURIComponent(dock)}/status`;
const TITLE: Record<Action, string> = { BLOCK: "Отметить неисправность", UNBLOCK: "Открыть после ремонта" };
const REFUSAL: Record<string, string> = {
  YARD_DOCK_NOT_FOUND: "Таких ворот нет в справочнике склада.", YARD_DOCK_AMBIGUOUS: "Название ворот повторяется в справочнике склада; команда не выполнена.",
  YARD_DOCK_STATUS_INVALID: "В справочнике записано недопустимое состояние ворот; команда не выполнена.",
  YARD_ACCESS_DENIED: "Нет права управлять двором этого склада.", ACCESS_DENIED: "Нет права управлять двором этого склада.",
};

function readIntent(ware: string): { intent: Intent | null; damaged: string } {
  let raw: string | null;
  try { raw = localStorage.getItem(key(ware)); } catch { return { intent: null, damaged: "Браузер не даёт прочитать сохранённую команду ворот; новые действия заблокированы." }; }
  if (!raw) return { intent: null, damaged: "" };
  try {
    const v = JSON.parse(raw) as Intent, body = JSON.parse(v.wire) as { operation_id?: string; action?: string };
    if (v.ware !== ware || v.scope !== apiOperationScope() || body.operation_id !== v.operation_id || body.action !== v.action || v.path !== pathOf(ware, v.dock)) throw new Error("shape");
    return { intent: v, damaged: "" };
  } catch { return { intent: null, damaged: "Сохранённая команда ворот повреждена. Запись оставлена в браузере; новые действия заблокированы." }; }
}

function saveIntent(ware: string, dock: string, action: Action, reason: string): Intent {
  const saved = readIntent(ware);
  if (saved.damaged) throw new Error(saved.damaged);
  if (saved.intent) throw new Error("Сначала завершите ранее сохранённую команду ворот.");
  const operation = `yard-dock-${crypto.randomUUID()}`;
  const intent: Intent = { ware, dock, action, path: pathOf(ware, dock), operation_id: operation, scope: apiOperationScope(), wire: JSON.stringify({ operation_id: operation, action, reason }) };
  const raw = JSON.stringify(intent);
  try { localStorage.setItem(key(ware), raw); } catch { throw new Error("Не удалось сохранить команду в браузере. Отправка не выполнена."); }
  if (localStorage.getItem(key(ware)) !== raw) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
  return intent;
}

const own = (intent: Intent) => { try { return intent.scope === apiOperationScope() && localStorage.getItem(key(intent.ware)) === JSON.stringify(intent); } catch { return false; } };
const clear = (intent: Intent) => { try { if (own(intent)) localStorage.removeItem(key(intent.ware)); } catch { /* останется до повтора */ } };
const FOREIGN: Sent = { kind: "unknown", message: "Вход сменился: сохранённая команда прежнего входа не отправлена и не показана." };

function refusal(error: ApiRequestError, intent: Intent, retry: boolean): Sent {
  const d = (typeof error.detail === "object" && error.detail ? error.detail : {}) as { code?: string; outcome_confirmed?: boolean };
  if (retry && [401, 403, 404, 422].includes(error.status))
    return { kind: "unknown", message: "Сервер не разрешил повтор сохранённой команды. Её первоначальный результат не подтверждён; номер команды сохранён." };
  if (d.code?.endsWith("OPERATION_CONFLICT")) return { kind: "unknown", message: "Номер этой операции уже использован с другими данными. Команда сохранена без изменений; обратитесь к руководителю." };
  if (error.status === 409 && d.outcome_confirmed === true) { clear(intent); return { kind: "refused", code: d.code ?? "HTTP 409" }; }
  if (error.status === 422 && Array.isArray(error.detail)) { clear(intent); return { kind: "refused", code: "YARD_REQUEST_INVALID" }; }  // тело не принято — исполнения не было
  return { kind: "unknown", message: error.status === 401 || error.status === 403 ? `${d.code && REFUSAL[d.code] ? REFUSAL[d.code] : "Доступ закрыт или сессия завершена."} Исход не подтверждён; команда сохранена — войдите с правом управления двором и повторите её.`
    : `Исход не подтверждён (HTTP ${error.status}). Команда сохранена; повторите её тем же номером.` };
}

async function send(intent: Intent, retry: boolean): Promise<Sent> {
  if (!own(intent)) return FOREIGN;
  try {
    const v = await apiFetch<{ operation_id?: string; dock?: string; blocked?: boolean }>(intent.path, { method: "POST", body: intent.wire });
    if (!own(intent)) return FOREIGN;  // поздний ответ после смены входа не применяется
    if (v?.operation_id !== intent.operation_id || v.dock !== intent.dock || v.blocked !== (intent.action === "BLOCK"))
      return { kind: "unknown", message: "Ответ сервера не относится к этой команде ворот. Команда сохранена; повторите её." };
    clear(intent);
    return { kind: "ack" };
  } catch (error) {
    if (!own(intent)) return FOREIGN;
    return error instanceof ApiRequestError ? refusal(error, intent, retry) : { kind: "unknown", message: "Сервер не ответил. Команда сохранена; повторите её тем же номером." };
  }
}

// Дубликат или недопустимое значение в справочнике: состояние не выдумывается, команды недоступны.
const unknownState = (d: Dock) => d.blocked === true || d.blocked === false ? null
  : d.ambiguous ? "состояние неизвестно: название ворот повторяется в справочнике (YARD_DOCK_AMBIGUOUS)" : `состояние неизвестно: недопустимое значение в справочнике${d.status_error ? ` (${d.status_error})` : ""}`;

/** Состояние ворот склада: исправны или отмечена неисправность; отметка и открытие с причиной. */
export function YardDockStatus({ wh, reload }: { wh: string; reload: number }) {
  const [local, setLocal] = useState(0), [tick, setTick] = useState(0);
  const read = useApiRead<{ warehouse_id: number; docks: Dock[] }>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/yard/docks`, reload + local);
  const pending = useMemo(() => readIntent(wh), [wh, tick]), intent = pending.intent;
  const [form, setForm] = useState<{ dock: string; action: Action; reason: string } | null>(null), [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  const docks = read.data?.warehouse_id === Number(wh) && Array.isArray(read.data.docks) ? read.data.docks : null;
  const blocked = busy || Boolean(intent) || Boolean(pending.damaged);

  const run = async (make: () => Intent) => {
    const retry = Boolean(readIntent(wh).intent);
    let next: Intent;
    try { next = make(); } catch (e) { setMessage((e as Error).message); return; }
    setBusy(true); setMessage("");
    const result = await send(next, retry);
    setBusy(false); setTick(n => n + 1); setLocal(n => n + 1);
    if (result.kind === "ack") { setForm(null); setMessage(`Выполнено: ворота ${next.dock} — ${next.action === "BLOCK" ? "отмечена неисправность" : "открыты"}.`); }
    else setMessage(result.kind === "refused" ? `Отказ: ${REFUSAL[result.code] ?? result.code}` : result.message);
  };

  return <div className="ops-dock-status" aria-label="Состояние ворот">
    <h4>Состояние ворот{" "}<HelpButton help={shiftHelp.dockRefresh} onClick={() => setLocal(n => n + 1)}>Обновить</HelpButton></h4>
    <p className="ops-note">Неисправные ворота не предлагаются для новых назначений и планов. Отметка не отменяет текущий визит, план, погрузку и отгрузку у этих ворот — их ведите отдельно ниже и в плане ворот.</p>
    {read.error && <p role="alert" className="ops-err">Состояние ворот не прочитано: {read.error}</p>}
    {pending.damaged && <p role="alert" className="ops-err">{pending.damaged}</p>}
    {intent && <div role="status" className="ops-err">Команда «{TITLE[intent.action]}» ворот {intent.dock} не подтверждена.{" "}
      <HelpButton help={shiftHelp.dockRetry} disabled={busy} onClick={() => run(() => intent)}>Повторить</HelpButton></div>}
    {message && <p role="status" className="ops-note">{message}</p>}
    {docks && docks.length === 0 && <p className="ops-note">В справочнике склада нет ворот.</p>}
    {docks && docks.length > 0 && <ul className="ops-list">{docks.map(d => <li key={d.dock}><span>
      <b>Ворота {d.dock}</b> <small className={d.blocked !== false ? "ops-err" : undefined}>{unknownState(d) ?? (d.blocked ? "неисправны" : "исправны")}</small>
      {d.reason && <><br /><small style={{ overflowWrap: "anywhere" }}>Причина: {d.reason}</small></>}
      {d.updated_at && <><br /><small>{fmtTime(null, d.updated_at)}{d.updated_by ? ` · ${d.updated_by}` : ""}</small></>}
      {form?.dock === d.dock && <><br />
        <input aria-label={form.action === "BLOCK" ? "Описание неисправности" : "Причина открытия"} maxLength={500} value={form.reason} onChange={e => setForm({ ...form, reason: e.target.value })} />
        <HelpButton help={form.action === "BLOCK" ? shiftHelp.dockBlock : shiftHelp.dockUnblock} disabled={blocked || Boolean(unknownState(d)) || form.reason.trim().length < 3}
          onClick={() => run(() => saveIntent(wh, d.dock, form.action, form.reason.trim()))}>{TITLE[form.action]}</HelpButton>
        <HelpButton help={shiftHelp.dockClose} onClick={() => setForm(null)}>Закрыть</HelpButton></>}
    </span><span>
      <HelpButton help={d.blocked ? shiftHelp.dockUnblock : shiftHelp.dockBlock} disabled={blocked} unavailable={unknownState(d) ?? undefined}
        onClick={() => setForm({ dock: d.dock, action: d.blocked ? "UNBLOCK" : "BLOCK", reason: "" })}>{d.blocked ? "Открыть…" : "Неисправность…"}</HelpButton>
    </span></li>)}</ul>}
  </div>;
}
