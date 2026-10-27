import { useEffect, useRef, useState } from "react";
import { adminAuthorization, currentSessionCredentials, API_BASE } from "../../api";

// C-0176: снять выбранные физические места одной сборки (СТ) с рейса; остальные места сборки остаются в рейсе.
// Команда сохраняется до отправки и повторяется точно (тот же номер операции и версия состава) после неизвестного исхода.
type Place = { member_id: number; pallet_uid: string; address: string | null; on_trip: boolean; other_trip: number | null; loaded: boolean; shipped: boolean; quantity: string | null };
type Places = { trip_id: number; st_number: string; on_trip: number; places: Place[]; source_hash: string };
type Intent = { operation_id: string; trip_id: number; st_number: string; member_ids: number[]; expected_source_hash: string; reason: string };
type Receipt = { operation_id: string; trip_id: number; st_number: string; removed: number[]; on_trip_after: number };

const REASONS: Record<string, string> = {
  TRIP_MEMBERSHIP_SNAPSHOT_CHANGED: "Состав мест рейса изменился после чтения. Перечитайте список.",
  TRIP_MEMBER_NOT_ON_TRIP: "Выбранное место уже не в этом рейсе. Перечитайте список.",
  LOADED_ST_REASSIGNMENT_FORBIDDEN: "Место уже погружено — сначала выгрузите его.",
  SHIPPED_ST_REASSIGNMENT_FORBIDDEN: "Место уже отгружено.",
  TRIP_MEMBERSHIP_CHANGE_FORBIDDEN: "Рейс отгружен, удалён или включён в счёт — состав менять нельзя.",
  OPERATION_CONFLICT: "Этот номер операции уже связан с другим запросом.",
  ACCESS_DENIED: "Нет права диспетчера на склад этого рейса.",
  TRADE_OWNER_ACCESS_DENIED: "Нет права работы с товаром собственника этих мест.",
};
const keyOf = (actor: string) => "retailcase.trip.place-removal.pending:" + JSON.stringify([API_BASE, actor]);
const headers = () => ({ Authorization: adminAuthorization(), "Content-Type": "application/json" });

function readIntent(key: string): Intent | null | "damaged" {
  try {
    const raw = localStorage.getItem(key); if (raw === null) return null;
    const v = JSON.parse(raw) as Intent;
    return typeof v.operation_id === "string" && Number.isSafeInteger(v.trip_id) && Array.isArray(v.member_ids) && /^[A-F0-9]{64}$/.test(v.expected_source_hash) ? v : "damaged";
  } catch { return "damaged"; }
}

export function TransportStPlaceRemoval({ tripId, stNumber, disabled, onChanged }: { tripId: number; stNumber: string; disabled: boolean; onChanged: () => void }) {
  const actor = (() => { try { return currentSessionCredentials().username; } catch { return ""; } })();
  const key = keyOf(actor);
  const [data, setData] = useState<Places | null>(null);
  const [error, setError] = useState(""), [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  const [chosen, setChosen] = useState<Set<number>>(new Set()), [count, setCount] = useState(""), [reason, setReason] = useState(""), [confirm, setConfirm] = useState(false);
  const [pending, setPending] = useState<Intent | null | "damaged">(null);
  const version = useRef(0);

  async function load() {
    const token = ++version.current; setBusy(true); setError("");
    try {
      const r = await fetch(`${API_BASE}/api/transport/trips/${tripId}/sts/${encodeURIComponent(stNumber)}/places`, { headers: headers() });
      const b = await r.json().catch(() => null);
      if (token !== version.current) return;  // поздний ответ другого рейса или сборки не показывается
      if (r.status === 401 || r.status === 403) { setData(null); setChosen(new Set()); setError("Нет доступа к местам этой сборки."); return; }
      if (!r.ok) throw new Error(REASONS[b?.detail?.code] ?? "Список мест не прочитан.");
      setData(b as Places); setChosen(new Set());
    } catch (e) { if (token === version.current) setError(e instanceof Error ? e.message : "Список мест не прочитан."); }
    finally { if (token === version.current) setBusy(false); }
  }
  useEffect(() => { setData(null); setConfirm(false); setPending(actor ? readIntent(key) : null); void load(); return () => { version.current++; }; }, [tripId, stNumber, actor]);

  async function send(intent: Intent) {
    setBusy(true); setMessage("");
    try {
      let r: Response;
      try { r = await fetch(`${API_BASE}/api/transport/trips/${intent.trip_id}/place-removals`, { method: "POST", headers: headers(), body: JSON.stringify({ ...intent, trip_id: undefined }) }); }
      catch { throw new Error("Сервер не ответил. Результат неизвестен — повторите сохранённую команду."); }
      const b = await r.json().catch(() => null);
      if (r.status === 401 || r.status === 403) { setData(null); throw new Error(REASONS[b?.detail?.code] ?? "Нет доступа. Команда сохранена."); }
      if (!r.ok) {
        // A confirmed business refusal settles the command; an operation conflict does not prove the earlier lost request failed.
        if (r.status === 409 && typeof b?.detail?.code === "string" && b.detail.outcome_confirmed === true) { localStorage.removeItem(key); setPending(null); throw new Error((REASONS[b.detail.code] ?? "Снятие отклонено") + " (" + b.detail.code + ")"); }
        if (r.status === 409) throw new Error((REASONS[b?.detail?.code] ?? "Конфликт операции") + ". Результат прежней команды не подтверждён — команда сохранена.");
        throw new Error("Результат не подтверждён (HTTP " + r.status + "). Повторите сохранённую команду.");
      }
      const receipt = b as Receipt;
      if (receipt.operation_id !== intent.operation_id || receipt.trip_id !== intent.trip_id) throw new Error("Ответ не подтверждает команду. Повторите сохранённую команду.");
      localStorage.removeItem(key); setPending(null);
      setMessage(`Снято мест: ${receipt.removed.length}. В рейсе осталось мест этой сборки: ${receipt.on_trip_after}. Товар, резерв, адреса и коды не изменены.`);
      onChanged(); void load();
    } catch (e) { setMessage(e instanceof Error ? e.message : "Ошибка снятия"); }
    finally { setBusy(false); setConfirm(false); }
  }

  function start() {
    if (!data) return;
    const intent: Intent = { operation_id: "TT.PLACES." + crypto.randomUUID(), trip_id: tripId, st_number: stNumber, member_ids: [...chosen].sort((a, b) => a - b),
                             expected_source_hash: data.source_hash, reason: reason.trim() };
    try { localStorage.setItem(key, JSON.stringify(intent)); if (localStorage.getItem(key) !== JSON.stringify(intent)) throw new Error(); }
    catch { setMessage("Не удалось надёжно сохранить команду — она не отправлена."); return; }
    setPending(intent); void send(intent);
  }
  const onTrip = data?.places.filter(p => p.on_trip && !p.loaded && !p.shipped) ?? [];
  const pickFirst = (n: number) => setChosen(new Set(onTrip.slice(-n).map(p => p.member_id)));
  const locked = busy || disabled || pending !== null;
  return <div className="dispatch-place-removal" aria-label={`Места сборки ${stNumber}`}>
    <h4 title="Снять часть физических мест этой сборки с рейса" data-help-id="transport.places.remove">Снять выбранные места сборки {stNumber}</h4>
    <p className="dispatch-hint">Снятые места остаются на складе у того же получателя с прежними адресом, кодами, собственником и резервом. Погруженные и отгруженные места снять нельзя.</p>
    {pending === "damaged" && <p role="alert">Сохранённая команда повреждена; новое снятие заблокировано до разбора.</p>}
    {pending && pending !== "damaged" && <p role="status">Команда снятия {pending.member_ids.length} мест не подтверждена.{" "}
      <button type="button" title="Повторить сохранённую команду с тем же номером операции" data-help-id="transport.places.retry" disabled={busy} onClick={() => void send(pending)}>Повторить команду</button></p>}
    {error && <p role="alert">{error}</p>}
    {message && <p role="status">{message}</p>}
    {data && <>
      <p>В рейсе {data.on_trip} из {data.places.length} мест; можно снять {onTrip.length}.</p>
      <label title="Выбрать столько последних мест сборки" data-help-id="transport.places.count">Количество мест{" "}
        <input type="number" min={1} max={onTrip.length} value={count} disabled={locked} onChange={e => { setCount(e.target.value); const n = Number(e.target.value); if (Number.isInteger(n) && n > 0 && n <= onTrip.length) pickFirst(n); }} /></label>
      <div style={{ maxHeight: 240, overflowY: "auto", maxWidth: "100%" }}>
        <table className="dispatch-grid"><thead><tr><th></th><th>Место</th><th>Адрес</th><th>Кол-во</th><th>Состояние</th></tr></thead><tbody>
          {data.places.map(p => <tr key={p.member_id}>
            <td><input type="checkbox" title="Выбрать место для снятия" data-help-id="transport.places.pick" disabled={locked || !p.on_trip || p.loaded || p.shipped}
              checked={chosen.has(p.member_id)} onChange={() => setChosen(prev => { const next = new Set(prev); if (next.has(p.member_id)) next.delete(p.member_id); else next.add(p.member_id); return next; })} /></td>
            <td>{p.pallet_uid}</td><td>{p.address ?? "—"}</td><td>{p.quantity ?? "—"}</td>
            <td>{p.shipped ? "отгружено" : p.loaded ? "погружено" : p.on_trip ? "в рейсе" : p.other_trip ? `в рейсе №${p.other_trip}` : "на складе"}</td></tr>)}
        </tbody></table></div>
      <label>Основание <input value={reason} maxLength={500} disabled={locked} onChange={e => setReason(e.target.value)} /></label>
      {!confirm
        ? <button type="button" title="Проверить выбор перед снятием" data-help-id="transport.places.prepare" disabled={locked || chosen.size === 0 || reason.trim().length < 3} onClick={() => setConfirm(true)}>Снять выбранные ({chosen.size})</button>
        : <span role="group" aria-label="Подтверждение снятия">Снять {chosen.size} из {data.on_trip} мест с рейса №{tripId}?{" "}
            <button type="button" title="Снять выбранные места с рейса" data-help-id="transport.places.confirm" disabled={locked} onClick={start}>Подтвердить</button>{" "}
            <button type="button" title="Не снимать" data-help-id="transport.places.cancel" disabled={busy} onClick={() => setConfirm(false)}>Отмена</button></span>}
      {" "}<button type="button" title="Перечитать места и версию состава" data-help-id="transport.places.reload" disabled={busy} onClick={() => void load()}>Перечитать</button>
    </>}
  </div>;
}
