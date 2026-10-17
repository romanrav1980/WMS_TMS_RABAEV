import { useEffect, useMemo, useState } from "react";
import { readUrlWarehouse, writeUrlWarehouse } from "../useUrlWarehouse";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { useApiRead } from "../../access-admin";
import { IsoStageScene } from "../IsoStageScene";
import type { IsoStage, IsoTone } from "../IsoStageScene";
import { KpiTile, SourceStrip } from "../OpsParts";
import { wsHelp } from "../help";
import { openLink } from "../resources/ResourceCard";
import { fmtTime } from "../resources/timelineModel";
import { SupplyFilterBar } from "./SupplyFilterBar";
import { BASIS, SUPPLY_LIMIT, filterError, sourceDate, supplyPath } from "./supplyQuery";
import type { SupplyFilter } from "./supplyQuery";

// Старший участка приёмки (C0049 lead_receiving). Только чтение. Приёмка паллет и закрытие поставки — в экране
// «Приёмка поставки SAP» (там operation_id и повтор тем же телом); здесь команды не отправляются.

type Order = { order_id: string; order_number: string; ware_id: number; condition: number; receive_cell?: string | null;
  date_of_accept: string | null; date_of_naklad?: string | null; planning_accept_time?: string | null; time_status?: string };
type Line = { line_number: string; articul: string; name: string | null; planned_qty: string; accepted_qty: string | null; remaining_qty: string | null; base_uom: string | null; marking_required: number | null };
type Detail = { order_id: string; order_number: string; sender: string | null; ware_id: number; receive_cell: string | null; closed_at: string | null;
  incoming_condition: number; receipt_allowed: boolean; receipt_state: string; lines: Line[] };
type Task = { task_id: number; task_type: string; status: string; from_cell: string | null; to_cell: string | null; uid_pallet: string | null; assigned_to: string | null; source_doc_type: string | null };

const h = (id: string, text: string): HelpEntry => ({ id: "receiving." + id, text, article: "receiving-lead" });
const help = {
  stage: h("scene.stage", "Состояние поставки по коду состояния SAP: приёмка открыта, принято, закрыто, сторно. Точное состояние — в карточке."),
  order: h("scene.order", "Поставка SAP. Нажмите — строки план/принято/остаток по артикулу."),
  open: h("open.receiving", "Открыть приёмку поставки: сканы паллет и закрытие выполняются там с повтором по тому же ключу."),
  putaway: h("putaway", "Открытые задания размещения после приёмки. Назначение — в складских заданиях."),
  backlog: h("backlog", "Поставки без плановой даты приёмки (backlog): в плитки и схему выбранных дней не входят, их срок источнику не известен."),
};
// Так же, как сервер выводит receipt_state из incoming_condition (supply_reads.py); closed_at виден только в карточке.
const STAGE: Record<number, { id: string; tone: IsoTone }> = { 0: { id: "OPEN", tone: "plan" }, 1: { id: "COMPLETE", tone: "warn" }, 2: { id: "CLOSED", tone: "muted" }, 3: { id: "REVERSED", tone: "bad" } };
const STAGES: IsoStage[] = [{ id: "OPEN", title: "Приёмка открыта", x: 0, y: 0 }, { id: "COMPLETE", title: "Принято (сверка — в карточке)", x: 1, y: 0 },
  { id: "CLOSED", title: "Закрыто", x: 2, y: 0 }, { id: "REVERSED", title: "Сторно", x: 1, y: 1 }, { id: "OTHER", title: "Другой код", x: 2, y: 1, dashed: true }];
const STATE_RU: Record<string, string> = { OPEN: "приёмка открыта", COMPLETE: "принято, ждёт сверки и закрытия", RECONCILED: "сверено и закрыто", LEGACY_CLOSED: "закрыто (старый контур)", REVERSED: "сторно" };

export function ReceivingLeadDesk({ day, isToday, reload }: { day: string; isToday: boolean; reload: number }) {
  const [f, setFState] = useState<SupplyFilter>(() => ({ warehouseId: readUrlWarehouse(), from: day, to: day, basis: "PLANNED_ACCEPT", unplanned: true }));
  // Склад фильтра пишется в адрес, чтобы переходы между рабочими местами открывали тот же склад (C0118).
  const setF = (next: SupplyFilter | ((old: SupplyFilter) => SupplyFilter)) => setFState(old => { const v = typeof next === "function" ? next(old) : next; if (v.warehouseId !== old.warehouseId) writeUrlWarehouse(v.warehouseId); return v; });
  const [orderId, setOrderId] = useState<string | null>(null);
  const wh = f.warehouseId;
  // Дата шапки задаёт окно «один день», пока пользователь не поменял даты сам.
  const [custom, setCustom] = useState(false);
  useEffect(() => { if (!custom) setF(old => ({ ...old, from: day, to: day })); }, [day, custom]);
  const orders = useApiRead<Order[]>(supplyPath(f), reload);
  const putaway = useApiRead<Task[]>(`/api/warehouse-tasks?status=PLANNED&task_type=PUTAWAY&limit=500${wh ? "&ware_id=" + wh : ""}`, reload); // ware_id режет сервер (C-0091)
  // Плановые в окне и backlog «без плановой даты» (include_unplanned) — разные списки: backlog не попадает в плитки дня.
  const backlogMode = f.basis === "PLANNED_ACCEPT" && f.unplanned;
  const all = useMemo(() => orders.data ?? [], [orders.data]);
  const list = useMemo(() => backlogMode ? all.filter(o => o.planning_accept_time) : all, [all, backlogMode]);
  const backlog = useMemo(() => backlogMode ? all.filter(o => !o.planning_accept_time) : [], [all, backlogMode]);
  const order = all.find(o => o.order_id === orderId);
  const basis = BASIS.find(b => b.id === f.basis)!;
  const items = list.map(o => ({ id: o.order_id, stage: STAGE[o.condition]?.id ?? "OTHER", tone: STAGE[o.condition]?.tone ?? "muted" as IsoTone, label: `Поставка ${o.order_number}`,
    title: `Поставка ${o.order_number} · склад ${o.ware_id} · код состояния ${o.condition} · ${basis.label}: ${sourceDate(o[basis.field])} (дата источника, пояс не известен). ${help.order.text}` }));
  const capped = all.length >= SUPPLY_LIMIT;
  const count = (c: number) => () => String(list.filter(o => o.condition === c).length) + (capped ? "+" : "");
  return <>
    <SupplyFilterBar f={f} onChange={(next, byUser) => { if (byUser) setCustom(true); setF(next); setOrderId(null); }} onReset={() => setCustom(false)} custom={custom} day={day}
      note={`Выборка до ${SUPPLY_LIMIT}${capped ? " — предел достигнут, сузьте окно или выберите склад" : ""}. Склад и даты фильтрует сервер.`} />
    {filterError(f) && <p className="ops-panel ops-err" style={{ gridColumn: "1/-1" }}>{filterError(f)}</p>}
    <div className="ops-kpis">
      <KpiTile icon="⤓" label="Приёмка открыта" read={orders} source="supply-orders · condition 0" value={count(0)} sub={() => "можно принимать паллеты"} />
      <KpiTile icon="⚖" label="Принято" read={orders} source="supply-orders · condition 1" value={count(1)} sub={() => "сверена ли — видно в карточке (closed_at)"} />
      <KpiTile icon="↺" label="Сторно" read={orders} source="supply-orders · condition 3" value={count(3)} sub={() => "отменённые"} />
      <KpiTile icon="▦" label="Ждут размещения" read={putaway} source="warehouse-tasks PUTAWAY PLANNED" value={(t: Task[]) => String(t.length) + (t.length >= 500 ? "+" : "")} sub={(t: Task[]) => `не назначено ${t.filter(x => !x.assigned_to).length}`} />
    </div>
    <SourceStrip isToday={isToday} day={day} sources={[["Поставки SAP", orders], ["Размещение", putaway]]} />
    <aside className="ops-panel ops-left" aria-label="Размещение после приёмки">
      <h3 title={help.putaway.text} data-help-id={help.putaway.id}>Ждут размещения <small>{putaway.data?.length ?? "—"}</small></h3>
      {putaway.error && <p className="ops-err">{putaway.error}</p>}
      <ul className="ops-list">{(putaway.data ?? []).slice(0, 15).map(t => <li key={t.task_id}><span><b>{t.uid_pallet ?? "задание " + t.task_id}</b><br />
        <small>{t.from_cell ?? "?"} → {t.to_cell ?? "?"} · {t.assigned_to ?? "не назначено"}</small></span></li>)}</ul>
      <HelpButton help={wsHelp.openTasks} onClick={() => openLink({ page: "warehouse-tasks.html" })}>Складские задания</HelpButton>
      {backlogMode && <><h3 style={{ marginTop: 14 }} title={help.backlog.text} data-help-id={help.backlog.id}>Без плановой даты <small>{orders.data ? backlog.length : "—"}</small></h3>
        <ul className="ops-list">{backlog.slice(0, 20).map(o => <li key={o.order_id}><span><b>{o.order_number}</b><br />
          <small>склад {o.ware_id} · документ {sourceDate(o.date_of_naklad)} · код {o.condition}</small></span>
          <HelpButton help={help.order} onClick={() => setOrderId(o.order_id)}>Карточка</HelpButton></li>)}</ul>
        {backlog.length > 20 && <p className="ops-note">Показано 20 из {backlog.length}.</p>}</>}
    </aside>
    <section className="ops-panel ops-center" aria-label="Поставки по состояниям">
      <span className="ops-scene-title">Поставки SAP по состояниям · схема условная</span>
      <IsoStageScene stages={STAGES} items={items} selected={orderId} onSelect={id => setOrderId(String(id))} ariaLabel="Поставки по состояниям (условная схема)"
        stageHelpId={help.stage.id} itemHelpId={help.order.id} stageHelp={help.stage.text} />
    </section>
    <aside className="ops-panel ops-right" aria-label="Выбранная поставка">
      {order ? <OrderCard order={order} reload={reload} onClose={() => setOrderId(null)} /> : <p className="ops-note">Выберите поставку на схеме.</p>}
    </aside>
  </>;
}

function OrderCard({ order, reload, onClose }: { order: Order; reload: number; onClose: () => void }) {
  const d = useApiRead<Detail>(`/api/integrations/sap/supply-orders/${encodeURIComponent(order.order_id)}`, reload);
  const lines = d.data?.lines ?? [], short = lines.filter(l => Number(l.remaining_qty) > 0);
  return <section className="ops-card" aria-label={"Поставка " + order.order_number}>
    <h3 style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><span>Поставка {order.order_number}<br /><small>склад {order.ware_id}{d.data?.sender ? " · " + d.data.sender : ""}</small></span>
      <HelpButton help={wsHelp.closeCard} onClick={onClose} aria-label="Закрыть карточку">×</HelpButton></h3>
    {d.error && <p className="ops-err">{d.error}</p>}{!d.data && !d.error && <p className="ops-note">Загрузка…</p>}
    {d.data && <><dl>
      <dt>Состояние</dt><dd>{STATE_RU[d.data.receipt_state] ?? d.data.receipt_state}</dd>
      <dt>Приём паллет</dt><dd>{d.data.receipt_allowed ? "разрешён" : "не разрешён"}</dd>
      <dt>Ячейка приёмки</dt><dd>{d.data.receive_cell ?? "—"}</dd>
      <dt>Закрыта</dt><dd>{d.data.closed_at ? fmtTime(null, d.data.closed_at) : "нет"}</dd>
      <dt>Строк</dt><dd>{lines.length}, с остатком {short.length}</dd>
    </dl>
      <ul className="ops-list">{lines.slice(0, 20).map(l => <li key={l.line_number}><span><b>{l.articul}</b> <small>{l.name ?? ""}</small><br />
        <small>план {l.planned_qty} · принято {l.accepted_qty ?? "—"} · остаток {l.remaining_qty ?? "—"} {l.base_uom ?? "(ед. не указана)"}{l.marking_required ? " · маркировка" : ""}</small></span>
        {Number(l.remaining_qty) > 0 && <span className="ops-chip other">остаток</span>}</li>)}</ul>
      <p className="ops-note">Количества — по артикулу в его базовой единице; разные артикулы не складываются.</p></>}
    <HelpButton help={help.open} onClick={() => openLink({ page: "receiving.html", params: { order_id: order.order_id } })}>Приёмка поставки</HelpButton>
  </section>;
}
