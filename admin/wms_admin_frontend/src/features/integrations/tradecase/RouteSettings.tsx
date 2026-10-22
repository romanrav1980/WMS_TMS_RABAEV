import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, Tech } from "./ui";
import { RoadRefresh } from "./RoadRefresh";

type Setting = { operation_id: string; kind: "DEPOT" | "DURATION"; warehouse_id: number; trip_id: number;
  expected_version: number; reason: string; depot_address?: string; source_hash?: string;
  drive_min?: number; drive_back_min?: number; source_reference?: string };
type Receipt = { operation_id: string; warehouse_id?: number; trip_id?: number; version: number };
type Depot = { version: number; depot_address: string | null; configured: boolean };
const pending = journal<Setting>("route-setting", "TC.ROUTE.UI", b => Number.isSafeInteger(b.trip_id) && b.trip_id > 0
  && Number.isSafeInteger(b.warehouse_id) && b.warehouse_id > 0 && Number.isSafeInteger(b.expected_version)
  && typeof b.reason === "string" && (b.kind === "DEPOT" ? typeof b.depot_address === "string"
    : b.kind === "DURATION" && /^[a-f0-9]{64}$/.test(b.source_hash ?? "")
      && [b.drive_min, b.drive_back_min].every(n => Number.isInteger(n) && Number(n) > 0 && Number(n) <= 1440)), "настройка маршрута");
const help = (id: string, text: string) => ({ id: "tradecase.route." + id, text, anchor: "route" });
const reasons = { VERSION_CONFLICT: "Настройки изменились. Перечитайте данные перед новой командой.",
  TT_ROUTE_SOURCE_CHANGED: "Состав или условия рейса изменились. Перечитайте маршрут.",
  TT_ROUTE_PHYSICAL_EXECUTION_FROZEN: "Погрузка или выезд уже зарегистрированы. Пересчёт плановых операций запрещён.",
  TT_ROUTE_OPERATION_EXECUTION_FROZEN: "Исполнение операций началось. Пересчёт плана запрещён.",
  TT_ROUTE_PLANNED_UNBILLED_REQUIRED: "Изменить оценку можно только у спланированного рейса, по которому ещё не выставлен счёт.",
  TT_ROUTE_OPERATION_PAYLOAD_CONFLICT: "Этот номер операции уже связан с другим запросом. Исходная команда сохранена.",
  WARE_DEPOT_VERSION_CHANGED: "Адрес склада изменился. Перечитайте настройки перед новой командой.",
  WARE_DEPOT_EXISTING_GEOCODED_ADDRESS_REQUIRED: "Выберите действующий адрес из справочника с подтверждёнными координатами.",
  WARE_DEPOT_OPERATION_PAYLOAD_CONFLICT: "Этот номер операции уже связан с другим адресом склада. Исходная команда сохранена." };

/** Existing depot and route-input commands; the shared intent journal preserves unknown outcomes. */
export function RouteSettings({ wh, user, trip, version, sourceHash, refreshing, onSaved }: {
  wh: string; user: string; trip: number; version: number; sourceHash: string; refreshing: boolean; onSaved: () => void;
}) {
  const [reload, setReload] = useState(0), [depot, setDepot] = useState(""), [drive, setDrive] = useState(""),
    [back, setBack] = useState(""), [reference, setReference] = useState(""), [reason, setReason] = useState("");
  const current = useRead<Depot>(`/api/transport/warehouse-depots/${encodeURIComponent(wh)}`, reload);
  const cmd = useCommand<Setting, Receipt>(pending, "", user, wh, reasons, (r, b) =>
    r.operation_id !== b.operation_id || (b.kind === "DEPOT" ? r.warehouse_id !== b.warehouse_id : r.trip_id !== b.trip_id)
      ? null : b.kind === "DEPOT" ? "Адрес склада сохранён. Расчёт маршрута обновлён."
        : "Оценка времени сохранена, операции пересчитаны. Проверьте окна и утвердите время рейса заново.", {
    path: b => b.kind === "DEPOT" ? "/api/transport/warehouse-depots" : "/api/transport/preflight/route-inputs",
    payload: b => b.kind === "DEPOT" ? { operation_id: b.operation_id, warehouse_id: b.warehouse_id,
      expected_version: b.expected_version, depot_address: b.depot_address, reason: b.reason }
      : { operation_id: b.operation_id, trip_id: b.trip_id, expected_version: b.expected_version, source_hash: b.source_hash,
        drive_min: b.drive_min, drive_back_min: b.drive_back_min, source_reference: b.source_reference, reason: b.reason },
  });
  const locked = cmd.busy || refreshing || cmd.stored.kind !== "none";
  const after = () => { setReload(n => n + 1); onSaved(); };
  const base = { warehouse_id: Number(wh), trip_id: trip, reason: reason.trim() };
  return <details className="tc-panel"><summary title="Изменить адрес склада выезда или оценку длительности рейса" data-help-id="tradecase.route.settings">Настроить исходные данные маршрута</summary>
    {cmd.stored.kind === "damaged" && <p role="alert" className="tc-err">Сохранённая команда повреждена. Новая запись заблокирована.<Tech value={cmd.stored.raw} /></p>}
    {cmd.stored.kind === "ok" && <div className="tc-msg warn"><p>Команда рейса № {cmd.stored.intent.body.trip_id} не завершена. Повтор использует прежние поля и номер операции.</p>
      <Act help={help("retry", "Повторить сохранённую команду без изменения полей и номера операции.")} disabled={cmd.busy || cmd.stored.intent.body.trip_id !== trip}
        onClick={() => { if (cmd.stored.kind === "ok") void cmd.send(cmd.stored.intent, after); }}>Повторить ту же команду</Act></div>}
    {cmd.msg && <p role="status" className={"tc-msg " + cmd.msg.tone}>{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>}
    <label>Основание изменения <input value={reason} maxLength={500} disabled={locked} onChange={e => setReason(e.target.value)} /></label>
    <h5>Адрес склада выезда</h5>
    {current.error && <p role="alert" className="tc-err">Настройки склада не прочитаны: {current.error}</p>}
    {current.data && !current.error && <p>Сохранённый адрес: {current.data.depot_address ?? "не задан"}.</p>}
    <label>Новый адрес склада <input value={depot} maxLength={200} disabled={locked} onChange={e => setDepot(e.target.value)} /></label>
    <Act help={help("depot.save", "Сохранить адрес выезда выбранного склада. Адрес применяется к расчётам всех его рейсов; товар и рейсы не перемещаются.")}
      disabled={locked || current.loading || !!current.error || !current.data || !depot.trim() || reason.trim().length < 8}
      onClick={() => cmd.start({ ...base, kind: "DEPOT", expected_version: current.data!.version, depot_address: depot.trim() }, after)}>Сохранить адрес склада</Act>
    <h5>Оценка длительности рейса</h5>
    <RoadRefresh wh={wh} user={user} trip={trip} version={version} sourceHash={sourceHash} refreshing={refreshing} onSaved={after} />
    <label>К точкам доставки, мин <input type="number" min={1} max={1440} step={1} value={drive} disabled={locked} onChange={e => setDrive(e.target.value)} /></label>
    <label>Возврат на склад, мин <input type="number" min={1} max={1440} step={1} value={back} disabled={locked} onChange={e => setBack(e.target.value)} /></label>
    <label>Источник оценки <input value={reference} maxLength={500} disabled={locked} onChange={e => setReference(e.target.value)} /></label>
    <p className="tc-note">Оценка пересчитывает плановые операции рейса. Время каждого дорожного плеча и окна получателей проверяются отдельно. После начала погрузки или исполнения пересчёт запрещён.</p>
    <Act help={help("duration.save", "Сохранить оценку диспетчера и пересчитать операции рейса по текущему составу. После изменения проверьте окна и повторно утвердите время.")}
      disabled={locked || !Number.isInteger(version) || !sourceHash || reason.trim().length < 8 || reference.trim().length < 8
        || ![drive, back].every(n => Number.isInteger(Number(n)) && Number(n) > 0 && Number(n) <= 1440)}
      onClick={() => cmd.start({ ...base, kind: "DURATION", expected_version: version, source_hash: sourceHash,
        drive_min: Number(drive), drive_back_min: Number(back), source_reference: reference.trim() }, after)}>Сохранить оценку и пересчитать операции</Act>
    <Act help={help("refresh", "Перечитать версии настроек и текущее основание рейса. Сохранённая команда остаётся неизменной.")} disabled={cmd.busy} onClick={after}>Перечитать данные</Act>
  </details>;
}
