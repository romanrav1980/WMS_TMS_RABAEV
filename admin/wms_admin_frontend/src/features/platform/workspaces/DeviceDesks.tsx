import { currentSessionCredentials } from "../../../api";
import { DriverLogin, useDriverWorkspace } from "../../transport";
import { HelpButton } from "../help/HelpButton";
import { formatMoment, useApiRead } from "../access-admin";
import { wsHelp } from "./help";
import { rawLink } from "./OpsParts";
import type { CaseTask } from "./types";

type CaseLine = { case_pick_line_id: number; articul: string; product_name: string | null; cell_code: string; planned_qty: string; picked_qty: string; status: string };
type CaseTaskDetail = CaseTask & { current_cell: string | null; lines: CaseLine[] };
const lineDone = (l: CaseLine) => Number(l.picked_qty) >= Number(l.planned_qty) || ["DONE", "SHORT", "SHORT_APPROVED"].includes(l.status);

/** ТСД комплектовщика: только своё задание (assigned_to = вошедший пользователь), следующая ячейка крупно, полоса маршрута.
 *  Сканы и подтверждения — в существующем ТСД сборки (там operation_id и повтор). Задание само себе не выбирается. */
export function PickerDesk({ reload }: { reload: number }) {
  let user = "";
  try { user = currentSessionCredentials().username; } catch { user = ""; }
  // scope=self: сервер отбирает задания вошедшего по ASSIGNED_TO до limit (C-0092); клиентский фильтр ниже — только защита формы.
  const tasks = useApiRead<CaseTask[]>("/api/case-pick/tasks?scope=self&limit=200", reload);
  const mine = (tasks.data ?? []).filter(t => t.assigned_to?.toLowerCase() === user.toLowerCase() && ["ASSIGNED", "IN_PROGRESS"].includes(t.status));
  const task = mine[0];
  const detail = useApiRead<CaseTaskDetail>(task ? `/api/case-pick/tasks/${task.case_pick_task_id}` : null, reload);
  const lines = detail.data?.lines ?? [];
  const next = lines.find(l => !lineDone(l));
  return <div className="ops ops-device" aria-label="Рабочее место комплектовщика">
    <header className="ops-header"><div className="ops-brand">Комплектовщик<small>{user || "не выполнен вход"}</small></div></header>
    {tasks.error && <p className="ops-err" role="alert">Задания не прочитаны: {tasks.error}</p>}
    {tasks.loading && !tasks.data && <p className="ops-note">Загрузка…</p>}
    {tasks.data && !task && <section className="ops-panel" aria-live="polite">
      <div className="ops-big">Заданий нет</div><p>Задания выдаются только по обеспеченной волне. Ожидайте — экран обновится по кнопке «Обновить».</p>
      <p className="ops-note" title={wsHelp.pickNone.text} data-help-id={wsHelp.pickNone.id}>Выбирать задание самому не нужно.</p></section>}
    {task && <>
      <section className="ops-panel">
        <h3>Задание {task.case_pick_task_id} · волна {task.wave_code}</h3>
        <p>{task.customer_name} · место {task.sscc} · {task.pallet_type_name}</p>
        <div className="ops-bar" aria-label={`Строк ${task.picked_lines} из ${task.total_lines}`}><span style={{ width: `${task.task_progress_pct}%` }} /></div>
        <p className="ops-note">Строк {task.picked_lines} из {task.total_lines} · мест маршрута {task.route_done_pallet_count} из {task.route_pallet_count}</p>
        {task.blocking_reason && <p className="ops-chip bad" role="alert">Остановка: {task.blocking_reason}{task.blocking_cell_code ? " · ячейка " + task.blocking_cell_code : ""}. Позовите старшего отбора.</p>}
      </section>
      <section className="ops-panel" aria-live="polite">
        {detail.error && <p className="ops-err">Строки не прочитаны: {detail.error}</p>}
        {next ? <><div className="ops-kpi-label">Следующая ячейка</div><div className="ops-big">{next.cell_code}</div>
          <p>{next.product_name ?? next.articul} · {Number(next.planned_qty) - Number(next.picked_qty)} шт</p></>
          : detail.data && <p>Все строки подтверждены — закройте место в ТСД сборки.</p>}
        {lines.length > 0 && <ol className="ops-route" aria-label="Маршрут по ячейкам">{lines.slice(0, 12).map(l =>
          <li key={l.case_pick_line_id} className={"ops-stop" + (lineDone(l) ? " done" : l === next ? " active" : "")}><i aria-hidden="true" />
            <span><b>{l.cell_code}</b> <small>{l.articul} · {l.picked_qty}/{l.planned_qty}</small></span></li>)}</ol>}
        {lines.length > 12 && <p className="ops-note">Ещё {lines.length - 12} строк в ТСД сборки.</p>}
      </section>
      <HelpButton help={wsHelp.pickContinue} className="ops-action" onClick={() => window.open(rawLink("case-pick-tsd.html"), "_self")}>Продолжить сборку</HelpButton>
      {mine.length > 1 && <p className="ops-note">За вами ещё заданий: {mine.length - 1}.</p>}
    </>}
    <p className="ops-note">Последнее событие задания: {task ? `${task.last_action ?? "—"} · ${formatMoment(task.last_event_at)}` : "—"}. Нет связи — данные не обновятся; повторите «Обновить».</p>
  </div>;
}

/** Телефон водителя: существующий вход по привязке и отметки операций (useDriverWorkspace), маршрут как лента остановок. */
export function DriverDesk() {
  const w = useDriverWorkspace();
  // Форма входа — компонент transport (чужой файл): справка набора полей на группе; help_id отдельных полей — у владельца формы.
  if (!w.driverId) return <div className="ops ops-device"><div role="group" aria-label="Вход водителя" title={wsHelp.driverLogin.text} data-help-id={wsHelp.driverLogin.id}>
    <DriverLogin onLogin={w.login} busy={w.loading} error={w.error} /></div></div>;
  const ops = w.tripOps, current = ops.find(o => o.status === "in_progress") ?? ops.find(o => o.status === "pending");
  return <div className="ops ops-device" aria-label="Рабочее место водителя">
    <header className="ops-header"><div className="ops-brand">Водитель<small>привязка #{w.driverId} · {w.tripDate}</small></div>
      <HelpButton help={wsHelp.refresh} onClick={() => void w.refresh()}>Обновить</HelpButton>
      <HelpButton help={{ id: "workspace.driver.logout", text: "Выйти из места водителя. Несохранённая отметка остаётся в журнале устройства.", article: "workspaces" }} onClick={w.logout}>Выйти</HelpButton></header>
    {w.error && <p className="ops-err" role="alert">{w.error}</p>}
    {w.pending && <section className="ops-panel" role="alert"><b>Отметка не подтверждена сервером.</b>
      <HelpButton help={{ id: "workspace.driver.retry", text: "Отправить ту же отметку повторно; время первого проведения сохранится.", article: "workspaces" }} onClick={() => void w.retry()}>Повторить отметку</HelpButton></section>}
    {(w.activeView === "trips" || !w.selectedTrip) && <section className="ops-panel"><h3>Мои рейсы</h3>
      {w.trips.length === 0 ? <p className="ops-note">{w.loading ? "Загрузка…" : "Рейсов на дату нет."}</p> :
        <ul className="ops-list">{w.trips.map(t => <li key={t.task_id}><span><b>Рейс {t.task_id}</b> <small>{t.num_plat} · СТ {t.st_count} · {t.condition}</small></span>
          <HelpButton help={{ id: "workspace.driver.trip", text: "Открыть операции и остановки рейса.", article: "workspaces" }} onClick={() => void w.selectTrip(t)}>Открыть</HelpButton></li>)}</ul>}</section>}
    {w.activeView !== "trips" && w.selectedTrip && <>
      <section className="ops-panel" aria-live="polite">
        <div className="ops-kpi-label">Рейс {w.selectedTrip.task_id} · {w.selectedTrip.num_plat}</div>
        <div className="ops-big">{current ? current.operation_code : "Все операции выполнены"}</div>
        {current && <p className="ops-note">план {current.plan_start?.slice(11, 16) ?? "—"}–{current.plan_end?.slice(11, 16) ?? "—"}{current.fact_start ? " · начато " + current.fact_start.slice(11, 16) : ""}</p>}
        {current && <HelpButton help={wsHelp.driverOp} className="ops-action" unavailable={(w.opLoading && "отметка отправляется") || (w.pending && "сначала повторите неподтверждённую отметку")}
          onClick={() => void w.markOp(current.op_id, current.status === "in_progress" ? "done" : "start")}>{current.status === "in_progress" ? "Завершить" : "Начать"}</HelpButton>}
      </section>
      <section className="ops-panel"><h3>Остановки</h3>
        <ol className="ops-route">{w.tripSts.map((s, i) => <li key={s.st_number + i} className="ops-stop"><i aria-hidden="true" />
          <span><b>{s.addr}</b><br /><small>СТ {s.st_number} · окно {s.time_from || "—"}–{s.time_to || "—"} · мест {s.pallet_count}</small></span></li>)}</ol></section>
      <section className="ops-panel"><h3>Операции</h3>
        <ol className="ops-route">{ops.map(o => <li key={o.op_id} className={"ops-stop" + (o.status === "done" ? " done" : o === current ? " active" : "")}><i aria-hidden="true" />
          <span><b>{o.operation_code}</b> <small>{o.status === "done" ? "выполнено" : o.status === "in_progress" ? "идёт" : "ожидает"}</small></span></li>)}</ol>
        <HelpButton help={{ id: "workspace.driver.back", text: "Вернуться к списку рейсов.", article: "workspaces" }} onClick={() => w.setActiveView("trips")}>К рейсам</HelpButton></section>
    </>}
  </div>;
}

type WhTask = { task_id: number; task_type: string; status: string; assigned_to: string | null; from_cell: string | null; to_cell: string | null;
  target_articul: string | null; uid_pallet: string | null; sscc: string | null; qty_exact: string | null; unit_code: string | null; priority: number | null; last_error: string | null };
const WH_OPEN = ["IN_PROGRESS", "ASSIGNED"];

/** ТСД водителя ричтрака (C0049 reach_driver): своё текущее задание крупно — откуда → куда, товар, паллета. Сканы и завершение —
 *  в существующем ТСД ричтрака: завершение размещения без operation_id, повтор только после перечитывания задания. */
export function ReachDriverDesk({ reload }: { reload: number }) {
  let user = "";
  try { user = currentSessionCredentials().username; } catch { user = ""; }
  const q = user ? `&assigned_to=${encodeURIComponent(user)}` : "";
  const inWork = useApiRead<WhTask[]>(user ? `/api/warehouse-tasks?status=IN_PROGRESS&limit=50${q}` : null, reload);
  const assigned = useApiRead<WhTask[]>(user ? `/api/warehouse-tasks?status=ASSIGNED&limit=50${q}` : null, reload);
  const mine = [...(inWork.data ?? []), ...(assigned.data ?? [])].filter(t => t.assigned_to?.toLowerCase() === user.toLowerCase() && WH_OPEN.includes(t.status));
  const task = mine[0], err = inWork.error || assigned.error;
  return <div className="ops ops-device" aria-label="Рабочее место водителя ричтрака">
    <header className="ops-header"><div className="ops-brand">Водитель ричтрака<small>{user || "не выполнен вход"}</small></div></header>
    {err && <p className="ops-err" role="alert">Задания не прочитаны: {err}</p>}
    {(inWork.loading || assigned.loading) && !task && <p className="ops-note">Загрузка…</p>}
    {inWork.data && assigned.data && !task && <section className="ops-panel" aria-live="polite"><div className="ops-big">Заданий нет</div>
      <p title={wsHelp.reachNone.text} data-help-id={wsHelp.reachNone.id}>Задание назначает старший участка или сервер. Ожидайте и нажмите «Обновить».</p></section>}
    {task && <section className="ops-panel" aria-live="polite">
      <h3>{task.task_type} · задание {task.task_id} <small>{task.status === "IN_PROGRESS" ? "выполняется" : "назначено"}</small></h3>
      <div className="ops-kpi-label">Откуда</div><div className="ops-big">{task.from_cell ?? "не указано"}</div>
      <div className="ops-kpi-label" style={{ marginTop: 8 }}>Куда</div><div className="ops-big">{task.to_cell ?? "не указано"}</div>
      <p>{task.target_articul ?? "товар не указан"} · паллета {task.uid_pallet ?? task.sscc ?? "—"} · {task.qty_exact ?? "?"} {task.unit_code ?? ""}</p>
      {task.last_error && <p className="ops-chip bad" role="alert">Ошибка: {task.last_error}. Позовите старшего участка.</p>}
    </section>}
    {task && <HelpButton help={wsHelp.reachContinue} className="ops-action" onClick={() => window.open(rawLink("reachtruck-tsd.html"), "_self")}>Продолжить на ТСД ричтрака</HelpButton>}
    {mine.length > 1 && <p className="ops-note">За вами ещё заданий: {mine.length - 1}. Порядок задаёт сервер.</p>}
    <p className="ops-note">Если после скана не пришёл ответ — не сканируйте повторно: откройте задание заново и проверьте, завершено ли оно.</p>
  </div>;
}
