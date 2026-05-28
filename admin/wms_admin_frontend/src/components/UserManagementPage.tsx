/**
 * UserManagementPage — управление пользователями и правами RBAC.
 * Sprint 99: просмотр пользователей, групп, прав
 * Sprint 100: редактирование прав групп, CRUD пользователей
 */

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface User {
  login: string;
  display_name: string;
  user_group: string;
  is_admin: boolean;
  is_deleted: boolean;
}

interface GroupRights {
  group: string;
  rights: string[];
}

interface UserForm {
  login: string;
  display_name: string;
  password: string;
  user_group: string;
  is_admin: boolean;
}

const emptyUserForm = (): UserForm => ({
  login: "", display_name: "", password: "", user_group: "", is_admin: false,
});

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function UserManagementPage({ onBack }: { onBack: () => void }) {
  const [activeTab, setActiveTab] = useState<"users" | "rights">("users");

  return (
    <div className="umgmt-shell">
      <header className="umgmt-topbar">
        <button className="umgmt-back" onClick={onBack}>◄</button>
        <div className="umgmt-title">
          <h1>Управление пользователями</h1>
          <span className="umgmt-subtitle">Пользователи и права доступа</span>
        </div>
      </header>

      <div className="umgmt-tabs">
        <button
          className={`umgmt-tab-btn${activeTab === "users" ? " umgmt-tab-active" : ""}`}
          onClick={() => setActiveTab("users")}
        >
          👤 Пользователи
        </button>
        <button
          className={`umgmt-tab-btn${activeTab === "rights" ? " umgmt-tab-active" : ""}`}
          onClick={() => setActiveTab("rights")}
        >
          🔑 Права групп
        </button>
      </div>

      <div className="umgmt-content">
        {activeTab === "users" ? <UsersTab /> : <RightsTab />}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Users Tab — Sprint 99/100
// ---------------------------------------------------------------------------

function UsersTab() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialog, setDialog] = useState<"add" | "edit" | "password" | null>(null);
  const [editLogin, setEditLogin] = useState<string | null>(null);
  const [form, setForm] = useState<UserForm>(emptyUserForm());
  const [passwordValue, setPasswordValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [showDeleted, setShowDeleted] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<User[]>("/api/admin/users");
      setUsers(data);
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const visible = showDeleted ? users : users.filter(u => !u.is_deleted);

  const openAdd = () => { setForm(emptyUserForm()); setEditLogin(null); setDialog("add"); };
  const openEdit = (u: User) => {
    setForm({ login: u.login, display_name: u.display_name, password: "", user_group: u.user_group, is_admin: u.is_admin });
    setEditLogin(u.login);
    setDialog("edit");
  };
  const openPassword = (u: User) => { setEditLogin(u.login); setPasswordValue(""); setDialog("password"); };

  const handleDelete = async (login: string) => {
    if (!confirm(`Удалить пользователя «${login}»?`)) return;
    try {
      await apiFetch(`/api/admin/users/${login}`, { method: "DELETE" });
      await load();
    } catch (e) { setError(String(e)); }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (dialog === "add") {
        await apiFetch("/api/admin/users", {
          method: "POST",
          body: JSON.stringify({
            login: form.login.trim(),
            display_name: form.display_name.trim(),
            password: form.password,
            user_group: form.user_group.trim(),
            is_admin: form.is_admin,
          }),
        });
      } else if (dialog === "edit" && editLogin) {
        await apiFetch(`/api/admin/users/${editLogin}`, {
          method: "PATCH",
          body: JSON.stringify({
            user_group: form.user_group.trim(),
            is_admin: form.is_admin,
            display_name: form.display_name.trim() || null,
          }),
        });
      } else if (dialog === "password" && editLogin) {
        await apiFetch(`/api/admin/users/${editLogin}/password`, {
          method: "PATCH",
          body: JSON.stringify({ new_password: passwordValue }),
        });
      }
      setDialog(null);
      await load();
    } catch (e) { setError(String(e)); }
    finally { setSaving(false); }
  };

  return (
    <div className="umgmt-section">
      <div className="umgmt-toolbar">
        <button className="umgmt-add-btn" onClick={openAdd}>+ Добавить пользователя</button>
        <label className="umgmt-deleted-toggle">
          <input type="checkbox" checked={showDeleted} onChange={e => setShowDeleted(e.target.checked)} />
          Показать удалённых
        </label>
        {loading && <span className="umgmt-loading">Загрузка…</span>}
        {error && <span className="umgmt-error" onClick={() => setError(null)}>⚠ {error}</span>}
      </div>

      <table className="umgmt-table">
        <thead>
          <tr>
            <th>Логин</th>
            <th>Имя</th>
            <th>Группа</th>
            <th>Admin</th>
            <th>Статус</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {visible.map(u => (
            <tr key={u.login} className={u.is_deleted ? "umgmt-row-deleted" : ""}>
              <td className="umgmt-login">{u.login}</td>
              <td>{u.display_name}</td>
              <td><span className="umgmt-group-badge">{u.user_group}</span></td>
              <td>{u.is_admin ? "✓" : ""}</td>
              <td>
                <span className={`umgmt-status ${u.is_deleted ? "umgmt-deleted" : "umgmt-active"}`}>
                  {u.is_deleted ? "Удалён" : "Активен"}
                </span>
              </td>
              <td className="umgmt-actions">
                {!u.is_deleted && (
                  <>
                    <button className="umgmt-edit-btn" onClick={() => openEdit(u)}>✏</button>
                    <button className="umgmt-pwd-btn" title="Сменить пароль" onClick={() => openPassword(u)}>🔒</button>
                    <button className="umgmt-del-btn" onClick={() => handleDelete(u.login)}>✕</button>
                  </>
                )}
              </td>
            </tr>
          ))}
          {!loading && visible.length === 0 && (
            <tr><td colSpan={6} className="umgmt-empty">Нет пользователей</td></tr>
          )}
        </tbody>
      </table>

      {(dialog === "add" || dialog === "edit") && (
        <div className="umgmt-modal-overlay" onClick={() => setDialog(null)}>
          <div className="umgmt-modal" onClick={e => e.stopPropagation()}>
            <div className="umgmt-modal-title">
              {dialog === "add" ? "Добавить пользователя" : `Редактировать: ${editLogin}`}
            </div>
            <div className="umgmt-form-grid">
              {dialog === "add" && (
                <>
                  <label>Логин *</label>
                  <input value={form.login} onChange={e => setForm(f => ({ ...f, login: e.target.value }))} />
                  <label>Пароль *</label>
                  <input type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
                </>
              )}
              <label>Имя</label>
              <input value={form.display_name} onChange={e => setForm(f => ({ ...f, display_name: e.target.value }))} />
              <label>Группа *</label>
              <input value={form.user_group} onChange={e => setForm(f => ({ ...f, user_group: e.target.value }))} placeholder="напр. TRANSPORT_TEAM" />
              <label>Права admin</label>
              <label className="umgmt-checkbox">
                <input type="checkbox" checked={form.is_admin} onChange={e => setForm(f => ({ ...f, is_admin: e.target.checked }))} />
                Вход в admin-панель
              </label>
            </div>
            <div className="umgmt-modal-actions">
              <button className="umgmt-modal-cancel" onClick={() => setDialog(null)}>Отмена</button>
              <button
                className="umgmt-modal-save"
                onClick={handleSave}
                disabled={saving || !form.user_group.trim() || (dialog === "add" && (!form.login.trim() || !form.password))}
              >
                {saving ? "Сохранение…" : "Сохранить"}
              </button>
            </div>
          </div>
        </div>
      )}

      {dialog === "password" && (
        <div className="umgmt-modal-overlay" onClick={() => setDialog(null)}>
          <div className="umgmt-modal" onClick={e => e.stopPropagation()}>
            <div className="umgmt-modal-title">Сменить пароль: {editLogin}</div>
            <div className="umgmt-form-grid">
              <label>Новый пароль *</label>
              <input type="password" value={passwordValue} onChange={e => setPasswordValue(e.target.value)} autoFocus />
            </div>
            <div className="umgmt-modal-actions">
              <button className="umgmt-modal-cancel" onClick={() => setDialog(null)}>Отмена</button>
              <button className="umgmt-modal-save" onClick={handleSave} disabled={saving || !passwordValue}>
                {saving ? "Сохранение…" : "Сменить"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Rights Tab — Sprint 99/100
// ---------------------------------------------------------------------------

function RightsTab() {
  const [groups, setGroups] = useState<GroupRights[]>([]);
  const [allRights, setAllRights] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [addingGroup, setAddingGroup] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [g, r] = await Promise.all([
        apiFetch<GroupRights[]>("/api/admin/users/groups"),
        apiFetch<string[]>("/api/admin/users/rights"),
      ]);
      setGroups(g);
      setAllRights(r);
      if (g.length > 0 && !selectedGroup) setSelectedGroup(g[0].group);
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []); // eslint-disable-line

  const currentGroup = groups.find(g => g.group === selectedGroup);
  const currentRights = new Set(currentGroup?.rights ?? []);

  const toggleRight = async (right: string, enabled: boolean) => {
    if (!selectedGroup) return;
    setSaving(true);
    try {
      if (enabled) {
        await apiFetch(`/api/admin/users/groups/${selectedGroup}/rights`, {
          method: "POST",
          body: JSON.stringify({ right }),
        });
      } else {
        await apiFetch(`/api/admin/users/groups/${selectedGroup}/rights/${right}`, { method: "DELETE" });
      }
      await load();
    } catch (e) { setError(String(e)); }
    finally { setSaving(false); }
  };

  const handleAddGroup = async () => {
    if (!newGroupName.trim()) return;
    setAddingGroup(true);
    try {
      await apiFetch("/api/admin/users/groups", {
        method: "POST",
        body: JSON.stringify({ group: newGroupName.trim() }),
      });
      setNewGroupName("");
      await load();
    } catch (e) { setError(String(e)); }
    finally { setAddingGroup(false); }
  };

  return (
    <div className="umgmt-section umgmt-rights-layout">
      {/* Left: group list */}
      <div className="umgmt-groups-panel">
        <div className="umgmt-groups-title">Группы</div>
        {groups.map(g => (
          <button
            key={g.group}
            className={`umgmt-group-item${selectedGroup === g.group ? " umgmt-group-selected" : ""}`}
            onClick={() => setSelectedGroup(g.group)}
          >
            <span>{g.group}</span>
            <span className="umgmt-group-count">{g.rights.length}</span>
          </button>
        ))}
        <div className="umgmt-add-group-row">
          <input
            placeholder="Название группы"
            value={newGroupName}
            onChange={e => setNewGroupName(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleAddGroup()}
          />
          <button onClick={handleAddGroup} disabled={addingGroup || !newGroupName.trim()}>+</button>
        </div>
      </div>

      {/* Right: rights checkboxes */}
      <div className="umgmt-rights-panel">
        {loading && <div className="umgmt-loading">Загрузка…</div>}
        {error && <div className="umgmt-error" onClick={() => setError(null)}>⚠ {error}</div>}
        {selectedGroup && (
          <>
            <div className="umgmt-rights-title">Права группы <b>{selectedGroup}</b></div>
            <div className="umgmt-rights-grid">
              {allRights.map(right => (
                <label key={right} className="umgmt-right-row">
                  <input
                    type="checkbox"
                    checked={currentRights.has(right)}
                    disabled={saving}
                    onChange={e => toggleRight(right, e.target.checked)}
                  />
                  <span className="umgmt-right-code">{right}</span>
                </label>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
