import { useMemo, useState } from "react";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { useApiRead } from "../../access-admin";
import type { ReadState } from "../../access-admin/useApiRead";
import { IsoStageScene } from "../IsoStageScene";
import type { IsoStage, IsoTone } from "../IsoStageScene";
import { KpiTile, ResourceList, SourceStrip } from "../OpsParts";
import { wsHelp } from "../help";
import { ResourcePlanner } from "../resources/ResourcePlanner";
import { WarehousePicker } from "../resources/WarehousePicker";
import { openLink } from "../resources/ResourceCard";
import { fmtTime } from "../resources/timelineModel";
import type { GanttSelection } from "../resources/timelineTypes";
import type { Session } from "../types";
import "../resources/gantt.css";
import { useUrlWarehouse } from "../useUrlWarehouse";

// Старший участка хранения и пополнения (диспетчер ричтраков), C0049 lead_storage. Только чтение; назначение ресурса —
// в экране складских заданий: dispatch-nearest без operation_id (автоповтор запрещён), здесь не отправляется.

type Task = { task_id: number; task_type: string; task_source: string | null; source_doc_type: string | null; source_doc_id: number | null; target_articul: string | null;
  uid_pallet: string | null; from_cell: string | null; to_cell: string | null; qty_exact: string | null; unit_code: string | null; fact_qty_exact: string | null;
  priority: number | null; status: string; assigned_to: string | null; resource_id: number | null; equipment_id: number | null;
  planned_start_at: string | null; planned_finish_at: string | null; created_at: string | null; last_error: string | null; wait_st_number: string | null; wait_target_tt_id: number | null };

const h = (id: string, text: string): HelpEntry => ({ id: "storage." + id, text, article: "storage-lead" });
const help = {
  stage: h("scene.stage", "Состояние складских заданий: запланировано, назначено, выполняется, ожидание или ошибка. Схема условная."),
  task: h("scene.task", "Складское задание. Нажмите — карточка: откуда/куда, товар, исполнитель, кандидаты."),
  process: h("process", "Показать задания этого вида справа."),
  candidates: h("candidates", "Кандидаты на задание по данным сервера (позиция, квалификация). Назначение — в экране складских заданий."),
  openTasks: h("open.tasks", "Открыть складские задания: там назначается ближайший ресурс с проверкой сервера."),
  openRepl: h("open.repl", "Открыть пополнение волны."),
};
const OPEN = ["PLANNED", "ASSIGNED", "IN_PROGRESS"] as const, LIMIT = 500;
const STAGES: IsoStage[] = [{ id: "PLANNED", title: "Запланировано", x: 0, y: 0 }, { id: "ASSIGNED", title: "Назначено", x: 1, y: 0 },
  { id: "IN_PROGRESS", title: "Выполняется", x: 2, y: 0 }, { id: "WAIT", title: "Ожидание / ошибка", x: 1, y: 1 }];
const PROC = [{ id: "REPLENISHMENT", title: "Пополнение отбора", types: ["REPLENISHMENT"] }, { id: "MOVE", title: "Перемещения в отбор", types: ["PICKING_MOVE"] },
  { id: "PUTAWAY", title: "Размещение", types: ["PUTAWAY", "FG_TO_STORAGE"] }, { id: "ERR", title: "С ошибкой / ожиданием", types: [] as string[] }];
const waiting = (t: Task) => Boolean(t.last_error || t.wait_st_number || t.wait_target_tt_id);
const tone = (t: Task): IsoTone => t.last_error ? "bad" : waiting(t) ? "warn" : t.status === "IN_PROGRESS" ? "ok" : "plan";

export function StorageLeadDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  // Склад обязателен: фильтр ware_id и native-права применяет сервер до limit (C-0091); при нескольких складах первый не угадываем.
  const [wh, setWh] = useUrlWarehouse(); // склад из адреса: сохраняется при переходах между рабочими местами (C0118)
  const q = (status: string) => wh ? `/api/warehouse-tasks?status=${status}&limit=${LIMIT}&ware_id=${wh}` : null;
  const reads = { PLANNED: useApiRead<Task[]>(q("PLANNED"), reload), ASSIGNED: useApiRead<Task[]>(q("ASSIGNED"), reload), IN_PROGRESS: useApiRead<Task[]>(q("IN_PROGRESS"), reload) };
  const sessions = useApiRead<Session[]>(wh ? `/api/resources/sessions?ware_id=${wh}` : null, reload);
  const [proc, setProc] = useState<string | null>("REPLENISHMENT"), [taskId, setTaskId] = useState<number | null>(null), [gantt, setGantt] = useState<GanttSelection>(null);
  const tasks = useMemo(() => OPEN.flatMap(s => reads[s].data ?? []), [reads.PLANNED.data, reads.ASSIGNED.data, reads.IN_PROGRESS.data]);
  const anyRead = reads.PLANNED as ReadState<unknown>;
  const capped = OPEN.some(s => (reads[s].data?.length ?? 0) >= LIMIT);
  const p = PROC.find(x => x.id === proc), list = p ? tasks.filter(t => p.id === "ERR" ? waiting(t) : p.types.includes(t.task_type)) : [];
  const task = tasks.find(t => t.task_id === taskId);
  const items = tasks.map(t => ({ id: t.task_id, stage: waiting(t) ? "WAIT" : t.status, tone: tone(t), label: `Задание ${t.task_id}`,
    title: `${t.task_type} ${t.task_id} · ${t.from_cell ?? "?"} → ${t.to_cell ?? "?"} · ${t.status}${t.assigned_to ? " · " + t.assigned_to : " · не назначено"}${t.last_error ? " · ошибка: " + t.last_error : ""}. ${help.task.text}` }));
  const picker = <div className="ops-panel rg-window" style={{ gridColumn: "1/-1" }}>
    <WarehousePicker capability="warehouse_tasks" value={wh} onChange={id => { setWh(id); setTaskId(null); setGantt(null); }} />
    <span className="ops-note">Задания и сессии одного склада; фильтр и права применяет сервер.</span></div>;
  if (!wh) return <>{picker}<p className="ops-panel ops-note" style={{ gridColumn: "1/-1" }}>Выберите склад: при нескольких доступных складах первый не подставляется.</p></>;
  return <>
    {picker}
    <div className="ops-kpis">
      {PROC.slice(0, 3).map(x => <KpiTile key={x.id} icon="⇅" label={x.title} read={anyRead} source="GET /api/warehouse-tasks (открытые)"
        value={() => String(tasks.filter(t => x.types.includes(t.task_type)).length) + (capped ? "+" : "")} sub={() => `не назначено ${tasks.filter(t => x.types.includes(t.task_type) && !t.assigned_to && !t.resource_id).length}`} />)}
      <KpiTile icon="!" label="С ошибкой / ожиданием" read={anyRead} source="last_error / wait_* заданий" value={() => String(tasks.filter(waiting).length)} sub={() => "требуют решения"} />
    </div>
    <SourceStrip isToday={isToday} day={day} sources={[["Запланировано", reads.PLANNED], ["Назначено", reads.ASSIGNED], ["Выполняется", reads.IN_PROGRESS], ["Сессии", sessions]]} />
    <aside className="ops-panel ops-left" aria-label="Процессы хранения">
      <h3>Процессы</h3>
      <ul className="ops-proc">{PROC.map(x => <li key={x.id}><button type="button" aria-pressed={proc === x.id} title={help.process.text} data-help-id={help.process.id + "." + x.id}
        onClick={() => { setProc(v => v === x.id ? null : x.id); setTaskId(null); }}><span className="ops-ico" aria-hidden="true">⇅</span><span><b>{x.title}</b></span>
        <span className="ops-count">{tasks.filter(t => x.id === "ERR" ? waiting(t) : x.types.includes(t.task_type)).length}</span></button></li>)}</ul>
      <p className="ops-note">Открытые задания из трёх выборок по статусу (до {LIMIT} каждая{capped ? "; предел достигнут — «+»" : ""}). Время заданий — без пояса источника, сроки не рассчитываются.</p>
    </aside>
    <section className="ops-panel ops-center" aria-label="Схема заданий хранения">
      <span className="ops-scene-title">Задания хранения и пополнения · схема условная</span>
      <IsoStageScene stages={STAGES} items={items} selected={taskId} onSelect={id => setTaskId(Number(id))} ariaLabel="Складские задания по состояниям (условная схема)"
        stageHelpId={help.stage.id} itemHelpId={help.task.id} stageHelp={help.stage.text} />
      <div className="ops-scene-legend"><span><i style={{ background: "#3d8bfd" }} />ждёт</span><span><i style={{ background: "#2fbf71" }} />выполняется</span>
        <span><i style={{ background: "#f0a531" }} />ожидание</span><span><i style={{ background: "#ef5b5b" }} />ошибка</span></div>
    </section>
    <aside className="ops-panel ops-right" aria-label="Выбранный объект">
      {task ? <TaskCard task={task} onClose={() => setTaskId(null)} /> : p ? <section className="ops-card"><h3>{p.title} <small>{list.length}</small></h3>
        {list.length === 0 ? <p className="ops-note">Открытых заданий нет.</p> : <ul className="ops-list">{list.slice(0, 40).map(t => <li key={t.task_id}>
          <span><b>{t.task_type} {t.task_id}</b> <small>{t.status}</small><br /><small>{t.from_cell ?? "?"} → {t.to_cell ?? "?"} · {t.qty_exact ?? "?"} {t.unit_code ?? ""} · {t.assigned_to ?? "не назначено"}</small></span>
          <HelpButton help={help.task} onClick={() => setTaskId(t.task_id)}>Карточка</HelpButton></li>)}</ul>}</section>
        : <p className="ops-note">Выберите задание на схеме или процесс слева.</p>}
    </aside>
    <section className="ops-panel" style={{ gridColumn: "1/-1" }} aria-label="Общий Гант ричтраков">
      <h3>Ричтраки и прочая техника: общий Гант</h3>
      <ResourcePlanner day={day} reload={reload} warehouseId={wh} selection={gantt} onSelect={setGantt} initialTypes={["REACH_TRUCK", "OTHER"]} />
    </section>
    <div style={{ gridColumn: "1/-1" }}><ResourceList read={sessions} /></div>
  </>;
}

function TaskCard({ task: t, onClose }: { task: Task; onClose: () => void }) {
  const cand = useApiRead<Record<string, unknown>[]>(`/api/resources/warehouse-tasks/${t.task_id}/candidates`);
  return <section className="ops-card" aria-label={"Задание " + t.task_id}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span>{t.task_type} {t.task_id}<br /><small>{t.status}{t.task_source ? " · " + t.task_source : ""}</small></span>
      <HelpButton help={wsHelp.closeCard} onClick={onClose} aria-label="Закрыть карточку">×</HelpButton></h3>
    <dl>
      <dt>Откуда → куда</dt><dd>{t.from_cell ?? "?"} → {t.to_cell ?? "?"}</dd>
      <dt>Товар / паллета</dt><dd>{t.target_articul ?? "—"} · {t.uid_pallet ?? "—"}</dd>
      <dt>Количество</dt><dd>{t.qty_exact ?? "?"} {t.unit_code ?? ""}{t.fact_qty_exact ? ` · факт ${t.fact_qty_exact}` : ""}</dd>
      <dt>Документ</dt><dd>{t.source_doc_type ?? "—"} {t.source_doc_id ?? ""}</dd>
      <dt>Исполнитель</dt><dd>{t.assigned_to ?? "не назначен"}{t.resource_id ? ` · ресурс ${t.resource_id}` : ""}{t.equipment_id ? ` · техника ${t.equipment_id}` : ""}</dd>
      <dt>Приоритет</dt><dd>{t.priority ?? "—"}</dd>
      <dt>План</dt><dd>{t.planned_start_at ? fmtTime(null, t.planned_start_at) : "не задан"}</dd>
      <dt>Создано</dt><dd>{t.created_at ? fmtTime(null, t.created_at) : "—"}</dd>
      {t.last_error && <><dt>Ошибка</dt><dd className="ops-err">{t.last_error}</dd></>}
      {(t.wait_st_number || t.wait_target_tt_id) && <><dt>Ожидание</dt><dd>{t.wait_st_number ? "СТ " + t.wait_st_number : ""} {t.wait_target_tt_id ? "рейс " + t.wait_target_tt_id : ""}</dd></>}
    </dl>
    <h3 title={help.candidates.text} data-help-id={help.candidates.id}>Кандидаты <small>{cand.data ? cand.data.length : ""}</small></h3>
    {cand.error ? <p className="ops-err">{cand.error}</p> : !cand.data ? <p className="ops-note">Загрузка…</p> : cand.data.length === 0 ? <p className="ops-note">Сервер не нашёл кандидатов (нет ресурса на смене или позиции).</p> :
      <ul className="ops-list">{cand.data.slice(0, 10).map((c, i) => <li key={i}><span><small>{Object.entries(c).slice(0, 6).map(([k, v]) => `${k}: ${String(v)}`).join(" · ")}</small></span></li>)}</ul>}
    <div className="aa-actions" style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
      <HelpButton help={help.openTasks} onClick={() => openLink({ page: "warehouse-tasks.html" })}>Складские задания</HelpButton>
      {t.source_doc_type === "PICK_WAVE" && t.source_doc_id != null && <HelpButton help={help.openRepl} onClick={() => openLink({ page: "wave-replenishment.html", params: { wave_id: t.source_doc_id! } })}>Пополнение волны</HelpButton>}
    </div>
  </section>;
}
