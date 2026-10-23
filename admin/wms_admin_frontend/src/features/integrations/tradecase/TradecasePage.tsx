import { useEffect, useRef, useState } from "react";
import { SupplyParts } from "./SupplyParts";
import { CompositionAck } from "./CompositionAck";
import { TABS, cardPath, listPath, sitePath, tcHelp } from "./api";
import type { Buyout, DocCard, DocRow, Kind, MsgCard, MsgRow, Page, Site, StockGroup, Tab } from "./api";
import { useRead } from "./useRead";
import { DocList, KIND_NAME, MsgList } from "./Lists";
import type { Names } from "./Lists";
import { DocumentView, MessageView } from "./Cards";
import { Flow } from "./Flow";
import { StockList } from "./Stock";
import { FullPalletBinding } from "./FullPalletBinding";
import { PalletFloorDeclaration } from "./PalletFloorDeclaration";
import { BindPanel } from "./Bind";
import { BuyoutList, BuyoutView } from "./Buyouts";
import { BuyoutBasis } from "./BuyoutCreate";
import { CaseReturn } from "./CaseReturn";
import { SortPanel } from "./Sort";
import { NeedPreview } from "./NeedPreview";
import { TripExecution } from "./TripExecution";
import { Act, HelpLink } from "./ui";
import "./tradecase.css";

type View = { wh: string; tab: Tab; after: string | null; open: string | null; pending: boolean };
const TAB_IDS = TABS.map(t => t.id);
function fromUrl(): View {
  const q = new URLSearchParams(location.search), tab = q.get("tc_tab") as Tab;
  return { wh: (q.get("tc_wh") ?? "").replace(/\D/g, ""), tab: TAB_IDS.includes(tab) ? tab : "ORDER", after: q.get("tc_after"), open: q.get("tc_open"), pending: q.get("tc_pending") === "1" };
}
function toUrl(v: View) {
  const url = new URL(location.href);
  for (const [k, val] of [["tc_wh", v.wh], ["tc_tab", v.tab], ["tc_after", v.after], ["tc_open", v.open], ["tc_pending", v.pending ? "1" : null]] as const) if (val) url.searchParams.set(k, val); else url.searchParams.delete(k);
  history.replaceState(history.state, "", url);
}
type Workspaces = { warehouses: { warehouse_id: number; title: string }[]; has_more: boolean; limit: number };

/** Рабочее место оснований, запаса и команд СНС/BLC. Склад/вкладка/курсор/карточка — в адресе, возврат сохраняет их. */
export function TradecasePage({ onBack, onWorkspace }: { onBack: () => void; onWorkspace?: (desk: "shift" | "yard", warehouse: string) => void }) {
  const [view, setView] = useState(fromUrl), [prev, setPrev] = useState<(string | null)[]>([]), [reload, setReload] = useState(0);
  const names = useRef<{ wh: string; map: Names }>({ wh: "", map: new Map() });
  const cardRef = useRef<HTMLElement>(null);
  useEffect(() => toUrl(view), [view]);
  const go = (patch: Partial<View>) => setView(v => ({ ...v, ...patch }));
  const chooseWh = (wh: string) => { setPrev([]); setView({ wh, tab: view.tab, after: null, open: null, pending: view.pending }); };
  const chooseTab = (tab: Tab) => { setPrev([]); go({ tab, after: null, open: null }); };
  const openRelated = (kind: Kind, id: string) => { setPrev([]); go({ tab: kind, after: null, open: id }); };
  const ws = useRead<Workspaces>("/api/access/workspaces?capability=tradecase");
  const user = useRead<{ username: string }>("/api/access/navigation").data?.username ?? "";
  const site = useRead<Site>(view.wh ? sitePath(view.wh) : null, reload);
  const list = useRead<Page<DocRow | MsgRow>>(view.wh && !["SORT", "RETURN"].includes(view.tab) ? listPath(view.wh, view.tab, view.after, view.pending) : null, reload);
  const openBuyout = (id: string) => { setPrev([]); setReload(n => n + 1); go({ tab: "BUYOUTS", after: null, open: id }); };
  const card = useRead<DocCard | MsgCard>(view.wh && view.open ? cardPath(view.wh, view.tab, view.open) : null, reload);
  if (names.current.wh !== view.wh) names.current = { wh: view.wh, map: new Map() };
  if (list.data && ["SKU", "OWNER", "RECIPIENT"].includes(view.tab))
    for (const r of list.data.items as DocRow[]) if (typeof r.payload.title === "string") names.current.map.set(view.tab + ":" + r.document_id, r.payload.title);
  useEffect(() => { if (view.open && card.data) cardRef.current?.scrollIntoView({ block: "nearest" }); }, [view.open, card.data]);
  const tabLabel = TABS.find(t => t.id === view.tab)!.label;
  return <main className="tc" aria-label="СНС/BLC: основания и обмен">
    <header className="tc-panel tc-head">
      <Act help={tcHelp.back} onClick={onBack}>← Назад</Act>
      <div className="tc-title"><b>СНС/BLC · основания и обмен</b><small>заказы, запас, выкуп и исполнение рейсов</small></div>
      <label>Склад <input list="tc-wh" inputMode="numeric" value={view.wh} placeholder="код склада" onChange={e => chooseWh(e.target.value.replace(/\D/g, ""))}
        title={tcHelp.warehouse.text} data-help-id={tcHelp.warehouse.id} />
        <datalist id="tc-wh">{ws.data?.warehouses.map(w => <option key={w.warehouse_id} value={String(w.warehouse_id)}>{w.title}</option>)}</datalist></label>
      <Act help={tcHelp.refresh} disabled={!view.wh} onClick={() => setReload(n => n + 1)}>Обновить</Act>
      {onWorkspace && <>
        <Act help={{ id: "tradecase.shift", anchor: "shift", text: "Открыть старшего смены и общий Гант ресурсов выбранного склада. Доступ к данным проверяет сервер." }} disabled={!view.wh} onClick={() => onWorkspace("shift", view.wh)}>Смена и ресурсы</Act>
        <Act help={{ id: "tradecase.yard", anchor: "shift", text: "Открыть обзор двора по всем доступным складам. Общий Гант откроется на выбранном складе; доступ проверяет сервер." }} disabled={!view.wh} onClick={() => onWorkspace("yard", view.wh)}>Двор: общий обзор</Act>
      </>}
      <HelpLink anchor="screen" />
    </header>
    {!view.wh ? <p className="tc-panel tc-note">Выберите склад. Список подсказок — ваши текущие доступы; право на СНС/BLC проверит сервер.{ws.data?.has_more ? ` Показаны первые ${ws.data.limit}; другой склад введите кодом.` : ""}</p> : <>
      <section className="tc-panel tc-site" aria-label="Площадка">
        {site.loading && !site.data ? <span>Читаем площадку…</span> : site.error ? <span className="tc-err" role="alert">{site.error}</span> : site.data && <>
          <span>Источник: <b>{site.data.source_id}</b></span><span>Активная СКМ: <b>{site.data.active_skm}</b></span>
          <span>План: <b>{site.data.planning_source === "SAP" ? "SAP" : site.data.planning_source === "INTERNAL" ? "встроенная ТМС" : site.data.planning_source}</b></span>
          <span className={"tc-chip " + (site.data.enabled ? "ok" : "off")}>{site.data.enabled ? "приём включён" : "приём выключен"}</span><small>версия настроек {site.data.version}</small></>}
      </section>
      <Flow onTab={chooseTab} />
      <label className="tc-mobile-tabs">Раздел<select value={view.tab} onChange={e => chooseTab(e.target.value as Tab)} title="Перейти к выбранному разделу на этом складе" data-help-id="tradecase.mobile-tab">
        {TABS.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
      </select></label>
      <div className="tc-tabs" role="tablist" aria-label="Виды документов">{TABS.map(t =>
        <button key={t.id} role="tab" aria-selected={view.tab === t.id} title={tcHelp.tab.text + " (" + t.label + ")"} data-help-id={tcHelp.tab.id + "." + t.id} onClick={() => chooseTab(t.id)}>{t.label}</button>)}</div>
      {view.tab === "RETURN" ? <CaseReturn key={view.wh} wh={view.wh} user={user} /> : view.tab === "SORT" ? <SortPanel wh={view.wh} user={user} /> : <div className="tc-body">
        <section className="tc-panel" aria-label={tabLabel}>
          <h3>{tabLabel} {view.after && view.after !== "0" && <small>· не первая страница</small>}
            {view.tab === "BUYOUTS" && <label className="tc-check"><input type="checkbox" checked={view.pending} onChange={e => { setPrev([]); go({ pending: e.target.checked, after: null, open: null }); }} title={tcHelp.pending.text} data-help-id={tcHelp.pending.id} /> Есть ожидающие коды</label>} <HelpLink anchor={view.tab === "MESSAGES" ? "exchange" : view.tab === "STOCK" ? "stock" : view.tab === "SUPPLY" ? "bind" : view.tab === "NEED" ? "need" : "order"} /></h3>
          {view.tab === "MESSAGES" && <SupplyParts key={"parts:" + view.wh + ":" + user} wh={view.wh} onResult={id => go({ tab: "MESSAGES", open: id, after: null })} />}
          {view.tab === "MESSAGES" && <CompositionAck key={"composition:" + view.wh + ":" + user} wh={view.wh} onOpen={id => go({ tab: "ORDER", open: id, after: null })} />}
          {list.error && <p className="tc-err" role="alert">{list.error}</p>}
          {list.loading && !list.data ? <p className="tc-note">Читаем страницу…</p> : list.data && (list.data.items.length === 0 ? <p className="tc-note">На этой странице записей нет.</p>
            : view.tab === "BUYOUTS" ? <BuyoutList rows={list.data.items as unknown as Buyout[]} names={names.current.map} selected={view.open ?? ""} onOpen={id => go({ open: id })} />
            : view.tab === "STOCK" ? <><StockList rows={list.data.items as unknown as StockGroup[]} names={names.current.map} filtered={list.data.owner_scope_filtered} /><FullPalletBinding key={view.wh + ":" + user} wh={view.wh} user={user} /><PalletFloorDeclaration key={"floor:" + view.wh + ":" + user} wh={view.wh} user={user} /></>
            : view.tab === "MESSAGES" ? <MsgList rows={list.data.items as MsgRow[]} selected={view.open ?? ""} onOpen={id => go({ open: id })} />
            : <DocList tab={view.tab} rows={list.data.items as DocRow[]} names={names.current.map} selected={view.open ?? ""} onOpen={id => go({ open: id })} />)}
          <div className="tc-pager">
            {(prev.length > 0 || view.after) && <Act help={tcHelp.first} onClick={() => { setPrev([]); go({ after: null, open: null }); }}>⟲ К первой странице</Act>}
            {prev.length > 0 && <Act help={{ ...tcHelp.first, id: "tradecase.prev", text: "Предыдущая страница этого вида." }} onClick={() => { const p = [...prev]; const back = p.pop() ?? null; setPrev(p); go({ after: back, open: null }); }}>← Назад</Act>}
            {list.data?.has_more && list.data.next_after && <Act help={tcHelp.next} onClick={() => { setPrev(p => [...p, view.after]); go({ after: list.data!.next_after, open: null }); }}>Далее →</Act>}
          </div>
        </section>
        {view.open && <section ref={cardRef} className="tc-panel tc-card" aria-label={"Карточка " + view.open}>
          <h3><span>{view.tab === "MESSAGES" ? "Сообщение обмена" : view.tab === "BUYOUTS" ? "Выкуп" : KIND_NAME[view.tab]} <b>{view.tab === "MESSAGES" ? view.open.slice(0, 8) + "…" : view.open}</b></span>
            <Act help={tcHelp.close} aria-label="Закрыть карточку" onClick={() => go({ open: null })}>×</Act></h3>
          {card.error ? <p className="tc-err" role="alert">{card.error}</p> : card.loading && !card.data ? <p className="tc-note">Читаем карточку…</p>
            : card.data && (view.tab === "BUYOUTS" ? <BuyoutView key={view.open} wh={view.wh} card={card.data as unknown as Buyout} names={names.current.map} /> : view.tab === "MESSAGES" ? <MessageView key={view.wh + ":" + view.open} card={card.data as MsgCard} onOpen={openRelated} onDone={() => setReload(n => n + 1)} /> : <DocumentView card={card.data as DocCard} names={names.current.map} onOpen={openRelated}
              bind={(card.data as DocCard).entity_type === "SUPPLY" ? <BindPanel wh={view.wh} user={user} card={card.data as DocCard} names={names.current.map} onOpen={openRelated} onDone={() => setReload(n => n + 1)} />
                : (card.data as DocCard).entity_type === "NEED" ? <NeedPreview key={view.open} wh={view.wh} id={view.open} />
                : (card.data as DocCard).entity_type === "TRIP" ? <TripExecution key={view.open} wh={view.wh} user={user} trip={card.data as DocCard} />
                : (card.data as DocCard).entity_type === "ORDER" && (card.data as DocCard).payload.order_kind === "BUYOUT" ? <BuyoutBasis wh={view.wh} user={user} order={card.data as DocCard} names={names.current.map} onDone={openBuyout} /> : null} />)}
        </section>}
      </div>}</>}
  </main>;
}
