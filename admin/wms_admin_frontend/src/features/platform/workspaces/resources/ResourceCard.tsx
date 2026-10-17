import { Fragment } from "react";
import type { ReactElement } from "react";
import { HelpButton } from "../../help/HelpButton";
import { appLink, rawLink } from "../OpsParts";
import { wsHelp } from "../help";
import { ganttHelp } from "./ganttHelp";
import { buildRows, fmtAxis, fmtTime, nowAxis, stateNow, zoneKnown } from "./timelineModel";
import type { Bar, Row } from "./timelineModel";
import { RESOURCE_TYPES } from "./timelineTypes";
import type { GanttSelection, ObjectLink, ResourceTimeline } from "./timelineTypes";

export function openLink(link: ObjectLink) {
  if (!link) return;
  const q = Object.entries(link.params ?? {}).map(([k, v]) => `&${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join("");
  location.href = link.page.endsWith(".html") ? rawLink(link.page) + (q ? "?" + q.slice(1) : "") : appLink(link.page, q);
}
const LEGACY: Record<string, string> = { plan_start: "План начало (старое)", plan_finish: "План конец (старое)", fact_start: "Факт начало (старое)", fact_finish: "Факт конец (старое)" };
const typeShort = (t: string) => RESOURCE_TYPES.find(x => x.id === t)?.short ?? t;
const when = (b: Bar) => b.point ? `с ${fmtAxis(b.start, true)}, окончание не задано` : `${fmtAxis(b.start, true)} — ${b.open ? "идёт" : fmtAxis(b.end, true)}`;

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
  return <section className="ops-card" aria-label={"Работа " + event.title}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span>{event.title}<br /><small>{event.event_kind} · {event.event_id}</small></span>{close}</h3>
    <dl>
      <dt>Состояние</dt><dd>{event.status ?? "нет данных"}</dd>
      {event.wave_id != null && <><dt>Волна</dt><dd>{onOpenWave ? <HelpButton help={ganttHelp.openWave} onClick={() => onOpenWave(event.wave_id!)}>{event.wave_id}</HelpButton> : event.wave_id}</dd></>}
      {event.task_id != null && <><dt>Задание</dt><dd>{event.task_id}</dd></>}
      {event.trip_id != null && <><dt>Рейс</dt><dd>{event.trip_id}</dd></>}
      <dt>План</dt><dd>{event.plan_start_at ? `${fmtTime(tz, event.plan_start_at)} — ${event.plan_finish_at ? fmtTime(tz, event.plan_finish_at) : "окончание не задано"}` : "нет времени"}</dd>
      <dt>Факт</dt><dd>{event.fact_start_at ? `${fmtTime(tz, event.fact_start_at)} — ${event.fact_finish_at ? fmtTime(tz, event.fact_finish_at) : event.terminal || event.finish_unresolved ? "окончание не известно" : "идёт"}` : "нет отметки"}</dd>
      <dt>Количество</dt><dd>{event.quantity ? `${event.quantity.value} ${event.quantity.uom}` : "нет данных"}</dd>
      <dt>Источник</dt><dd>{event.source}</dd>
      {(event.details ?? []).map(([k, v]) => <Fragment key={k}><dt>{k}</dt><dd>{v}</dd></Fragment>)}
      {Object.entries(event.legacy_time ?? {}).filter(([, v]) => v).map(([k, v]) => <Fragment key={k}><dt>{LEGACY[k] ?? k}</dt><dd>{String(v).replace("T", " ").slice(0, 16)} <small className="ops-note">местное время источника без пояса — на шкалу не ставится</small></dd></Fragment>)}
    </dl>
    <h3>Ресурсы работы <small>{links.length + unbound.length}</small></h3>
    {links.length + unbound.length === 0 ? <p className="ops-note">Ресурс не назначен — работа в очереди «без ресурса».</p> :
      <ul className="ops-list">{links.map(({ r, b }) => <li key={b.key}>
        <span><b>{r.resource.code}</b> <small>{typeShort(r.resource.resource_type)} · {b.binding.role} · {b.basis === "FACT" ? "факт" : "план"}</small><br /><small>{when(b)}{b.conflict ? " · пересечение" : ""}</small></span>
        <HelpButton help={ganttHelp.row} onClick={() => onSelect({ kind: "resource", key: r.resource.resource_key })}>Ресурс</HelpButton></li>)}
        {unbound.map(b => <li key={b.binding_id}><span><b>{b.resource_key}</b><br /><small>{b.role} · ресурс вне выборки или без доступа</small></span></li>)}</ul>}
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
    {row.bars.length === 0 ? <p className="ops-note">Назначений в окне нет по данным источников.</p> :
      <ul className="ops-list">{row.bars.slice(0, 30).map(b => <li key={b.key}>
        <span><b>{b.event.title}</b> <small>{b.basis === "FACT" ? "факт" : "план"}{b.conflict ? " · пересечение" : ""}</small><br /><small>{when(b)}</small></span>
        <HelpButton help={ganttHelp.barPlan} onClick={() => onSelect({ kind: "event", id: b.event.event_id })}>Работа</HelpButton></li>)}</ul>}
    <HelpButton help={ganttHelp.open} unavailable={!r.link && "у ресурса нет экрана-владельца в контракте"} onClick={() => openLink(r.link)}>Открыть ресурс</HelpButton>
  </section>;
}

function Missing({ close }: { close: ReactElement }) {
  return <section className="ops-card"><h3 style={{ display: "flex", justifyContent: "space-between" }}>Объект вне выборки{close}</h3>
    <p className="ops-note">Выбранного объекта нет в текущем окне или фильтре, либо к нему нет доступа.</p></section>;
}
