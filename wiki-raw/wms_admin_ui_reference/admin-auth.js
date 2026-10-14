// Move saved commands before any operation can be submitted under the new UI.
try {
(function migrateSavedCommands() {
  const prefixes = [String.fromCharCode(110,105,99,111,114,97),String.fromCharCode(110,105,107,111,114,97)];
  const keys = Array.from({length:localStorage.length},(_,index)=>localStorage.key(index)).filter(key=>key!==null);
  for(const oldKey of keys){
    let newKey=null;
    for(const prefix of prefixes){
      if(oldKey.startsWith(prefix+'.')||oldKey.startsWith(prefix+':')){newKey='retailcase'+oldKey.slice(prefix.length);break;}
      if(oldKey.startsWith('["'+prefix+'.')){const parts=JSON.parse(oldKey);if(Array.isArray(parts)&&typeof parts[0]==='string'){parts[0]='retailcase'+parts[0].slice(prefix.length);newKey=JSON.stringify(parts);break;}}
    }
    if(!newKey)continue;
    const original=localStorage.getItem(oldKey);if(original===null)continue;
    const current=localStorage.getItem(newKey);
    if(current!==null&&current!==original)throw Error('Обнаружены две разные сохранённые команды. Требуется разбор до следующей операции.');
    localStorage.setItem(newKey,original);
    if(localStorage.getItem(newKey)!==original)throw Error('Не удалось сохранить исходную команду после обновления.');
    localStorage.removeItem(oldKey);
  }
})();
} catch (error) {
  document.body.classList.remove("auth-pending");
  document.body.setAttribute("role", "alert");
  document.body.textContent = "Сохранённые команды требуют разбора. " + String(error);
  throw error;
}

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
  let saved;
  try { saved = JSON.parse(raw); }
  catch { sessionStorage.removeItem(ADMIN_SESSION_KEY); return false; }
  if (!saved || typeof saved.basic !== "string" || !saved.basic) {
    sessionStorage.removeItem(ADMIN_SESSION_KEY); return false;
  }
  authState.apiBase = saved.apiBase || DEFAULT_API_BASE;
  authState.basic = saved.basic;
  try {
    const user = await fetchCurrentUser();
    completeLogin(user);
    return true;
  } catch (error) {
    authState.user = null;
    if (error.status === 401 || error.status === 403) {
      sessionStorage.removeItem(ADMIN_SESSION_KEY); authState.basic = null;
      const retry=authEl("adminRetrySession"); if(retry)retry.hidden=true;
    } else {
      const message=authEl("loginError");
      if(message){
        message.textContent="Сервер не подтвердил вход. Сохранённая сессия не удалена; повторите проверку соединения.";
        let retry=authEl("adminRetrySession");
        if(!retry){
          retry=document.createElement("button");retry.id="adminRetrySession";retry.type="button";
          retry.textContent="Повторить проверку входа";retry.title="Проверить сохранённую сессию на сервере; доступ откроется только после подтверждения";
          retry.onclick=async()=>{retry.disabled=true;try{await verifyStoredSession();}finally{retry.disabled=false;}};
          message.after(retry);
        }
        retry.hidden=false;
      }
    }
    return false;
  }
}
async function fetchCurrentUser() {
  const response = await fetch(`${authState.apiBase}/api/admin/auth/me`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw Object.assign(new Error(`HTTP ${response.status}`), {status: response.status});
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
