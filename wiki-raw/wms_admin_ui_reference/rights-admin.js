const rightsState = {
  users: [],
  groups: [],
  rights: [],
  selectedUserId: null,
  selectedGroupId: null,
};

const rEl = (id) => document.getElementById(id);

function rightsApiBase() {
  return window.wmsAdminAuth?.state.apiBase || "http://127.0.0.1:8088";
}

function rightsHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

function canEditRights() {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission("rights_admin_edit");
}

async function rightsFetch(path, options = {}) {
  const response = await fetch(`${rightsApiBase()}${path}`, {
    ...options,
    headers: rightsHeaders(options.headers || {}),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function loadGroups() {
  rightsState.groups = await rightsFetch("/api/admin/rights/groups");
  renderGroupSelects();
  if (!rightsState.selectedGroupId && rightsState.groups.length) {
    rightsState.selectedGroupId = rightsState.groups[0].id;
  }
  if (rightsState.selectedGroupId) {
    rEl("rightsGroupSelect").value = rightsState.selectedGroupId;
    await loadGroupRights();
  }
}

async function loadUsers() {
  const params = new URLSearchParams();
  const query = rEl("rightsSearch").value.trim();
  const groupId = rEl("rightsGroupFilter").value;
  const limit = rEl("rightsUserLimit").value || "200";
  if (query) params.set("query", query);
  if (groupId) params.set("group_id", groupId);
  params.set("limit", limit);
  rightsState.users = await rightsFetch(`/api/admin/rights/users?${params.toString()}`);
  renderUsers();
  rEl("rightsStatus").textContent = `Пользователей: ${rightsState.users.length}`;
}

async function loadGroupRights() {
  rightsState.selectedGroupId = rEl("rightsGroupSelect").value || rightsState.selectedGroupId;
  if (!rightsState.selectedGroupId) return;
  rightsState.rights = await rightsFetch(`/api/admin/rights/groups/${encodeURIComponent(rightsState.selectedGroupId)}/rights`);
  renderRights();
}

function renderGroupSelects() {
  const options = ['<option value="">Все группы</option>']
    .concat(rightsState.groups.map((group) => `<option value="${escapeHtml(group.id)}">${escapeHtml(group.id)} (${group.rights_count ?? 0})</option>`))
    .join("");
  rEl("rightsGroupFilter").innerHTML = options;
  rEl("rightsGroupSelect").innerHTML = rightsState.groups
    .map((group) => `<option value="${escapeHtml(group.id)}">${escapeHtml(group.id)} - ${escapeHtml(group.name ?? "")}</option>`)
    .join("");
  rEl("rightsAssignGroup").innerHTML = rEl("rightsGroupSelect").innerHTML;
}

function renderUsers() {
  const tbody = rEl("rightsUsersRows");
  tbody.innerHTML = "";
  for (const user of rightsState.users) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(user.id ?? "")}</td>
      <td>${escapeHtml(user.name ?? "")}</td>
      <td>${escapeHtml(user.user_group ?? "")}</td>
      <td>${user.pravo_admin_login ?? ""}</td>
      <td>${user.ware_id ?? ""}</td>
      <td>${escapeHtml(user.smena ?? "")}</td>
    `;
    tr.addEventListener("click", () => {
      rightsState.selectedUserId = user.id;
      rightsState.selectedGroupId = user.user_group;
      rEl("rightsAssignGroup").value = user.user_group || "";
      rEl("rightsGroupSelect").value = user.user_group || rEl("rightsGroupSelect").value;
      loadGroupRights().catch(showRightsError);
      document.querySelectorAll(".rights-table tbody tr").forEach((row) => row.classList.remove("selected"));
      tr.classList.add("selected");
    });
    tbody.appendChild(tr);
  }
}

function renderRights() {
  const tbody = rEl("rightsRows");
  tbody.innerHTML = "";
  for (const right of rightsState.rights) {
    const tr = document.createElement("tr");
    const rightName = right.right1 ?? "";
    tr.innerHTML = `
      <td>${escapeHtml(rightName)}</td>
      <td>${right.id ?? ""}</td>
      <td>${escapeHtml(right.descr ?? "")}</td>
      <td>${canEditRights() ? `<button type="button" data-right="${escapeHtml(rightName)}">Удалить</button>` : ""}</td>
    `;
    const button = tr.querySelector("button");
    if (button) {
      button.addEventListener("click", () => revokeRight(rightName).catch(showRightsError));
    }
    tbody.appendChild(tr);
  }
  rEl("rightsStatus").textContent = `Группа ${rightsState.selectedGroupId}: прав ${rightsState.rights.length}`;
}

async function assignUserGroup() {
  if (!rightsState.selectedUserId) throw new Error("Сначала выберите пользователя.");
  const groupId = rEl("rightsAssignGroup").value;
  await rightsFetch(`/api/admin/rights/users/${encodeURIComponent(rightsState.selectedUserId)}/group`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_group: groupId }),
  });
  await loadUsers();
  rightsState.selectedGroupId = groupId;
  rEl("rightsGroupSelect").value = groupId;
  await loadGroupRights();
}

async function addRight() {
  const groupId = rEl("rightsGroupSelect").value;
  const rightName = rEl("rightsNewRight").value.trim();
  const description = rEl("rightsNewDescr").value.trim();
  if (!groupId || !rightName) throw new Error("Укажите группу и право.");
  await rightsFetch(`/api/admin/rights/groups/${encodeURIComponent(groupId)}/rights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ right_name: rightName, description }),
  });
  rEl("rightsNewRight").value = "";
  rEl("rightsNewDescr").value = "";
  await loadGroups();
}

async function revokeRight(rightName) {
  const groupId = rEl("rightsGroupSelect").value;
  const ok = window.confirm(`Удалить право ${rightName} из группы ${groupId}?`);
  if (!ok) return;
  await rightsFetch(`/api/admin/rights/groups/${encodeURIComponent(groupId)}/rights/${encodeURIComponent(rightName)}`, {
    method: "DELETE",
  });
  await loadGroups();
}

function initRightsAdmin() {
  if (!rEl("rightsRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("rights_admin_view")) return;

  document.querySelectorAll("[data-permission='rights_admin_edit']").forEach((node) => {
    node.hidden = !canEditRights();
  });
  rEl("rightsRefresh").addEventListener("click", () => loadUsers().catch(showRightsError));
  rEl("rightsRefreshUsers").addEventListener("click", () => loadUsers().catch(showRightsError));
  rEl("rightsLoadGroup").addEventListener("click", () => loadGroupRights().catch(showRightsError));
  rEl("rightsGroupFilter").addEventListener("change", () => loadUsers().catch(showRightsError));
  rEl("rightsUserLimit").addEventListener("change", () => loadUsers().catch(showRightsError));
  rEl("rightsSearch").addEventListener("change", () => loadUsers().catch(showRightsError));
  rEl("rightsAssignUser").addEventListener("click", () => assignUserGroup().catch(showRightsError));
  rEl("rightsAddRight").addEventListener("click", () => addRight().catch(showRightsError));

  loadGroups()
    .then(loadUsers)
    .catch(showRightsError);
}

function showRightsError(error) {
  rEl("rightsStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initRightsAdmin();
} else {
  window.addEventListener("wms-admin-auth-ready", initRightsAdmin, { once: true });
}
