import { RAW_ADMIN_BASE } from "../../../../api";
import { HelpButton } from "../../help/HelpButton";
import { rawLink } from "../OpsParts";
import { WarehousePicker } from "../resources/WarehousePicker";
import { SHIFT_LIMITS } from "./useShiftData";

const API_ORIGIN = RAW_ADMIN_BASE.replace(/\/wms-admin$/, "");

/** Склад старшего смены и переходы к соседним рабочим местам/экранам (C0116–C0118). Склад хранится в адресе. */
export function ShiftWarehouseBar({ wh, onChange }: { wh: string; onChange: (id: string) => void }) {
  return <div className="ops-panel rg-window" style={{ gridColumn: "1/-1" }}>
    <WarehousePicker capability="waves" value={wh} onChange={onChange} />
    {wh && <HelpButton help={{ id: "shift.open.consolidation", text: "Открыть ожидаемый состав паллет (планы консолидации) этого склада. План и физическое дерево показаны раздельно.", article: "consolidation-plan" }}
      onClick={() => { location.href = `?page=workspace&workspace=consolidation&warehouse_id=${wh}`; }}>Ожидаемый состав</HelpButton>}
    {/* C0118: переходы к существующим экранам контроля и магазина. Склад они не принимают параметром — открываются как есть. */}
    <HelpButton help={{ id: "shift.open.control", text: "Открыть грузовые места (контроль состава и веса места) в новой вкладке. Склад там выбирается сканом места.", article: "shift-navigation" }}
      onClick={() => window.open(rawLink("warehouse-hus.html"), "_blank", "noopener")}>Грузовые места</HelpButton>
    <HelpButton help={{ id: "shift.open.store", text: "Открыть приложение приёмки магазина в новой вкладке. Вход — учётной записью магазина.", article: "shift-navigation" }}
      onClick={() => window.open(`${API_ORIGIN}/store/`, "_blank", "noopener")}>Приложение магазина</HelpButton>
    <a className="rc-link" href={`${API_ORIGIN}/help/shift-navigation.html`} target="_blank" rel="noopener"
      title="Справка: как переходить «склад → волна → задание → ресурс» и обратно, не теряя склад. Откроется в новой вкладке" data-help-id="shift.navigation.help">Справка</a>
    <span className="ops-note">Сменный обзор одного склада: волны, сборка (до {SHIFT_LIMITS.caseTasks}), недостачи и сессии — по этому складу, фильтр и права применяет сервер.</span>
  </div>;
}
