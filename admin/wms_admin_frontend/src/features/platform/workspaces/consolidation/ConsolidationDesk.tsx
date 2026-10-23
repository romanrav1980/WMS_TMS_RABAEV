import { useEffect, useState } from "react";
import { apiFetch, apiOperationScope } from "../../../../api";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { readError } from "../../access-admin";
import { WarehousePicker } from "../resources/WarehousePicker";
import { HuTreeDesk } from "./HuTreeDesk";
import { PlanEditor } from "./PlanEditor";
import type { EditorValue } from "./PlanEditor";
import { PlanView } from "./PlanView";
import { refusalText, readPending, savePending, sendPending } from "./planCommands";
import type { PlanIntent } from "./planCommands";
import { PlanShapeError, parseDetail, planHelpUrl, utcShort } from "./planModel";
import type { PlanDetail } from "./planModel";
import { PLAN_PAGE, usePlanList } from "./usePlanList";
import type { PlanFilter } from "./usePlanList";
import "./plan.css";
import { readUrlWarehouse, writeUrlWarehouse } from "../useUrlWarehouse";

const h = (id: string, text: string): HelpEntry => ({ id: "consolidation." + id, text, article: "consolidation-plan" });
const help = {
  filter: h("filter", "Какие планы показать: действующие, отменённые или все."),
  plan: h("plan", "Открыть план: ожидаемый состав и готовность."),
  more: h("more", `Показать следующие ${PLAN_PAGE} планов выбранного склада.`),
  create: h("create", "Создать новый план ожидаемого состава для выбранного склада."),
  retry: h("retry", "Повторить сохранённую команду с тем же номером и телом: второй раз изменение не применится."),
  reread: h("reread", "Перечитать план с сервера и проверить, применилась ли команда."),
  shift: h("shift", "Открыть старшего смены этого склада."),
};
const newPlanId = (wh: string) => `CP.${wh}.${new Date().toISOString().slice(0, 10).replace(/-/g, "")}.${crypto.randomUUID().slice(0, 8)}`;
const initialWh = readUrlWarehouse;

/** Ожидаемый состав паллеты (план) и физическое дерево — раздельно, в стиле двойника (C0116). Только чтение + PUT/cancel плана через журнал. */
export function ConsolidationDesk() {
  const scope = apiOperationScope();
  const [wh, setWh] = useState(initialWh), [filter, setFilter] = useState<PlanFilter>("ACTIVE"), [reload, setReload] = useState(0);
  const [planId, setPlanId] = useState<string | null>(null), [plan, setPlan] = useState<PlanDetail | null>(null), [planError, setPlanError] = useState("");
  const [editing, setEditing] = useState<"edit" | "new" | null>(null), [draftId, setDraftId] = useState(""), [tree, setTree] = useState("");
  const [pending, setPending] = useState(readPending()), [busy, setBusy] = useState(false), [note, setNote] = useState("");
  const [plansOpen, setPlansOpen] = useState(() => !!pending.intent || !!pending.damaged);
  const list = usePlanList(wh, filter, scope, reload);
  const chooseWh = (id: string) => { setWh(id); setPlanId(null); setPlan(null); setEditing(null); setTree(""); writeUrlWarehouse(id); };
  useEffect(() => { // карточка плана: ответ другого плана/склада не применяется; 401/403/404 очищают
    setPlan(null); setPlanError(""); if (!planId) return;
    const ctrl = new AbortController();
    apiFetch<unknown>(`/api/consolidation-plans/${encodeURIComponent(planId)}`, { signal: ctrl.signal })
      .then(v => { if (!ctrl.signal.aborted) { const d = parseDetail(v, planId); if (String(d.warehouse_id) !== wh) throw new PlanShapeError("План относится к другому складу."); setPlan(d); } })
      .catch(e => { if (!ctrl.signal.aborted) setPlanError(e instanceof PlanShapeError ? e.message : readError(e)); });
    return () => ctrl.abort();
  }, [planId, wh, reload, scope]);
  async function run(intent: PlanIntent) {
    setBusy(true); setNote("");
    const r = await sendPending(intent);
    setBusy(false); setPending(readPending());
    if (r.kind === "ack") { setNote(`Сохранено: план ${r.ack.plan_id}, версия ${r.ack.version}${r.ack.status === "CANCELLED" ? " (отменён)" : ""}.`); setPlansOpen(true); setEditing(null); setPlanId(r.ack.plan_id); setReload(n => n + 1); }
    else if (r.kind === "refused") { setNote(refusalText(r.code) + " Изменение не применено."); setEditing(null); setReload(n => n + 1); }
    else setNote(r.message);
  }
  function start(kind: "SAVE" | "CANCEL", id: string, body: Record<string, unknown>) {
    try { const intent = savePending(kind, id, { operation_id: `CP.${crypto.randomUUID()}`, ...body }); setPending(readPending()); void run(intent); }
    catch (e) { setNote(e instanceof Error ? e.message : String(e)); setPending(readPending()); }
  }
  const save = (v: EditorValue) => start("SAVE", editing === "new" ? draftId : planId!, { expected_version: editing === "new" ? 0 : plan!.version, reason: v.reason,
    root_identifier: v.root_identifier, warehouse_id: Number(wh), cell: v.cell, fulfillment_ids: [...new Set(v.members.map(m => m.fulfillment_id))].sort((a, b) => a - b) });
  const cancelPlan = (reason: string) => start("CANCEL", planId!, { expected_version: plan!.version, reason });
  const blocked = !!pending.intent || !!pending.damaged || busy;
  return <>
    <div className="ops-panel rg-window" style={{ gridColumn: "1/-1" }}>
      <WarehousePicker capability="warehouse_tasks" value={wh} onChange={chooseWh} />
      <label>Планы <select value={filter} onChange={e => setFilter(e.target.value as PlanFilter)} title={help.filter.text} data-help-id={help.filter.id}>
        <option value="ACTIVE">действующие</option><option value="CANCELLED">отменённые</option><option value="ALL">все</option></select></label>
      <HelpButton help={help.create} unavailable={!wh && "выберите склад"} disabled={blocked} onClick={() => { setPlansOpen(true); setDraftId(newPlanId(wh)); setEditing("new"); setPlanId(null); }}>Новый план</HelpButton>
      {wh && <HelpButton help={help.shift} onClick={() => { location.href = `?page=workspace&workspace=shift&warehouse_id=${wh}`; }}>Старший смены</HelpButton>}
      <a href={planHelpUrl("save")} target="_blank" rel="noopener" title="Справка по плану ожидаемого состава; откроется в новой вкладке" data-help-id="consolidation.help">Справка</a>
    </div>
    {(pending.intent || pending.damaged) && <section className="ops-panel cp-pending" style={{ gridColumn: "1/-1" }} role="status">
      {pending.damaged ? <p className="ops-err">{pending.damaged}</p> : <>
        <b>Команда плана ожидает подтверждения</b> · {pending.intent!.kind === "SAVE" ? "сохранение" : "отмена"} плана {pending.intent!.plan_id}. Новые изменения заблокированы.
        <div className="cp-actions"><HelpButton help={help.retry} disabled={busy} onClick={() => void run(pending.intent!)}>Повторить ту же команду</HelpButton>
          <HelpButton help={help.reread} disabled={busy} onClick={() => { setPlansOpen(true); setPlanId(pending.intent!.plan_id); setReload(n => n + 1); }}>Перечитать план</HelpButton>
          <a href={planHelpUrl("conflict")} target="_blank" rel="noopener" title="Справка: потеря ответа и конфликт версии" data-help-id="consolidation.pending.help">Справка</a></div></>}
    </section>}
    {note && <p className="ops-panel ops-note" style={{ gridColumn: "1/-1" }} role="status">{note}</p>}
    <details className="ops-panel cp-plan-section" open={plansOpen} onToggle={e => setPlansOpen(e.currentTarget.open)}>
      <summary title="Открыть или свернуть список и редактор планов консолидации" data-help-id="consolidation.plans.toggle">Планы консолидации{list.error ? " · недоступны" : ""}</summary>
      <div className={"cp-plan-grid" + (editing ? " cp-plan-editing" : "")}>
    <aside className="ops-panel ops-left" aria-label="Планы склада">
      <h3>Планы <small>{wh ? `загружено ${list.items.length}${list.hasMore ? ", есть ещё" : ""} · время UTC` : "выберите склад"}</small></h3>
      {list.error && <p className="ops-err">{list.error}</p>}
      {wh && !list.loading && !list.error && list.items.length === 0 && <p className="ops-note">Планов нет.</p>}
      <ul className="ops-list">{list.items.map(p => <li key={p.plan_id} className={planId === p.plan_id ? "cp-selected" : ""}>
        <span><b className="cp-uid" title={p.root_identifier}>{p.root_identifier}</b><br /><small>{p.status === "CANCELLED" ? "отменён · " : ""}ожидается {p.expected_count} · {p.cell} · {utcShort(p.updated_at)}</small></span>
        <HelpButton help={help.plan} onClick={() => { setPlanId(p.plan_id); setEditing(null); }}>Открыть</HelpButton></li>)}</ul>
      {list.hasMore && <HelpButton help={help.more} disabled={list.loading} onClick={list.more}>Ещё</HelpButton>}
      {list.loading && wh && <p className="ops-note">Загрузка…</p>}
    </aside>
    <section className="ops-panel ops-center cp-center" aria-label="Ожидаемый состав">
      {planError && <p className="ops-err">{planError}</p>}
      {plan ? <PlanView plan={plan} busy={blocked} onTree={() => setTree(plan.root_identifier)} onEdit={() => setEditing("edit")} onRefresh={() => setReload(n => n + 1)} />
        : !planError && <p className="ops-note">{wh ? "Выберите план слева или создайте новый." : "Выберите склад."}</p>}
    </section>
    {editing && <aside className="ops-panel ops-right" aria-label="Изменение плана">
      <PlanEditor key={(editing === "new" ? draftId : planId) + ":" + (plan?.version ?? 0)} plan={editing === "edit" ? plan : null} warehouseId={wh}
        planId={editing === "new" ? draftId : planId ?? ""} busy={blocked} onSave={save} onCancelPlan={cancelPlan} onClose={() => setEditing(null)} />
    </aside>}
      </div>
    </details>
    <HuTreeDesk identifier={tree} />
  </>;
}
