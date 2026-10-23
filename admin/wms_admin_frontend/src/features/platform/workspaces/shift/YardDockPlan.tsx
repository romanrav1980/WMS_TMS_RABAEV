import { useMemo, useState } from "react";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { fmtTime } from "../resources/timelineModel";
import { shiftHelp } from "./help";
import { readPlanPending, savePlanPending, sendPlanPending } from "./yardCommands";
import type { PlanAction, PlanIntent } from "./yardCommands";
import { PLANNABLE, parsePlans, planDeviation, planRefusalText } from "./yardModel";
import type { DockPlan, DockPlans, YardVisit } from "./yardModel";

const DAY = 24 * 3600 * 1000;
const local = (iso: string) => { const d = new Date(iso); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16); };
const iso = (value: string) => new Date(value).toISOString();  // datetime-local в часовом поясе браузера → момент UTC
type Edit = { plan: DockPlan | null; action: PlanAction; visit: string; dock: string; from: string; to: string; reason: string } | null;

/** План ворот (C-0158): будущие интервалы ворот для визитов рядом с фактами двора. Пересечения, права и версии проверяет сервер. */
export function YardDockPlan({ wh, reload, visits, onGantt }: { wh: string; reload: number; visits: YardVisit[]; onGantt: (eventId: string) => void }) {
  const [local_, setLocal] = useState(0), [anchor] = useState(() => Date.now());
  const from = new Date(anchor - DAY).toISOString(), to = new Date(anchor + 6 * DAY).toISOString();  // окно сервера — не больше 7 суток
  const read = useApiRead<unknown>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/yard/dock-plans?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`, reload + local_);
  const parsed = useMemo((): { snap: DockPlans | null; error: string } => {
    if (read.data == null) return { snap: null, error: "" };
    try { return { snap: parsePlans(read.data, Number(wh)), error: "" }; } catch (e) { return { snap: null, error: (e as Error).message }; }
  }, [read.data, wh]);
  const [tick, setTick] = useState(0);
  const pending = useMemo(() => readPlanPending(wh), [wh, tick]), intent = pending.intent;
  const [edit, setEdit] = useState<Edit>(null), [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  const snap = parsed.snap, planned = new Set(snap?.plans.map(p => p.visit_id) ?? []);
  const free = visits.filter(v => PLANNABLE.has(v.state) && !planned.has(v.visit_id));
  const blocked = busy || Boolean(intent) || Boolean(pending.damaged);

  const run = async (make: () => PlanIntent) => {
    const retry = Boolean(readPlanPending(wh).intent);
    let next: PlanIntent;
    try { next = make(); } catch (e) { setMessage((e as Error).message); return; }
    setBusy(true); setMessage("");
    const result = await sendPlanPending(next, retry);
    setBusy(false); setTick(n => n + 1);
    if (result.kind === "ack") { setEdit(null); setMessage(next.action === "PLAN" ? "План ворот сохранён." : next.action === "MOVE" ? "План перенесён." : "План отменён."); }
    else setMessage(result.kind === "refused" ? planRefusalText(result.code) : result.message);
    setLocal(n => n + 1);
  };
  const submit = (e: NonNullable<Edit>) => run(() => e.action === "CANCEL"
    ? savePlanPending(wh, e.plan!.plan_id, "CANCEL", { expected_version: e.plan!.version, reason: e.reason.trim() })
    : savePlanPending(wh, e.plan?.plan_id ?? 0, e.action, { ...(e.action === "PLAN" ? { visit_id: Number(e.visit) } : { expected_version: e.plan!.version }),
        dock: e.dock.trim(), planned_from: iso(e.from), planned_to: iso(e.to) }));
  const valid = (e: NonNullable<Edit>) => e.action === "CANCEL" ? e.reason.trim().length >= 3
    : Boolean((e.action !== "PLAN" || e.visit) && e.dock.trim() && e.from && e.to && Date.parse(e.to) > Date.parse(e.from));

  return <div className="ops-yard-plan" aria-label="План ворот" title={shiftHelp.yardPlan.text} data-help-id={shiftHelp.yardPlan.id}>
    <h4>План ворот <HelpButton help={shiftHelp.yardPlanRefresh} onClick={() => setLocal(n => n + 1)}>Обновить план</HelpButton></h4>
    <p className="ops-note">План — намерение диспетчера, а не факт приезда и не гарантия свободных ворот. При опоздании план сам не пересчитывается.</p>
    {(read.error || parsed.error) && <p role="alert" className="ops-err">{read.error.includes("YARD_PLAN_NOT_AVAILABLE")
      ? "План ворот на сервере ещё не включён: планы неизвестны (это не «ворота свободны»)." : `План ворот не прочитан: ${read.error || parsed.error}`}</p>}
    {pending.damaged && <p role="alert" className="ops-err">{pending.damaged}</p>}
    {intent && <div role="status" className="ops-err">Команда плана «{intent.action === "PLAN" ? "запланировать" : intent.action === "MOVE" ? "перенести" : "отменить"}» не подтверждена.{" "}
      <HelpButton help={shiftHelp.yardPlanRetry} disabled={busy} onClick={() => run(() => intent)}>Повторить команду плана</HelpButton></div>}
    {message && <p role="status" className="ops-note">{message}</p>}
    {snap && snap.plans.length === 0 && <p className="ops-note">Планов ворот на ближайшие дни нет (планы недоступных владельцев не показываются).</p>}
    {snap && snap.plans.length > 0 && <ul className="ops-list">{snap.plans.map(p => {
      const dev = planDeviation(p, snap.observed_at, visits), own = edit?.plan?.plan_id === p.plan_id;
      return <li key={p.plan_id}><span>
        <b>Ворота {p.dock}</b> <small>{fmtTime(null, p.planned_from)}–{fmtTime(null, p.planned_to)} · визит {p.visit_id} · {p.visit_kind === "INBOUND" ? "приёмка" : `рейс ${p.trip_id ?? "?"}`} · {p.vehicle ?? "машина ?"}</small><br />
        <small>Факт: {p.arrived_at ? `приехала ${fmtTime(null, p.arrived_at)}` : "не приехала"}{p.docked_at ? ` · у ворот ${p.fact_dock} с ${fmtTime(null, p.docked_at)}` : ""}{p.departed_at ? ` · выехала ${fmtTime(null, p.departed_at)}` : ""}</small>
        {dev.length > 0 && <><br /><small className="ops-err">{dev.join("; ")}</small></>}
        {own && edit && <PlanForm edit={edit} setEdit={setEdit} free={[]} blocked={blocked || !valid(edit)} onSubmit={() => submit(edit)} />}
      </span>
      <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {PLANNABLE.has(p.visit_state) && <HelpButton help={shiftHelp.yardPlanMove} disabled={blocked}
          onClick={() => setEdit({ plan: p, action: "MOVE", visit: String(p.visit_id), dock: p.dock, from: local(p.planned_from), to: local(p.planned_to), reason: "" })}>Перенести</HelpButton>}
        <HelpButton help={shiftHelp.yardPlanCancel} disabled={blocked} onClick={() => setEdit({ plan: p, action: "CANCEL", visit: "", dock: "", from: "", to: "", reason: "" })}>Отменить план</HelpButton>
        <HelpButton help={shiftHelp.yardPlanGantt} onClick={() => onGantt("YARD_DOCK_PLAN:" + p.plan_id)}>План в Ганте</HelpButton>
      </span></li>;
    })}</ul>}
    {edit?.action === "PLAN" ? <PlanForm edit={edit} setEdit={setEdit} free={free} blocked={blocked || !valid(edit)} onSubmit={() => submit(edit)} />
      : <p><HelpButton help={shiftHelp.yardPlanSave} disabled={blocked || free.length === 0}
          onClick={() => setEdit({ plan: null, action: "PLAN", visit: free.length === 1 ? String(free[0].visit_id) : "", dock: free[0]?.planned_dock ?? "", from: "", to: "", reason: "" })}>Запланировать ворота</HelpButton>
        {free.length === 0 && <small> Нет визитов без плана, ожидающих ворота.</small>}</p>}
  </div>;
}

function PlanForm({ edit, setEdit, free, blocked, onSubmit }: { edit: NonNullable<Edit>; setEdit: (e: Edit) => void; free: YardVisit[]; blocked: boolean; onSubmit: () => void }) {
  const set = (patch: Partial<NonNullable<Edit>>) => setEdit({ ...edit, ...patch });
  const title = edit.action === "PLAN" ? "Запланировать" : edit.action === "MOVE" ? "Перенести план" : "Отменить план";
  return <form className="ops-yard-plan-form" style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "flex-end", marginTop: 6 }} onSubmit={e => { e.preventDefault(); if (!blocked) onSubmit(); }}>
    {edit.action === "CANCEL"
      ? <label>Причина отмены плана <input value={edit.reason} maxLength={500} onChange={e => set({ reason: e.target.value })} title={shiftHelp.yardPlanCancel.text} data-help-id={shiftHelp.yardPlanCancel.id} /></label>
      : <>
        {edit.action === "PLAN" && <label>Визит <select value={edit.visit} onChange={e => set({ visit: e.target.value })} title={shiftHelp.yardPlanVisit.text} data-help-id={shiftHelp.yardPlanVisit.id}>
          <option value="">выберите визит</option>
          {free.map(v => <option key={v.visit_id} value={v.visit_id}>Визит {v.visit_id} · {v.visit_kind === "INBOUND" ? "приёмка" : `рейс ${v.trip_id ?? "?"}`} · {v.vehicle ?? "машина ?"}</option>)}</select></label>}
        <label>Ворота <input value={edit.dock} maxLength={50} onChange={e => set({ dock: e.target.value })} title={shiftHelp.yardPlanDock.text} data-help-id={shiftHelp.yardPlanDock.id} /></label>
        <label>Начало <input type="datetime-local" value={edit.from} onChange={e => set({ from: e.target.value })} title={shiftHelp.yardPlanFrom.text} data-help-id={shiftHelp.yardPlanFrom.id} /></label>
        <label>Конец <input type="datetime-local" value={edit.to} onChange={e => set({ to: e.target.value })} title={shiftHelp.yardPlanTo.text} data-help-id={shiftHelp.yardPlanTo.id} /></label>
      </>}
    <HelpButton key={edit.action} help={edit.action === "CANCEL" ? shiftHelp.yardPlanCancel : edit.action === "MOVE" ? shiftHelp.yardPlanMove : shiftHelp.yardPlanSave} type="submit" disabled={blocked}>{title}</HelpButton>
    <HelpButton key="close" help={shiftHelp.yardPlanClose} type="button" onClick={() => setEdit(null)}>Закрыть</HelpButton>
  </form>;
}
