import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { HelpButton } from "../help/HelpButton";
import { useApiRead } from "../access-admin";
import { apiOperationScope } from "../../../api";
import { useRecovery } from "./recovery/useRecovery";
import type { RecoveryRow } from "./recovery/recoveryModel";
import type { ReadState } from "../access-admin/useApiRead";
import { DockGantt } from "./DockGantt";
import { DockYardScene } from "./DockYardScene";
import { KpiTile, ResourceList, SourceStrip, TripCard } from "./OpsParts";
import type { CaseTask, GanttVehicle, Selection, Session, SupplyOrder, Trip, Wave } from "./types";
import { ResourcePlanner } from "./resources/ResourcePlanner";
import type { GanttSelection, ResourceType } from "./resources/timelineTypes";
import "./resources/gantt.css";

export type DeskData = { trips: ReadState<Trip[]>; gantt: ReadState<GanttVehicle[]>; waves: ReadState<Wave[]>; sessions: ReadState<Session[]>;
  caseTasks: ReadState<CaseTask[]>; supply: ReadState<SupplyOrder[]>; recovery: ReadState<RecoveryRow[]> };
export type ProcessItem = { key: string; title: string; sub: string };
/** Процесс: либо фильтр рейсов на схеме (filter), либо список своих объектов справа и переход к экрану-владельцу (list/owner). */
export type Process = { id: string; icon: string; title: string; sub: (d: DeskData) => string; count: (d: DeskData) => string;
  filter?: (t: Trip) => boolean; list?: (d: DeskData) => { read: ReadState<unknown>; items: ProcessItem[]; limit: number }; owner?: { label: string; href: string } };
export const LIMITS = { waves: 100, caseTasks: 200, supply: 100, recovery: 50 } as const;

/** Все чтения стола независимы: отказ одного источника (403/сеть) не скрывает остальные и не превращается в ноль. */
export function useDeskData(day: string, reload: number, withWarehouse: boolean): DeskData {
  const recovery = useRecovery(withWarehouse ? "all" : null, apiOperationScope(), reload);
  return {
    trips: useApiRead<Trip[]>(`/api/admin/transport/tasks?shipment_date=${day}&include_readiness=true`, reload),
    gantt: useApiRead<GanttVehicle[]>(`/api/admin/transport/vehicles/gantt?gantt_date=${day}`, reload),
    waves: useApiRead<Wave[]>(withWarehouse ? `/api/picking/waves?limit=${LIMITS.waves}` : null, reload),
    sessions: useApiRead<Session[]>("/api/resources/sessions", reload),
    caseTasks: useApiRead<CaseTask[]>(withWarehouse ? `/api/case-pick/tasks?scope=all&limit=${LIMITS.caseTasks}` : null, reload),
    supply: useApiRead<SupplyOrder[]>(withWarehouse ? `/api/integrations/sap/supply-orders?limit=${LIMITS.supply}` : null, reload),
    // Обзор директора: все разрешённые склады (без ware_id), типизированно и строго (C0117); это не выборка одного склада.
    recovery: { data: recovery.rows, error: recovery.error, loading: recovery.loading, at: recovery.at },
  };
}

function ProcessListCard({ process, data, onClose }: { process: Process; data: DeskData; onClose: () => void }) {
  const list = process.list?.(data);
  if (!list) return null;
  return <section className="ops-card" aria-label={process.title}>
    <h3>{process.title} <small>{list.read.data != null ? `показано ${list.items.length}${list.items.length >= list.limit ? `, выборка до ${list.limit}` : ""}` : ""}</small></h3>
    {list.read.error && <p className="ops-err">{list.read.error}</p>}
    {!list.read.data && !list.read.error && <p className="ops-note">Загрузка…</p>}
    {list.read.data != null && (list.items.length === 0 ? <p className="ops-note">В выборке ничего нет.</p> :
      <ul className="ops-list">{list.items.slice(0, 40).map(i => <li key={i.key}><span><b>{i.title}</b><br /><small>{i.sub}</small></span></li>)}</ul>)}
    <div className="aa-actions" style={{ marginTop: 10 }}>
      {process.owner && <HelpButton help={{ id: "workspace.process.owner." + process.id, text: `Открыть экран «${process.owner.label}», где выполняются действия этого этапа.`, article: "workspaces" }}
        onClick={() => window.open(process.owner?.href, "_blank")}>{process.owner.label}</HelpButton>}
      <HelpButton help={{ id: "workspace.process.close", text: "Закрыть список этапа.", article: "workspaces" }} onClick={onClose}>Закрыть</HelpButton>
    </div>
  </section>;
}

/** Стол в стиле цифрового двойника: плитки, процессы, схема ворот, выбранный объект, лента операций, ресурсы. */
export function TwinDesk({ day, isToday, data, kpis, processes, sceneTitle, extraLeft, resourceTypes, reload = 0 }: {
  day: string; isToday: boolean; data: DeskData; kpis: Parameters<typeof KpiTile>[0][]; processes: Process[]; sceneTitle: string; extraLeft?: ReactNode;
  /** Типы ресурсов общего Ганта внизу стола (C0074); не задано — Гант не показывается. */ resourceTypes?: ResourceType[]; reload?: number;
}) {
  const [ganttSel, setGanttSel] = useState<GanttSelection>(null);
  const [selection, setSelection] = useState<Selection>(null);
  const [processId, setProcessId] = useState<string | null>(null);
  const process = processes.find(p => p.id === processId);
  const trips = useMemo(() => (data.trips.data ?? []).filter(t => !process?.filter || process.filter(t)), [data.trips.data, process]);
  const trip = selection?.kind === "trip" ? (data.trips.data ?? []).find(t => t.ID === selection.id) : undefined;
  const vehicle = trip ? (data.gantt.data ?? []).find(v => v.operations.some(o => o.tt_id === trip.ID)) : undefined;
  const select = (s: Selection) => { setSelection(s); if (s && process?.list) setProcessId(null); };
  return <>
    <div className="ops-kpis">{kpis.map(k => <KpiTile key={k.label} {...k} />)}</div>
    <SourceStrip isToday={isToday} day={day} sources={[["Рейсы", data.trips], ["Операции", data.gantt], ["Волны", data.waves], ["Сборка", data.caseTasks],
      ["Поставки SAP", data.supply], ["Восстановления", data.recovery], ["Сессии", data.sessions]]} />
    <aside className="ops-panel ops-left" aria-label="Процессы">
      <h3>Процессы <small>{day}</small></h3>
      <ul className="ops-proc">{processes.map(p => <li key={p.id}>
        <button type="button" aria-pressed={processId === p.id}
          title={p.filter ? `Оставить на схеме только рейсы этапа «${p.title}». Повторное нажатие снимает фильтр.` : `Показать справа список «${p.title}» из выборки и переход к экрану этапа. Схема не фильтруется.`}
          data-help-id={"workspace.process." + p.id} onClick={() => { setProcessId(v => v === p.id ? null : p.id); if (p.list) setSelection(null); }}>
          <span className="ops-ico" aria-hidden="true">{p.icon}</span><span><b>{p.title}</b><small>{p.sub(data)}</small></span><span className="ops-count">{p.count(data)}</span>
        </button></li>)}</ul>
      {extraLeft}
      <p className="ops-note">Числа — объекты из выборки API на момент чтения; «—» — источник не прочитан или нет права, это не ноль. «N+» — выборка упёрлась в предел.</p>
    </aside>
    <section className="ops-panel ops-center" aria-label="Схема ворот и двора">
      <span className="ops-scene-title">Ворота и двор · {trips.length} рейсов{process?.filter ? ` · фильтр: ${process.title}` : ""}</span>
      {data.trips.error && !data.trips.data ? <p className="ops-err" style={{ padding: 40 }}>Рейсы не прочитаны: {data.trips.error}</p>
        : <DockYardScene trips={trips} selection={selection} onSelect={select} title={sceneTitle} />}
      {data.trips.data && trips.length === 0 && <p className="ops-scene-empty" role="status">{process?.filter ? `По фильтру «${process.title}» рейсов нет` : "Рейсов на эту дату нет"}</p>}
      <div className="ops-scene-legend"><span><i style={{ background: "#3d8bfd" }} />спланирован</span><span><i style={{ background: "#2fbf71" }} />отгружен</span>
        <span><i style={{ background: "#7c8794" }} />закрыт</span><span><i style={{ background: "#f0a531" }} />другое</span><span>схема здания условная; ворота — из рейсов</span></div>
    </section>
    <aside className="ops-panel ops-right" aria-label="Выбранный объект">
      {trip ? <TripCard trip={trip} vehicle={vehicle} day={day} onClose={() => setSelection(null)} />
        : process?.list ? <ProcessListCard process={process} data={data} onClose={() => setProcessId(null)} />
        : <p className="ops-note">Выберите машину на схеме или полосу на ленте — здесь откроется карточка рейса. Этапы без фильтра схемы показывают здесь свой список.</p>}
    </aside>
    <div className="ops-bottom">
      <section className="ops-panel" aria-label="Лента операций"><h3>Операции рейсов по машинам: план и факт <small>{day}</small></h3>
        {data.gantt.error && <p className="ops-err">{data.gantt.error}</p>}{data.gantt.loading && !data.gantt.data && <p className="ops-note">Загрузка…</p>}
        {data.gantt.data && <DockGantt vehicles={data.gantt.data} day={day} isToday={isToday} selection={selection} onSelect={select} />}</section>
      <ResourceList read={data.sessions} />
    </div>
    {resourceTypes && <section className="ops-panel" style={{ gridColumn: "1/-1" }} aria-label="Общий Гант ресурсов">
      <h3>Общий Гант ресурсов</h3>
      <ResourcePlanner day={day} reload={reload} selection={ganttSel} onSelect={setGanttSel} initialTypes={resourceTypes} />
    </section>}
  </>;
}
