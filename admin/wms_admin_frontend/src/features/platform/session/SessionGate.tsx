import { useState } from "react";
import type { ReactNode, FormEvent } from "react";
import { setSessionCredentials } from "../../../api";
import "./session.css";

export function SessionGate({children}: {children: ReactNode}) {
  const driver = new URLSearchParams(location.search).get("page") === "driver";
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [identity, setIdentity] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [help, setHelp] = useState(false);
  async function login(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const bytes = new TextEncoder().encode(user.trim()+":"+password);
      const response = await fetch((import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088")+"/api/access/me", {
        headers: {Authorization:"Basic "+btoa(String.fromCharCode(...bytes))}, cache:"no-store"});
      const body = await response.json();
      if (!response.ok) throw new Error(response.status === 401 ? "Проверьте пользователя и пароль." : "Вход недоступен. Повторите после восстановления связи.");
      setSessionCredentials({username:body.username,password}); setPassword(""); setIdentity(body.username);
    } catch (reason) { setError(String(reason)); }
    finally { setBusy(false); }
  }
  if (driver) return <>{children}</>;
  if (identity) return <><div className="session-identity"><span>{identity}</span>
    <button type="button" data-help-id="session.logout" title="Завершить работу под этой учётной записью. Отправленные команды не отменяются, сохранённые черновики остаются." onClick={() => {setSessionCredentials(null); setIdentity("");}}>Выйти</button>
  </div>{children}</>;
  return <main className="session-login"><form onSubmit={event => void login(event)}>
    <h1>retailcase</h1><p>Войдите своей учётной записью. Доступ определяется сервером.</p>
    <fieldset disabled={busy}>
      <label>Пользователь<input required autoComplete="username" value={user} onChange={event => setUser(event.target.value)} title="Идентификатор вашей учётной записи WMS." data-help-id="session.username" /></label>
      <label>Пароль<input required type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} title="Пароль используется для проверки входа и не сохраняется приложением в хранилище браузера." data-help-id="session.password" /></label>
      <button type="submit" data-help-id="session.login" title="Проверить учётную запись и открыть доступное рабочее место.">{busy ? "Проверка…" : "Войти"}</button>
      <button type="button" data-help-id="session.help" title="Объяснить вход, хранение пароля и восстановление сохранённых команд." aria-expanded={help} onClick={() => setHelp(value => !value)}>Помощь со входом</button>
    </fieldset>
    {help && <aside><h2>Вход и сохранённая работа</h2><p>Используйте свою учётную запись. Организационная должность сама по себе не выдаёт прав. Пароль находится только в памяти открытой вкладки; после обновления страницы потребуется вход.</p><p>Выход не отменяет отправленную команду и не удаляет её журнал. После повторного входа восстановите исход в рабочем экране. Полные инструкции доступны в «Справке» после входа.</p></aside>}
    {error && <p role="alert">{error}</p>}
  </form></main>;
}
