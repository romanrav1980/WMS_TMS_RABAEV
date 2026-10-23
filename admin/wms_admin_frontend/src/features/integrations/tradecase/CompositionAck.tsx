import { useState } from "react";
import { ApiRequestError, apiFetch } from "../../../api";
import { Act, HelpLink } from "./ui";
import { useRead } from "./useRead";

// Состав собранного заказа и деловые ответы SAP и СКМ (C-0164): сборка закрыта отдельно от подтверждения состава;
// заказ считается переданным только когда обе системы приняли именно этот состав. Список приходит без недоступных собственников.
type Row = { warehouse_id: number; order_id: string; order_version: number; assembly_closed: boolean; live_carriers: number; status: string;
  composition_no?: number; carriers?: number; units?: number; codes?: number; source_id?: string; skm_id?: string | null;
  sap_status?: string; sap_reason?: string | null; skm_status?: string; skm_reason?: string | null; change_reason?: string | null };
type Page = { items: Row[]; has_more: boolean };

const STATUS: Record<string, string> = { ASSEMBLY_OPEN: "сборка не закрыта", NOT_REPORTED: "сборка закрыта, состав не отправлен",
  WAITING: "ждёт подтверждения состава", REJECTED: "состав отклонён", CHANGED: "состав изменился после отправки", CONFIRMED: "состав подтверждён" };
const SYSTEM: Record<string, string> = { WAITING: "ждём ответа", ACCEPTED: "принял", REJECTED: "отклонил", NOT_REQUIRED: "не требуется (нет кодов)" };
const CHANGE: Record<string, string> = { ASSEMBLY_REOPENED: "сборка снова открыта", COMPOSITION_CHANGED: "фактический состав паллет другой",
  ORDER_VERSION_CHANGED: "пришла новая версия заказа", SOURCE_CHANGED: "сменился источник заказов", SKM_CHANGED: "сменилась действующая СКМ" };
const help = (id: string, text: string) => ({ id: "tradecase.composition." + id, text, anchor: "composition-ack" });

export function CompositionAck({ wh, onOpen }: { wh: string; onOpen: (orderId: string) => void }) {
  const [reload, setReload] = useState(0), [busy, setBusy] = useState(""), [message, setMessage] = useState("");
  const read = useRead<Page>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/order-compositions?limit=50`, reload);
  const report = async (r: Row) => {
    setBusy(r.order_id); setMessage("");
    try {
      await apiFetch("/api/tradecase/order-compositions/report", { method: "POST", body: JSON.stringify({ warehouse_id: r.warehouse_id, order_id: r.order_id }) });
      setMessage(`Состав заказа ${r.order_id} отправлен на подтверждение.`);
    } catch (e) {
      setMessage(e instanceof ApiRequestError && e.status === 409 ? "Состав не отправлен: обновите список и проверьте сборку заказа."
        : e instanceof ApiRequestError && (e.status === 401 || e.status === 403) ? "Нет права отправлять состав этого заказа."
        : "Исход отправки не подтверждён — повторите: тот же состав не будет отправлен второй раз.");
    } finally { setBusy(""); setReload(n => n + 1); }
  };
  return <section className="tc-bind" aria-label="Подтверждение состава заказов">
    <h4>Подтверждение состава заказов <HelpLink anchor="composition-ack" /> <Act help={help("refresh", "Перечитать состояние собранных заказов этого склада.")} onClick={() => setReload(n => n + 1)}>Обновить</Act></h4>
    <p className="tc-note">Закрытая сборка ещё не значит, что заказ передан: нужен деловой ответ SAP и, если в составе есть коды маркировки, действующей СКМ — именно на этот состав.</p>
    {read.error && <p className="tc-err" role="alert">Состояние не прочитано: {read.error}</p>}
    {message && <p role="status" className="tc-note">{message}</p>}
    {read.data && read.data.items.length === 0 && <p className="tc-note">Собранных заказов нет (заказы недоступных собственников не показываются).</p>}
    {read.data && read.data.items.length > 0 && <ul className="tc-list">{read.data.items.map(r => <li key={r.order_id}>
      <b>{r.order_id}</b> версия {r.order_version} · {STATUS[r.status] ?? r.status}<br />
      <small>{r.assembly_closed ? "сборка закрыта" : "сборка не закрыта"} · паллет {r.live_carriers}
        {r.composition_no !== undefined && <> · отправлен состав №{r.composition_no} ({r.carriers} паллет, {r.units} ед., {r.codes} кодов)
          {" · SAP "}{r.source_id}: {SYSTEM[r.sap_status ?? ""] ?? r.sap_status}{r.sap_reason ? ` (${r.sap_reason})` : ""}
          {" · СКМ "}{r.skm_id ?? "—"}: {SYSTEM[r.skm_status ?? ""] ?? r.skm_status}{r.skm_reason ? ` (${r.skm_reason})` : ""}</>}
        {r.change_reason ? " · " + (CHANGE[r.change_reason] ?? r.change_reason) + ": отправьте состав заново" : ""}</small><br />
      <Act help={help("open", "Открыть заказ в списке документов обмена.")} onClick={() => onOpen(r.order_id)}>Открыть заказ</Act>
      {(r.status === "NOT_REPORTED" || r.status === "CHANGED") && r.assembly_closed && <Act help={help("report", "Отправить фактический состав собранного заказа в SAP и СКМ. Повтор того же состава не создаёт второго сообщения.")}
        disabled={busy === r.order_id} onClick={() => void report(r)}>Отправить состав</Act>}
    </li>)}</ul>}
    {read.data?.has_more && <p className="tc-note">Показаны последние 50 заказов.</p>}
  </section>;
}
