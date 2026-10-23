import { useState } from "react";
import { ApiRequestError, apiFetch } from "../../../api";
import { Act, HelpLink } from "./ui";
import { useRead } from "./useRead";

// Состав поставки частями (C-0163): какие части и подтверждения ещё не пришли, несовпадение итога и передача в приём.
// Список приходит с сервера уже без недоступных собственников; принятая поставка открывается как обычный документ SUPPLY.
type Transfer = { warehouse_id: number; source_id: string; transfer_id: string; document_id: string; version: number; part_count: number;
  received_codes: number; missing_parts: number[]; end_received: boolean; status: string; status_reason: string | null; owner_id: string | null };
type Page = { items: Transfer[]; has_more: boolean };

const STATUS: Record<string, string> = { OPEN: "ждёт данных", MISMATCH: "состав не сходится", COMPLETE: "собран, передаётся в приём",
  DELIVERED: "передан в приём", DELIVERY_REJECTED: "приём отклонил документ", SUPERSEDED: "заменён новой версией" };
const help = (id: string, text: string) => ({ id: "tradecase.supply.parts." + id, text, anchor: "supply-parts" });
const reason = (t: Transfer) => !t.status_reason ? "" : t.status_reason === "WAITING_END" ? "нет уведомления о завершении"
  : t.status_reason.startsWith("TOTAL_MISMATCH") ? `число кодов не сходится (получено/заявлено ${t.status_reason.split(":")[1]})`
  : t.status_reason === "CODES_HASH_MISMATCH" ? "контрольная сумма кодов не сходится с уведомлением о завершении"
  : t.status_reason === "SUPPLY_ASSEMBLED_TOO_LARGE" ? "собранный документ больше предела приёма 1 МБ" : t.status_reason;

export function SupplyParts({ wh, onOpen }: { wh: string; onOpen: (documentId: string) => void }) {
  const [reload, setReload] = useState(0), [busy, setBusy] = useState(""), [message, setMessage] = useState("");
  const read = useRead<Page>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/supply-transfers?limit=50`, reload);
  const deliver = async (t: Transfer) => {
    setBusy(t.transfer_id); setMessage("");
    try {
      // Identifiers may contain "/": they go in the body, not in the path.
      await apiFetch(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/supply-transfers/deliver`, { method: "POST",
        body: JSON.stringify({ source_id: t.source_id, transfer_id: t.transfer_id }) });
      setMessage(`Состав ${t.transfer_id} передан в приём.`);
    } catch (e) {
      setMessage(e instanceof ApiRequestError && e.status === 409 ? "Передача отклонена: обновите список и проверьте причину." : "Исход передачи не подтверждён — повторите: повтор не создаст второй документ.");
    } finally { setBusy(""); setReload(n => n + 1); }
  };
  return <section className="tc-bind" aria-label="Состав поставок частями">
    <h4>Состав поставок частями <HelpLink anchor="supply-parts" /> <Act help={help("refresh", "Перечитать передачи состава частями этого склада.")} onClick={() => setReload(n => n + 1)}>Обновить</Act></h4>
    <p className="tc-note">Поставка не принимается, пока не пришли все части и уведомление о завершении и пока число и контрольная сумма кодов не сошлись.</p>
    {read.error && <p className="tc-err" role="alert">Передачи не прочитаны: {read.error}</p>}
    {message && <p role="status" className="tc-note">{message}</p>}
    {read.data && read.data.items.length === 0 && <p className="tc-note">Передач частями нет (передачи недоступных собственников не показываются).</p>}
    {read.data && read.data.items.length > 0 && <ul className="tc-list">{read.data.items.map(t => <li key={t.source_id + ":" + t.transfer_id}>
      <b>{t.document_id}</b> версия {t.version} · {STATUS[t.status] ?? t.status}<br />
      <small>частей {t.missing_parts.length >= 50 ? "?" : t.part_count - t.missing_parts.length}/{t.part_count}{t.missing_parts.length ? ` · нет частей: ${t.missing_parts.join(", ")}${t.missing_parts.length >= 50 ? "…" : ""}` : ""}
        {" · "}{t.end_received ? "завершение получено" : "завершения ещё нет"} · кодов {t.received_codes}{reason(t) ? " · " + reason(t) : ""}</small><br />
      {t.status === "DELIVERED" && <Act help={help("open", "Открыть принятый документ поставки.")} onClick={() => onOpen(t.document_id)}>Открыть поставку</Act>}
      {t.status === "COMPLETE" && <Act help={help("deliver", "Передать собранный состав в приём ещё раз тем же сообщением: если он уже принят, второй документ не появится.")}
        disabled={busy === t.transfer_id} onClick={() => void deliver(t)}>Передать в приём</Act>}
    </li>)}</ul>}
    {read.data?.has_more && <p className="tc-note">Показаны последние 50 передач.</p>}
  </section>;
}
