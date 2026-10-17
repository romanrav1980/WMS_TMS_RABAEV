import { useEffect, useState } from "react";
import { readUrlWarehouse, writeUrlWarehouse } from "../useUrlWarehouse";
import { HelpButton } from "../../help/HelpButton";
import { SourceChips } from "./SourceChips";
import { WarehousePicker } from "./WarehousePicker";
import { ResourceCard } from "./ResourceCard";
import { ResourceGantt } from "./ResourceGantt";
import { ganttHelp } from "./ganttHelp";
import { MAX_HOURS, useResourceTimeline } from "./useResourceTimeline";
import type { TimelineWindow } from "./useResourceTimeline";
import type { GanttSelection, ResourceTimeline, ResourceType } from "./timelineTypes";

const startOfDayLocal = (day: string) => `${day}T00:00`;

/** Общий Гант на реальном API /api/resources/timeline: склад, интервал, Гант, карточка. Ответ для другого склада не показывается.
 *  onOpenWave/waveFocus — необязательная навигация к волне, подключается вызывающим рабочим местом (например, старшим смены).
 *  waveFocus — структурный фильтр по точному числовому wave_id (не текстовый поиск, см. C-0110).
 *  onTimeline — отдаёт уже прочитанный ответ вызывающему месту (например, для сопоставления сессии с ресурсом); не второй запрос/engine. */
export function ResourcePlanner({ day, reload, initialTypes, warehouseId: fixedWarehouse, selection, onSelect, onOpenWave, waveFocus, onTimeline }:
  { day: string; reload: number; initialTypes?: ResourceType[]; warehouseId?: string; selection: GanttSelection; onSelect: (s: GanttSelection) => void;
    onOpenWave?: (id: number) => void; waveFocus?: { waveId: number; label: string; token: number }; onTimeline?: (t: ResourceTimeline | null) => void }) {
  // Без склада от стола — склад из адреса (C0118): Гант директора/диспетчера/двора открывается на выбранном ранее складе.
  const [w, setW] = useState<TimelineWindow>(() => ({ warehouseId: fixedWarehouse ?? readUrlWarehouse(), startLocal: startOfDayLocal(day), hours: 24 }));
  const [tz, setTz] = useState<string | null>(null);
  // Интервал следует за датой шапки, пока пользователь не задал свой (C-0089): старые данные не подписываются новой датой.
  const [custom, setCustom] = useState(false);
  useEffect(() => { if (!custom) setW(old => ({ ...old, startLocal: startOfDayLocal(day), hours: 24 })); }, [day, custom]);
  // Склад, заданный столом (старший смены), управляет Гантом; иначе — собственный выбор.
  const win = fixedWarehouse != null ? { ...w, warehouseId: fixedWarehouse } : w;
  useEffect(() => setTz(null), [fixedWarehouse]); // пояс прежнего склада не применяется к новому
  const read = useResourceTimeline(win, tz, reload);
  // Ответ показывается только для своего запроса (склад + окно + пояс).
  const own = read.dataPath != null && read.dataPath === read.path;
  const data = own ? read.data : null;
  if (data && data.warehouse.time_zone !== tz) setTz(data.warehouse.time_zone);
  useEffect(() => { onTimeline?.(data); }, [data, onTimeline]);
  return <div className="rg-planner">
    <div className="rg-window">
      {fixedWarehouse == null ? <WarehousePicker capability="resource_timeline" value={w.warehouseId} onChange={id => { setTz(null); setW({ ...w, warehouseId: id }); writeUrlWarehouse(id); }} />
        : <span className="ops-note">склад {fixedWarehouse || "не выбран"} (выбран на рабочем месте)</span>}
      <label>Начало ({tz ?? "UTC"}) <input type="datetime-local" value={w.startLocal} onChange={e => { if (e.target.value) { setCustom(true); setW({ ...w, startLocal: e.target.value }); } }} title={ganttHelp.window.text} data-help-id={ganttHelp.window.id + ".start"} /></label>
      <label>Часов <input type="number" min={1} max={MAX_HOURS} value={w.hours} onChange={e => { setCustom(true); setW({ ...w, hours: Math.max(1, Math.min(MAX_HOURS, Number(e.target.value) || 1)) }); }}
        title={ganttHelp.window.text} data-help-id={ganttHelp.window.id + ".hours"} style={{ width: 80 }} /></label>
      <HelpButton help={ganttHelp.window} onClick={() => { setCustom(false); setW({ ...w, startLocal: startOfDayLocal(day), hours: 24 }); }}>Сутки {day}</HelpButton>
      {custom && <span className="ops-note">свой интервал — не следует за датой шапки</span>}
      {data && <span className="ops-note">{data.warehouse.time_zone ? `время склада ${data.warehouse.time_zone}` : "пояс РЦ не подтверждён — окно и ось в UTC"}</span>}
    </div>
    {!win.warehouseId && <p className="ops-note">Укажите склад или РЦ: Гант строится по одному объекту доступа.</p>}
    {read.error && <p className="ops-err">{read.error}{data && read.at ? ` Показан прежний ответ этого окна от ${read.at.toLocaleTimeString("ru-RU")}.` : ""}</p>}
    {win.warehouseId && read.loading && <p className="ops-note">Загрузка таймлайна…</p>}
    {data && <PlannerBody timeline={data} selection={selection} onSelect={onSelect} initialTypes={initialTypes} onOpenWave={onOpenWave} waveFocus={waveFocus} />}
  </div>;
}

export function PlannerBody({ timeline, selection, onSelect, initialTypes, onOpenWave, waveFocus }: { timeline: ResourceTimeline; selection: GanttSelection; onSelect: (s: GanttSelection) => void;
  initialTypes?: ResourceType[]; onOpenWave?: (id: number) => void; waveFocus?: { waveId: number; label: string; token: number } }) {
  return <>
    <SourceChips timeline={timeline} />
    <div className="rg-split">
      <ResourceGantt timeline={timeline} selection={selection} onSelect={onSelect} initialTypes={initialTypes} waveFocus={waveFocus} />
      <ResourceCard timeline={timeline} selection={selection} onSelect={onSelect} onOpenWave={onOpenWave} />
    </div>
  </>;
}
