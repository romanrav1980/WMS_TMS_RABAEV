import { useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { accessHelp } from "./help";
import { ObjectPicker } from "./ObjectPicker";
import { useApiRead } from "./useApiRead";
import { OBJECT_KINDS } from "./types";
import type { AccessObject, ObjectKind } from "./types";

type Draft = { kind: ObjectKind; object_id: string; title: string; parent_kind: ObjectKind | ""; parent_id: string; parent_title: string; active: boolean; expected_version: number };
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$/;
// Склады и магазины регистрирует источник (RRL_ADDR/склады, opaque ID у STORE/REGION — C-0070); вручную создаются только организационные объекты.
const CREATABLE: ObjectKind[] = ["DC", "ZONE", "REGION", "CARRIER"];

/** Оргобъекты: название, родитель, активность (OBJECT_SAVE). Изменение — по серверной способности manage_objects. */
export function ObjectsPanel({ reload, canManage, blocked, busy, onSave }: { reload: number; canManage: boolean; blocked: boolean; busy: boolean; onSave: (payload: Record<string, unknown>, label: string) => void }) {
  const [kind, setKind] = useState<ObjectKind>("DC");
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [parentKind, setParentKind] = useState<ObjectKind>("DC");
  const list = useApiRead<AccessObject[]>(`/api/access/objects?kind=${kind}&limit=100` + (submitted ? "&query=" + encodeURIComponent(submitted) : ""), reload);
  const edit = (o: AccessObject) => setDraft({ kind: o.kind, object_id: o.object_id, title: o.title, parent_kind: o.parent_kind ?? "", parent_id: o.parent_id ?? "", parent_title: o.parent_id ?? "",
    active: Boolean(o.active), expected_version: o.version });
  const invalid = !draft ? "форма пуста" : !ID.test(draft.object_id) ? "код: латиница, цифры, _.:- до 80 символов" : !draft.title.trim() ? "нужно название"
    : draft.parent_id && draft.parent_id === draft.object_id && draft.parent_kind === draft.kind ? "объект не может быть родителем самому себе" : "";
  const unavailable = !canManage ? "нет способности manage_objects" : blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : invalid;
  return <div className="aa-split">
    <section aria-labelledby="aa-objects-title">
      <h3 id="aa-objects-title">Оргобъекты <HelpHint help={accessHelp.tabObjects} /></h3>
      <form className="aa-inline" onSubmit={e => { e.preventDefault(); setSubmitted(query.trim()); }}>
        <label>Вид<select value={kind} onChange={e => setKind(e.target.value as ObjectKind)} title="Вид объектов в списке." data-help-id="access.object.kind">{OBJECT_KINDS.map(k => <option key={k}>{k}</option>)}</select></label>
        <label>Поиск<input value={query} maxLength={120} onChange={e => setQuery(e.target.value)} title={accessHelp.objectSearch.text} data-help-id={accessHelp.objectSearch.id} /></label>
        <HelpButton help={accessHelp.objectSearch} type="submit">Найти</HelpButton>
      </form>
      {list.loading && <p role="status">Загрузка…</p>}{list.error && <p role="alert">{list.error}</p>}
      {list.data && (list.data.length === 0 ? <p className="aa-empty">Объектов этого вида нет.</p> :
        <table className="aa-table"><thead><tr><th>Код</th><th>Название</th><th>Родитель</th><th>Акт.</th><th>v</th><th /></tr></thead>
          <tbody>{list.data.map(o => <tr key={o.kind + o.object_id} className={draft?.object_id === o.object_id && draft.kind === o.kind ? "aa-selected" : ""}>
            <td data-label="Код"><code>{o.object_id}</code></td><td data-label="Название">{o.title}</td>
            <td data-label="Родитель">{o.parent_kind ? `${o.parent_kind}:${o.parent_id}` : "—"}</td><td data-label="Акт.">{o.active ? "да" : "нет"}</td><td data-label="v">{o.version}</td>
            <td><HelpButton help={accessHelp.objectEdit} onClick={() => edit(o)}>Изменить</HelpButton></td></tr>)}</tbody></table>)}
      {list.data?.length === 100 && <p className="aa-note">Показаны первые 100 — уточните поиск.</p>}
      <HelpButton help={accessHelp.objectNew} unavailable={!CREATABLE.includes(kind) && "склады и магазины приходят из справочников"}
        onClick={() => setDraft({ kind, object_id: "", title: "", parent_kind: "", parent_id: "", parent_title: "", active: true, expected_version: 0 })}>Новый объект</HelpButton>
    </section>
    {draft && <section className="aa-form" aria-label="Оргобъект">
      <h3>{draft.expected_version ? `${draft.kind} ${draft.object_id} · версия ${draft.expected_version}` : `Новый ${draft.kind}`} <HelpHint help={accessHelp.objectSave} /></h3>
      <label>Код<input value={draft.object_id} disabled={draft.expected_version > 0} maxLength={80} onChange={e => setDraft({ ...draft, object_id: e.target.value })} title="Постоянный код объекта." data-help-id="access.object.id" /></label>
      <label>Название<input value={draft.title} maxLength={200} onChange={e => setDraft({ ...draft, title: e.target.value })} title="Название в списках и назначениях." data-help-id="access.object.title" /></label>
      <label className="aa-check"><input type="checkbox" checked={draft.active} onChange={e => setDraft({ ...draft, active: e.target.checked })} title="Неактивный объект не даёт области назначениям." data-help-id="access.object.active" />Активен</label>
      <fieldset><legend>Родитель</legend>
        <p>{draft.parent_id ? <>Сейчас: <code>{draft.parent_kind}:{draft.parent_id}</code> {draft.parent_title !== draft.parent_id ? draft.parent_title : ""}</> : "Без родителя"}</p>
        {draft.parent_id && <HelpButton help={{ id: "access.object.parent.clear", text: "Убрать родителя в форме (до сохранения).", article: "access-admin" }} onClick={() => setDraft({ ...draft, parent_kind: "", parent_id: "", parent_title: "" })}>Убрать родителя</HelpButton>}
        <label>Вид родителя<select value={parentKind} onChange={e => setParentKind(e.target.value as ObjectKind)} title={accessHelp.parentPick.text} data-help-id={accessHelp.parentPick.id}>{OBJECT_KINDS.map(k => <option key={k}>{k}</option>)}</select></label>
        <ObjectPicker kind={parentKind} actionLabel="Сделать родителем" onPick={o => setDraft(d => d && { ...d, parent_kind: o.kind, parent_id: o.object_id, parent_title: o.title })} />
      </fieldset>
      <div className="aa-actions">
        <HelpButton help={accessHelp.objectSave} unavailable={unavailable} onClick={() => onSave({ kind: draft.kind, object_id: draft.object_id, title: draft.title.trim(),
          parent_kind: draft.parent_kind || null, parent_id: draft.parent_id || null, active: draft.active, expected_version: draft.expected_version }, `Объект ${draft.kind}:${draft.object_id}`)}>Сохранить объект</HelpButton>
        <HelpButton help={{ id: "access.object.cancel", text: "Закрыть форму без отправки.", article: "access-admin" }} onClick={() => setDraft(null)}>Отмена</HelpButton>
      </div>
    </section>}
  </div>;
}
