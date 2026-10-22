import { CapacityPreview } from "./CapacityPreview";
import { TopupPreview } from "./TopupPreview";
import { TopupProposals, useTopup } from "./TopupProposals";
import { TripRoute } from "./TripRoute";
import { useState } from "react";
import { RAW_ADMIN_BASE } from "../../../api";
import { executionPath, nativeTripPath, tcHelp, tripBindingPath } from "./api";
import type { BindingBody, DocCard, NativeTrip, TripExec } from "./api";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech, Time, str } from "./ui";

const bindingJournal = journal<BindingBody>("tripbind", "TC.TRIPBIND.UI", b => Number.isSafeInteger(b.native_task_id) && b.native_task_id > 0
  && Number.isSafeInteger(b.expected_trip_version) && Number.isSafeInteger(b.expected_binding_version), "привязку рейса");
const REASONS: Record<string, string> = { ACCESS_DENIED: "нет права привязки рейсов на этом складе", VERSION_CONFLICT: "рейс или привязка изменились — перечитайте карточку",
  OPERATION_CONFLICT: "номер операции уже использован с другими данными", OPERATION_CONTENT_CONFLICT: "номер операции уже использован с другими данными" };
const DOC: Record<string, string> = { READY: "транспортный документ готов", ERROR: "ошибка транспортного документа", REVOKED: "транспортный документ отозван", MISSING: "транспортного документа нет" };
const LOAD: Record<string, string> = { DEPARTED: "выехал", LOADED: "погружен", PLANNED: "запланирован" };
export const tripScreen = (nativeId: number) => `${RAW_ADMIN_BASE}/transport-loading.html?trip_id=${nativeId}`;

/** Фактическое исполнение внешнего рейса: привязка к рейсу склада, документ и погрузки. Документ ≠ доставка; очередь ≠ внешний документ. */
export function TripExecution({ wh, user, trip }: { wh: string; user: string; trip: DocCard }) {
  const [reload, setReload] = useState(0), [edit, setEdit] = useState(false), topup = useTopup(wh, user);
  const ex = useRead<TripExec>(executionPath(wh, trip.document_id), reload);
  const missing = Boolean(ex.error) && ex.error.includes("не найден");
  const e = ex.data;
  return <section className="tc-bind"><h4>Фактическое исполнение рейса <HelpLink anchor="trip" /></h4>
    {ex.loading && !e ? <p className="tc-note">Читаем исполнение…</p> : missing ? <p className="tc-note">Рейс ещё не привязан к погрузке. Сверьте номер и машину, затем привяжите рейс.</p>
      : ex.error ? <p className="tc-err" role="alert">{ex.error}</p> : e && <>
      <dl className="tc-fields">
        <dt>Фактический рейс склада</dt><dd>{e.native_task_id ? <>№ {e.native_task_id} · <a href={tripScreen(e.native_task_id)} target="_blank" rel="noopener" title="Открыть погрузку и выезд этого рейса в новой вкладке" data-help-id="tradecase.trip.open">открыть погрузку и выезд</a></> : "не привязан"}</dd>
        <dt>Актуальность</dt><dd>{e.basis_current ? "привязка к текущей версии рейса" : "рейс изменился после привязки — проверьте состав"} · состав {e.manifest_matched ? "совпадает с погрузкой" : "не совпадает с погрузкой"}</dd>
        <dt>Документ</dt><dd>{DOC[e.document_status] ?? "состояние документа неизвестно"}{e.external_document_id ? ` (${e.external_document_id})` : ""}{e.error_reason ? `: ${e.error_reason}` : ""}. Готовность документа не означает доставку.</dd>
        <dt>Версии</dt><dd>рейс {e.trip_version}, привязка {e.binding_version}{e.document_version ? `, документ ${e.document_version}` : ""}</dd>
      </dl>
      {e.loads.length > 0 && <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Погрузка</th><th>Место</th><th>Состояние</th><th>Выезд</th><th>Груз передан получателю</th></tr></thead>
        <tbody>{e.loads.map(l => <tr key={l.load_operation_id}><td>{l.load_operation_id}</td><td>{l.identifier}</td><td>{LOAD[l.status] ?? l.status}</td><td><Time value={l.departed_at} /></td><td>{l.custody_released ? "да" : "нет"}</td></tr>)}</tbody></table></div>}
      <Tech value={e} /></>}
    {e && !edit && <Act help={tcHelp.rebindTrip} onClick={() => setEdit(true)}>Изменить привязку</Act>}
    {(missing || edit) && <BindForm wh={wh} user={user} trip={trip} bindingVersion={e?.binding_version ?? 0} onDone={() => { setEdit(false); setReload(n => n + 1); }} />}
    <TripRoute wh={wh} user={user} trip={trip.document_id} nativeTask={e?.native_task_id ?? null} bindingState={ex.loading && !e ? "LOADING" : ex.error && !missing ? "UNAVAILABLE" : "KNOWN"} />
    <CapacityPreview wh={wh} trip={trip.document_id} />
    <TopupPreview wh={wh} trip={trip.document_id} saveLocked={topup.cmd.stored.kind !== "none" || topup.cmd.busy}
      onSave={(needIds, age) => topup.cmd.start({ action: "SAVE", trip: trip.document_id, need_ids: needIds, max_age_minutes: age }, topup.refresh)} />
    <TopupProposals wh={wh} trip={trip.document_id} topup={topup} />
  </section>;
}

/** Сверка фактического рейса через существующий транспортный GET, затем явная привязка. Транспортный документ кнопкой не создаётся. */
function BindForm({ wh, user, trip, bindingVersion, onDone }: { wh: string; user: string; trip: DocCard; bindingVersion: number; onDone: () => void }) {
  const [input, setInput] = useState(""), [checked, setChecked] = useState<number | null>(null);
  const native = useRead<NativeTrip>(checked ? nativeTripPath(checked) : null);
  const cmd = useCommand<BindingBody, { native_task_id?: number; binding_version?: number }>(bindingJournal, tripBindingPath(wh, trip.document_id), user, wh, REASONS,
    (r, b) => r.native_task_id === undefined || r.native_task_id === b.native_task_id ? `Внешний рейс ${trip.document_id} привязан к рейсу склада № ${b.native_task_id}.` : null);
  const s = cmd.stored, vehicle = str(trip.payload.vehicle_id), n = native.data;
  const note = cmd.msg && <p className={"tc-msg " + cmd.msg.tone} role="status">{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>;
  if (s.kind === "damaged") return <div className="tc-msg bad">Сохранённая команда привязки повреждена; новая не создаётся.<Tech value={s.raw} /></div>;
  if (s.kind === "ok") return <div className="tc-bind warn"><p>Сохранённая команда привязки к рейсу склада № {s.intent.body.native_task_id}. {s.intent.sent ? "Результат не подтверждён." : "Ещё не отправлена."} Данные не меняются.</p>
    <Act help={tcHelp.retry} disabled={cmd.busy} onClick={() => cmd.send(s.intent, onDone)}>Повторить ту же команду</Act>{note}</div>;
  return <div className="tc-bindform">
    <form onSubmit={ev => { ev.preventDefault(); const v = Number(input); if (Number.isSafeInteger(v) && v > 0) setChecked(v); }}>
      <label>Номер фактического рейса склада<input value={input} inputMode="numeric" onChange={ev => { setInput(ev.target.value.replace(/\D/g, "")); setChecked(null); }} title="Номер рейса из экрана погрузки и выезда" data-help-id="tradecase.trip.native" /></label>
      <button type="submit" disabled={!input} title={tcHelp.checkTrip.text} data-help-id={tcHelp.checkTrip.id}>Сверить</button></form>
    {native.error && <p className="tc-err" role="alert">{native.error}</p>}
    {n && <div className="tc-review"><p>Рейс склада № {n.ID}: машина <b>{str(n.TRANSPORT)}</b>, ворота {str(n.DOCK)}, состояние «{str(n.CONDITION)}», водитель {str(n.VODITEL_NAME)}. Во внешнем рейсе машина <b>{vehicle}</b>.</p>
      {str(n.TRANSPORT) !== vehicle && <p className="tc-msg warn">Машина не совпадает с внешним рейсом. Проверьте номер рейса; сервер тоже сверит привязку.</p>}
      <Act help={tcHelp.bindTrip} disabled={cmd.busy} onClick={() => cmd.start({ native_task_id: n.ID, expected_trip_version: trip.document_version, expected_binding_version: bindingVersion }, onDone)}>Привязать рейс</Act></div>}
    {note}</div>;
}
