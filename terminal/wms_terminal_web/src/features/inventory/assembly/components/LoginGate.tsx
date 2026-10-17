import { useState } from "react";
import type { AssemblyAuthState } from "../useAssemblyAuth";

export function LoginGate({ auth, purpose }: { auth: AssemblyAuthState; purpose?: string }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const submit = () => void auth.login(username, password);
  return <div className="asm-login">
    <h1>{purpose || "Пост сборки"}</h1>
    <p className="asm-note">Вход существующей учётной записью. Пароль хранится только в памяти этой страницы.</p>
    <label>Логин
      <input value={username} autoFocus autoComplete="username" disabled={auth.busy}
        onChange={e => setUsername(e.target.value)} onKeyDown={e => e.key === "Enter" && submit()}
        title="Код оператора/логин учётной записи" data-help-id="assembly.login.username" /></label>
    <label>Пароль
      <input type="password" value={password} autoComplete="current-password" disabled={auth.busy}
        onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === "Enter" && submit()}
        title="Пароль учётной записи" data-help-id="assembly.login.password" /></label>
    {auth.error && <p className="asm-err" role="alert">{auth.error}</p>}
    <button type="button" disabled={auth.busy} onClick={submit} title="Войти учётной записью" data-help-id="assembly.login.submit">
      {auth.busy ? "Вход…" : "Войти"}
    </button>
  </div>;
}

