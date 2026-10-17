import { useState } from "react";
import type { AssemblySession, AssemblyStep, RecoveryRequestBody } from "../contracts";
export function RecoveryPanel({ session, step, disabled, onRequest }: {
  session: AssemblySession; step: AssemblyStep | null; disabled: boolean; onRequest: (body: RecoveryRequestBody) => void;
}) {
  const [reason, setReason] = useState("");
  if (!step || !["WAITING_BEFORE","ARMED","READY","DISCREPANCY","CANCELLED"].includes(step.state)) return null;
  const recon = session.reconciliation?.step_id === step.step_id ? session.reconciliation : null;
  if (step.state === "CANCELLED" && !recon) return null;
  const pending = recon?.state === "REQUESTED" || recon?.state === "AUTHORIZED";
  const canRequest = !disabled && !pending && step.state !== "CANCELLED" && reason.trim().length >= 8;
  const send = () => {
    if (canRequest) onRequest({ operation_id: `ASM.RECON.UI:${crypto.randomUUID()}`, step_id: step.step_id, expected_content_version: session.content_version, reason: reason.trim() });
  };
  return <section className="asm-recovery asm-err-box">
    <h3>Сверка укладки</h3>
    {recon?.state === "REQUESTED" && session.state !== "BLOCKED" && <p>Остановка ещё не подтверждена текущим состоянием. Ничего не убирайте с весов.</p>}
    {recon?.state === "REQUESTED" && session.state === "BLOCKED" && !disabled && <>
      <p>Сессия остановлена сервером. Теперь уберите только непринятый товар этой укладки. Принятый товар и тару не трогайте.</p>
      <p>После удаления передайте проверку другому контролёру. Он входит своей учётной записью и подтверждает фактическое удаление.</p>
      <a href={`/assembly/?reconciliation_id=${encodeURIComponent(recon.reconciliation_id)}`} target="_blank" rel="noopener noreferrer" title="Открыть отдельное рабочее место сверки. Контролёр входит своей учётной записью, без передачи пароля оператора." data-help-id="assembly.recovery.controller-link">Открыть место контролёра ↗</a>
    </>}
    {pending && disabled && <p>Состояние сейчас уточняется. Не меняйте физический состав по неподтверждённому экрану.</p>}
    {recon?.state === "AUTHORIZED" && <p>Контролёр подтвердил удаление непринятого товара. Ожидаем новый стабильный замер весов; вручную вес не вводится.</p>}
    {recon?.state === "COMPLETED" && <p>Сверка завершена сервером. Старый шаг отменён без товарной проводки; следующая укладка создаётся отдельно.</p>}
    {recon?.state === "DISCREPANCY" && <p>Измерение не подтвердило исходный принятый вес. Сессия остаётся заблокированной; нужен новый разбор и новое подтверждение контролёра.</p>}
    {!pending && step.state !== "CANCELLED" && <>
      <p>Сначала запросите остановку. До подтверждения остановки ничего не убирайте с весов и не обнуляйте их.</p>
      <label>Причина сверки<textarea maxLength={500} value={reason} onChange={e => setReason(e.target.value)} disabled={disabled}
        title="Опишите причину остановки и сверки — от 8 до 500 символов." data-help-id="assembly.recovery.reason" /></label>
      <button type="button" disabled={!canRequest} onClick={send} title="Остановить эту сессию серверной командой. Удалять непринятый товар можно только после подтверждённого ответа." data-help-id="assembly.recovery.request">Остановить и сверить</button>
    </>}
  </section>;
}


