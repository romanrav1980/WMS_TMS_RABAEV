import { useEffect, useId, useRef, useState } from "react";
import type { ReactNode } from "react";
import { parseHuSnapshot, positiveId } from "./huTreeModel";
import { HuMassFacts } from "./HuMassPanel";
import type { HuNode, HuReference, HuSnapshot } from "./huTreeModel";
import "./HuTreeWorkspace.css";

export type HuTreeWorkspaceProps = {
 loadComposition: (identifier: string, signal: AbortSignal) => Promise<unknown>;
 /** Change on authenticated identity/server transition; clears private data. */
 accessKey: string;
 initialIdentifier?: string;
 onReference?: (reference: HuReference) => void;
 helpSlot?: ReactNode;
};
function NodeFacts({ node, snapshot, onReference }: { node: HuNode; snapshot: HuSnapshot; onReference?: (reference: HuReference) => void }) {
 const references: HuReference[] = [];
 if (positiveId(node.case_task_id)) references.push({ kind: "case", id: node.case_task_id });
 if (positiveId(node.wave_id)) references.push({ kind: "wave", id: node.wave_id });
 if (node.uid === snapshot.root && snapshot.placement) references.push({ kind: "warehouse-task", id: snapshot.placement.task_id });
 return <aside className="hu-tree-inspector" aria-label="Выбранное грузовое место">
  <span className="hu-tree-eyebrow">{node.kind} · {node.type || "тип не передан"}</span><h3>{node.uid}</h3>
  <dl><dt>Идентификатор паллеты</dt><dd>{node.sscc || node.uid}</dd>
   <dt>Состояние</dt><dd>{node.status || "Не передано"}</dd><dt>Версия состава</dt><dd>{node.version ?? "Не передана"}</dd>
   <dt>Ячейка</dt><dd>{node.cell || snapshot.cell}</dd><dt>Способ сборки</dt><dd>Неизвестен: основание способа не передано</dd>
   {node.article && <><dt>Артикул</dt><dd>{node.article}</dd></>}
   {node.quantity != null && <><dt>Количество</dt><dd>{node.quantity} {node.base_uom || "единица не передана"}</dd></>}
   <dt>Открытые задания</dt><dd>{node.open_task_count ?? "Не передано"}</dd></dl>
  <HuMassFacts node={node} snapshot={snapshot} />
  {node.scale_qc && <details><summary title="Показать исходные поля основания массы без переинтерпретации QC" data-help-id="hu.mass.basis">Основание scale_qc</summary><pre>{JSON.stringify(node.scale_qc, null, 2)}</pre></details>}
  {node.uid === snapshot.root && snapshot.placement && <p className="hu-tree-note">Размещение: {snapshot.placement.slot_code} · {snapshot.placement.task_status}. {snapshot.placement.version_matches ? "Версия совпадает." : "Версия отличается: запись не подтверждает состав."} Записанный GROSS: {snapshot.placement.gross_weight_kg ?? "не передан"} кг; это не новое измерение.</p>}
  {references.length > 0 && <div className="hu-tree-references" aria-label="Связанные объекты">{references.map(reference => onReference
   ? <button key={reference.kind} type="button" title="Открыть связанный объект по реальному серверному ID" data-help-id="hu.reference.open" onClick={() => onReference(reference)}>{reference.kind} #{reference.id} →</button>
   : <span key={reference.kind}>{reference.kind} #{reference.id}</span>)}</div>}
 </aside>;
}
function TreeBranch({ uid, snapshot, selected, onSelect, collapsed, onToggle }: {
 uid: string; snapshot: HuSnapshot; selected: string; onSelect: (uid: string) => void;
 collapsed: Set<string>; onToggle: (uid: string) => void;
}) {
 const node = snapshot.nodes.find(item => item.uid === uid)!;
 const children = snapshot.links.filter(link => link.parent === uid), open = !collapsed.has(uid);
 return <li><div className={"hu-tree-node" + (selected === uid ? " is-selected" : "")}>
  {children.length > 0 ? <button type="button" className="hu-tree-toggle" aria-expanded={open} aria-label={(open ? "Скрыть" : "Показать") + " детей " + uid}
   title="Показать или скрыть дочерние места без изменения состава" data-help-id="hu.branch.toggle" onClick={() => onToggle(uid)}>{open ? "−" : "+"}</button> : <span className="hu-tree-leaf">·</span>}
  <button type="button" className="hu-tree-select" aria-pressed={selected === uid} title="Выбрать узел и посмотреть состояние, количество и основание массы" data-help-id="hu.node.select" onClick={() => onSelect(uid)}>
   <span className="hu-tree-kind">{node.kind}</span><strong>{node.sscc || uid}</strong><small>{node.status || "Статус не передан"}{node.quantity != null ? " · " + node.quantity + " " + (node.base_uom || "") : ""}</small>
  </button></div>
  {open && children.length > 0 && <ul>{children.map(child => <TreeBranch key={child.child} uid={child.child} snapshot={snapshot} selected={selected} onSelect={onSelect} collapsed={collapsed} onToggle={onToggle} />)}</ul>}
 </li>;
}
export function HuTreeWorkspace({ loadComposition, accessKey, initialIdentifier = "", onReference, helpSlot }: HuTreeWorkspaceProps) {
 const [identifier, setIdentifier] = useState(initialIdentifier), [snapshot, setSnapshot] = useState<HuSnapshot | null>(null);
 const [selected, setSelected] = useState(""), [collapsed, setCollapsed] = useState(new Set<string>());
 const [busy, setBusy] = useState(false), [error, setError] = useState("");
 const inputId = useId();
 const active = useRef<AbortController | null>(null), generation = useRef(0);
 useEffect(() => {
  generation.current++; active.current?.abort(); setSnapshot(null); setSelected(""); setIdentifier(initialIdentifier); setBusy(false); setError("");
  return () => { generation.current++; active.current?.abort(); };
 }, [accessKey, initialIdentifier]);
 async function read(code = identifier) {
  const target = code.trim(); if (!target || target.length > 200) { setError("Укажите идентификатор от 1 до 200 символов."); return; }
  active.current?.abort(); const controller = new AbortController(); active.current = controller;
  const request = ++generation.current; setBusy(true); setError(""); setSnapshot(null); setSelected("");
  try {
   const value = parseHuSnapshot(await loadComposition(target, controller.signal));
   if (request !== generation.current || controller.signal.aborted) return;
   setSnapshot(value); setSelected(value.root); setCollapsed(new Set()); setIdentifier(target);
  } catch (failure) { if (request === generation.current && !controller.signal.aborted) setError(failure instanceof Error ? failure.message : "Не удалось прочитать состав."); }
  finally { if (request === generation.current) setBusy(false); }
 }
 function toggle(uid: string) { setCollapsed(previous => { const next = new Set(previous); if (next.has(uid)) next.delete(uid); else next.add(uid); return next; }); }
 const node = snapshot?.nodes.find(item => item.uid === selected);
 return <section className="hu-tree-workspace" aria-label="Дерево грузовых мест" aria-busy={busy}>
  <header><div><span className="hu-tree-eyebrow">Цифровой двойник · состав</span><h2>Грузовое место</h2></div>
   {helpSlot ?? <details><summary title="Показать помощь по дереву грузового места" data-help-id="hu.tree.help">Помощь</summary><p>Сканируйте место любого уровня. Выберите узел для фактов. Неизвестные масса и способ сборки не рассчитываются.</p></details>}</header>
  <form onSubmit={event => { event.preventDefault(); void read(); }} className="hu-tree-search"><label htmlFor={inputId}>Идентификатор паллеты / места<input id={inputId} title="Введите или отсканируйте SSCC либо внутренний идентификатор любого уровня; Enter читает состав" data-help-id="hu.identifier" maxLength={200} value={identifier} onChange={event => setIdentifier(event.target.value)} autoComplete="off" /></label>
   <button type="submit" title="Перечитать состав с сервера без изменения товара" data-help-id="hu.composition.read" disabled={busy || !identifier.trim()}>{busy ? "Чтение…" : "Показать состав"}</button></form>
  {error && <p role="alert" className="hu-tree-error">{error}</p>}
  {!snapshot && !busy && !error && <p className="hu-tree-note">Сканируйте паллету, коробку, CASE или товарное место. Состав и доступ проверит сервер.</p>}
  {snapshot && <><div className="hu-tree-metrics"><span>Склад <b>{snapshot.warehouse}</b></span><span>Ячейка <b>{snapshot.cell}</b></span><span>Узлов <b>{snapshot.nodes.length}</b></span><span>Листьев <b>{snapshot.leaf_count ?? "?"}</b></span></div>
   {snapshot.historical_composition && <p className="hu-tree-error">Исторический состав отгрузки. Не подтверждает текущее положение, статус или доступность товара.</p>}
   {snapshot.ancestors.length > 0 && <nav className="hu-tree-ancestors" aria-label="Родительские места">{snapshot.ancestors.map(ancestor => <button type="button" key={ancestor.uid} title="Прочитать родительское место с повторной проверкой доступа" data-help-id="hu.parent.read" disabled={busy} onClick={() => void read(ancestor.uid)}>↑ {ancestor.uid}</button>)}</nav>}
   <div className="hu-tree-layout"><div className="hu-tree-canvas"><ul aria-label="Серверное дерево HU"><TreeBranch uid={snapshot.root} snapshot={snapshot} selected={selected} onSelect={setSelected} collapsed={collapsed} onToggle={toggle} /></ul></div>{node && <NodeFacts node={node} snapshot={snapshot} onReference={onReference} />}</div>
  </>}
 </section>;
}
