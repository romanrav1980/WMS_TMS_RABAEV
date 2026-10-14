import "./DriverWorkspace.css";
import {useState} from "react";
import type {DriverCredentials} from "./driverApi";
export function DriverLogin({onLogin,busy,error}:{onLogin:(credentials:DriverCredentials)=>Promise<void>;busy:boolean;error:string|null}){
 const [id,setId]=useState(()=>new URLSearchParams(location.search).get("driver_id")||new URLSearchParams(location.search).get("id")||"");
 const [username,setUsername]=useState(""),[password,setPassword]=useState("");
 return <div className="driver-login"><form className="driver-login-card" onSubmit={event=>{event.preventDefault();const driverId=Number(id);if(Number.isSafeInteger(driverId)&&driverId>0)void onLogin({driverId,username,password});}}>
  <div className="driver-login-logo">🚛</div><h1>Рабочее место водителя</h1>
  <p>Войдите своей учётной записью. Доступ к рейсам определяется привязкой водителя.</p>
  <fieldset disabled={busy}>
   <label>ID водителя<input type="number" min="1" required value={id} onChange={e=>setId(e.target.value)} title="Идентификатор водителя из назначения диспетчера"/></label>
   <label>Пользователь<input autoComplete="username" required value={username} onChange={e=>setUsername(e.target.value)} title="Учётная запись, привязанная к этому водителю"/></label>
   <label>Пароль<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} title="Пароль не сохраняется в браузере"/></label>
   <button type="submit" title="Проверить учётную запись и открыть назначенные рейсы">{busy?"Вход…":"Войти"}</button>
  </fieldset>{error&&<p role="alert">{error}</p>}
 </form></div>;
}
