import { useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { apiOperationScope } from "../../../../api";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { KpiTile, ResourceList, SourceStrip } from "../OpsParts";
import { ResourcePlanner } from "../resources/ResourcePlanner";
import { WarehousePicker } from "../resources/WarehousePicker";
import { openLink } from "../resources/ResourceCard";
import { fmtTime } from "../resources/timelineModel";
import type { GanttSelection, ResourceTimeline } from "../resources/timelineTypes";
import type { CaseTask, Wave } from "../types";
import { WaveCard, RiskList } from "./WaveCard";
import { WaveFlowScene } from "./WaveFlowScene";
import { ShiftWarehouseBar } from "./ShiftWarehouseBar";
import { RecoveryPanel } from "../recovery/RecoveryPanel";
import { RECOVERY_LIMIT } from "../recovery/recoveryModel";
import type { RecoveryRow, Stage } from "../recovery/recoveryModel";
import { useRecovery } from "../recovery/useRecovery";
import { shiftHelp } from "./help";
import { isOpenCase } from "./executionState";
import { executionRisks, waveRisks } from "./risks";
import { SHIFT_LIMITS, useShiftData, useWaveDetails } from "./useShiftData";
import { useShiftWave, useResourceKeyBySession, useShiftWarehouse } from "./useShiftContext";
import type { Risk } from "./types";
import "../resources/gantt.css";

type Panel = "future" | "risks" | "picking" | "blocked" | "repl" | "recovery" | "people";
const PANELS: { id: Panel; icon: string; title: string }[] = [
  { id: "future", icon: "◇", title: "Будущие волны" }, { id: "risks", icon: "!", title: "Риски запуска" }, { id: "picking", icon: "▤", title: "Текущая сборка" },
  { id: "blocked", icon: "⛔", title: "Блокировки сборки" }, { id: "repl", icon: "⇅", title: "Пополнения" }, { id: "recovery", icon: "⚠", title: "Восстановление недостач" }, { id: "people", icon: "👤", title: "Люди и техника" },
];
const plus = (n: number, limit: number) => (n >= limit ? `${n}+` : String(n));

/** Рабочее место старшего смены (C0074): поток волн на схеме склада, подготовка будущей волны, риски, текущая сборка, общий Гант ресурсов.
 *  Запуск и переназначение — только в экранах-владельцах существующими командами; здесь команды не отправляются. */
export function ShiftSupervisorDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  // Склад — из адреса (warehouse_id), чтобы переходы «Консолидация ↔ старший смены» открывали тот же склад (C0116).
  const [wh, setWh] = useShiftWarehouse();
  const data = useShiftData(reload, wh);
  // C0117: недостачи и этап восстановления выбранного склада; выбор недостачи хранится здесь, чтобы вернуться к ней после карточки волны.
  const [recoveryReload, setRecoveryReload] = useState(0);
  const recovery = useRecovery(wh || null, apiOperationScope(), reload + recoveryReload);
  const [recoveryOpen, setRecoveryOpen] = useState<RecoveryRow | null>(null), [recoveryFilter, setRecoveryFilter] = useState<Stage | null>(null);
  const recoverySource = { data: recovery.rows, error: recovery.error, loading: recovery.loading, at: recovery.at };
  const [waveId, setWaveId] = useShiftWave();
  const [panel, setPanel] = useState<Panel | null>("future");
  const [gantt, setGantt] = useState<GanttSelection>(null);
  // Структурный фильтр Ганта по точному wave_id (навигация «волна → её ресурсы», C-0110: не текстовый поиск по wave_code,
  // его событие может не содержать); token меняется при каждом переходе, не перетирает ручной текстовый поиск.
  const [waveFocus, setWaveFocus] = useState<{ waveId: number; label: string; token: number } | null>(null);
  const ganttRef = useRef<HTMLElement>(null);
  const scrollToGantt = () => ganttRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  const waveCardRef = useRef<HTMLElement>(null);
  const scrollToWaveCard = () => waveCardRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  // Уже прочитанный Гантом таймлайн (не второй запрос): по нему строится настоящее сопоставление сессия → ресурс для панели «Люди и техника».
  const [timeline, setTimeline] = useState<ResourceTimeline | null>(null);
  const resourceKeyBySession = useResourceKeyBySession(timeline);
  const future = data.future.data ?? [], launched = data.launched.data ?? [];
  // Только волны выбранного склада: списки прежнего склада (до перечитывания) не попадают ни на схему, ни в пакет проверок.
  const listed = [...future, ...launched].some(w => w.pick_wave_id === waveId && String(w.ware_id) === wh);
  const requested = useApiRead<Wave>(wh && waveId != null && !listed ? `/api/picking/waves/${waveId}/header?ware_id=${wh}` : null, reload);
  const extra = !requested.loading && !requested.error && requested.data?.pick_wave_id === waveId && String(requested.data.ware_id) === wh ? requested.data : null;
  const waves = useMemo(() => [...future, ...launched, ...(extra && !listed ? [extra] : [])].filter(w => String(w.ware_id) === wh), [future, launched, wh, extra, listed]);
  // Детали — по всем видимым волнам склада (bulk shift-overview, C-0088), выбранная волна первой.
  const ids = useMemo(() => [...new Set(waves.map(w => w.pick_wave_id))], [waves]);
  const { details, loading, coverage } = useWaveDetails(ids, wh, reload);
  const risks = useMemo(() => {
    const list: Risk[] = waves.flatMap(w => { const d = details.get(w.pick_wave_id); return d ? waveRisks(w, d) : []; });
    return [...list, ...executionRisks(data.caseTasks.data ?? [], data.shorts.data ?? [])];
  }, [waves, details, data.caseTasks.data, data.shorts.data]);
  const risky = new Set(risks.filter(r => r.severity === "BLOCKER" && r.wave_id != null).map(r => r.wave_id!));
  const wave = waves.find(w => w.pick_wave_id === waveId);
  const picking = (data.caseTasks.data ?? []).filter(t => isOpenCase(t.status));
  const blocked = (data.caseTasks.data ?? []).filter(t => t.blocking_reason);
  const clearWave = () => setWaveId(null);
  const selectWave = (id: number) => { setWaveId(id); setGantt(null); };
  const selectGantt = (s: GanttSelection) => { setGantt(s); if (s) clearWave(); };
  // Переход «текущая работа → её ресурсы в Ганте»: выделяет событие и прокручивает к общему Ганту (важно на мобильном экране).
  const jumpToGantt = (s: GanttSelection) => { selectGantt(s); scrollToGantt(); };
  // Переход «волна → её ресурсы в Ганте»: точный структурный фильтр по wave_id (не по тексту кода — он не всегда есть в событии),
  // карточка волны остаётся открытой (возврат к контексту).
  const showWaveInGantt = (w: Wave) => { setWaveFocus(old => ({ waveId: w.pick_wave_id, label: w.wave_code, token: (old?.token ?? 0) + 1 })); scrollToGantt(); };
  // Переход «работа в Ганте → её волна»: возврат к контексту карточки волны с прокруткой (работа могла быть выбрана далеко внизу).
  const backToWave = (id: number) => { selectWave(id); scrollToWaveCard(); };
  const picker = <ShiftWarehouseBar wh={wh} onChange={id => { setWh(id); clearWave(); setGantt(null); setRecoveryOpen(null); setRecoveryFilter(null); }} />;
  if (!wh) return <>{picker}<p className="ops-panel ops-note" style={{ gridColumn: "1/-1" }}>Выберите склад или РЦ: при нескольких доступных складах первый не подставляется.</p></>;
  return <>
    {picker}
    <div className="ops-kpis">
      <KpiTile icon="◇" label="Будущие волны (до запуска)" read={data.future} source="picking/waves PREVIEW" value={(d: Wave[]) => plus(d.length, SHIFT_LIMITS.future)} sub={() => "статус PREVIEW"} />
      <KpiTile icon="▶" label="Волны в работе" read={data.launched} source="picking/waves LAUNCHED" value={(d: Wave[]) => plus(d.length, SHIFT_LIMITS.launched)} sub={() => `подробно проверено ${coverage.read} из ${coverage.requested}`} />
      <KpiTile icon="!" label="Подтверждённые блокировки" read={data.launched} source="readiness/pick-readiness/case-pick" value={() => String(risks.filter(r => r.severity === "BLOCKER").length)} sub={() => `по ${details.size} волнам и выборке сборки`} />
      <KpiTile icon="▤" label="Сборка в работе" read={data.caseTasks} source="case-pick/tasks" value={() => plus(picking.length, SHIFT_LIMITS.caseTasks)} sub={() => `остановлено ${blocked.length}`} />
      <KpiTile icon="👤" label="Открытые сессии" read={data.sessions} source="resources/sessions" value={(d: { status: string }[]) => String(d.filter(s => s.status === "ACTIVE").length)} sub={() => "люди и техника в терминале"} />
    </div>
    <SourceStrip isToday={isToday} day={day} sources={[["Будущие волны", data.future], ["Волны в работе", data.launched], ["Сборка", data.caseTasks], ["Недостачи", data.shorts], ["Восстановления", recoverySource], ["Сессии", data.sessions]]} />
    <aside className="ops-panel ops-left" aria-label="Процессы старшего смены">
      <h3>Процессы</h3>
      <ul className="ops-proc">{PANELS.map(p => <li key={p.id}>
        <button type="button" aria-pressed={panel === p.id} title={shiftHelp.process.text} data-help-id={shiftHelp.process.id + "." + p.id} onClick={() => { setPanel(v => v === p.id ? null : p.id); setWaveId(null); setGantt(null); }}>
          <span className="ops-ico" aria-hidden="true">{p.icon}</span><span><b>{p.title}</b></span>
          <span className="ops-count">{{ future: future.length, risks: risks.length, picking: picking.length, blocked: blocked.length, repl: [...details.values()].reduce((n, d) => n + (d.replenishment.data?.filter(r => r.status !== "DONE").length ?? 0), 0),
            recovery: recovery.rows ? plus(recovery.rows.length, RECOVERY_LIMIT) : "—", people: (data.sessions.data ?? []).length }[p.id]}</span>
        </button></li>)}</ul>
      <p className="ops-note" title={shiftHelp.details.text} data-help-id={shiftHelp.details.id}>Подробные проверки — {coverage.read} из {coverage.requested} видимых волн{loading || data.future.loading || data.launched.loading ? " (загрузка…)" : ""}
        {coverage.batches > 1 ? `, ${coverage.batches} снимков (не единый снимок смены)` : ""}{coverage.observed.length ? `, прочитано ${coverage.observed.map(o => fmtTime(null, o)).join(", ")}` : ""}.
        {coverage.failed > 0 && <span className="ops-err"> Не прочитано батчей: {coverage.failed} — {coverage.error}</span>}
        {" "}Список волн сам ограничен выборкой (до {SHIFT_LIMITS.future} будущих и {SHIFT_LIMITS.launched} в работе). Риски — только с основанием из источника; проценты и сроки не рассчитываются.</p>
    </aside>
    <section className="ops-panel ops-center" aria-label="Поток волн по складу">
      <span className="ops-scene-title">Поток волн по этапам склада · схема условная</span>
      {data.future.error && data.launched.error ? <p className="ops-err" style={{ padding: 40 }}>Волны не прочитаны: {data.launched.error}</p>
        : <WaveFlowScene waves={waves} details={details} riskyWaves={risky} selected={waveId ?? (panel === "recovery" ? recoveryOpen?.pick_wave_id ?? null : null)} onSelect={selectWave} />}
      <div className="ops-scene-legend"><span><i style={{ background: "#3d8bfd" }} />до запуска</span><span><i style={{ background: "#2fbf71" }} />в работе</span>
        <span><i style={{ background: "#ef5b5b" }} />есть подтверждённая блокировка</span><span>этап — по данным готовности</span></div>
    </section>
    <aside className="ops-panel ops-right" aria-label="Выбранный объект" ref={waveCardRef}>
      {wave ? <WaveCard wave={wave} detail={details.get(wave.pick_wave_id)} risks={risks.filter(r => r.wave_id === wave.pick_wave_id)}
          tasks={(data.caseTasks.data ?? []).filter(ct => ct.pick_wave_id === wave.pick_wave_id)} onClose={clearWave}
          onShowInGantt={() => showWaveInGantt(wave)} onOpenTask={id => jumpToGantt({ kind: "event", id: "CASE_PICK_TASK:" + id })} />
        : waveId != null && (requested.error || (requested.data && String(requested.data.ware_id) !== wh)) ? <p role="alert" className="ops-err">Выбранная волна недоступна на этом складе. Проверьте склад и право просмотра волны.</p>
        : panel === "recovery" ? <RecoveryPanel read={recovery} scopeLabel={`Склад ${wh}`} openId={recoveryOpen?.short_id ?? null} onSelect={setRecoveryOpen}
            filter={recoveryFilter} onFilter={setRecoveryFilter} onWave={selectWave} onRefresh={() => setRecoveryReload(n => n + 1)} />
        : panel ? <PanelList panel={panel} future={future} risks={risks} picking={picking} blocked={blocked} details={details} sessions={data.sessions} onWave={selectWave}
            onTask={id => jumpToGantt({ kind: "event", id: "CASE_PICK_TASK:" + id })}
            resourceKeyBySession={resourceKeyBySession} onOpenResource={key => jumpToGantt({ kind: "resource", key })} />
        : <p className="ops-note">Выберите волну на схеме, процесс слева или ресурс в Ганте ниже.</p>}
    </aside>
    <section className="ops-panel" style={{ gridColumn: "1/-1" }} aria-label="Общий Гант ресурсов" ref={ganttRef}>
      <h3>Люди, техника, ворота и машины: общий Гант</h3>
      <ResourcePlanner day={day} reload={reload} warehouseId={wh} selection={gantt} onSelect={selectGantt} initialTypes={["PICKER", "REACH_TRUCK", "DOCK", "VEHICLE", "OTHER"]}
        onOpenWave={backToWave} waveFocus={waveFocus ?? undefined} onTimeline={setTimeline} />
    </section>
  </>;
}

type ListProps = { panel: Panel; future: Wave[]; risks: Risk[]; picking: CaseTask[]; blocked: CaseTask[]; details: ReturnType<typeof useWaveDetails>["details"];
  sessions: Parameters<typeof ResourceList>[0]["read"]; onWave: (id: number) => void; onTask: (id: number) => void;
  resourceKeyBySession: Map<number, string>; onOpenResource: (key: string) => void };

function PanelList({ panel, future, risks, picking, blocked, details, sessions, onWave, onTask, resourceKeyBySession, onOpenResource }: ListProps) {
  const title = PANELS.find(p => p.id === panel)!.title;
  const box = (body: ReactNode, note?: string) => <section className="ops-card" aria-label={title}><h3>{title}</h3>{body}{note && <p className="ops-note">{note}</p>}</section>;
  if (panel === "people") return <ResourceList read={sessions} resourceKeyBySession={resourceKeyBySession} onOpenResource={onOpenResource} />;
  if (panel === "risks") return box(risks.length ? <RiskList risks={risks} onWave={onWave} /> : <p className="ops-note">Подтверждённых рисков по прочитанным источникам нет.</p>);
  if (panel === "future") return box(future.length === 0 ? <p className="ops-note">Будущих волн (PREVIEW) в выборке нет.</p> :
    <ul className="ops-list">{future.slice(0, 40).map(w => <li key={w.pick_wave_id}><span><b>{w.wave_code}</b><br /><small>заказов {w.order_count} · заданий {w.task_count} · {w.ware_name || w.ware_id}</small></span>
      <HelpButton help={shiftHelp.wavePick} onClick={() => onWave(w.pick_wave_id)}>Подготовка</HelpButton></li>)}</ul>);
  if (panel === "repl") {
    const rows = [...details.values()].flatMap(d => (d.replenishment.data ?? []).filter(r => r.status !== "DONE"));
    return box(rows.length === 0 ? <p className="ops-note">Незавершённых пополнений по проверенным волнам нет.</p> :
      <ul className="ops-list">{rows.slice(0, 40).map(r => <li key={r.pick_wave_replenish_task_id}><span><b>{r.articul}</b> <small>{r.status}{r.wait_reason ? " · ждёт: " + r.wait_reason : ""}</small><br />
        <small>{r.source_cell_code ?? "?"} → {r.target_cell_code ?? "?"} · осталось {r.demand_remaining_base ?? "нет данных"} баз. ед. · волна {r.pick_wave_id}</small></span>
        <HelpButton help={shiftHelp.openRepl} onClick={() => openLink({ page: "wave-replenishment.html", params: { wave_id: r.pick_wave_id } })}>Открыть</HelpButton></li>)}</ul>,
      "По волнам с подробной проверкой. Пополнения выполняют ричтраки — их занятость в Ганте ниже.");
  }
  const list = panel === "picking" ? picking : blocked;
  return box(list.length === 0 ? <p className="ops-note">В выборке нет.</p> :
    <ul className="ops-list">{list.slice(0, 40).map(t => <li key={t.case_pick_task_id} title={shiftHelp.task.text} data-help-id={shiftHelp.task.id}>
      <span><b>Сборка {t.case_pick_task_id}</b> <small>{t.status} · волна {t.wave_code}</small><br />
        <small>строк {t.picked_lines} из {t.total_lines} · {t.assigned_to ?? "исполнитель не назначен"}{t.blocking_reason ? ` · остановка: ${t.blocking_reason}${t.blocking_cell_code ? " · " + t.blocking_cell_code : ""}` : ""}</small>
        <div className="ops-bar" aria-hidden="true"><span style={{ width: `${t.total_lines ? Math.round(t.picked_lines / t.total_lines * 100) : 0}%` }} /></div></span>
      <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <HelpButton help={shiftHelp.task} onClick={() => onTask(t.case_pick_task_id)}>В Ганте</HelpButton>
        <HelpButton help={shiftHelp.wavePick} onClick={() => onWave(t.pick_wave_id)}>Волна</HelpButton></span></li>)}</ul>,
    "Прогресс — строки одной сборки (разные SKU не складываются в объём).");
}
