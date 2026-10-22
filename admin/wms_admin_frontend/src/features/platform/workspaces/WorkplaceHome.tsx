import { useEffect, useState } from "react";
import { apiOperationScope } from "../../../api";
import { HelpButton } from "../help/HelpButton";
import { DriverDesk, PickerDesk, ReachDriverDesk } from "./DeviceDesks";
import { ReceivingLeadDesk } from "./receiving/ReceivingLeadDesk";
import { appLink } from "./OpsParts";
import { DirectorDesk, DispatcherDesk, YardDesk } from "./RoleDesks";
import { StorageLeadDesk } from "./storage/StorageLeadDesk";
import { wsHelp } from "./help";
import { ConsolidationDesk } from "./consolidation/ConsolidationDesk";
import { ShiftSupervisorDesk } from "./shift/ShiftSupervisorDesk";
import { KpiDesk } from "./kpi";
import { ExceptionsDesk } from "./exceptions/ExceptionsDesk";
import "../access-admin/access-admin.css";
import "./ops.css";

type Role = "kpi" | "consolidation" | "director" | "shift" | "receiving" | "storage" | "dispatcher" | "yard" | "exceptions" | "picker" | "reach" | "driver";
const ROLES: { id: Role; label: string }[] = [
  { id: "kpi", label: "KPI" },
  { id: "consolidation", label: "Консолидация" }, { id: "director", label: "Директор РЦ" }, { id: "shift", label: "Старший смены" }, { id: "receiving", label: "Приёмка" }, { id: "storage", label: "Хранение и ричтраки" }, { id: "dispatcher", label: "Диспетчер" }, { id: "yard", label: "Двор и ворота" }, { id: "exceptions", label: "Исключения" }, { id: "picker", label: "Комплектовщик (ТСД)" }, { id: "reach", label: "Ричтрак (ТСД)" }, { id: "driver", label: "Водитель" }];
const localDay = (d = new Date()) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const DEVICE = new Set<Role>(["picker", "reach", "driver"]);
const initialRole = (): Role => { const v = new URLSearchParams(location.search).get("workspace"); return ROLES.some(r => r.id === v) ? v as Role : "director"; };

/** Ролевые рабочие места C0056 (блок 4) в стиле цифрового двойника. Выбор места не меняет прав: данные режет сервер. */
export function WorkplaceHome({ onBack }: { onBack?: () => void }) {
  const [role, setRole] = useState<Role>(initialRole);
  useEffect(() => { const sync = () => setRole(initialRole()); window.addEventListener("popstate", sync); return () => window.removeEventListener("popstate", sync); }, []);
  const [day, setDay] = useState(localDay);
  const [reload, setReload] = useState(0);
  const choose = (next: Role) => { setRole(next); const url = new URL(location.href); url.searchParams.set("workspace", next); history.replaceState(history.state, "", url); };
  // Свежесть показывает каждый источник по моменту успешного ответа (SourceStrip), а не момент нажатия.
  const refresh = () => setReload(n => n + 1);
  const header = <header className="ops-panel ops-header">
    <div className="ops-brand">Склад · рабочее место<small>данные сервера; права определяет сервер</small></div>
    <label className="ops-role-select">Рабочее место <select value={role} title="Выбрать рабочее место. Доступ к его данным проверяет сервер."
      data-help-id="workspace.role.select" onChange={event=>choose(event.target.value as Role)}>{ROLES.map(item=><option key={item.id} value={item.id}>{item.label}</option>)}</select></label>
    <div role="tablist" aria-label="Рабочее место" className="ops-roles">{ROLES.map(r =>
      <button key={r.id} role="tab" aria-selected={role === r.id} title={wsHelp.role.text} data-help-id={wsHelp.role.id + "." + r.id} onClick={() => choose(r.id)}>{r.label}</button>)}</div>
    {!DEVICE.has(role) && role !== "consolidation" && role !== "kpi" && role !== "exceptions" && <label>Дата <input type="date" value={day} onChange={e => e.target.value && setDay(e.target.value)} title={wsHelp.date.text} data-help-id={wsHelp.date.id} /></label>}
    {role !== "consolidation" && <HelpButton help={wsHelp.refresh} onClick={refresh}>Обновить</HelpButton>}
    <HelpButton help={wsHelp.model} onClick={() => { location.href = appLink("twin"); }}>3D-модель смены</HelpButton>
    {onBack && <HelpButton help={{ id: "workspace.back", text: "Вернуться к предыдущему экрану.", article: "workspaces" }} onClick={onBack}>← Назад</HelpButton>}
  </header>;
  // Смена пользователя (другой вход) пересоздаёт стол: данные и выбор прежнего пользователя не остаются на экране.
  const scope = apiOperationScope();
  if (DEVICE.has(role)) return <div className="ops" style={{ display: "block" }}>{header}<div style={{ marginTop: 10 }} key={scope}>
    {role === "picker" ? <PickerDesk reload={reload} /> : role === "reach" ? <ReachDriverDesk reload={reload} /> : <DriverDesk />}</div></div>;
  const isToday = day === localDay();
  return <main className={"ops" + (role === "kpi" ? " ops-kpi-page" : role === "consolidation" || role === "exceptions" ? " ops-consolidation" : role === "shift" || role === "receiving" ? " ops-shift" : role === "storage" ? " ops-storage" : "")} aria-label="Рабочее место">{header}
    {role === "kpi" ? <KpiDesk key={scope} day={day} reload={reload} /> : role === "consolidation" ? <ConsolidationDesk key={scope} />
      : role === "director" ? <DirectorDesk key={scope} day={day} isToday={isToday} reload={reload} />
      : role === "shift" ? <ShiftSupervisorDesk key={scope} day={day} isToday={isToday} reload={reload} />
      : role === "receiving" ? <ReceivingLeadDesk key={scope} day={day} isToday={isToday} reload={reload} />
      : role === "storage" ? <StorageLeadDesk key={scope} day={day} isToday={isToday} reload={reload} />
      : role === "exceptions" ? <ExceptionsDesk key={scope} reload={reload} />
      : role === "yard" ? <YardDesk key={scope} day={day} isToday={isToday} reload={reload} />
      : <DispatcherDesk key={scope} day={day} isToday={isToday} reload={reload} />}</main>;
}
