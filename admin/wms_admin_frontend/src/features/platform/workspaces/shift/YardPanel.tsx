import { useMemo, useState } from "react";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { fmtTime } from "../resources/timelineModel";
import { shiftHelp } from "./help";
import { YardDockPlan } from "./YardDockPlan";
import { readPending, savePending, sendPending } from "./yardCommands";
import type { YardIntent } from "./yardCommands";
import { ACTIONS, ACTION_TITLE, GROUPS, STATE_TITLE, conflicts, delay, missing, parseSnapshot, queue, refusalText } from "./yardModel";
import type { YardAction, YardSnapshot, YardVisit } from "./yardModel";

type Form = { visit: YardVisit; action: YardAction; value: string } | null;

/** Двор склада для старшего смены (C-0149): кто ожидается, кто ждёт ворот, кто у ворот, и переходы визита. */
export function YardPanel({ wh, reload, onGantt }: { wh: string; reload: number; onGantt: (eventId: string) => void }) {
  const [local, setLocal] = useState(0);
  const read = useApiRead<unknown>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/yard/visits?active=true`, reload + local);
  const parsed = useMemo((): { snap: YardSnapshot | null; error: string } => {
    if (read.data == null) return { snap: null, error: "" };
    try { return { snap: parseSnapshot(read.data, Number(wh)), error: "" }; } catch (e) { return { snap: null, error: (e as Error).message }; }
  }, [read.data, wh]);
  // Журнал команды читается из браузера при каждом изменении: переживает перезагрузку и смену вкладки.
  const [tick, setTick] = useState(0);
  const pending = useMemo(() => readPending(wh), [wh, tick]), intent = pending.intent;
  const pendingBody = intent ? JSON.parse(intent.wire) as { trip_id?: string; vehicle?: string; supply_ids?: string[] } : null;
  const [form, setForm] = useState<Form>(null), [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  const [trip, setTrip] = useState(""), [planned, setPlanned] = useState("");
  const [incoming, setIncoming] = useState(false), [supplies, setSupplies] = useState(""), [vehicle, setVehicle] = useState("");
  const supplyIds = supplies.split(/\r?\n/).map(s => s.trim()).filter(Boolean);

  const run = async (make: () => YardIntent) => {
    const retry = Boolean(readPending(wh).intent);
    let next: YardIntent;
    try { next = make(); } catch (e) { setMessage((e as Error).message); return; }
    setBusy(true); setMessage("");
    const result = await sendPending(next, retry);
    setBusy(false); setTick(n => n + 1);
    if (result.kind === "ack") { setForm(null); setTrip(""); setSupplies(""); setVehicle(""); setPlanned(""); if (next.action === "EXPECT") setIncoming(Array.isArray(JSON.parse(next.wire).supply_ids)); setMessage(`Выполнено: ${next.action === "EXPECT" ? "визит добавлен" : ACTION_TITLE[next.action]}.`); }
    else setMessage(result.kind === "refused" ? refusalText(result.code) : result.message);
    setLocal(n => n + 1);
  };
  const act = (v: YardVisit, action: YardAction, value = "") => run(() => savePending(wh, v.visit_id, v.version, action,
    action === "CANCEL" ? { reason: value.trim() } : action === "ASSIGN_DOCK" || action === "REASSIGN_DOCK" ? { dock: value.trim() } : {}));
  const expect = () => run(() => savePending(wh, 0, 0, "EXPECT", { ...(incoming ? { supply_ids: supplyIds, vehicle: vehicle.trim() } : { trip_id: trip.trim() }), ...(planned ? { planned_arrival_at: new Date(planned).toISOString() } : {}) }));
  const blocked = busy || Boolean(intent) || Boolean(pending.damaged);
  const snap = parsed.snap;
  const places = snap ? queue(snap.visits) : new Map<number, number>(), clash = snap ? conflicts(snap.visits) : new Map<number, string>();

  return <section className="ops-card ops-yard" aria-label="Двор" title={shiftHelp.yard.text} data-help-id={shiftHelp.yard.id}>
    <h3>Двор</h3>
    <p className="ops-note">{snap ? `Снимок сервера ${fmtTime(null, snap.observed_at)}` : read.loading ? "Загрузка…" : ""}{" "}
      <HelpButton help={shiftHelp.yardRefresh} onClick={() => setLocal(n => n + 1)}>Обновить</HelpButton></p>
    {(read.error || parsed.error) && <p role="alert" className="ops-err">{read.error.includes("YARD_NOT_AVAILABLE")
      ? "Учёт двора на сервере ещё не включён: визиты и занятость ворот неизвестны (это не «ворота свободны»)."
      : `Двор не прочитан: ${read.error || parsed.error}`}</p>}
    {pending.damaged && <p role="alert" className="ops-err">{pending.damaged}</p>}
    {intent && <div role="status" className="ops-err">Команда «{intent.action === "EXPECT" ? "добавить визит" : ACTION_TITLE[intent.action]}»{intent.visit_id ? ` визита ${intent.visit_id}` : ""} не подтверждена.{" "}
      {intent.action === "EXPECT" && pendingBody && <p style={{ overflowWrap: "anywhere" }}>{Array.isArray(pendingBody.supply_ids)
        ? `Приёмка машины ${pendingBody.vehicle ?? "?"} по основаниям: ${pendingBody.supply_ids.join(", ")}` : `Отгрузка по рейсу ${pendingBody.trip_id ?? "?"}`}</p>}
      <HelpButton help={shiftHelp.yardRetry} disabled={busy} onClick={() => run(() => intent)}>Повторить</HelpButton></div>}
    {message && <p role="status" className="ops-note">{message}</p>}
    {snap && GROUPS.map(state => {
      const rows = snap.visits.filter(v => v.state === state);
      return rows.length > 0 && <div key={state}><h4>{STATE_TITLE[state]} · {rows.length}</h4>
        <ul className="ops-list">{rows.map(v => {
          const d = delay(v, snap.observed_at), gaps = missing(v), conflict = clash.get(v.visit_id), place = places.get(v.visit_id);
          return <li key={v.visit_id}><span>
            <b>Визит {v.visit_id}</b> <small style={{ overflowWrap: "anywhere" }}>{v.visit_kind === "INBOUND" ? `приёмка: ${(v.supply_ids ?? []).join(", ")}` : `рейс ${v.trip_id ?? "?"}`} · {v.vehicle ?? "машина ?"} · {v.dock ? `ворота ${v.dock}` : v.planned_dock ? `план: ворота ${v.planned_dock}` : "ворота не назначены"}</small><br />
            {place != null && <small>очередь на ворота: {place} · </small>}
            {d && <small className={d.kind === "LATE" ? "ops-err" : undefined}>{d.kind === "LATE" ? `опаздывает на ${d.min} мин` : `ждёт ${d.min} мин`} · </small>}
            {v.planned_arrival_at && v.state === "EXPECTED" && <small>план {fmtTime(null, v.planned_arrival_at)}</small>}
            {conflict && <><br /><small className="ops-err">Конфликт: {conflict}</small></>}
            {gaps.length > 0 && <><br /><small>Нет данных: {gaps.join("; ")}</small></>}
            {form?.visit.visit_id === v.visit_id && <><br />
              <input aria-label={form.action === "CANCEL" ? "Причина отмены" : "Ворота"} value={form.value} onChange={e => setForm({ ...form, value: e.target.value })} />
              <HelpButton help={shiftHelp.yardConfirm} disabled={blocked || form.value.trim().length < (form.action === "CANCEL" ? 3 : 1)}
                onClick={() => act(v, form.action, form.value)}>{ACTION_TITLE[form.action]}</HelpButton></>}
          </span>
          <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {ACTIONS[v.state].map(a => <HelpButton key={a} help={shiftHelp.yardAction} disabled={blocked}
              onClick={() => a === "CANCEL" || a === "ASSIGN_DOCK" || a === "REASSIGN_DOCK" ? setForm({ visit: v, action: a, value: a === "CANCEL" ? "" : v.planned_dock ?? "" }) : act(v, a)}>{ACTION_TITLE[a]}</HelpButton>)}
            <HelpButton help={shiftHelp.yardGantt} onClick={() => onGantt("YARD_VISIT:" + v.visit_id)}>В Ганте</HelpButton>
          </span></li>;
        })}</ul></div>;
    })}
    {snap && snap.visits.length === 0 && <p className="ops-note">Активных визитов нет (визиты недоступных владельцев не показываются).</p>}
    {snap && <YardDockPlan wh={wh} reload={reload + local} visits={snap.visits} onGantt={onGantt} />}
    <h4>Ожидать машину</h4>
    <p><a href="/help/tradecase-documents.html#yard-inbound" target="_blank" rel="noopener" title="Открыть порядок записи машины и назначения ворот" data-help-id="shift.yard.inbound.help">Как зарегистрировать машину на приёмку</a></p>
    <label>Назначение визита{" "}<select aria-label="Назначение визита" title={shiftHelp.yardExpect.text} data-help-id={shiftHelp.yardExpect.id}
      value={incoming ? "INBOUND" : "OUTBOUND"} onChange={e => setIncoming(e.target.value === "INBOUND")}>
      <option value="OUTBOUND">Отгрузка по рейсу</option><option value="INBOUND">Приёмка поставки</option></select></label>
    {incoming ? <div><label>Основания поставки<textarea aria-label="Основания поставки" rows={3} maxLength={20200} style={{ width: "100%", boxSizing: "border-box" }}
      placeholder="По одному номеру полученного основания на строку" value={supplies} onChange={e => setSupplies(e.target.value)} /></label>
      <label>Номер машины<input aria-label="Номер машины" maxLength={50} value={vehicle} onChange={e => setVehicle(e.target.value)} /></label>
      <p className="ops-note">Выберите номера из <a href={`?page=tradecase&tc_wh=${encodeURIComponent(wh)}&tc_tab=SUPPLY`} target="_blank" rel="noopener" title="Открыть полученные поставки этого склада, сохранив форму визита" data-help-id="shift.yard.supplies">полученных документов поставки</a>. После приезда назначьте ворота; товар примите в рабочем месте приёмки.</p></div>
      : <p><input aria-label="Номер рейса" placeholder="рейс" value={trip} onChange={e => setTrip(e.target.value)} /></p>}
    <p><label>План приезда{" "}
      <input aria-label="План приезда" type="datetime-local" value={planned} onChange={e => setPlanned(e.target.value)} />{" "}
      </label><HelpButton help={shiftHelp.yardExpect} data-help-url="/help/tradecase-documents.html#yard-inbound" disabled={blocked || (incoming ? !vehicle.trim() || !supplyIds.length || supplyIds.length > 200 || supplyIds.some(s => s.length > 100) || new Set(supplyIds).size !== supplyIds.length : !trip.trim())} onClick={expect}>Добавить визит</HelpButton></p>
  </section>;
}
