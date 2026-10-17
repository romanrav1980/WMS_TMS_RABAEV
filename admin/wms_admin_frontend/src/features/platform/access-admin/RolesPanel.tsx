import { useMemo, useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { accessHelp } from "./help";
import type { AccessCatalog, AccessRole } from "./types";

type Draft = { role_id: string; title: string; permissions: string[]; active: boolean; expected_version: number };
const ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$/;

/** Роли и их права. ROLE_SAVE — по серверной способности manage_roles; сервер проверяет, что роль не шире мандата дизайнера (C-0071). */
export function RolesPanel({ catalog, canManage, blocked, busy, onSave }: {
  catalog: AccessCatalog; canManage: boolean; blocked: boolean; busy: boolean;
  onSave: (payload: Draft, label: string) => void;
}) {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [filter, setFilter] = useState("");
  const rights = useMemo(() => catalog.rights.filter(r => r.includes(filter.trim().toLowerCase())), [catalog.rights, filter]);
  const edit = (role: AccessRole) => setDraft({ role_id: role.role_id, title: role.title, permissions: [...role.permissions], active: Boolean(role.active), expected_version: role.version });
  const toggle = (right: string) => setDraft(d => d && { ...d, permissions: d.permissions.includes(right) ? d.permissions.filter(x => x !== right) : [...d.permissions, right].sort() });
  const invalid = !draft ? "форма пуста" : !ID.test(draft.role_id) ? "код роли: латиница, цифры, _.:- до 80 символов"
    : !draft.title.trim() ? "нужно название" : draft.permissions.length > 200 ? "не больше 200 прав" : "";
  const unavailable = !canManage ? "нет права проектировать роли (access_role_manage на PLATFORM)" : blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : invalid;
  return <div className="aa-split">
    <section aria-labelledby="aa-roles-title">
      <h3 id="aa-roles-title">Роли доступа <HelpHint help={accessHelp.tabRoles} /></h3>
      {catalog.roles.length === 0 ? <p className="aa-empty">Ролей пока нет. Роль без назначения никому ничего не даёт.</p> :
        <table className="aa-table"><thead><tr><th>Код</th><th>Название</th><th>Прав</th><th>Активна</th><th>Версия</th><th /></tr></thead>
          <tbody>{catalog.roles.map(role => <tr key={role.role_id} className={draft?.role_id === role.role_id ? "aa-selected" : ""}>
            <td data-label="Код"><code>{role.role_id}</code></td><td data-label="Название">{role.title}</td><td data-label="Прав">{role.permissions.length}</td>
            <td data-label="Активна">{role.active ? "да" : "нет"}</td><td data-label="Версия">{role.version}</td>
            <td><HelpButton help={accessHelp.roleEdit} onClick={() => edit(role)}>Изменить</HelpButton></td></tr>)}</tbody></table>}
      <HelpButton help={accessHelp.roleNew} onClick={() => setDraft({ role_id: "", title: "", permissions: [], active: true, expected_version: 0 })}>Новая роль</HelpButton>
    </section>
    {draft && <section className="aa-form" aria-labelledby="aa-role-form">
      <h3 id="aa-role-form">{draft.expected_version ? `Роль ${draft.role_id} · версия ${draft.expected_version}` : "Новая роль"}</h3>
      <label>Код роли<input value={draft.role_id} disabled={draft.expected_version > 0} maxLength={80} onChange={e => setDraft({ ...draft, role_id: e.target.value })}
        title="Постоянный код роли; после создания не меняется." data-help-id="access.role.id" /></label>
      <label>Название<input value={draft.title} maxLength={200} onChange={e => setDraft({ ...draft, title: e.target.value })} title="Понятное название для назначающих." data-help-id="access.role.title" /></label>
      <label className="aa-check"><input type="checkbox" checked={draft.active} onChange={e => setDraft({ ...draft, active: e.target.checked })}
        title="Неактивная роль не даёт прав, назначения сохраняются." data-help-id="access.role.active" />Активна</label>
      <label>Права ({draft.permissions.length} выбрано)<input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Фильтр прав…"
        title={accessHelp.rightsFilter.text} data-help-id={accessHelp.rightsFilter.id} /></label>
      <div className="aa-rights" role="group" aria-label="Права роли">{rights.map(right =>
        <label key={right} className="aa-check"><input type="checkbox" checked={draft.permissions.includes(right)} onChange={() => toggle(right)}
          title={`Включить право ${right} в роль. Действует только в области назначения.`} data-help-id="access.role.right" /><code>{right}</code></label>)}</div>
      <div className="aa-actions">
        <HelpButton help={accessHelp.roleSave} unavailable={unavailable} onClick={() => onSave({ ...draft, title: draft.title.trim() }, `Роль ${draft.role_id}`)}>Сохранить роль</HelpButton>
        <HelpHint help={accessHelp.roleSave} />
        <HelpButton help={{ id: "access.role.cancel", text: "Закрыть форму без отправки. Сервер не меняется.", article: "access-admin" }} onClick={() => setDraft(null)}>Отмена</HelpButton>
      </div>
    </section>}
  </div>;
}
