import { useRef, useState } from "react";
import { apiFetch } from "../../../api";
import { classify } from "./intent";
import type { Intent, journal } from "./intent";

export type Msg = { text: string; tone: "ok" | "warn" | "bad"; tech?: unknown };
type Journal<B extends { operation_id: string }> = ReturnType<typeof journal<B>>;

/** Отправка долговечной команды: тело сохранено до POST; неизвестный исход блокирует изменения и повторяется тем же телом;
 *  подтверждённый отказ снимает команду; отказ при повторе после неизвестной отправки и конфликт операции её сохраняют. */
export function useCommand<B extends { operation_id: string }, R>(j: Journal<B>, path: string, user: string, wh: string,
  reasons: Record<string, string>, accept: (r: R, body: B) => string | null, transport?: { path: (body: B) => string; payload: (body: B) => unknown }) {
  const lock = useRef(false), [busy, setBusy] = useState(false), [msg, setMsg] = useState<Msg | null>(null), [, rerender] = useState(0);
  async function send(intent: Intent<B>, after?: (r: R) => void) {
    if (lock.current) return;
    lock.current = true; setBusy(true); setMsg({ text: "Отправка…", tone: "warn" });
    const prior = intent.sent;
    try {
      j.markSent(user, wh, intent);
      const r = await apiFetch<R>(transport?.path(intent.body) ?? path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(transport ? transport.payload(intent.body) : intent.body) });
      const done = accept(r, intent.body);
      if (done === null) { setMsg({ text: "Ответ сервера не подтверждает эту команду. Повторите ту же команду.", tone: "warn", tech: r }); return; }
      j.clear(user, wh); setMsg({ text: done, tone: "ok", tech: r }); after?.(r);
    } catch (e) {
      const c = classify(e, prior), reason = reasons[c.code] ?? "данные не прошли проверку сервера";
      if (c.outcome === "unknown") setMsg({ text: "Результат неизвестен: ответ не получен. Команда сохранена — повторите её; повтор не создаст новую операцию.", tone: "warn" });
      else if (c.outcome === "auth") setMsg({ text: "Сессия завершена — войдите снова и повторите ту же команду.", tone: "warn" });
      else if (c.outcome === "kept") setMsg({ text: "Отказ сервера (" + reason + "). Прежняя отправка могла дойти, поэтому команда сохранена: новая команда вместо неё не создаётся.", tone: "bad", tech: (e as { detail?: unknown }).detail });
      else { j.clear(user, wh); setMsg({ text: "Сервер отклонил команду: " + reason + ". Команда снята.", tone: "bad", tech: (e as { detail?: unknown }).detail }); }
    } finally { lock.current = false; setBusy(false); rerender(n => n + 1); }
  }
  function start(body: Omit<B, "operation_id">, after?: (r: R) => void) {
    if (lock.current) return;
    try { send(j.create(user, wh, body), after); } catch (e) { setMsg({ text: (e as Error).message, tone: "bad" }); }
  }
  return { stored: j.read(user, wh), busy, msg, setMsg, send, start };
}
