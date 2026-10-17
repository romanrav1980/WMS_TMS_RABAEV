import { useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { accessHelp } from "./help";
import { ObjectPicker } from "./ObjectPicker";
import { apiFetch } from "../../../api";
import { formatMoment, readError, useApiRead } from "./useApiRead";
import { OBJECT_KINDS } from "./types";
import type { AccessGroup, AccessGroupSummary, GroupImpact, ObjectKind } from "./types";

type Draft = { group_id: string; title: string; member_kind: ObjectKind; members: { kind: ObjectKind; object_id: string; title: string }[]; active: boolean; expected_version: number };
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$/;

/** Группы объектов для области назначения. Перед сохранением — назначения, которые используют группу (влияние изменения). */
export function GroupsPanel({ reload, blocked, busy, onSave }: { reload: number; blocked: boolean; busy: boolean; onSave: (payload: Record<string, unknown>, label: string) => void }) {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [openId, setOpenId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const list = useApiRead<AccessGroupSummary[]>("/api/access/groups?limit=100" + (submitted ? "&query=" + encodeURIComponent(submitted) : ""), reload);
  const detail = useApiRead<AccessGroup>(openId ? "/api/access/groups/" + encodeURIComponent(openId) : null, reload);
  const [impact, setImpact] = useState<{ key: string; data: GroupImpact } | null>(null);
  const [impactError, setImpactError] = useState("");
  const [impactBusy, setImpactBusy] = useState(false);
  const payload = (d: Draft) => ({ group_id: d.group_id, title: d.title.trim(), member_kind: d.member_kind,
    members: d.members.map(m => ({ kind: m.kind, object_id: m.object_id })), active: d.active, expected_version: d.expected_version });
  const draftKey = draft ? JSON.stringify(payload(draft)) : "";
  const impactFresh = impact !== null && impact.key === draftKey;
  // Влияние считает сервер (POST /api/access/groups/preview, C-0064) по тому же телу, что GROUP_SAVE.
  const loadImpact = async () => {
    if (!draft) return;
    const key = draftKey; setImpactBusy(true); setImpactError("");
    try { setImpact({ key, data: await apiFetch<GroupImpact>("/api/access/groups/preview", { method: "POST", body: key }) }); }
    catch (reason) { setImpact(null); setImpactError(readError(reason)); } finally { setImpactBusy(false); }
  };
  const open = (id: string) => { setOpenId(id); setDraft(null); };
  const startEdit = (g: AccessGroup) => setDraft({ group_id: g.group_id, title: g.title, member_kind: g.member_kind, members: g.members, active: Boolean(g.active), expected_version: g.version });
  const invalid = !draft ? "форма пуста" : !ID.test(draft.group_id) ? "код группы: латиница, цифры, _.:-" : !draft.title.trim() ? "нужно название"
    : draft.members.length > 200 ? "не больше 200 объектов" : draft.members.some(m => m.kind !== draft.member_kind) ? "все объекты должны быть одного вида" : "";
  const unavailable = blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : invalid || (!impactFresh && "сначала посмотрите влияние текущего состава");
  return <div className="aa-split">
    <section aria-labelledby="aa-groups-title">
      <h3 id="aa-groups-title">Группы объектов <HelpHint help={accessHelp.tabGroups} /></h3>
      <form className="aa-inline" onSubmit={e => { e.preventDefault(); setSubmitted(query.trim()); }}>
        <label>Поиск<input value={query} maxLength={120} onChange={e => setQuery(e.target.value)} title="Найти группу по коду или названию." data-help-id="access.group.search" /></label>
        <HelpButton help={{ id: "access.group.search", text: "Найти группу по коду или названию. Ничего не изменяет.", article: "access-admin" }} type="submit">Найти</HelpButton>
      </form>
      {list.loading && <p role="status">Загрузка…</p>}{list.error && <p role="alert">{list.error}</p>}
      {list.data && (list.data.length === 0 ? <p className="aa-empty">Групп нет.</p> :
        <ul className="aa-list">{list.data.map(g => <li key={g.group_id} className={openId === g.group_id ? "aa-selected" : ""}>
          <span><code>{g.group_id}</code> {g.title} · {g.member_kind} · v{g.version}{g.active ? "" : " · неактивна"}</span>
          <HelpButton help={accessHelp.groupOpen} onClick={() => open(g.group_id)}>Открыть</HelpButton></li>)}</ul>)}
      <HelpButton help={accessHelp.groupNew} onClick={() => { setOpenId(null); setDraft({ group_id: "", title: "", member_kind: "WAREHOUSE", members: [], active: true, expected_version: 0 }); }}>Новая группа</HelpButton>
    </section>
    <section className="aa-form" aria-label="Группа">
      {openId && !draft && <>
        {detail.loading && <p role="status">Загрузка группы…</p>}{detail.error && <p role="alert">{detail.error}</p>}
        {detail.data && <><h3>{detail.data.title} <small>v{detail.data.version}</small></h3>
          <p>Вид объектов: {detail.data.member_kind}; объектов: {detail.data.members.length} из 200.</p>
          <ul className="aa-list">{detail.data.members.map(m => <li key={m.kind + m.object_id}><span><code>{m.object_id}</code> {m.title}</span></li>)}</ul>
          <HelpButton help={accessHelp.roleEdit} onClick={() => startEdit(detail.data as AccessGroup)}>Изменить состав</HelpButton></>}
      </>}
      {draft && <>
        <h3>{draft.expected_version ? `Группа ${draft.group_id} · версия ${draft.expected_version}` : "Новая группа"}</h3>
        <label>Код<input value={draft.group_id} disabled={draft.expected_version > 0} maxLength={80} onChange={e => setDraft({ ...draft, group_id: e.target.value })} title="Постоянный код группы." data-help-id="access.group.id" /></label>
        <label>Название<input value={draft.title} maxLength={200} onChange={e => setDraft({ ...draft, title: e.target.value })} title="Название, понятное назначающим." data-help-id="access.group.title" /></label>
        <label>Вид объектов<select value={draft.member_kind} disabled={draft.members.length > 0} onChange={e => setDraft({ ...draft, member_kind: e.target.value as ObjectKind })}
          title="Группа содержит объекты одного вида. Вид меняется только у пустой группы." data-help-id="access.group.kind">
          {OBJECT_KINDS.map(k => <option key={k} value={k}>{k}</option>)}</select></label>
        <label className="aa-check"><input type="checkbox" checked={draft.active} onChange={e => setDraft({ ...draft, active: e.target.checked })} title="Неактивная группа не даёт области назначениям." data-help-id="access.group.active" />Активна</label>
        <h4>Состав ({draft.members.length})</h4>
        <ul className="aa-list">{draft.members.map(m => <li key={m.kind + m.object_id}><span><code>{m.object_id}</code> {m.title}</span>
          <HelpButton help={accessHelp.memberRemove} onClick={() => setDraft({ ...draft, members: draft.members.filter(x => x !== m) })}>Убрать</HelpButton></li>)}</ul>
        <ObjectPicker kind={draft.member_kind} actionLabel="Добавить" onPick={o => setDraft(d => d && (d.members.some(m => m.object_id === o.object_id) ? d : { ...d, members: [...d.members, { kind: o.kind, object_id: o.object_id, title: o.title }] }))} />
        <h4>Влияние изменения <HelpHint help={accessHelp.groupSave} /></h4>
        <HelpButton help={accessHelp.groupImpact} unavailable={impactBusy ? "идёт запрос" : invalid} onClick={() => void loadImpact()}>{impactFresh ? "Пересчитать влияние" : "Показать влияние"}</HelpButton>
        {impactError && <p role="alert">Влияние не получено: {impactError}. Сохранение недоступно.</p>}
        {impact && !impactFresh && <p className="aa-note">Состав изменился после расчёта — посчитайте влияние заново.</p>}
        {impact && impactFresh && <div className="aa-impact" role="status">
          <p>Добавится объектов: {impact.data.added.length} · уберётся: {impact.data.removed.length} · затронуто назначений: {impact.data.affected_total}
            {impact.data.affected_total > impact.data.affected_assignments.length ? ` (показаны первые ${impact.data.affected_assignments.length} из ${impact.data.affected_total})` : ""}</p>
          {impact.data.activation_changed && <p className="aa-warn">Меняется активность группы — это влияет и на назначения со снимком состава.</p>}
          <p className="aa-note">Назначения со снимком сохраняют прежний состав; смена активности действует и на них.</p>
          {impact.data.affected_assignments.length > 0 && <ul className="aa-list">{impact.data.affected_assignments.map((a, i) => <li key={String(a.assignment_id ?? i)}>
            <span>{String(a.username ?? "")} · {String(a.role_id ?? "")} · {a.membership === "SNAPSHOT" ? `снимок v${String(a.snapshot_version ?? "")}` : "актуальный состав"}{a.valid_until ? " · до " + formatMoment(String(a.valid_until)) : ""}</span></li>)}</ul>}
        </div>}
        <div className="aa-actions">
          <HelpButton help={accessHelp.groupSave} unavailable={unavailable} onClick={() => onSave(payload(draft), `Группа ${draft.group_id}`)}>Сохранить группу</HelpButton>
          <HelpButton help={{ id: "access.group.cancel", text: "Закрыть форму без отправки.", article: "access-admin" }} onClick={() => setDraft(null)}>Отмена</HelpButton>
        </div>
      </>}
      {!openId && !draft && <p className="aa-empty">Выберите группу слева или создайте новую.</p>}
    </section>
  </div>;
}
