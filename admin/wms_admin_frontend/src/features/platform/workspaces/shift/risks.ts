import { isClosedWave, isOpenCase, isOpenReplenishment, isPendingShort } from "./executionState";
import type { CaseTask, Session, Wave } from "../types";
import type { CaseShort, Risk, WaveDetail } from "./types";

const BLOCKER_TEXT: Record<string, string> = {
  REPLENISHMENT: "Открыто пополнение отборной ячейки", STAGING: "Открыта задача размещения целой паллеты", CASE_PICK: "Открыта сборка",
  DOMAIN_SYNC: "Факт складского задания не синхронизирован с волной", SHORTAGE: "Неразрешённая недостача",
};
const BLOCKER_ACTION: Record<string, { label: string; page: string }> = {
  REPLENISHMENT: { label: "Пополнение волны", page: "wave-replenishment.html" }, STAGING: { label: "Складские задания", page: "warehouse-tasks.html" },
  CASE_PICK: { label: "Управление сборкой", page: "case-pick-management.html" }, DOMAIN_SYNC: { label: "Синхронизация заданий", page: "warehouse-task-sync.html" },
  SHORTAGE: { label: "Разбор недостачи", page: "short-investigation.html" },
};
const num = (v: string | null | undefined) => { const n = Number(v); return Number.isFinite(n) ? n : null; };
const uom = (u: string | null) => u ?? "баз. ед. (не указана)";
const minutes = (from: string, to: string) => Math.floor((Date.parse(to) - Date.parse(from)) / 60000);

/** Риски по волне из фактических данных источников. Владелец — только если источник его называет (иначе null).
 *  Нет экрана-владельца действия в приложении — action null (не ссылка обратно на это же рабочее место). */
export function waveRisks(wave: Wave, d: WaveDetail): Risk[] {
  if (isClosedWave(wave.status)) return [];
  const out: Risk[] = [], w = wave.pick_wave_id;
  for (const [source, read] of Object.entries(d).filter(([key]) => key !== "wave_id")) {
    if (typeof read !== "object" || read == null) continue;
    if (read.error || read.data == null) out.push({ key: `${w}:UNKNOWN:${source}`, wave_id: w, task_id: null, severity: "WARNING",
      basis: `Подготовка не проверена: ${source}`, source, impact: read.error || "Нет данных источника; готовность не подтверждена", owner: null, action: null });
  }
  for (const b of d.readiness.data?.blockers ?? []) out.push({ key: `${w}:B:${b.blocker_type}:${b.status}`, wave_id: w, task_id: null, severity: "BLOCKER",
    basis: BLOCKER_TEXT[b.blocker_type] ?? b.message, source: "readiness",
    impact: `${b.count} шт.${b.qty ? `, количество ${b.qty}` : ""}`, owner: null, action: BLOCKER_ACTION[b.blocker_type] ? { ...BLOCKER_ACTION[b.blocker_type], params: { wave_id: w } } : null });
  for (const t of d.pick.data?.tasks ?? []) {
    const missing = num(t.missing_base);
    if (missing != null && missing > 0) out.push({ key: `${w}:M:${t.pick_task_id}`, wave_id: w, task_id: t.pick_task_id, severity: "BLOCKER",
      basis: `Не покрыт запасом: ${t.article}${t.cell ? " · ячейка " + t.cell : ""}`, source: "pick-readiness",
      impact: `не хватает ${t.missing_base} из ${t.required_base} ${uom(t.base_uom)}`, owner: null, action: { label: "Пополнение волны", page: "wave-replenishment.html", params: { wave_id: w } } });
  }
  if (wave.status === "LAUNCHED" && d.pick.data && !d.pick.data.released_at) out.push({ key: `${w}:R`, wave_id: w, task_id: null, severity: "WARNING",
    basis: "Отбор волны не разрешён", source: "pick-readiness", impact: "комплектовщики не получат задания этой волны", owner: null, action: null });
  if (d.time.data?.plan_status === "NO_APPROVED_PLAN") out.push({ key: `${w}:T`, wave_id: w, task_id: null, severity: "WARNING",
    basis: "Время волны не утверждено", source: "time-context", impact: "нет утверждённого окна для расчёта загрузки людей и техники", owner: null,
    action: { label: "Загрузка ресурсов", page: "resource-workload.html", params: { wave_id: w } } });
  // C-0159: срок — только утверждённый план времени (APPROVED, моменты с поясом) против часов сервера этого снимка.
  const t = d.time.data, now = d.observed_at;
  if (t?.plan_status === "APPROVED" && now) {
    if (wave.status === "LAUNCHED" && t.finish_at && minutes(t.finish_at, now) > 0) out.push({ key: `${w}:TF`, wave_id: w, task_id: null, severity: "BLOCKER",
      basis: `Утверждённое окончание волны прошло ${minutes(t.finish_at, now)} мин назад`, source: "time-context", impact: "волна не завершена; утверждённое время её не покрывает", owner: null,
      action: { label: "Загрузка ресурсов", page: "resource-workload.html", params: { wave_id: w } } });
    if (wave.status === "PREVIEW" && t.start_at && minutes(t.start_at, now) > 0) out.push({ key: `${w}:TS`, wave_id: w, task_id: null, severity: "WARNING",
      basis: `Утверждённое начало волны прошло ${minutes(t.start_at, now)} мин назад, волна не запущена`, source: "time-context", impact: "сборка начнётся позже утверждённого времени", owner: null,
      action: { label: "Загрузка ресурсов", page: "resource-workload.html", params: { wave_id: w } } });
  }
  for (const r of d.replenishment.data ?? []) if (r.wait_reason && isOpenReplenishment(r.status)) out.push({ key: `${w}:P:${r.pick_wave_replenish_task_id}`, wave_id: w, task_id: r.pick_wave_replenish_task_id, severity: "WARNING",
    basis: `Пополнение ждёт: ${r.wait_reason} · ${r.articul}`, source: "replenishment-progress", impact: `осталось ${r.demand_remaining_base ?? "нет данных"} баз. ед.`, owner: null,
    action: { label: "Пополнение волны", page: "wave-replenishment.html", params: { wave_id: w } } });
  return out;
}

/** Риски текущего исполнения: блокировки сборки и открытые недостачи. Исполнитель — из assigned_to, если есть. */
export function executionRisks(tasks: CaseTask[], shorts: CaseShort[]): Risk[] {
  const out: Risk[] = tasks.filter(t => isOpenCase(t.status) && t.blocking_reason).map(t => ({ key: `C:${t.case_pick_task_id}`, wave_id: t.pick_wave_id, task_id: t.case_pick_task_id, severity: "BLOCKER" as const,
    basis: `Сборка остановлена: ${t.blocking_reason}${t.blocking_cell_code ? " · ячейка " + t.blocking_cell_code : ""}`, source: "case-pick/tasks",
    impact: `строк ${t.picked_lines} из ${t.total_lines}`, owner: t.assigned_to, action: { label: "Открыть задание", page: "case-pick-management.html", params: { task_id: t.case_pick_task_id } } }));
  for (const s of shorts.filter(x => isPendingShort(x.status))) out.push({ key: `S:${s.case_pick_short_id}`, wave_id: s.pick_wave_id, task_id: s.case_pick_task_id,
    severity: "WARNING", basis: `Недостача ждёт решения: ${s.articul}${s.reason_code ? " · " + s.reason_code : ""}`, source: "case-pick/shorts",
    impact: `не собрано ${s.short_qty}`, owner: null, action: { label: "Разбор недостачи", page: "short-investigation.html" } });
  return out;
}

const CONTROL = new Set(["WAIT_CONTROL", "CONTROL_IN_PROGRESS"]);

/** C-0159: ход сборки запущенной волны — контроль и назначение. Считаются только видимые сотруднику задания (сервер фильтрует
 *  владельцев до лимита); при обрезанной выборке число — «не меньше». Свободность ресурсов не выводится: открытые сессии — факт. */
export function progressRisks(waves: Wave[], details: Map<number, WaveDetail>, tasks: CaseTask[] | null, truncated: boolean,
  sessions: Session[] | null, sessionsTruncated: boolean): Risk[] {
  if (!tasks) return [];
  const out: Risk[] = [], prefix = truncated ? "не меньше " : "";
  const pickers = sessions && !sessionsTruncated ? sessions.filter(s => s.status === "ACTIVE" && s.resource_type === "CASE_PICKER").length : null;
  for (const wave of waves.filter(x => x.status === "LAUNCHED")) {
    const w = wave.pick_wave_id, own = tasks.filter(t => t.pick_wave_id === w);
    const control = own.filter(t => CONTROL.has(t.status));
    if (control.length) out.push({ key: `${w}:CTL`, wave_id: w, task_id: control[0].case_pick_task_id, severity: "WARNING",
      basis: `Ждут контроля: ${prefix}${control.length} коробов`, source: "case-pick/tasks", impact: "волна не завершится, пока контроль не выполнен",
      owner: null, action: { label: "Открыть задание", page: "case-pick-management.html", params: { task_id: control[0].case_pick_task_id } } });
    const released = details.get(w)?.pick.data?.released_at;  // неразрешённый отбор — отдельный риск выше
    const free = own.filter(t => t.status === "NEW" && !t.assigned_to);
    if (released && free.length) out.push({ key: `${w}:UNA`, wave_id: w, task_id: free[0].case_pick_task_id, severity: "WARNING",
      basis: `Задания без исполнителя: ${prefix}${free.length}`, source: "case-pick/tasks",
      impact: pickers == null ? "сессии комплектовщиков не проверены полностью" : pickers === 0 ? "открытых сессий комплектовщиков на складе нет" : `открытых сессий комплектовщиков: ${pickers}`,
      owner: null, action: { label: "Открыть задание", page: "case-pick-management.html", params: { task_id: free[0].case_pick_task_id } } });
  }
  return out;
}
