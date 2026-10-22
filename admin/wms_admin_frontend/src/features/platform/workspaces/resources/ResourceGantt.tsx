import { useEffect, useMemo, useState } from "react";
import { HelpButton } from "../../help/HelpButton";
import { ganttHelp } from "./ganttHelp";
import { axisMinutes, buildRows, fmtAxis, groupRows, nowAxis, stateNow, summarize, ticks, unscheduled, zoneKnown } from "./timelineModel";
import type { Bar, Filters, Group, Row } from "./timelineModel";
import { RESOURCE_TYPES } from "./timelineTypes";
import type { GanttSelection, ResourceTimeline, ResourceType } from "./timelineTypes";
import "./gantt.css";

const ZOOMS = [{ min: 120, label: "2 ч" }, { min: 240, label: "4 ч" }, { min: 480, label: "8 ч" }, { min: 720, label: "12 ч" }, { min: 1440, label: "сутки" }, { min: 0, label: "всё окно" }];
const ROW_CAP = 300;
const typeLabel = (t: ResourceType) => RESOURCE_TYPES.find(x => x.id === t)?.label ?? t;
const typeShort = (t: ResourceType) => RESOURCE_TYPES.find(x => x.id === t)?.short ?? t;

type Props = { timeline: ResourceTimeline; selection: GanttSelection; onSelect: (s: GanttSelection) => void; initialTypes?: ResourceType[];
  /** Внешний структурный фильтр «показать ресурсы и работы этой волны» по точному числовому wave_id (не текстовый поиск).
   *  Применяется при каждом новом token; ручной текстовый поиск (query) не трогает и не трогается этим фильтром. */
  waveFocus?: { waveId: number; label: string; token: number } };

/** Общий Гант ресурсов (C0074): одна шкала для ричтраков, комплектовщиков, ворот и машин; выбор общий со сценой и карточкой. */
export function ResourceGantt({ timeline, selection, onSelect, initialTypes, waveFocus }: Props) {
  const [filters, setFilters] = useState<Filters>({ types: new Set(initialTypes ?? RESOURCE_TYPES.map(t => t.id)), query: "", groupBy: "type", onlyConflicts: false, waveId: null, waveLabel: null });
  useEffect(() => { if (waveFocus) setFilters(f => ({ ...f, waveId: waveFocus.waveId, waveLabel: waveFocus.label })); }, [waveFocus?.token]);
  const clearWave = () => setFilters(f => ({ ...f, waveId: null, waveLabel: null }));
  const tz = zoneKnown(timeline) ? timeline.warehouse.time_zone : null;
  const from = axisMinutes(timeline.window.start_at, tz) ?? 0, to = axisMinutes(timeline.window.finish_at, tz) ?? from + 1440;
  const [zoom, setZoom] = useState(0);
  const [viewStart, setViewStart] = useState(from);
  useEffect(() => setViewStart(from), [from]);
  const span = zoom ? Math.min(zoom, to - from) : to - from;
  const view = { from: Math.max(from, Math.min(viewStart, to - span)), to: 0 }; view.to = view.from + span;
  const rows = useMemo(() => buildRows(timeline), [timeline]);
  const groups = useMemo(() => groupRows(rows, filters, typeLabel), [rows, filters]);
  // Очередь без времени/ресурса фильтруется тем же точным wave_id, когда фильтр волны активен.
  const queue = useMemo(() => unscheduled(timeline).filter(q => filters.waveId == null || q.event.wave_id === filters.waveId), [timeline, filters.waveId]);
  const visibleRows = groups.flatMap(g => g.rows);
  const sum = summarize(timeline, visibleRows);
  const now = nowAxis(timeline);
  const pan = (dir: number) => setViewStart(Math.max(from, Math.min(to - span, view.from + dir * span / 2)));
  return <section className="rg" aria-label="Общий Гант ресурсов" data-warehouse={timeline.warehouse.warehouse_id} data-window={timeline.window.start_at}>
    <GanttToolbar filters={filters} setFilters={setFilters} zoom={zoom} setZoom={setZoom} pan={pan} canPan={span < to - from} clearWave={clearWave} />
    <p className="rg-summary" aria-live="polite">
      Ресурсов {sum.resources} · работ {sum.events} (по event_id) · назначений {sum.bindings} · пересечений {sum.conflicts}{timeline.overlap_limit != null && (timeline.overlaps?.length ?? 0) >= timeline.overlap_limit ? ` (не меньше; предел сервера ${timeline.overlap_limit})` : ""}
      {sum.quantifiedEvents > 0 && ` · количество указано у ${sum.quantifiedEvents} работ (отдельно в карточках, без общего объёма разных товаров)`}
      {!tz && <b className="rg-tz-warn" title="Часовой пояс склада не подтверждён. Записи без часового пояса показаны в очереди; местные опоздания по ним не рассчитываются."> · время UTC</b>}
      {tz && <span> · время склада ({tz})</span>}
    </p>
    <GanttLegend />
    <div className="rg-body" role="grid" aria-rowcount={visibleRows.length}>
      <Axis view={view} now={now} />
      {groups.length === 0 && <p className="rg-empty">{filters.waveId != null ? "У этой волны нет видимых ресурсов/работ в текущем окне и фильтре." : "По фильтру ресурсов нет."}</p>}
      <GanttGroups groups={groups} view={view} now={now} selection={selection} onSelect={onSelect} waveId={filters.waveId} />
    </div>
    <UnscheduledQueue queue={queue} selection={selection} onSelect={onSelect} />
  </section>;
}

function GanttToolbar({ filters, setFilters, zoom, setZoom, pan, canPan, clearWave }: { filters: Filters; setFilters: (f: Filters) => void; zoom: number; setZoom: (z: number) => void; pan: (d: number) => void; canPan: boolean; clearWave: () => void }) {
  const toggle = (t: ResourceType) => { const next = new Set(filters.types); if (next.has(t)) next.delete(t); else next.add(t); setFilters({ ...filters, types: next }); };
  return <div className="rg-toolbar">
    {filters.waveId != null && <span className="ops-chip ship" title={ganttHelp.waveFilter.text} data-help-id={ganttHelp.waveFilter.id}>
      Волна {filters.waveLabel ?? filters.waveId}
      <HelpButton help={ganttHelp.waveFilterClear} onClick={clearWave} aria-label="Снять фильтр волны" style={{ marginLeft: 6 }}>×</HelpButton>
    </span>}
    <label className="rg-search">Поиск <input type="search" value={filters.query} onChange={e => setFilters({ ...filters, query: e.target.value })}
      placeholder="код, зона, задание, рейс" title={ganttHelp.search.text} data-help-id={ganttHelp.search.id} /></label>
    <div role="group" aria-label="Типы ресурсов" className="rg-seg">{RESOURCE_TYPES.map(t =>
      <button key={t.id} type="button" aria-pressed={filters.types.has(t.id)} title={ganttHelp.type.text} data-help-id={ganttHelp.type.id + "." + t.id} onClick={() => toggle(t.id)}>{t.label}</button>)}</div>
    <label>Группы <select value={filters.groupBy} onChange={e => setFilters({ ...filters, groupBy: e.target.value as Filters["groupBy"] })} title={ganttHelp.group.text} data-help-id={ganttHelp.group.id}>
      <option value="type">по типу</option><option value="warehouse">по складу/РЦ</option></select></label>
    <label className="rg-check"><input type="checkbox" checked={filters.onlyConflicts} onChange={e => setFilters({ ...filters, onlyConflicts: e.target.checked })} title={ganttHelp.conflicts.text} data-help-id={ganttHelp.conflicts.id} /> только пересечения</label>
    <div role="group" aria-label="Масштаб" className="rg-seg">{ZOOMS.map(z =>
      <button key={z.min} type="button" aria-pressed={zoom === z.min} title={ganttHelp.zoom.text} data-help-id={ganttHelp.zoom.id} onClick={() => setZoom(z.min)}>{z.label}</button>)}</div>
    <HelpButton help={ganttHelp.pan} unavailable={!canPan && "всё окно уже на экране"} onClick={() => pan(-1)} aria-label="Раньше">←</HelpButton>
    <HelpButton help={ganttHelp.pan} unavailable={!canPan && "всё окно уже на экране"} onClick={() => pan(1)} aria-label="Позже">→</HelpButton>
  </div>;
}

function GanttLegend() {
  return <div className="rg-legend" aria-label="Обозначения">
    <span><i className="rg-sw plan" />план</span><span><i className="rg-sw fact" />факт</span><span><i className="rg-sw open" />факт идёт (до момента чтения)</span>
    <span><i className="rg-sw point" />момент / нет окончания</span><span><i className="rg-sw conflict" />пересечение</span>
    <span><i className="rg-sw shift" />на смене</span><span><i className="rg-sw planned" />план выхода</span><span title={ganttHelp.unknown.text}><i className="rg-sw unknown" />нет данных ≠ свободен</span><span><i className="rg-sw down" />недоступен</span>
  </div>;
}

type View = { from: number; to: number };
const pct = (v: View, m: number) => `${((Math.max(v.from, Math.min(v.to, m)) - v.from) / (v.to - v.from)) * 100}%`;
const width = (v: View, s: number, e: number) => `${Math.max(0, (Math.min(v.to, e) - Math.max(v.from, s)) / (v.to - v.from)) * 100}%`;

function Axis({ view, now }: { view: View; now: number | null }) {
  const list = ticks(view.from, view.to);
  return <div className="rg-row rg-axis" role="row">
    <div className="rg-label" role="columnheader">Ресурс</div>
    <div className="rg-track" role="columnheader" aria-label={`Шкала ${fmtAxis(view.from, true)} — ${fmtAxis(view.to, true)}`}>
      {list.map(m => <span key={m} className={"rg-tick" + (m % 1440 === 0 ? " day" : "")} style={{ left: pct(view, m) }}>{fmtAxis(m, m % 1440 === 0 || m === list[0])}</span>)}
      {now != null && now >= view.from && now <= view.to && <span className="rg-now" style={{ left: pct(view, now) }} />}
    </div>
  </div>;
}

function GanttGroups({ groups, view, now, selection, onSelect, waveId }: { groups: Group[]; view: View; now: number | null; selection: GanttSelection; onSelect: (s: GanttSelection) => void; waveId: number | null }) {
  let budget = ROW_CAP;
  const total = groups.reduce((n, g) => n + g.rows.length, 0);
  return <>{groups.map(g => {
    const shown = g.rows.slice(0, Math.max(0, budget)); budget -= shown.length;
    if (!shown.length) return null;
    return <div key={g.key} role="rowgroup" aria-label={g.label}>
      <div className="rg-group">{g.label} <small>{g.rows.length}</small></div>
      {shown.map(r => <GanttRow key={r.resource.resource_key} row={r} view={view} now={now} selection={selection} onSelect={onSelect} waveId={waveId} />)}
    </div>;
  })}{total > ROW_CAP && <p className="rg-empty">Показано {ROW_CAP} из {total} ресурсов — уточните поиск или тип.</p>}</>;
}

function GanttRow({ row, view, now, selection, onSelect, waveId }: { row: Row; view: View; now: number | null; selection: GanttSelection; onSelect: (s: GanttSelection) => void; waveId: number | null }) {
  const r = row.resource, st = stateNow(row, now);
  const selected = selection?.kind === "resource" && selection.key === r.resource_key;
  // При активном фильтре волны на оси видны только бары этой волны (ряд остаётся из-за фактического совпадения хотя бы одного бара);
  // состояние «сейчас» слева считается по всем барам ресурса — иначе занятый другой волной ресурс мог бы ложно показаться свободным.
  const bars = row.bars.filter(b => b.end >= view.from && b.start <= view.to && (waveId == null || b.event.wave_id === waveId));
  return <div className={"rg-row" + (selected ? " selected" : "")} role="row">
    <button type="button" className="rg-label" role="rowheader" aria-pressed={selected} title={`${ganttHelp.row.text}\n${st.label}: ${st.basis}${row.untimed.length ? `\nНазначено работ без времени: ${row.untimed.length}` : ""}`} data-help-id={ganttHelp.row.id}
      onClick={() => onSelect({ kind: "resource", key: r.resource_key })}>
      <b>{r.code}</b><small>{typeShort(r.resource_type)}{r.zone_code ? " · " + r.zone_code : ""}{row.untimed.length ? ` · без времени ${row.untimed.length}` : ""}</small>
      <i className={"rg-state " + st.tone}>{st.label}</i>
    </button>
    <div className="rg-track unknown" title={ganttHelp.unknown.text}>
      {row.availability.map((s, i) => <span key={i} className={"rg-avail " + s.a.state.toLowerCase()} style={{ left: pct(view, s.start), width: width(view, s.start, s.open ? Math.max(s.start, now ?? s.start) : s.end) }}
        title={`${s.a.state === "ON_SHIFT" ? "На смене" : s.a.state === "PLANNED" ? "План выхода (присутствие не подтверждено)" : s.a.state === "OFF_SHIFT" ? "Не на смене" : s.a.state === "DOWN" ? "Недоступен" : "Нет данных"} · ${s.a.source}${s.a.reason ? " · " + s.a.reason : ""}${s.open ? " · окончание не задано" : ""}`} />)}
      {bars.map(b => <GanttBar key={b.key} bar={b} view={view} selection={selection} onSelect={onSelect} />)}
      {now != null && now >= view.from && now <= view.to && <span className="rg-now" style={{ left: pct(view, now) }} />}
    </div>
  </div>;
}

function GanttBar({ bar, view, selection, onSelect }: { bar: Bar; view: View; selection: GanttSelection; onSelect: (s: GanttSelection) => void }) {
  const e = bar.event, sel = selection?.kind === "event" && selection.id === e.event_id;
  const help = bar.point ? bar.open ? ganttHelp.point : ganttHelp.confirmedPoint : bar.basis === "FACT" ? ganttHelp.barFact : ganttHelp.barPlan;
  const when = bar.point ? bar.open ? `начало ${fmtAxis(bar.start, true)}, окончание не задано` : `подтверждённый момент ${fmtAxis(bar.start, true)}` : `${fmtAxis(bar.start, true)} — ${bar.open ? "идёт (на момент чтения " + fmtAxis(bar.end) + ")" : fmtAxis(bar.end, true)}`;
  const cls = ["rg-bar", bar.basis.toLowerCase(), bar.open && !bar.point ? "open" : "", bar.point ? "point" : "", bar.conflict ? "conflict" : "", sel ? "selected" : ""].join(" ");
  return <button type="button" className={cls} style={{ left: pct(view, bar.start), width: bar.point ? undefined : width(view, bar.start, bar.end) }}
    title={`${e.title} · ${bar.basis === "FACT" ? "факт" : "план"} · ${when}${e.status ? " · " + e.status : ""}${bar.conflict ? " · пересекается с другой работой ресурса" : ""}\n${help.text}`}
    data-help-id={help.id} aria-pressed={sel} onClick={() => onSelect({ kind: "event", id: e.event_id })}>
    <span>{e.title}</span>
  </button>;
}

function UnscheduledQueue({ queue, selection, onSelect }: { queue: ReturnType<typeof unscheduled>; selection: GanttSelection; onSelect: (s: GanttSelection) => void }) {
  return <section className="rg-queue" aria-label="Очередь без времени">
    <h4 title={ganttHelp.queue.text} data-help-id={ganttHelp.queue.id}>Без времени или без ресурса <small>{queue.length}</small></h4>
    {queue.length === 0 ? <p className="rg-empty">Все работы окна имеют время и ресурс.</p> :
      <ul>{queue.slice(0, 60).map(q => <li key={q.event.event_id}>
        <button type="button" aria-pressed={selection?.kind === "event" && selection.id === q.event.event_id} title={ganttHelp.queue.text} data-help-id={ganttHelp.queue.id}
          onClick={() => onSelect({ kind: "event", id: q.event.event_id })}>
          <b>{q.event.title}</b><small>{q.reason === "NO_TIME" ? "нет времени" : q.reason === "NO_ZONE" ? "время без пояса" : "нет ресурса"}{q.event.status ? " · " + q.event.status : ""}</small>
        </button></li>)}</ul>}
    {queue.length > 60 && <p className="rg-empty">Показано 60 из {queue.length}.</p>}
  </section>;
}
