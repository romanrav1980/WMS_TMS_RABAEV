const ADMIN_SESSION_KEY = "wmsAdminAuth";
const DEFAULT_API_BASE = "http://127.0.0.1:8088";

if (window.location.hash === "#api-audit" && !window.location.pathname.endsWith("api-audit.html")) {
  window.location.replace("api-audit.html");
}

const authState = {
  apiBase: sessionStorage.getItem("wmsAdminApiBase") || DEFAULT_API_BASE,
  basic: null,
  user: null,
};

function isDemoMode() {
  return new URLSearchParams(window.location.search).get("demo") === "1"
    || new URLSearchParams(window.location.hash.replace(/^#/, "").replaceAll(";", "&")).get("demo") === "1";
}

function authEl(id) {
  return document.getElementById(id);
}

function authHeaders(extra = {}) {
  return authState.basic ? { ...extra, Authorization: authState.basic } : { ...extra };
}

function hasPermission(permission) {
  if (!permission || !authState.user) return false;
  const permissions = authState.user.permissions || [];
  return permissions.includes("*") || permissions.includes(permission);
}

function requireCurrentPagePermission() {
  const required = document.body.dataset.requiredPermission;
  if (!required || hasPermission(required)) return true;
  document.body.classList.add("access-denied-mode");
  const workspace = document.querySelector(".workspace");
  if (workspace) {
    workspace.innerHTML = `
      <header class="topbar">
        <div class="breadcrumbs"><b>Админ-панель WMS</b><span>/</span><b>Нет доступа</b></div>
      </header>
      <section class="admin-page">
        <article class="panel access-denied">
          <h2>Нет прав на этот раздел</h2>
          <p>Для страницы требуется право <b>${escapeHtml(required)}</b>.</p>
        </article>
      </section>
    `;
  }
  return false;
}

function applyPermissions() {
  document.querySelectorAll("[data-permission]").forEach((node) => {
    const permission = node.dataset.permission;
    node.hidden = !hasPermission(permission);
  });
  const role = authEl("adminUserRole");
  if (role && authState.user) {
    role.textContent = (authState.user.permissions || []).join(", ");
  }
  const name = authEl("adminUserName");
  if (name && authState.user) {
    name.textContent = authState.user.username;
  }
}

async function verifyStoredSession() {
  const raw = sessionStorage.getItem(ADMIN_SESSION_KEY);
  if (!raw) return false;
  try {
    const saved = JSON.parse(raw);
    authState.apiBase = saved.apiBase || DEFAULT_API_BASE;
    authState.basic = saved.basic || null;
    if (!authState.basic) return false;
    const user = await fetchCurrentUser();
    completeLogin(user);
    return true;
  } catch {
    sessionStorage.removeItem(ADMIN_SESSION_KEY);
    return false;
  }
}

async function fetchCurrentUser() {
  const response = await fetch(`${authState.apiBase}/api/admin/auth/me`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function login(username, password, apiBase) {
  authState.apiBase = apiBase.replace(/\/$/, "") || DEFAULT_API_BASE;
  authState.basic = `Basic ${btoa(`${username}:${password}`)}`;
  const response = await fetch(`${authState.apiBase}/api/admin/auth/login`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(await buildLoginError(response));
  const user = await response.json();
  sessionStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify({
    apiBase: authState.apiBase,
    basic: authState.basic,
  }));
  sessionStorage.setItem("wmsAdminApiBase", authState.apiBase);
  completeLogin(user);
}

function completeLogin(user) {
  authState.user = user;
  applyPermissions();
  const allowed = requireCurrentPagePermission();
  document.body.classList.remove("auth-pending");
  const loginScreen = authEl("adminLoginScreen");
  if (loginScreen) loginScreen.hidden = true;
  if (allowed) {
    window.dispatchEvent(new CustomEvent("wms-admin-auth-ready", { detail: user }));
  }
}

function logout() {
  sessionStorage.removeItem(ADMIN_SESSION_KEY);
  authState.basic = null;
  authState.user = null;
  document.body.classList.add("auth-pending");
  showLogin();
}

function showLogin() {
  let screen = authEl("adminLoginScreen");
  if (!screen) {
    screen = document.createElement("section");
    screen.id = "adminLoginScreen";
    screen.className = "login-screen";
    screen.innerHTML = `
      <form id="adminLoginForm" class="login-card">
        <div class="brand login-brand"><div class="brand-mark">W</div><div class="brand-text"><span>WMS</span> PRO</div></div>
        <h1>Вход в админку</h1>
        <label>Логин<input id="loginUser" value="admin" autocomplete="off" required /></label>
        <label>Пароль<input id="loginPassword" type="password" value="admin123" autocomplete="new-password" required /></label>
        <div class="login-hints">
          <span>Пользователь берется из Oracle <b>RUSERS</b>: <b>admin/admin123</b></span>
          <button id="loginFillAdmin" type="button">Заполнить admin</button>
        </div>
        <button type="submit">Войти</button>
        <p id="loginError"></p>
      </form>
    `;
    document.body.appendChild(screen);
    authEl("loginFillAdmin").addEventListener("click", () => {
      authEl("loginUser").value = "admin";
      authEl("loginPassword").value = "admin123";
    });
    authEl("adminLoginForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      const error = authEl("loginError");
      error.textContent = "";
      try {
        await login(
          authEl("loginUser").value.trim(),
          authEl("loginPassword").value,
          authState.apiBase,
        );
      } catch (exc) {
        error.textContent = exc.message;
      }
    });
  }
  screen.hidden = false;
  const logoutButton = authEl("adminLogout");
  if (logoutButton) logoutButton.addEventListener("click", logout);
}

async function buildLoginError(response) {
  let detail = "";
  try {
    const payload = await response.json();
    detail = payload.detail ? `: ${payload.detail}` : "";
  } catch {
    detail = "";
  }
  if (response.status === 401) return `Неверный логин или пароль (${response.status})${detail}`;
  if (response.status === 403) return `Нет нужных прав (${response.status})${detail}`;
  if (response.status === 404) return `Backend не обновлен или endpoint auth не найден (${response.status})`;
  return `Ошибка входа (${response.status})${detail}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

window.wmsAdminAuth = {
  headers: authHeaders,
  hasPermission,
  state: authState,
};

showLogin();
if (isDemoMode()) {
  completeLogin({
    username: "demo",
    permissions: ["*"],
  });
} else {
  verifyStoredSession().then((ok) => {
    if (!ok) {
      document.body.classList.add("auth-pending");
    }
  });
}
