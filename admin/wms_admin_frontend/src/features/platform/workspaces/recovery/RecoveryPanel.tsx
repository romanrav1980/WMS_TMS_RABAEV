import { useState } from "react";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { RECOVERY_LIMIT, STAGES, legacyDate, ownerLinks, recoveryHelpUrl, remainingText, stageMeta, stageOf } from "./recoveryModel";
import type { RecoveryRow, Stage } from "./recoveryModel";
import type { RecoveryRead } from "./useRecovery";
import "./recovery.css";

const h = (id: string, text: string): HelpEntry => ({ id: "recovery." + id, text, article: "short-recovery" });
const help = {
  stage: h("stage", "Показать недостачи только этого этапа восстановления. Повторное нажатие снимает фильтр."),
  row: h("row", "Открыть карточку недостачи: этап, сборка, волна, задания и ссылки на экраны-владельцы."),
  back: h("back", "Вернуться к списку недостач; выбранный этап фильтра сохраняется."),
  wave: h("wave", "Открыть карточку этой волны на рабочем месте и подсветить её на схеме."),
  investigation: h("open.investigation", "Открыть разбор недостачи. Решения по недостаче принимаются там, с проверкой права."),
  inventory: h("open.inventory", "Открыть пересчёт ячейки по заданию инвентаризации."),
  replenishment: h("open.replenishment", "Открыть пополнение волны на этом складе."),
  task: h("open.task", "Открыть складское задание пополнения."),
  refresh: h("refresh", "Перечитать недостачи с сервера. Ничего не меняет."),
};
const link = (href: string, e: HelpEntry, label: string) => <a className="rc-link" href={href} target="_blank" rel="noopener" title={e.text} data-help-id={e.id}>{label}</a>;

/** Обзор восстановления недостач. Только чтение и навигация: решения, пересчёт и пополнение — в экранах-владельцах. */
export function RecoveryPanel({ read, scopeLabel, onWave, onSelect, onRefresh, openId: openProp, filter: filterProp, onFilter }: { read: RecoveryRead; scopeLabel: string;
  onWave?: (waveId: number) => void; onSelect?: (row: RecoveryRow | null) => void; onRefresh: () => void;
  /** Управляемый выбор (стол хранит его, чтобы вернуться к той же недостаче после перехода к волне). */ openId?: number | null; filter?: Stage | null; onFilter?: (s: Stage | null) => void }) {
  const [filterOwn, setFilterOwn] = useState<Stage | null>(null), [openOwn, setOpenOwn] = useState<number | null>(null);
  const openId = openProp !== undefined ? openProp : openOwn, filter = filterProp !== undefined ? filterProp : filterOwn;
  const setOpenId = (v: number | null) => { if (openProp === undefined) setOpenOwn(v); };
  const setFilter = (f: (old: Stage | null) => Stage | null) => { const next = f(filter); if (onFilter) onFilter(next); else setFilterOwn(next); };
  const rows = read.rows ?? [], open = rows.find(r => r.short_id === openId) ?? null;
  const select = (r: RecoveryRow | null) => { setOpenId(r?.short_id ?? null); onSelect?.(r); };
  const counts = new Map<Stage, number>(); for (const r of rows) counts.set(stageOf(r), (counts.get(stageOf(r)) ?? 0) + 1);
  const shown = filter ? rows.filter(r => stageOf(r) === filter) : rows;
  return <section className="ops-card rc" aria-label="Восстановление недостач">
    <h3 className="rc-head"><span>Восстановление недостач</span>
      <a className="rc-link" href={recoveryHelpUrl()} target="_blank" rel="noopener" title="Справка: этапы восстановления и ограничения выборки. Откроется в новой вкладке" data-help-id="recovery.help">Справка</a></h3>
    <p className="ops-note">{scopeLabel} · {read.rows ? `показано ${rows.length}${rows.length >= RECOVERY_LIMIT ? `, выборка до ${RECOVERY_LIMIT} — полнота неизвестна` : ""}` : ""}
      {read.at ? ` · прочитано ${read.at.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })}` : ""}</p>
    {read.error && <p className="ops-err" role="alert">{read.error}{read.stale ? " Показан прежний снимок — он устарел, «проблем нет» из него не следует." : ""}</p>}
    {read.loading && !read.rows && <p className="ops-note">Загрузка…</p>}
    {read.rows && rows.length === 0 && !read.error && <p className="ops-note">Открытых недостач в выборке нет.</p>}
    {open ? <RecoveryCard row={open} onBack={() => select(null)} onWave={onWave} /> : rows.length > 0 && <>
      <div className="rc-stages" role="group" aria-label="Этапы восстановления">{STAGES.filter(s => counts.get(s.id)).map(s =>
        <button key={s.id} type="button" aria-pressed={filter === s.id} className={"ops-chip " + s.tone} title={help.stage.text} data-help-id={help.stage.id + "." + s.id}
          onClick={() => setFilter(f => f === s.id ? null : s.id)}>{s.label} · {counts.get(s.id)}</button>)}</div>
      <ul className="ops-list rc-list">{shown.map(r => { const st = stageMeta(stageOf(r)); return <li key={r.short_id}>
        <button type="button" className="rc-row" title={help.row.text} data-help-id={help.row.id} onClick={() => select(r)}>
          <b className="rc-ellipsis">{r.article ?? "артикул не указан"} · {r.cell ?? "ячейка не указана"}</b>
          <small>недостача {r.short_quantity ?? "—"} · волна {r.pick_wave_id}{scopeLabel.startsWith("Все") ? ` · склад ${r.warehouse_id}` : ""}{st.id === "UNKNOWN" ? ` · код ${r.status}/${r.recovery_state ?? "—"}` : ""}</small>
          <span className={"ops-chip " + st.tone}>{st.label}</span>
        </button></li>; })}</ul></>}
    <div className="rc-actions"><HelpButton help={help.refresh} disabled={read.loading} onClick={onRefresh}>Обновить</HelpButton></div>
  </section>;
}

function RecoveryCard({ row: r, onBack, onWave }: { row: RecoveryRow; onBack: () => void; onWave?: (waveId: number) => void }) {
  const st = stageMeta(stageOf(r)), links = ownerLinks(r), left = remainingText(r.remaining_seconds);
  return <div className="rc-card" aria-label={"Недостача " + r.short_id}>
    <HelpButton help={help.back} onClick={onBack}>← К списку</HelpButton>
    <p><span className={"ops-chip " + st.tone}>{st.label}</span> <small className="ops-note">недостача {r.short_id} · {r.status}{r.recovery_state ? " / " + r.recovery_state : ""}</small></p>
    {st.id === "UNKNOWN" && <p className="ops-err">Состояние сервера не распознано: не трактуется как «готово». Проверьте в разборе недостачи.</p>}
    {r.recovery_last_error && <p className="ops-err">Ошибка восстановления: {r.recovery_last_error}</p>}
    <dl>
      <dt>Товар / ячейка</dt><dd>{r.article ?? "—"} · {r.cell ?? "—"}</dd>
      <dt>Количество</dt><dd>недостача {r.short_quantity ?? "—"} · восстановлено {r.restored_quantity ?? "—"} · осталось по строке {r.order_remaining_quantity ?? "—"} <small>(в единице строки)</small></dd>
      <dt>Сборка</dt><dd>задание {r.case_pick_task_id} · строка {r.case_pick_line_id}{r.picker ? " · " + r.picker : ""}</dd>
      <dt>Волна</dt><dd>{r.pick_wave_id} {onWave && <HelpButton help={help.wave} onClick={() => onWave(r.pick_wave_id)}>Волна</HelpButton>}</dd>
      <dt>Пересчёт</dt><dd>{r.inventory_task_id ? `задание ${r.inventory_task_id} · ${r.inventory_status ?? "статус —"}${r.auditor ? " · " + r.auditor : ""}${r.count_operation_id ? " · пересчёт " + r.count_operation_id : ""}` : "не назначен"}</dd>
      <dt>Пополнение</dt><dd>{r.replenish_task_id ? `${r.replenish_status ?? "статус —"}${r.wait_reason ? " · ждёт: " + r.wait_reason : ""}${r.warehouse_task_id ? " · складское задание " + r.warehouse_task_id : ""}` : "не назначено"}</dd>
      <dt>Срок</dt><dd>{left ? `${left} (по часам сервера на момент чтения)` : "—"}{r.recovery_deadline_at ? ` · до ${legacyDate(r.recovery_deadline_at)}` : ""}</dd>
      {r.restored_at && <><dt>Восстановлено</dt><dd>{legacyDate(r.restored_at)}</dd></>}
    </dl>
    <p className="ops-note">Даты — время источника без часового пояса.</p>
    <div className="rc-actions">
      {link(links.investigation, help.investigation, "Разбор недостачи")}
      {links.inventory && link(links.inventory, help.inventory, "Пересчёт")}
      {link(links.replenishment, help.replenishment, "Пополнение волны")}
      {links.warehouseTask && link(links.warehouseTask, help.task, "Складское задание")}
    </div>
  </div>;
}
