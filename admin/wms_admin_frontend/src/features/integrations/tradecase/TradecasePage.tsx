import { useEffect, useRef, useState } from "react";
import { TABS, cardPath, listPath, sitePath, tcHelp } from "./api";
import type { DocCard, DocRow, Kind, MsgCard, MsgRow, Page, Site, StockGroup, Tab } from "./api";
import { useRead } from "./useRead";
import { DocList, KIND_NAME, MsgList } from "./Lists";
import type { Names } from "./Lists";
import { DocumentView, MessageView } from "./Cards";
import { Flow } from "./Flow";
import { StockList } from "./Stock";
import { BindPanel } from "./Bind";
import { Act, HelpLink } from "./ui";
import "./tradecase.css";

type View = { wh: string; tab: Tab; after: string | null; open: string | null };
const TAB_IDS = TABS.map(t => t.id);
function fromUrl(): View {
  const q = new URLSearchParams(location.search), tab = q.get("tc_tab") as Tab;
  return { wh: (q.get("tc_wh") ?? "").replace(/\D/g, ""), tab: TAB_IDS.includes(tab) ? tab : "ORDER", after: q.get("tc_after"), open: q.get("tc_open") };
}
function toUrl(v: View) {
  const url = new URL(location.href);
  for (const [k, val] of [["tc_wh", v.wh], ["tc_tab", v.tab], ["tc_after", v.after], ["tc_open", v.open]] as const) if (val) url.searchParams.set(k, val); else url.searchParams.delete(k);
  history.replaceState(history.state, "", url);
}
type Workspaces = { warehouses: { warehouse_id: number; title: string }[]; has_more: boolean; limit: number };

/** Рабочее место оснований СНС/BLC (C-0130): только GET. Склад/вкладка/курсор/карточка — в адресе, возврат сохраняет их. */
export function TradecasePage({ onBack }: { onBack: () => void }) {
  const [view, setView] = useState(fromUrl), [prev, setPrev] = useState<(string | null)[]>([]), [reload, setReload] = useState(0);
  const names = useRef<{ wh: string; map: Names }>({ wh: "", map: new Map() });
  const cardRef = useRef<HTMLElement>(null);
  useEffect(() => toUrl(view), [view]);
  const go = (patch: Partial<View>) => setView(v => ({ ...v, ...patch }));
  const chooseWh = (wh: string) => { setPrev([]); setView({ wh, tab: view.tab, after: null, open: null }); };
  const chooseTab = (tab: Tab) => { setPrev([]); go({ tab, after: null, open: null }); };
  const openRelated = (kind: Kind, id: string) => { setPrev([]); go({ tab: kind, after: null, open: id }); };
  const ws = useRead<Workspaces>("/api/access/workspaces?capability=tradecase");
  const user = useRead<{ username: string }>("/api/access/navigation").data?.username ?? "";
  const site = useRead<Site>(view.wh ? sitePath(view.wh) : null, reload);
  const list = useRead<Page<DocRow | MsgRow>>(view.wh ? listPath(view.wh, view.tab, view.after) : null, reload);
  const card = useRead<DocCard | MsgCard>(view.wh && view.open ? cardPath(view.wh, view.tab, view.open) : null, reload);
  if (names.current.wh !== view.wh) names.current = { wh: view.wh, map: new Map() };
  if (list.data && ["SKU", "OWNER", "RECIPIENT"].includes(view.tab))
    for (const r of list.data.items as DocRow[]) if (typeof r.payload.title === "string") names.current.map.set(view.tab + ":" + r.document_id, r.payload.title);
  useEffect(() => { if (view.open && card.data) cardRef.current?.scrollIntoView({ block: "nearest" }); }, [view.open, card.data]);
  const tabLabel = TABS.find(t => t.id === view.tab)!.label;
  return <main className="tc" aria-label="СНС/BLC: основания и обмен">
    <header className="tc-panel tc-head">
      <Act help={tcHelp.back} onClick={onBack}>← Назад</Act>
      <div className="tc-title"><b>СНС/BLC · основания и обмен</b><small>принятые документы источника; физическое исполнение здесь не показывается</small></div>
      <label>Склад <input list="tc-wh" inputMode="numeric" value={view.wh} placeholder="код склада" onChange={e => chooseWh(e.target.value.replace(/\D/g, ""))}
        title={tcHelp.warehouse.text} data-help-id={tcHelp.warehouse.id} />
        <datalist id="tc-wh">{ws.data?.warehouses.map(w => <option key={w.warehouse_id} value={String(w.warehouse_id)}>{w.title}</option>)}</datalist></label>
      <Act help={tcHelp.refresh} disabled={!view.wh} onClick={() => setReload(n => n + 1)}>Обновить</Act>
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
      <div className="tc-tabs" role="tablist" aria-label="Виды документов">{TABS.map(t =>
        <button key={t.id} role="tab" aria-selected={view.tab === t.id} title={tcHelp.tab.text + " (" + t.label + ")"} data-help-id={tcHelp.tab.id + "." + t.id} onClick={() => chooseTab(t.id)}>{t.label}</button>)}</div>
      <div className="tc-body">
        <section className="tc-panel" aria-label={tabLabel}>
          <h3>{tabLabel} {view.after && <small>· не первая страница</small>} <HelpLink anchor={view.tab === "MESSAGES" ? "exchange" : view.tab === "STOCK" ? "stock" : view.tab === "SUPPLY" ? "bind" : "order"} /></h3>
          {list.error && <p className="tc-err" role="alert">{list.error}</p>}
          {list.loading && !list.data ? <p className="tc-note">Читаем страницу…</p> : list.data && (list.data.items.length === 0 ? <p className="tc-note">На этой странице записей нет.</p>
            : view.tab === "STOCK" ? <StockList rows={list.data.items as unknown as StockGroup[]} names={names.current.map} />
            : view.tab === "MESSAGES" ? <MsgList rows={list.data.items as MsgRow[]} selected={view.open ?? ""} onOpen={id => go({ open: id })} />
            : <DocList tab={view.tab} rows={list.data.items as DocRow[]} names={names.current.map} selected={view.open ?? ""} onOpen={id => go({ open: id })} />)}
          <div className="tc-pager">
            {(prev.length > 0 || view.after) && <Act help={tcHelp.first} onClick={() => { setPrev([]); go({ after: null, open: null }); }}>⟲ К первой странице</Act>}
            {prev.length > 0 && <Act help={{ ...tcHelp.first, id: "tradecase.prev", text: "Предыдущая страница этого вида." }} onClick={() => { const p = [...prev]; const back = p.pop() ?? null; setPrev(p); go({ after: back, open: null }); }}>← Назад</Act>}
            {list.data?.has_more && list.data.next_after && <Act help={tcHelp.next} onClick={() => { setPrev(p => [...p, view.after]); go({ after: list.data!.next_after, open: null }); }}>Далее →</Act>}
          </div>
        </section>
        {view.open && <section ref={cardRef} className="tc-panel tc-card" aria-label={"Карточка " + view.open}>
          <h3><span>{view.tab === "MESSAGES" ? "Сообщение обмена" : KIND_NAME[view.tab]} <b>{view.tab === "MESSAGES" ? view.open.slice(0, 8) + "…" : view.open}</b></span>
            <Act help={tcHelp.close} aria-label="Закрыть карточку" onClick={() => go({ open: null })}>×</Act></h3>
          {card.error ? <p className="tc-err" role="alert">{card.error}</p> : card.loading && !card.data ? <p className="tc-note">Читаем карточку…</p>
            : card.data && (view.tab === "MESSAGES" ? <MessageView card={card.data as MsgCard} onOpen={openRelated} /> : <DocumentView card={card.data as DocCard} names={names.current.map} onOpen={openRelated}
              bind={<BindPanel wh={view.wh} user={user} card={card.data as DocCard} names={names.current.map} onOpen={openRelated} onDone={() => setReload(n => n + 1)} />} />)}
        </section>}
      </div></>}
  </main>;
}
