import { useState } from "react";
import { HelpHint } from "../help/HelpHint";

export function LoginScreen({ busy, error, onLogin }: { busy: boolean; error: string; onLogin: (username: string, password: string) => void }) {
 const [username, setUsername] = useState("");
 const [password, setPassword] = useState("");
 return <section className="store-app-screen store-app-login" aria-label="Вход приёмщика магазина">
  <h1>Приложение магазина</h1>
  <p>Вход собственной учётной записью приёмщика. Пароль не сохраняется на устройстве.</p>
  <form onSubmit={(event) => { event.preventDefault(); onLogin(username, password); }}>
   <label>
    <span>Имя пользователя <HelpHint helpId="login.username" tip="Собственная учётная запись приёмщика магазина, не админский вход склада" article="store-receiving-app" /></span>
    <input title="Введите логин приёмщика назначенных вам магазинов" data-help-id="login.username" autoComplete="username" autoFocus value={username} onChange={(event) => setUsername(event.target.value)} disabled={busy} />
   </label>
   <label>
    <span>Пароль <HelpHint helpId="login.password" tip="Пароль хранится только в памяти этой сессии и не сохраняется на устройстве" article="store-receiving-app" /></span>
    <input title="Введите пароль; он не сохраняется приложением на устройстве" data-help-id="login.password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} disabled={busy} />
   </label>
   <button type="submit" data-help-id="login.submit" title="Войти собственной учётной записью приёмщика" disabled={busy || !username || !password}>{busy ? "Проверка…" : "Войти"}</button>
  </form>
  <p role="status" className="store-app-message">{error}</p>
 </section>;
}
