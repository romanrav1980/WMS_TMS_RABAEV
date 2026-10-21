import { HelpButton } from "../help/HelpButton";
import { formatMoment } from "../access-admin";
import { wsHelp } from "./help";
import { stageMeta, stageOf } from "./recovery/recoveryModel";
import { rawLink } from "./OpsParts";
import { LIMITS, TwinDesk, useDeskData } from "./TwinDesk";
import type { DeskData, Process } from "./TwinDesk";
import type { GanttVehicle, Trip } from "./types";

// Плитки и счётчики — количество объектов в выборке API, не утверждённые KPI. «—» — не прочитано/нет права (не ноль); «N+» — выборка до предела.
const cnt = (d: { data: unknown[] | null }, limit?: number) => d.data ? (limit && d.data.length >= limit ? `${limit}+` : String(d.data.length)) : "—";
const ofTrips = (d: DeskData, f: (t: Trip) => boolean) => d.trips.data ? String(d.trips.data.filter(f).length) : "—";
const byCond = (c: string) => (t: Trip) => t.CONDITION === c;
const unready = (t: Trip) => (t.UNREADY_COUNT ?? 0) > 0 || (t.READY_PERC != null && t.READY_PERC < 100);
const noDock = (t: Trip) => !t.DOCK;
const noDriver = (t: Trip) => !t.VODITEL_ID;

const tripTile = (d: DeskData) => ({ icon: "🚚", label: "Рейсы на дату", read: d.trips, source: "GET /api/admin/transport/tasks",
  value: (t: Trip[]) => t.length, sub: (t: Trip[]) => `спланировано ${t.filter(byCond("Спланирован")).length} · отгружено ${t.filter(byCond("Отгружен")).length} · закрыто ${t.filter(byCond("Закрыт")).length}` });
const readyTile = (d: DeskData) => ({ icon: "📦", label: "Рейсы с неготовым грузом", read: d.trips, source: "READY_PERC / UNREADY_COUNT рейса",
  value: (t: Trip[]) => t.filter(unready).length, sub: (t: Trip[]) => `без данных о готовности: ${t.filter(x => x.READY_PERC == null).length}` });
const sessionTile = (d: DeskData) => ({ icon: "👷", label: "Открытые сессии ресурсов", read: d.sessions, source: "GET /api/resources/sessions",
  value: (s: { status: string }[]) => s.filter(x => x.status === "ACTIVE").length, sub: () => "сотрудники и техника, вошедшие в терминал" });

const warehouseProcesses: Process[] = [
  { id: "supply", icon: "⤓", title: "Приёмка по SAP", sub: () => `поставки, выборка до ${LIMITS.supply}`, count: d => cnt(d.supply, LIMITS.supply),
    list: d => ({ read: d.supply, limit: LIMITS.supply, items: (d.supply.data ?? []).map(o => ({ key: o.order_id, title: o.order_number, sub: `склад ${o.ware_id} · состояние ${o.condition} · ${formatMoment(o.date_of_accept)}` })) }),
    owner: { label: "Приёмка поставки SAP", href: rawLink("receiving.html") } },
  { id: "waves", icon: "≋", title: "Волны", sub: d => d.waves.data ? `запущено ${d.waves.data.filter(w => w.launched_at).length} в выборке до ${LIMITS.waves}` : "не прочитано", count: d => cnt(d.waves, LIMITS.waves),
    list: d => ({ read: d.waves, limit: LIMITS.waves, items: (d.waves.data ?? []).map(w => ({ key: String(w.pick_wave_id), title: w.wave_code, sub: `${w.status} · ${w.ware_name} · заказов ${w.order_count} · заданий ${w.task_count}${w.launched_at ? " · запущена " + formatMoment(w.launched_at) : ""}` })) }),
    owner: { label: "Панель смены", href: rawLink("shift-supervisor-wave.html") } },
  { id: "picking", icon: "✋", title: "Комплектация", sub: d => d.caseTasks.data ? `с остановкой ${d.caseTasks.data.filter(t => t.blocking_reason).length} · выборка до ${LIMITS.caseTasks}` : "не прочитано",
    count: d => d.caseTasks.data ? String(d.caseTasks.data.filter(t => t.picked_lines < t.total_lines).length) + (d.caseTasks.data.length >= LIMITS.caseTasks ? "+" : "") : "—",
    list: d => ({ read: d.caseTasks, limit: LIMITS.caseTasks, items: (d.caseTasks.data ?? []).filter(t => t.picked_lines < t.total_lines).map(t => ({ key: String(t.case_pick_task_id),
      title: `Задание ${t.case_pick_task_id} · ${t.wave_code}`, sub: `${t.status} · строк ${t.picked_lines}/${t.total_lines} · ${t.assigned_to ?? "не назначено"}${t.blocking_reason ? " · остановка: " + t.blocking_reason : ""}` })) }),
    owner: { label: "Комплектация", href: rawLink("case-pick-management.html") } },
  { id: "recovery", icon: "⚠", title: "Восстановление недостач", sub: () => `все разрешённые склады (не один выбранный), выборка до ${LIMITS.recovery} — полнота неизвестна`, count: d => cnt(d.recovery, LIMITS.recovery),
    list: d => ({ read: d.recovery, limit: LIMITS.recovery, items: (d.recovery.data ?? []).map(r => { const st = stageMeta(stageOf(r)); return { key: String(r.short_id),
      title: `${r.article ?? "товар не указан"} · ${r.cell ?? "ячейка не указана"}`,
      sub: `склад ${r.warehouse_id} · волна ${r.pick_wave_id} · недостача ${r.short_quantity ?? "—"} · ${st.label}${st.id === "UNKNOWN" ? ` (${r.status}/${r.recovery_state ?? "—"})` : ""} · №${r.short_id}` }; }) }),
    owner: { label: "Старший смены (по складу)", href: "?page=workspace&workspace=shift" } },
  { id: "loading", icon: "⇪", title: "Погрузка: груз не готов", sub: () => "рейсы с неготовыми местами", count: d => ofTrips(d, unready), filter: unready },
  { id: "shipped", icon: "➜", title: "Отгружено", sub: () => "рейсы «Отгружен»", count: d => ofTrips(d, byCond("Отгружен")), filter: byCond("Отгружен") },
];

export function DirectorDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  const data = useDeskData(day, reload, true);
  const waveTile = { icon: "≋", label: "Волны", read: data.waves, source: `GET /api/picking/waves (выборка до ${LIMITS.waves})`,
    value: (w: { launched_at: string | null }[]) => w.length >= LIMITS.waves ? `${LIMITS.waves}+` : w.length,
    sub: (w: { launched_at: string | null }[]) => `запущено ${w.filter(x => x.launched_at).length}${w.length >= LIMITS.waves ? ` в выборке до ${LIMITS.waves}` : ""}` };
  return <TwinDesk day={day} isToday={isToday} data={data} sceneTitle="РЦ · склад" processes={warehouseProcesses}
    kpis={[tripTile(data), readyTile(data), waveTile, sessionTile(data)]} resourceTypes={["PICKER", "REACH_TRUCK", "DOCK", "VEHICLE", "OTHER"]} reload={reload}
    extraLeft={<div className="aa-actions" style={{ marginTop: 10 }}>
      <HelpButton help={wsHelp.openShift} onClick={() => window.open(rawLink("shift-supervisor-wave.html"), "_blank")}>Панель смены</HelpButton>
      <HelpButton help={wsHelp.openTasks} onClick={() => window.open(rawLink("warehouse-tasks.html"), "_blank")}>Задания</HelpButton></div>} />;
}

const dispatchProcesses: Process[] = [
  { id: "planned", icon: "🗓", title: "Спланированы", sub: () => "ещё не отгружены", count: d => ofTrips(d, byCond("Спланирован")), filter: byCond("Спланирован") },
  { id: "nodock", icon: "🚪", title: "Без ворот", sub: () => "нужно назначить ворота", count: d => ofTrips(d, noDock), filter: noDock },
  { id: "nodriver", icon: "🧑", title: "Без водителя", sub: () => "нужно назначить водителя", count: d => ofTrips(d, noDriver), filter: noDriver },
  { id: "unready", icon: "📦", title: "Груз не готов", sub: () => "склад ещё собирает или контролирует", count: d => ofTrips(d, unready), filter: unready },
  { id: "shipped", icon: "➜", title: "Отгружены", sub: () => "в доставке", count: d => ofTrips(d, byCond("Отгружен")), filter: byCond("Отгружен") },
  { id: "closed", icon: "✓", title: "Закрыты", sub: () => "рейс завершён", count: d => ofTrips(d, byCond("Закрыт")), filter: byCond("Закрыт") },
];

export function DispatcherDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  const data = useDeskData(day, reload, false);
  // Только факт отметок: опоздание не рассчитывается, пока пояс РЦ не утверждён на сервере (C-0072).
  const factTile = { icon: "⏱", label: "Операции рейсов с отметкой факта", read: data.gantt, source: "fact_end операций (vehicles/gantt)",
    value: (v: GanttVehicle[]) => { const ops = v.flatMap(x => x.operations); return `${ops.filter(o => o.fact_end).length} / ${ops.length}`; },
    sub: () => "завершено по факту / всего операций на дату" };
  const issues = { icon: "🚪", label: "Рейсы без ворот / водителя", read: data.trips, source: "DOCK / VODITEL_ID рейса",
    value: (t: Trip[]) => `${t.filter(noDock).length} / ${t.filter(noDriver).length}`, sub: () => "требуют назначения" };
  return <TwinDesk day={day} isToday={isToday} data={data} sceneTitle="РЦ · ворота" processes={dispatchProcesses} kpis={[tripTile(data), issues, readyTile(data), factTile]} resourceTypes={["DOCK", "VEHICLE"]} reload={reload} />;
}

const atDock = (t: Trip) => Boolean(t.DOCK) && t.CONDITION === "Спланирован";
const yardProcesses: Process[] = [
  { id: "atdock", icon: "🚪", title: "У ворот (спланированы)", sub: () => "рейсу назначены ворота", count: d => ofTrips(d, atDock), filter: atDock },
  { id: "nodock", icon: "🅿", title: "Без ворот", sub: () => "во дворе на схеме; ворота назначает диспетчер", count: d => ofTrips(d, noDock), filter: noDock },
  { id: "unready", icon: "📦", title: "Груз не готов", sub: () => "машина может ждать склад", count: d => ofTrips(d, unready), filter: unready },
  { id: "shipped", icon: "➜", title: "Убыли (отгружены)", sub: () => "рейсы «Отгружен»", count: d => ofTrips(d, byCond("Отгружен")), filter: byCond("Отгружен") },
];

/** Координатор двора и ворот (C0049 yard_coordinator): модуля двора нет — показываем то, что есть в рейсах, и честно помечаем пробелы. */
export function YardDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  const data = useDeskData(day, reload, false);
  const docks = { icon: "🚪", label: "Ворота в работе", read: data.trips, source: "DOCK рейсов на дату",
    value: (t: Trip[]) => new Set(t.filter(x => x.DOCK).map(x => x.DOCK)).size, sub: (t: Trip[]) => `рейсов у ворот ${t.filter(atDock).length} · без ворот ${t.filter(noDock).length}` };
  return <TwinDesk day={day} isToday={isToday} data={data} sceneTitle="Двор и ворота · все доступные склады" processes={yardProcesses} kpis={[tripTile(data), docks, readyTile(data)]}
    resourceTypes={["DOCK", "VEHICLE"]} reload={reload}
    extraLeft={<div className="ops-note" style={{ marginTop: 10 }} title={wsHelp.yardGap.text} data-help-id={wsHelp.yardGap.id}>
      <p>Сводка рейсов показывает все разрешённые склады. Склад в общем Ганте выбирается отдельно.</p>
      <b>Нет в системе:</b> журнала прибытия машин и очереди двора — время ожидания у ворот не рассчитывается. Назначение ворот — правкой рейса у диспетчера.</div>} />;
}
