import { Fragment } from "react";
import type { ReactElement } from "react";
import { HelpButton } from "../../help/HelpButton";
import { appLink, rawLink, openShift } from "../OpsParts";
import { wsHelp } from "../help";
import { ganttHelp } from "./ganttHelp";
import { buildRows, fmtAxis, fmtTime, nowAxis, stateNow, zoneKnown } from "./timelineModel";
import type { Bar, Row } from "./timelineModel";
import { RESOURCE_TYPES } from "./timelineTypes";
import type { GanttSelection, ObjectLink, ResourceTimeline } from "./timelineTypes";

export function openLink(link: ObjectLink) {
  if (!link) return;
  if (link.page === "shift-supervisor-wave.html") { openShift(Number(link.params?.wave_id)); return; }
  const q = Object.entries(link.params ?? {}).map(([k, v]) => `&${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join("");
  location.href = link.page.endsWith(".html") ? rawLink(link.page) + (q ? "?" + q.slice(1) : "") : appLink(link.page, q);
}
const LEGACY: Record<string, string> = { plan_start: "План начало (старое)", plan_finish: "План конец (старое)", fact_start: "Факт начало (старое)", fact_finish: "Факт конец (старое)" };
const typeShort = (t: string) => RESOURCE_TYPES.find(x => x.id === t)?.short ?? t;
const ROLE: Record<string, string> = { EXECUTOR: "исполнитель", EQUIPMENT: "техника", DOCK: "ворота", VEHICLE: "машина" };
const STATUS: Record<string, string> = { NEW: "Новое", PLANNED: "Запланировано", ASSIGNED: "Назначено", IN_PROGRESS: "В работе",
  DONE: "Выполнено", CANCELLED: "Отменено", SHIPPED: "Отгружено", CONTROLLED: "Проверено", READY_TO_SHIP: "Готово к отгрузке",
  WAIT_CONTROL: "Ожидает контроля", CONTROL_IN_PROGRESS: "Идёт контроль", PICKED: "Собрано", PARTIAL: "Собрано частично", WAIT_REPLENISHMENT: "Ожидает пополнения", FAILED: "Ошибка",
  EXPECTED: "Ожидается", ARRIVED: "На площадке", AT_DOCK: "У ворот", WORKING: "Идёт работа", WORK_DONE: "Работа закончена, не выехала", DEPARTED: "Выехала" };
const SOURCE: Record<string, string> = { RRL_TT_HU_LOAD_FACT: "Журнал погрузки", RRL_WAREHOUSE_TASK: "Складские задания",
  RRL_CASE_PICK_TASK: "Задания сборки", RRL_TT_OPERATIONS: "Операции рейса", RRL_WORKLOAD_ATTENDANCE: "План выхода", RRL_YARD_VISIT: "Визиты двора" };
const when = (b: Bar) => b.point ? b.open ? `с ${fmtAxis(b.start, true)}, окончание не задано` : `подтверждённый момент ${fmtAxis(b.start, true)}` : `${fmtAxis(b.start, true)} — ${b.open ? "идёт" : fmtAxis(b.end, true)}`;

/** Карточка выбранного ресурса или работы. Одна работа показывает все свои ресурсы (одно событие, несколько привязок).
 *  onOpenWave — необязательная ссылка назад к карточке волны (есть только там, где её показывает вызывающее рабочее место). */
export function ResourceCard({ timeline, selection, onSelect, onOpenWave }: { timeline: ResourceTimeline; selection: GanttSelection; onSelect: (s: GanttSelection) => void; onOpenWave?: (id: number) => void }) {
  if (!selection) return <section className="ops-card"><h3>Объект не выбран</h3><p className="ops-note">Выберите ресурс или работу на схеме, в Ганте или в очереди.</p></section>;
  const rows = buildRows(timeline), tz = zoneKnown(timeline) ? timeline.warehouse.time_zone : null;
  const close = <HelpButton help={wsHelp.closeCard} onClick={() => onSelect(null)} aria-label="Закрыть карточку">×</HelpButton>;
  if (selection.kind === "resource") {
    const row = rows.find(r => r.resource.resource_key === selection.key);
    return row ? <ResourceView row={row} tz={tz} now={nowAxis(timeline)} close={close} onSelect={onSelect} /> : <Missing close={close} />;
  }
  const event = timeline.events.find(e => e.event_id === selection.id);
  if (!event) return <Missing close={close} />;
  const links = rows.flatMap(r => r.bars.filter(b => b.event.event_id === event.event_id).map(b => ({ r, b })));
  const unbound = timeline.bindings.filter(b => b.event_id === event.event_id && !rows.some(r => r.resource.resource_key === b.resource_key));
  // Назначение есть, но времени на оси нет: ресурс показывается, работа не выдаётся за «без ресурса».
  const untimed = rows.filter(r => r.untimed.some(e => e.event_id === event.event_id));
  const total = links.length + unbound.length + untimed.length;
  return <section className="ops-card" aria-label={"Работа " + event.title}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span>{event.title}</span>{close}</h3>
    <dl>
      <dt>Состояние</dt><dd>{event.status ? STATUS[event.status] ?? "состояние не распознано" : "нет данных"}</dd>
      {event.wave_id != null && <><dt>Волна</dt><dd>{onOpenWave ? <HelpButton help={ganttHelp.openWave} onClick={() => onOpenWave(event.wave_id!)}>{event.wave_id}</HelpButton> : event.wave_id}</dd></>}
      {event.task_id != null && <><dt>Задание</dt><dd>{event.task_id}</dd></>}
      {event.trip_id != null && <><dt>Рейс</dt><dd>{event.trip_id}</dd></>}
      <dt>План</dt><dd>{event.plan_start_at ? `${fmtTime(tz, event.plan_start_at)} — ${event.plan_finish_at ? fmtTime(tz, event.plan_finish_at) : "окончание не задано"}` : "нет времени"}</dd>
      <dt>Факт</dt><dd>{event.fact_start_at && event.fact_start_at === event.fact_finish_at ? `подтверждено ${fmtTime(tz, event.fact_start_at)}` : event.fact_start_at ? `${fmtTime(tz, event.fact_start_at)} — ${event.fact_finish_at ? fmtTime(tz, event.fact_finish_at) : event.terminal || event.finish_unresolved ? "окончание не известно" : "идёт"}` : "нет отметки"}</dd>
      {event.quantity && <><dt>Количество</dt><dd>{event.quantity.value} {event.quantity.uom}</dd></>}
      <dt>Источник</dt><dd>{SOURCE[event.source] ?? "см. технические данные"}</dd>
      {(event.details ?? []).map(([k, v]) => <Fragment key={k}><dt>{k}</dt><dd>{v}</dd></Fragment>)}
      {Object.entries(event.legacy_time ?? {}).filter(([, v]) => v).map(([k, v]) => <Fragment key={k}><dt>{LEGACY[k] ?? k}</dt><dd>{String(v).replace("T", " ").slice(0, 16)} <small className="ops-note">местное время источника без пояса — на шкалу не ставится</small></dd></Fragment>)}
    </dl>
    <details className="ops-note"><summary title="Показать исходные идентификаторы события для обращения в поддержку">Технические данные</summary><p>{event.event_kind} · {event.event_id}<br />{event.source} · {event.status ?? "—"}</p></details>
    <h3>Ресурсы работы <small>{total}</small></h3>
    {total === 0 ? <p className="ops-note">Ресурс не назначен — работа в очереди «без ресурса».</p> :
      <ul className="ops-list">{links.map(({ r, b }) => <li key={b.key}>
        <span><b>{r.resource.code}</b> <small>{typeShort(r.resource.resource_type)} · {ROLE[b.binding.role] ?? b.binding.role} · {b.basis === "FACT" ? "факт" : "план"}</small><br /><small>{when(b)}{b.conflict ? " · пересечение" : ""}</small></span>
        <HelpButton help={ganttHelp.row} onClick={() => onSelect({ kind: "resource", key: r.resource.resource_key })}>Ресурс</HelpButton></li>)}
        {untimed.map(r => <li key={"u:" + r.resource.resource_key}>
          <span><b>{r.resource.code}</b> <small>{typeShort(r.resource.resource_type)}</small><br /><small>назначен, но времени на шкале нет — длительность не рассчитывается</small></span>
          <HelpButton help={ganttHelp.row} onClick={() => onSelect({ kind: "resource", key: r.resource.resource_key })}>Ресурс</HelpButton></li>)}
        {unbound.map(b => <li key={b.binding_id}><span><b>{b.resource_key}</b><br /><small>{ROLE[b.role] ?? b.role} · ресурс вне выборки или без доступа</small></span></li>)}</ul>}
    <HelpButton help={ganttHelp.open} unavailable={!event.link && "у работы нет экрана-владельца в контракте"} onClick={() => openLink(event.link)}>Открыть работу</HelpButton>
  </section>;
}

function ResourceView({ row, tz, now, close, onSelect }: { row: Row; tz: string | null; now: number | null; close: ReactElement; onSelect: (s: GanttSelection) => void }) {
  const r = row.resource, st = stateNow(row, now);
  return <section className="ops-card" aria-label={"Ресурс " + r.code}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span>{r.code}<br /><small>{typeShort(r.resource_type)}{r.name ? " · " + r.name : ""}</small></span>{close}</h3>
    <p><span className={"rg-state " + st.tone} style={{ display: "inline-block" }}>{st.label}</span> <small className="ops-note">{st.basis}</small></p>
    <dl>
      <dt>Склад/РЦ</dt><dd>{r.warehouse_name || r.warehouse_id}</dd>
      <dt>Зона</dt><dd>{r.zone_code ?? "нет данных"}</dd>
      {r.kind_raw && <><dt>Вид в источнике</dt><dd>{r.kind_raw}{r.source_state ? " · " + r.source_state : ""}</dd></>}
      <dt>Сигнал</dt><dd>{r.last_signal ? `${r.last_signal.state} · ${fmtTime(tz, r.last_signal.observed_at)} · ${r.last_signal.source}` : "нет сигнала"}</dd>
      <dt>Квалификации</dt><dd>{r.qualifications == null ? "нет данных" : r.qualifications.join(", ") || "не заданы"}</dd>
      <dt>Доступность</dt><dd>{row.availability.length ? row.availability.map(s => `${s.a.state} ${fmtAxis(s.start, true)}–${s.open ? "…" : fmtAxis(s.end)}`).join("; ") : "нет данных (не «свободен»)"}</dd>
      {row.sourceDown && <><dt>Источник</dt><dd className="ops-err">не ответил — состояние неизвестно</dd></>}
    </dl>
    <h3>Работы в окне <small>{row.bars.length}{row.conflicts ? ` · пересечений ${row.conflicts}` : ""}</small></h3>
    {row.bars.length === 0 ? <p className="ops-note">{row.untimed.length ? "На шкале работ нет: у назначенных работ нет времени." : "Назначений в окне нет по данным источников."}</p> :
      <ul className="ops-list">{row.bars.slice(0, 30).map(b => <li key={b.key}>
        <span><b>{b.event.title}</b> <small>{b.basis === "FACT" ? "факт" : "план"}{b.conflict ? " · пересечение" : ""}</small><br /><small>{when(b)}</small></span>
        <HelpButton help={ganttHelp.barPlan} onClick={() => onSelect({ kind: "event", id: b.event.event_id })}>Работа</HelpButton></li>)}</ul>}
    {row.untimed.length > 0 && <><h3 title={ganttHelp.queue.text}>Назначены без времени <small>{row.untimed.length}</small></h3>
      <ul className="ops-list">{row.untimed.slice(0, 30).map(e => <li key={e.event_id}>
        <span><b>{e.title}</b><br /><small>{Object.values(e.legacy_time ?? {}).some(Boolean) ? "время без часового пояса — на шкалу не ставится" : "время не задано"}{e.status ? " · " + e.status : ""}</small></span>
        <HelpButton help={ganttHelp.queue} onClick={() => onSelect({ kind: "event", id: e.event_id })}>Работа</HelpButton></li>)}</ul>
      {row.untimed.length > 30 && <p className="ops-note">Показано 30 из {row.untimed.length}.</p>}</>}
    <HelpButton help={ganttHelp.open} unavailable={!r.link && "у ресурса нет экрана-владельца в контракте"} onClick={() => openLink(r.link)}>Открыть ресурс</HelpButton>
  </section>;
}

function Missing({ close }: { close: ReactElement }) {
  return <section className="ops-card"><h3 style={{ display: "flex", justifyContent: "space-between" }}>Объект вне выборки{close}</h3>
    <p className="ops-note">Выбранного объекта нет в текущем окне или фильтре, либо к нему нет доступа.</p></section>;
}
