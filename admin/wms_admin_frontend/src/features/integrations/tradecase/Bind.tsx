import { useRef, useState } from "react";
import { apiFetch, ApiRequestError } from "../../../api";
import { bindPath, tcHelp } from "./api";
import type { BindResult, DocCard, Kind } from "./api";
import { clearIntent, createIntent, markSent, readIntent } from "./bindIntent";
import type { Intent } from "./bindIntent";
import type { Names } from "./Lists";
import { Act, HelpLink, Tech, str } from "./ui";

const REASONS: Record<string, string> = {
  TRADE_OWNER_ACCESS_DENIED: "нет права на собственника этого товара", ACCESS_DENIED: "нет права привязки на этом складе",
  TRADE_SITE_DISABLED: "приём на площадке выключен", VERSION_CONFLICT: "поставка изменилась — перечитайте документ и отсканируйте снова",
  OPERATION_CONFLICT: "номер операции уже использован с другими данными",
};
const codeOf = (e: ApiRequestError) => typeof e.detail === "object" && e.detail ? str((e.detail as { code?: string }).code) : str(e.detail);
type Msg = { text: string; tone: "ok" | "warn" | "bad"; tech?: unknown };

/** Привязка собственника/МРЦ/срока поставки к уже принятому товару паллеты. Не принимает товар физически,
 *  не подтверждает коды СКМ и не выкупает. Тело и operation_id неизменны до доказанного исхода. */
export function BindPanel({ wh, user, card, names, onDone, onOpen }: { wh: string; user: string; card: DocCard; names: Names; onDone: () => void; onOpen: (k: Kind, id: string) => void }) {
  const [scan, setScan] = useState(""), [review, setReview] = useState(""), [busy, setBusy] = useState(false), [msg, setMsg] = useState<Msg | null>(null), [, rerender] = useState(0);
  const lock = useRef(false); // синхронная защита от двойного клика до перерисовки
  const stored = readIntent(user, wh), p = card.payload;
  const name = (kind: string, id: unknown) => { const v = str(id), t = names.get(kind + ":" + v); return t ? `${t} (${v})` : v; };

  async function send(intent: Intent) {
    if (lock.current) return;
    lock.current = true; setBusy(true); setReview(""); // тело сохранено до отправки
    setMsg({ text: "Отправка…", tone: "warn" });
    const prior = intent.sent;
    try {
      markSent(user, wh, intent);
      const r = await apiFetch<BindResult>(bindPath(wh), { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(intent.body) });
      if (r.operation_id !== intent.body.operation_id || r.supply_id !== intent.body.supply_id || r.attributes_bound !== true) {
        setMsg({ text: "Ответ сервера не подтверждает эту привязку. Повторите ту же команду.", tone: "warn", tech: r }); return; }
      clearIntent(user, wh); setScan(""); setReview(""); onDone();
      setMsg({ text: `${r.replayed ? "Повтор: результат уже был сохранён. " : ""}Привязано единиц: ${r.bound_units} на паллете ${r.pallet_identifier}. Количество не менялось; коды ожидают подтверждения СКМ.`, tone: "ok", tech: r });
    } catch (e) {
      if (!(e instanceof ApiRequestError) || e.status >= 500) setMsg({ text: "Результат неизвестен: ответ не получен. Команда сохранена — повторите её; повтор не создаст новую операцию.", tone: "warn" });
      else if (e.status === 401) setMsg({ text: "Сессия завершена — войдите снова и повторите ту же команду.", tone: "warn" });
      else if (e.status === 409 && codeOf(e) === "OPERATION_CONFLICT" && prior) setMsg({ text: "Сервер сообщил о конфликте сохранённой команды. Команда сохранена — передайте номер операции ответственному за обмен.", tone: "bad", tech: e.detail });
      else if (e.status === 403 && prior) setMsg({ text: "Нет права (" + (REASONS[codeOf(e)] ?? "отказ сервера") + "). Прежняя отправка могла дойти, поэтому команда сохранена: после восстановления прав повторите её.", tone: "bad", tech: e.detail });
      else { clearIntent(user, wh); setReview(""); setMsg({ text: "Сервер отклонил привязку: " + (REASONS[codeOf(e)] ?? "данные не прошли проверку") + ". Команда снята — исправьте и отсканируйте снова.", tone: "bad", tech: e.detail }); }
    } finally { lock.current = false; setBusy(false); rerender(n => n + 1); }
  }
  const start = () => { if (lock.current) return; try { send(createIntent(user, wh, card.document_id, card.document_version, review)); } catch (e) { setMsg({ text: String((e as Error).message), tone: "bad" }); } };
  const note = msg && <p className={"tc-msg " + msg.tone} role="status">{msg.text}{msg.tech !== undefined && <Tech value={msg.tech} />}</p>;

  if (!user) return <section className="tc-bind"><p className="tc-note">Определяем пользователя — привязка станет доступна после чтения профиля.</p></section>;
  if (stored.kind === "damaged") return <section className="tc-bind bad"><h4>Привязка заблокирована</h4>
    <p>Сохранённая в браузере привязка на этом складе повреждена. Новая привязка не создаётся, чтобы не потерять след прежней команды; передайте технические сведения ответственному.</p><Tech value={stored.raw} /></section>;
  if (stored.kind === "ok" && stored.intent.body.supply_id !== card.document_id) return <section className="tc-bind warn"><h4>Есть незавершённая привязка</h4>
    <p>На этом складе сохранена привязка поставки <b>{stored.intent.body.supply_id}</b> к паллете <b>{stored.intent.body.scanned_pallet}</b>. Откройте её и повторите, прежде чем начинать новую.</p>
    <Act help={tcHelp.related} onClick={() => onOpen("SUPPLY", stored.intent.body.supply_id)}>Открыть поставку</Act></section>;
  if (stored.kind === "ok") { const b = stored.intent.body; return <section className="tc-bind warn"><h4>Сохранённая команда привязки <HelpLink anchor="unknown" label="Что делать" /></h4>
    <p>Паллета <b>{b.scanned_pallet}</b>, поставка {b.supply_id} (версия {b.expected_supply_version}). {stored.intent.sent ? "Отправка уже была, результат не подтверждён." : "Команда ещё не отправлена."} Данные команды не меняются до получения результата.</p>
    <Act help={tcHelp.retry} disabled={busy} onClick={() => send(stored.intent)}>Повторить ту же команду</Act>{note}<Tech value={b} label="Номер операции и тело команды" /></section>; }
  return <section className="tc-bind"><h4>Привязать поставку к принятому товару <HelpLink anchor="bind" /></h4>
    {!review ? <form onSubmit={e => { e.preventDefault(); if (scan.trim()) { setMsg(null); setReview(scan.trim()); } }}>
      <label>Идентификатор паллеты<input value={scan} onChange={e => setScan(e.target.value)} autoComplete="off" maxLength={50} title={tcHelp.scan.text} data-help-id={tcHelp.scan.id} /></label>
      <button type="submit" disabled={!scan.trim()} title={tcHelp.review.text} data-help-id={tcHelp.review.id}>Проверить</button></form>
    : <div className="tc-review"><p>Будет записано: паллета <b>{review}</b> — товар {name("SKU", p.sku_id)}, собственник {name("OWNER", p.owner_id)}, МРЦ {str(p.mrc)}, срок {str(p.expiry_date)}, партия {str(p.supplier_batch)}; поставка {card.document_id}, версия {card.document_version}.</p>
      {str(p.pallet_identifier) !== review && <p className="tc-msg warn">В поставке указана паллета {str(p.pallet_identifier)}. Сервер проверит соответствие и откажет, если товар не тот.</p>}
      <p className="tc-note">Действие записывает юридические атрибуты товара. Оно не принимает товар физически, не подтверждает коды в СКМ и не выкупает товар.</p>
      <Act help={tcHelp.bind} disabled={busy} onClick={start}>Привязать</Act> <Act help={tcHelp.cancelReview} disabled={busy} onClick={() => setReview("")}>Отмена</Act></div>}
    {note}</section>;
}
