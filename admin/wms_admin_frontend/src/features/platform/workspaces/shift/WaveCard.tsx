import { preparationComplete } from "./executionState";
import { HelpButton } from "../../help/HelpButton";
import { wsHelp } from "../help";
import { fmtTime } from "../resources/timelineModel";
import { openLink } from "../resources/ResourceCard";
import type { CaseTask, Wave } from "../types";
import { shiftHelp } from "./help";
import type { Risk, WaveDetail } from "./types";

const t = (iso: string | null | undefined) => iso ? fmtTime(null, iso) : "не задано";

/** Карточка подготовки волны: спрос/запас, пополнение, время, ворота, риски, текущая сборка волны и переход к реальному действию.
 *  Количества показываются по артикулу и базовой единице; разные SKU не складываются в процент.
 *  onShowInGantt/onOpenTask — навигация к работам и ресурсам этой волны в общем Ганте ниже (не второй расчёт занятости). */
export function WaveCard({ wave, detail, risks, tasks, onClose, onShowInGantt, onOpenTask }:
  { wave: Wave & { dock_id?: number | null; route_code?: string | null }; detail: WaveDetail | undefined; risks: Risk[]; tasks: CaseTask[]; onClose: () => void; onShowInGantt: () => void; onOpenTask: (id: number) => void }) {
  const pick = detail?.pick.data, ready = detail?.readiness.data, time = detail?.time.data, repl = detail?.replenishment.data;
  const missing = (pick?.tasks ?? []).filter(x => Number(x.missing_base) > 0);
  const replWait = (repl ?? []).filter(r => r.status !== "DONE");
  return <section className="ops-card" aria-label={"Волна " + wave.wave_code}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
      <span>Волна {wave.wave_code}<br /><small>{wave.status} · {wave.wave_kind} · склад {wave.ware_name || wave.ware_id}</small></span>
      <HelpButton help={wsHelp.closeCard} onClick={onClose} aria-label="Закрыть карточку">×</HelpButton></h3>
    {!detail && <p className="ops-note" title={shiftHelp.details.text}>Подробные проверки загружаются…</p>}
    {!preparationComplete(detail) && <p className="ops-note" role="status">Подготовка не проверена полностью. Отсутствие прочитанных блокировок не подтверждает готовность.</p>}
    <dl>
      <dt>Заказы / задания</dt><dd>{wave.order_count} / {wave.task_count}</dd>
      <dt>Окно волны</dt><dd>{wave.planned_start_at || wave.planned_finish_at ? `${t(wave.planned_start_at)} — ${t(wave.planned_finish_at)}` : "не задано"}</dd>
      <dt>Время утверждено</dt><dd>{detail?.time.error ? <span className="ops-err">{detail.time.error}</span> : time ? (time.plan_status === "NO_APPROVED_PLAN" ? "нет утверждённого плана" : time.plan_status) : "—"}</dd>
      <dt>Ворота / маршрут</dt><dd>{wave.dock_id ?? "ворота не назначены"}{wave.route_code ? " · " + wave.route_code : ""}</dd>
      <dt>Отбор разрешён</dt><dd>{pick ? (pick.released_at ? `${t(pick.released_at)} · ${pick.released_by ?? ""}` : "нет") : detail?.pick.error || "—"}</dd>
      <dt>Запас под задания</dt><dd>{detail?.pick.error ? <span className="ops-err">{detail.pick.error}</span> : pick ? `${pick.tasks.length - missing.length} из ${pick.tasks.length} заданий покрыты` : "—"}</dd>
      <dt>Пополнение</dt><dd>{detail?.replenishment.error ? <span className="ops-err">{detail.replenishment.error}</span> : repl ? `${repl.length} строк, не завершено ${replWait.length}` : "—"}</dd>
      <dt>Открыто по волне</dt><dd>{detail?.readiness.error ? <span className="ops-err">{detail.readiness.error}</span> : ready ? `пополнений ${ready.summary.open_replenishment_count}, размещений ${ready.summary.open_staging_count}, сборок ${ready.summary.open_case_pick_count}, недостач ${ready.summary.shortage_count}` : "—"}</dd>
      <dt>Люди и техника</dt><dd>квалификация и выход — в «Загрузке ресурсов» и общем Ганте ниже; здесь не рассчитываются</dd>
    </dl>
    {missing.length > 0 && <><h3>Не хватает запаса <small>{missing.length}</small></h3>
      <ul className="ops-list">{missing.slice(0, 12).map(m => <li key={m.pick_task_id}><span><b>{m.article}</b><br />
        <small>не хватает {m.missing_base} из {m.required_base} {m.base_uom ?? "баз. ед. (не указана)"}{m.cell ? " · " + m.cell : ""}</small></span></li>)}</ul></>}
    <h3>Риски запуска <small>{risks.length}</small></h3>
    {risks.length === 0 ? <p className="ops-note">{preparationComplete(detail) ? "В прочитанном снимке блокировок не найдено. Допуск к запуску проверяет сервер при команде." : "Нет полной проверки подготовки; готовность неизвестна."}</p> :
      <RiskList risks={risks} />}
    <h3>Сборка этой волны <small>{tasks.length}</small></h3>
    {tasks.length === 0 ? <p className="ops-note">Активных заданий сборки по этой волне в текущей выборке нет.</p> :
      <ul className="ops-list">{tasks.slice(0, 12).map(ct => <li key={ct.case_pick_task_id}>
        <span><b>Сборка {ct.case_pick_task_id}</b> <small>{ct.status}{ct.blocking_reason ? " · остановка: " + ct.blocking_reason : ""}</small><br />
          <small>строк {ct.picked_lines} из {ct.total_lines} · {ct.assigned_to ?? "исполнитель не назначен"}</small></span>
        <HelpButton help={shiftHelp.task} onClick={() => onOpenTask(ct.case_pick_task_id)}>В Ганте</HelpButton></li>)}</ul>}
    <div className="aa-actions" style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
      <HelpButton help={shiftHelp.waveGantt} onClick={onShowInGantt}>Ресурсы волны в Ганте</HelpButton>
      <HelpButton help={shiftHelp.openShift} onClick={() => openLink({ page: "shift-supervisor-wave.html", params: { wave_id: wave.pick_wave_id } })}>Панель смены</HelpButton>
      <HelpButton help={shiftHelp.openRepl} onClick={() => openLink({ page: "wave-replenishment.html", params: { wave_id: wave.pick_wave_id } })}>Пополнение</HelpButton>
      <HelpButton help={shiftHelp.openWorkload} onClick={() => openLink({ page: "resource-workload.html", params: { wave_id: wave.pick_wave_id } })}>Загрузка ресурсов</HelpButton>
    </div>
  </section>;
}

export function RiskList({ risks, onWave }: { risks: Risk[]; onWave?: (id: number) => void }) {
  return <ul className="ops-list">{risks.slice(0, 40).map(r => <li key={r.key} title={shiftHelp.risk.text} data-help-id={shiftHelp.risk.id}>
    <span><span className={"ops-chip " + (r.severity === "BLOCKER" ? "bad" : "other")}>{r.severity === "BLOCKER" ? "блокирует" : "внимание"}</span> <b>{r.basis}</b><br />
      <small>{r.wave_id != null ? `волна ${r.wave_id}` : ""}{r.task_id != null ? ` · задание ${r.task_id}` : ""} · влияние: {r.impact} · ответственный: {r.owner ?? "не указан в источнике"} · источник: {r.source}</small></span>
    <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {onWave && r.wave_id != null && <HelpButton help={shiftHelp.wavePick} onClick={() => onWave(r.wave_id!)}>Волна</HelpButton>}
      {r.action && <HelpButton help={shiftHelp.riskAction} onClick={() => openLink(r.action)}>{r.action.label}</HelpButton>}
    </span></li>)}</ul>;
}
