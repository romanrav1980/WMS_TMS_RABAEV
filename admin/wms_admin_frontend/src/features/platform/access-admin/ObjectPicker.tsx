import { useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { accessHelp } from "./help";
import { useApiRead } from "./useApiRead";
import type { AccessObject, ObjectKind } from "./types";

/** Поиск объекта области (склад, РЦ, магазин, регион, перевозчик, зона) через GET /api/access/objects, не более 100 строк. */
export function ObjectPicker({ kind, onPick, actionLabel = "Выбрать" }: { kind: ObjectKind; onPick: (object: AccessObject) => void; actionLabel?: string }) {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const path = `/api/access/objects?kind=${kind}&limit=50` + (submitted ? "&query=" + encodeURIComponent(submitted) : "");
  const read = useApiRead<AccessObject[]>(path);
  return <div className="aa-picker">
    <form onSubmit={e => { e.preventDefault(); setSubmitted(query.trim()); }}>
      <label>Найти объект ({kind})<input value={query} maxLength={120} onChange={e => setQuery(e.target.value)} title={accessHelp.objectSearch.text} data-help-id={accessHelp.objectSearch.id} /></label>
      <HelpButton help={accessHelp.objectSearch} type="submit">Найти</HelpButton>
    </form>
    {read.loading && <p role="status">Поиск…</p>}
    {read.error && <p role="alert">{read.error}</p>}
    {read.data && (read.data.length === 0 ? <p className="aa-empty">Ничего не найдено.</p> :
      <ul className="aa-list">{read.data.map(o => <li key={o.kind + o.object_id}>
        <span><code>{o.object_id}</code> {o.title}{o.active ? "" : " · неактивен"}</span>
        <HelpButton help={accessHelp.memberAdd} onClick={() => onPick(o)}>{actionLabel}</HelpButton></li>)}</ul>)}
    {read.data?.length === 50 && <p className="aa-note">Показаны первые 50 — уточните поиск.</p>}
  </div>;
}
