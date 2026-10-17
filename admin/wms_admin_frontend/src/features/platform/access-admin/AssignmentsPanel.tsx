import { useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { accessHelp } from "./help";
import { ObjectPicker } from "./ObjectPicker";
import { formatMoment, localToOffsetIso, useApiRead } from "./useApiRead";
import { OBJECT_KINDS } from "./types";
import type { AccessAssignment, AccessCatalog, AccessGroupSummary, ObjectKind, ScopeKind } from "./types";

type Draft = { username: string; role_id: string; scope_kind: ScopeKind; scope_id: string; scope_title: string; membership: "CURRENT" | "SNAPSHOT";
  snapshot_version: string; valid_from: string; valid_until: string; reason: string };
const NO_SCOPE_ID: ScopeKind[] = ["SELF", "NETWORK", "PLATFORM"];
// Состояние назначения по сроку считает сервер; клиент не выводит права из суммы ролей.
const STATE: Record<string, string> = { ACTIVE: "действует по сроку", SCHEDULED: "начнёт действовать", EXPIRED: "срок истёк", REVOKED: "отозвано" };
const nowLocal = () => { const d = new Date(Date.now() - new Date().getTimezoneOffset() * 60000); return d.toISOString().slice(0, 16); };

/** Назначения пользователя: роль + область + срок [с, до) + основание; отзыв с причиной. Сервер не даёт выйти за мандат назначающего. */
export function AssignmentsPanel({ catalog, accessRevision, reload, blocked, busy, onSubmit }: {
  catalog: AccessCatalog; accessRevision: number | null; reload: number; blocked: boolean; busy: boolean;
  onSubmit: (type: "ASSIGN" | "REVOKE", payload: Record<string, unknown>, label: string) => void;
}) {
  const [user, setUser] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [revoking, setRevoking] = useState<{ a: AccessAssignment; reason: string } | null>(null);
  const list = useApiRead<AccessAssignment[]>("/api/access/assignments?limit=100" + (submitted ? "&username=" + encodeURIComponent(submitted) : ""), reload);
  const groups = useApiRead<AccessGroupSummary[]>(draft?.scope_kind === "GROUP" ? "/api/access/groups?limit=100" : null, reload);
  const lock = blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : "";
  const isObjectKind = (k: ScopeKind): k is ObjectKind => (OBJECT_KINDS as string[]).includes(k);
  const invalid = !draft ? "форма пуста" : !draft.username.trim() ? "укажите пользователя" : !draft.role_id ? "выберите роль"
    : !NO_SCOPE_ID.includes(draft.scope_kind) && !draft.scope_id.trim() ? "выберите объект области"
    : draft.scope_kind === "ORG_BRANCH" && !/^[A-Z_]+:[A-Za-z0-9_.:-]+$/.test(draft.scope_id) ? "ветвь задаётся как ВИД:КОД (например REGION:12)"
    : draft.membership === "SNAPSHOT" && !(Number(draft.snapshot_version) >= 1) ? "для снимка нужна версия ≥ 1"
    : !draft.valid_from ? "укажите начало срока" : draft.valid_until && draft.valid_until <= draft.valid_from ? "окончание должно быть позже начала"
    : !draft.reason.trim() ? "укажите основание" : "";
  const send = () => { if (!draft) return; const snapshot = draft.membership === "SNAPSHOT";
    onSubmit("ASSIGN", { assignment_id: "ASG." + crypto.randomUUID(), username: draft.username.trim(), role_id: draft.role_id, scope_kind: draft.scope_kind,
      scope_id: NO_SCOPE_ID.includes(draft.scope_kind) ? null : draft.scope_id.trim(), membership: draft.membership,
      snapshot_version: snapshot ? Number(draft.snapshot_version) : null, valid_from: localToOffsetIso(draft.valid_from),
      valid_until: draft.valid_until ? localToOffsetIso(draft.valid_until) : null, reason: draft.reason.trim(), expected_version: 0 },
      `Назначение ${draft.role_id} → ${draft.username.trim()}`); };
  return <div className="aa-split">
    <section aria-labelledby="aa-assign-title">
      <h3 id="aa-assign-title">Назначения <HelpHint help={accessHelp.tabAssign} /></h3>
      <form className="aa-inline" onSubmit={e => { e.preventDefault(); setSubmitted(user.trim()); }}>
        <label>Пользователь<input value={user} maxLength={50} onChange={e => setUser(e.target.value)} title={accessHelp.userSearch.text} data-help-id={accessHelp.userSearch.id} /></label>
        <HelpButton help={accessHelp.userSearch} type="submit">Показать</HelpButton>
      </form>
      {list.loading && <p role="status">Загрузка…</p>}{list.error && <p role="alert">{list.error}</p>}
      {list.data && (list.data.length === 0 ? <p className="aa-empty">Назначений нет. Прежние права группы пользователя действуют без изменений.</p> :
        <table className="aa-table"><thead><tr><th>Пользователь</th><th>Роль</th><th>Область</th><th>С</th><th>До</th><th>Состояние</th><th>Основание</th><th /></tr></thead>
          <tbody>{list.data.map(a => <tr key={a.assignment_id}>
            <td data-label="Пользователь">{a.username}</td><td data-label="Роль"><code>{a.role_id}</code></td>
            <td data-label="Область">{a.scope_kind}{a.scope_id ? ":" + a.scope_id : ""}{a.membership === "SNAPSHOT" ? ` (снимок v${a.snapshot_version})` : ""}</td>
            <td data-label="С">{formatMoment(a.valid_from)}</td><td data-label="До">{formatMoment(a.valid_until)}</td>
            <td data-label="Состояние">{STATE[a.assignment_state ?? ""] ?? "состояние не получено"}{a.revoked_at ? " " + formatMoment(a.revoked_at) : ""} · v{a.version}</td>
            <td data-label="Основание">{a.reason} <small>({a.assigned_by})</small></td>
            <td>{!a.revoked_at && a.assignment_state !== "EXPIRED" && <HelpButton help={accessHelp.revoke} unavailable={lock} onClick={() => setRevoking({ a, reason: "" })}>Отозвать</HelpButton>}</td></tr>)}</tbody></table>)}
      {list.data?.length === 100 && <p className="aa-note">Показаны первые 100 — уточните пользователя.</p>}
      {revoking && <div className="aa-form" role="group" aria-label="Отзыв назначения">
        <p>Отозвать {revoking.a.role_id} у {revoking.a.username} ({revoking.a.scope_kind}{revoking.a.scope_id ? ":" + revoking.a.scope_id : ""})?</p>
        <label>Причина<input value={revoking.reason} maxLength={500} onChange={e => setRevoking({ ...revoking, reason: e.target.value })} title="Причина сохраняется в истории назначения." data-help-id="access.revoke.reason" /></label>
        <div className="aa-actions">
          <HelpButton help={accessHelp.revoke} unavailable={lock || (!revoking.reason.trim() && "укажите причину")}
            onClick={() => { onSubmit("REVOKE", { assignment_id: revoking.a.assignment_id, reason: revoking.reason.trim(), expected_version: revoking.a.version }, `Отзыв ${revoking.a.role_id} у ${revoking.a.username}`); setRevoking(null); }}>Подтвердить отзыв</HelpButton>
          <HelpButton help={{ id: "access.revoke.cancel", text: "Не отзывать. Сервер не меняется.", article: "access-admin" }} onClick={() => setRevoking(null)}>Отмена</HelpButton>
        </div></div>}
      <HelpButton help={accessHelp.assignNew} onClick={() => setDraft({ username: submitted, role_id: "", scope_kind: "WAREHOUSE", scope_id: "", scope_title: "", membership: "CURRENT",
        snapshot_version: accessRevision ? String(accessRevision) : "", valid_from: nowLocal(), valid_until: "", reason: "" })}>Новое назначение</HelpButton>
    </section>
    {draft && <section className="aa-form" aria-label="Новое назначение">
      <h3>Новое назначение <HelpHint help={accessHelp.assignSave} /></h3>
      <label>Пользователь<input value={draft.username} maxLength={50} onChange={e => setDraft({ ...draft, username: e.target.value })} title="Учётная запись получает роль дополнительно к прежней группе." data-help-id="access.assign.user" /></label>
      <label>Роль<select value={draft.role_id} onChange={e => setDraft({ ...draft, role_id: e.target.value })} title="Только активные роли каталога." data-help-id="access.assign.role">
        <option value="">— выберите —</option>{catalog.roles.filter(r => r.active).map(r => <option key={r.role_id} value={r.role_id}>{r.title} ({r.role_id})</option>)}</select></label>
      {catalog.roles.length === 0 && <p className="aa-note">Ролей нет — сначала роль создаёт глобальный администратор.</p>}
      <label>Вид области<select value={draft.scope_kind} onChange={e => setDraft({ ...draft, scope_kind: e.target.value as ScopeKind, scope_id: "", scope_title: "", membership: "CURRENT" })}
        title="Где действуют права роли. SELF — свои объекты по серверной привязке; NETWORK — вся сеть." data-help-id="access.assign.scope_kind">
        {catalog.scope_kinds.map(k => <option key={k} value={k}>{k}</option>)}</select></label>
      {isObjectKind(draft.scope_kind) && <>{draft.scope_id && <p>Выбрано: <code>{draft.scope_id}</code> {draft.scope_title}</p>}
        <ObjectPicker kind={draft.scope_kind} onPick={o => setDraft(d => d && { ...d, scope_id: o.object_id, scope_title: o.title })} /></>}
      {draft.scope_kind === "GROUP" && <label>Группа объектов<select value={draft.scope_id} onChange={e => setDraft({ ...draft, scope_id: e.target.value })} title="Именованная группа объектов как область." data-help-id="access.assign.group">
        <option value="">— выберите —</option>{(groups.data ?? []).map(g => <option key={g.group_id} value={g.group_id}>{g.title} ({g.member_kind}, v{g.version})</option>)}</select></label>}
      {draft.scope_kind === "ORG_BRANCH" && <label>Ветвь (ВИД:КОД)<input value={draft.scope_id} maxLength={100} onChange={e => setDraft({ ...draft, scope_id: e.target.value })} placeholder="REGION:12"
        title="Организационная ветвь в формате ВИД:КОД (C-0057)." data-help-id="access.assign.branch" /></label>}
      {(draft.scope_kind === "GROUP" || draft.scope_kind === "ORG_BRANCH") && <fieldset><legend>Состав области</legend>
        <label className="aa-check"><input type="radio" checked={draft.membership === "CURRENT"} onChange={() => setDraft({ ...draft, membership: "CURRENT" })} title="Изменения состава группы сразу меняют область." data-help-id="access.assign.current" />Актуальный состав</label>
        <label className="aa-check"><input type="radio" checked={draft.membership === "SNAPSHOT"} onChange={() => setDraft({ ...draft, membership: "SNAPSHOT" })} title="Состав фиксируется на версии и не меняется вместе с группой." data-help-id="access.assign.snapshot" />Снимок версии</label>
        {draft.membership === "SNAPSHOT" && <label>Версия снимка<input type="number" min={1} value={draft.snapshot_version} onChange={e => setDraft({ ...draft, snapshot_version: e.target.value })}
          title={draft.scope_kind === "ORG_BRANCH" ? "Для ветви — access_revision из /api/access/me." : "Версия группы, которую фиксирует снимок."} data-help-id="access.assign.snapshot_version" /></label>}
      </fieldset>}
      <label>Действует с<input type="datetime-local" value={draft.valid_from} onChange={e => setDraft({ ...draft, valid_from: e.target.value })} title="Включительно; часовой пояс браузера отправляется явно." data-help-id="access.assign.from" /></label>
      <label>Действует до (не включительно)<input type="datetime-local" value={draft.valid_until} onChange={e => setDraft({ ...draft, valid_until: e.target.value })} title="Пусто — без срока окончания; рекомендуется задать срок." data-help-id="access.assign.until" /></label>
      <label>Основание<input value={draft.reason} maxLength={500} onChange={e => setDraft({ ...draft, reason: e.target.value })} title="Приказ, заявка или причина; сохраняется в истории." data-help-id="access.assign.reason" /></label>
      <div className="aa-actions">
        <HelpButton help={accessHelp.assignSave} unavailable={lock || invalid} onClick={send}>Назначить</HelpButton>
        <HelpButton help={{ id: "access.assign.cancel", text: "Закрыть форму без отправки.", article: "access-admin" }} onClick={() => setDraft(null)}>Отмена</HelpButton>
      </div>
    </section>}
  </div>;
}
