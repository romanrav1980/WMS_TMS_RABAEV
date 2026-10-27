import { useState } from "react";
import { currentSessionCredentials } from "../api";
import { journal, useCommand } from "../features/integrations";
import { HelpButton, openHelpArticle, useApiRead } from "../features/platform";

// C-0176: снять выбранные физические места одной сборки (СТ) с рейса; остальные места сборки остаются в рейсе.
// Команда сохраняется общим журналом до отправки и повторяется тем же телом; ключ — пользователь и рейс. Компонент монтируется
// заново при смене рейса или сборки (key), поэтому поздний ответ прежнего контекста не меняет новый экран.
type Place = { member_id: number; pallet_uid: string; address: string | null; on_trip: boolean; other_trip: number | null; loaded: boolean; shipped: boolean };
type Places = { trip_id: number; st_number: string; on_trip: number; places: Place[]; source_hash: string };
type Body = { operation_id: string; trip_id: number; st_number: string; member_ids: number[]; expected_source_hash: string; reason: string };
type Receipt = { operation_id: string; trip_id: number; st_number: string; removed: number[]; on_trip_after: number };

export const PLACE_REMOVAL_ARTICLE = "trip-place-removal";
const pending = journal<Body>("trip-place-removal", "TT.PLACES", b => Number.isSafeInteger(b.trip_id) && b.trip_id > 0 && Array.isArray(b.member_ids)
  && b.member_ids.length > 0 && b.member_ids.every(Number.isSafeInteger) && /^[A-F0-9]{64}$/.test(b.expected_source_hash), "снятие мест");
const REASONS: Record<string, string> = {
  TRIP_MEMBERSHIP_SNAPSHOT_CHANGED: "состав мест рейса изменился после чтения — перечитайте список",
  TRIP_MEMBER_NOT_ON_TRIP: "выбранное место уже не в этом рейсе",
  LOADED_ST_REASSIGNMENT_FORBIDDEN: "место уже погружено — сначала выгрузите его",
  SHIPPED_ST_REASSIGNMENT_FORBIDDEN: "место уже отгружено",
  TRIP_MEMBERSHIP_CHANGE_FORBIDDEN: "рейс отгружен, удалён или включён в счёт",
  ST_WAREHOUSE_REQUIRED: "у места сборки не указан склад",
  OPERATION_CONFLICT: "этот номер операции уже связан с другим запросом",
  ACCESS_DENIED: "нет права диспетчера на склад этого рейса",
  TRADE_OWNER_ACCESS_DENIED: "нет права работы с товаром собственника этих мест",
};
const help = (id: string, text: string) => ({ id: "transport.places." + id, text, article: PLACE_REMOVAL_ARTICLE });

export function TransportStPlaceRemoval({ tripId, stNumber, disabled, onChanged }: { tripId: number; stNumber: string; disabled: boolean; onChanged: () => void }) {
  const user = (() => { try { return currentSessionCredentials().username; } catch { return ""; } })();
  const [reload, setReload] = useState(0), [chosen, setChosen] = useState<Set<number>>(new Set());
  const [count, setCount] = useState(""), [reason, setReason] = useState(""), [confirm, setConfirm] = useState(false);
  const read = useApiRead<Places>(`/api/transport/trips/${tripId}/sts/${encodeURIComponent(stNumber)}/places`, reload);
  const cmd = useCommand<Body, Receipt>(pending, `/api/transport/trips/${tripId}/place-removals`, user, "trip:" + tripId, REASONS,
    (r, b) => r.operation_id !== b.operation_id || r.trip_id !== b.trip_id || r.st_number !== b.st_number ? null
      : `Снято мест: ${r.removed.length}. В рейсе осталось мест этой сборки: ${r.on_trip_after}. Товар, резерв, адреса и коды не изменены.`,
    { path: b => `/api/transport/trips/${b.trip_id}/place-removals`, payload: ({ trip_id: _trip, ...b }) => b });
  const data = read.data, stored = cmd.stored;
  const after = () => { setChosen(new Set()); setConfirm(false); setReload(n => n + 1); onChanged(); };
  const removable = data?.places.filter(p => p.on_trip && !p.loaded && !p.shipped) ?? [];
  const locked = cmd.busy || disabled || stored.kind !== "none";
  const toggle = (id: number) => setChosen(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  return <div className="dispatch-place-removal" aria-label={`Места сборки ${stNumber}`}>
    <h4>Снять выбранные места сборки {stNumber}{" "}
      <HelpButton help={help("guide", "Открыть порядок выборочного снятия мест: что остаётся в рейсе и на складе, когда снятие недоступно.")}
        onClick={() => openHelpArticle(PLACE_REMOVAL_ARTICLE)}>?</HelpButton></h4>
    <p className="dispatch-hint">Снятые места остаются на складе у того же получателя с прежними адресом, кодами, собственником и резервом. Погруженные и отгруженные места снять нельзя.</p>
    {stored.kind === "damaged" && <p role="alert">Сохранённая команда повреждена; новое снятие заблокировано до разбора.</p>}
    {stored.kind === "ok" && <p role="status">Команда снятия {stored.intent.body.member_ids.length} мест рейса №{stored.intent.body.trip_id} не подтверждена.{" "}
      <HelpButton help={help("retry", "Повторить сохранённую команду с тем же номером операции и версией состава; новая операция не создаётся.")}
        disabled={cmd.busy} onClick={() => { if (stored.kind === "ok") void cmd.send(stored.intent, after); }}>Повторить команду</HelpButton></p>}
    {cmd.msg && <p role="status">{cmd.msg.text}</p>}
    {read.error && <p role="alert">{read.error}</p>}
    {data && <>
      <p>В рейсе {data.on_trip} из {data.places.length} мест; можно снять {removable.length}.</p>
      <label>Количество мест{" "}
        <input type="number" min={1} max={removable.length} value={count} disabled={locked} title="Выбрать столько последних мест сборки"
          onChange={e => { setCount(e.target.value); const n = Number(e.target.value); if (Number.isInteger(n) && n > 0 && n <= removable.length) setChosen(new Set(removable.slice(-n).map(p => p.member_id))); }} /></label>
      <div style={{ maxHeight: 240, overflow: "auto", maxWidth: "100%" }}>
        <table className="dispatch-grid"><thead><tr><th></th><th>Место</th><th>Адрес</th><th>Состояние</th></tr></thead><tbody>
          {data.places.map(p => <tr key={p.member_id}>
            <td><input type="checkbox" title="Выбрать место для снятия" disabled={locked || !p.on_trip || p.loaded || p.shipped}
              checked={chosen.has(p.member_id)} onChange={() => toggle(p.member_id)} /></td>
            <td>{p.pallet_uid}</td><td>{p.address ?? "—"}</td>
            <td>{p.shipped ? "отгружено" : p.loaded ? "погружено" : p.on_trip ? "в рейсе" : p.other_trip ? `в рейсе №${p.other_trip}` : "на складе"}</td></tr>)}
        </tbody></table></div>
      <label>Основание <input value={reason} maxLength={500} disabled={locked} onChange={e => setReason(e.target.value)} /></label>
      {!confirm
        ? <HelpButton help={help("prepare", "Проверить выбранные места перед снятием. Ничего не меняется до подтверждения.")}
            disabled={locked || chosen.size === 0 || reason.trim().length < 3} onClick={() => setConfirm(true)}>Снять выбранные ({chosen.size})</HelpButton>
        : <span role="group" aria-label="Подтверждение снятия">Снять {chosen.size} из {data.on_trip} мест с рейса №{tripId}?{" "}
            <HelpButton help={help("confirm", "Снять выбранные места с рейса одной командой. Остальные места сборки остаются в рейсе.")} disabled={locked}
              onClick={() => cmd.start({ trip_id: tripId, st_number: stNumber, member_ids: [...chosen].sort((a, b) => a - b), expected_source_hash: data.source_hash, reason: reason.trim() }, after)}>Подтвердить</HelpButton>{" "}
            <HelpButton help={help("cancel", "Не снимать места; выбор остаётся.")} disabled={cmd.busy} onClick={() => setConfirm(false)}>Отмена</HelpButton></span>}
      {" "}
    </>}
    <HelpButton help={help("reload", "Перечитать места и версию состава рейса. Сохранённая команда не меняется.")} disabled={cmd.busy || read.loading}
      onClick={() => setReload(n => n + 1)}>Перечитать</HelpButton>
  </div>;
}
