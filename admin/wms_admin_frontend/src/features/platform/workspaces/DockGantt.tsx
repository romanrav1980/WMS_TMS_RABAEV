import { wsHelp } from "./help";
import type { GanttVehicle, Selection } from "./types";

// Лента операций рейсов по машинам (GET /api/admin/transport/vehicles/gantt). Время API — "YYYY-MM-DD HH:MM" без пояса,
// поэтому считается в минутах от 00:00 выбранной даты, без пересчёта пояса.
const GROUP: Record<string, { label: string; color: string }> = {
  DOCK_ASSIGN: { label: "склад", color: "#3d8bfd" }, WAIT_LOAD: { label: "склад", color: "#3d8bfd" }, LOADING: { label: "погрузка", color: "#5aa9ff" },
  CLOSE_GATE: { label: "склад", color: "#3d8bfd" }, DOCUMENTS: { label: "склад", color: "#3d8bfd" }, DEPART: { label: "выезд", color: "#2fbf71" },
  DRIVE: { label: "в пути", color: "#2fbf71" }, DRIVE_BACK: { label: "возврат", color: "#2fbf71" }, UNLOAD: { label: "разгрузка", color: "#f0a531" },
  LOAD_RETURNS: { label: "возвраты", color: "#a17cf0" }, RETURN_HANDOVER: { label: "возвраты", color: "#a17cf0" }, CLEAN_RETURNS: { label: "возвраты", color: "#a17cf0" }, REST: { label: "перерыв", color: "#7c8794" },
};
function minutes(stamp: string | null, day: string): number | null {
  const m = stamp ? /^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})/.exec(stamp) : null;
  if (!m) return null;
  const dayDiff = (Date.UTC(+m[1].slice(0, 4), +m[1].slice(5, 7) - 1, +m[1].slice(8, 10)) - Date.UTC(+day.slice(0, 4), +day.slice(5, 7) - 1, +day.slice(8, 10))) / 86400000;
  return dayDiff * 1440 + Number(m[2]) * 60 + Number(m[3]);
}
const hm = (v: number) => `${String(Math.floor(((v % 1440) + 1440) % 1440 / 60)).padStart(2, "0")}:${String(((v % 60) + 60) % 60).padStart(2, "0")}`;

export function DockGantt({ vehicles, day, isToday, selection, onSelect }: { vehicles: GanttVehicle[]; day: string; isToday: boolean; selection: Selection; onSelect: (s: Selection) => void }) {
  const spans = vehicles.flatMap(v => v.operations.map(o => [minutes(o.plan_start, day), minutes(o.plan_end, day)] as const)).filter((x): x is readonly [number, number] => x[0] !== null && x[1] !== null);
  if (spans.length === 0) return <p className="ops-note">Операций с плановым временем на эту дату нет.</p>;
  const now = new Date(), nowMin = now.getHours() * 60 + now.getMinutes();
  const from = Math.floor(Math.min(...spans.map(s => s[0]), isToday ? nowMin : Infinity) / 60) * 60;
  const to = Math.ceil(Math.max(...spans.map(s => s[1]), isToday ? nowMin + 30 : -Infinity) / 60) * 60;
  const span = Math.max(60, to - from), pos = (m: number) => `${((m - from) / span) * 100}%`;
  const ticks = Array.from({ length: Math.floor(span / 60) + 1 }, (_, i) => from + i * 60).filter((_, i, a) => a.length <= 13 || i % 2 === 0);
  return <div className="ops-gantt" role="group" aria-label="Операции рейсов по машинам">
    <div className="ops-gantt-axis"><div /><div>{ticks.map(t => <span key={t} style={{ left: pos(t) }}>{hm(t)}</span>)}</div></div>
    {vehicles.map(v => <div className="ops-gantt-row" key={v.vehicle_num + (v.vehicle_id ?? "")}>
      <div className="ops-gantt-label" title={v.vehicle_type ?? ""}>{v.vehicle_num}</div>
      <div className="ops-gantt-track">
        {v.operations.map(o => {
          const s = minutes(o.plan_start, day), e = minutes(o.plan_end, day);
          if (s === null || e === null) return null;
          const g = GROUP[o.operation_code] ?? { label: o.operation_code, color: "#93a6ba" };
          const active = selection?.kind === "trip" && selection.id === o.tt_id;
          const fact = minutes(o.fact_start, day);
          return <span key={o.op_id}>
            <button type="button" style={{ left: pos(s), width: `max(3px, ${((e - s) / span) * 100}%)`, background: g.color, outline: active ? "2px solid #e6eef6" : undefined }}
              title={`${wsHelp.ganttBar.text} Рейс ${o.tt_id} · ${g.label} (${o.operation_code}) · план ${hm(s)}–${hm(e)}${fact !== null ? " · факт " + hm(fact) : " · факта нет"}`}
              aria-label={`Рейс ${o.tt_id}, ${g.label}, план ${hm(s)}–${hm(e)}`} data-help-id={wsHelp.ganttBar.id} onClick={() => onSelect({ kind: "trip", id: o.tt_id })} />
            {fact !== null && <i className="ops-gantt-fact" style={{ left: pos(fact) }} />}
          </span>;
        })}
        {isToday && nowMin >= from && nowMin <= to && <i className="ops-gantt-now" style={{ left: pos(nowMin) }} />}
      </div>
    </div>)}
    <p className="ops-note">Время как в API (без пересчёта пояса). Цвет — этап: склад, погрузка, в пути, разгрузка, возвраты; светлая метка — факт начала.</p>
  </div>;
}
