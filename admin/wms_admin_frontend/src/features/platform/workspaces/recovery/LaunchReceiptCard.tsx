import { useState } from "react";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { useApiRead } from "../../access-admin";
import { openLink } from "../resources/ResourceCard";

// Восстановление после неподтверждённого запуска волны (C-0092/C-0094). Только чтение:
// GET /api/picking/waves/{wave}/launch-receipts/{operation} и фактическое состояние волны. Команды не отправляются:
// повтор запуска — в «Панели смены» тем же operation_id, когда root выпустит команду (до READY кнопки нет).

type Receipt = { operation_id: string; wave_id: number; state: string; launch_outcome_confirmed: boolean; continuation_state: string; commands_executed: boolean };
type Readiness = { pick_wave_id: number; wave_code: string; wave_status: string; status: string; is_ready: boolean;
  summary: { open_replenishment_count: number; open_staging_count: number; open_case_pick_count: number; shortage_count: number } };

const h = (id: string, text: string): HelpEntry => ({ id: "launch-receipt." + id, text, article: "shift-supervisor" });
const help = {
  wave: h("wave", "Номер волны, запуск которой не подтвердился."),
  operation: h("operation", "Ключ операции (operation_id) исходной команды запуска — из сообщения панели смены. Новый ключ не создаётся."),
  read: h("read", "Прочитать квитанцию запуска и фактическое состояние волны. Ничего не отправляет и не меняет."),
  shift: h("open.shift", "Открыть панель смены по этой волне: повтор запуска — только той же командой с тем же ключом."),
};

/** Объяснение состояния квитанции без утверждений сверх источника. */
function explain(r: Receipt): { title: string; tone: "ship" | "other" | "bad"; text: string } {
  if (r.state === "APPLIED") return { title: "Запуск проведён", tone: "ship",
    text: "Сервер подтверждает, что запуск волны проведён. Квитанция не подтверждает подготовку заданий: проверьте открытые задачи волны ниже. Повторная команда второй запуск не создаст." };
  if (r.state === "NOT_VISIBLE") return { title: "Квитанция не видна", tone: "other",
    text: "Проведённого запуска с этим ключом не видно: команда могла не дойти, ключ мог быть введён с ошибкой, или квитанция принадлежит другому автору. Это не доказательство отмены или отката. Повторите исходную команду в панели смены тем же ключом." };
  return { title: `Состояние проводки: ${r.state}`, tone: "bad", text: "Состояние не подтверждено как проведённое. Не создавайте новую команду; повторите исходную тем же ключом или обратитесь к старшему смены." };
}

export function LaunchReceiptCard({ initialWave = "", initialOperation = "" }: { initialWave?: string; initialOperation?: string }) {
  const [wave, setWave] = useState(initialWave), [op, setOp] = useState(initialOperation);
  const [asked, setAsked] = useState<{ wave: string; op: string; n: number } | null>(initialWave && initialOperation ? { wave: initialWave, op: initialOperation, n: 0 } : null);
  const receipt = useApiRead<Receipt>(asked ? `/api/picking/waves/${asked.wave}/launch-receipts/${encodeURIComponent(asked.op)}` : null, asked?.n ?? 0);
  const ready = useApiRead<Readiness>(asked ? `/api/picking/waves/${asked.wave}/readiness` : null, asked?.n ?? 0);
  // Ответ показывается только для запрошенной пары волна+ключ.
  const r = receipt.data && asked && String(receipt.data.wave_id) === asked.wave && receipt.data.operation_id === asked.op ? receipt.data : null;
  const e = r && explain(r);
  const valid = /^\d+$/.test(wave) && op.trim().length >= 1 && op.trim().length <= 100;
  return <section className="ops-card" aria-label="Квитанция запуска волны">
    <h3>Запуск волны не подтвердился</h3>
    <div className="rg-window">
      <label>Волна <input inputMode="numeric" value={wave} onChange={ev => setWave(ev.target.value.replace(/\D/g, ""))} title={help.wave.text} data-help-id={help.wave.id} style={{ width: 100 }} /></label>
      <label>Ключ операции <input value={op} onChange={ev => setOp(ev.target.value)} title={help.operation.text} data-help-id={help.operation.id} style={{ width: 280 }} /></label>
      <HelpButton help={help.read} unavailable={!valid && "укажите номер волны и ключ операции"} onClick={() => setAsked({ wave, op: op.trim(), n: (asked?.n ?? 0) + 1 })}>Прочитать квитанцию</HelpButton>
    </div>
    {receipt.error && <p className="ops-err">{receipt.error}</p>}
    {asked && receipt.loading && <p className="ops-note">Чтение…</p>}
    {r && e && <>
      <p><span className={"ops-chip " + e.tone}>{e.title}</span> <small className="ops-note">ключ {r.operation_id} · волна {r.wave_id}</small></p>
      <p>{e.text}</p>
      <h3>Волна сейчас</h3>
      {ready.error ? <p className="ops-err">{ready.error}</p> : !ready.data ? <p className="ops-note">Чтение…</p> :
        <dl><dt>Статус волны</dt><dd>{ready.data.wave_status}</dd>
          <dt>Открыто</dt><dd>пополнений {ready.data.summary.open_replenishment_count}, размещений {ready.data.summary.open_staging_count}, сборок {ready.data.summary.open_case_pick_count}, недостач {ready.data.summary.shortage_count}</dd></dl>}
      <HelpButton help={help.shift} onClick={() => openLink({ page: "shift-supervisor-wave.html", params: { wave_id: r.wave_id } })}>Панель смены</HelpButton>
    </>}
  </section>;
}
