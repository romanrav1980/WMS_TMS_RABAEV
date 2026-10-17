import type { useStoreReceivingFlow } from "../useStoreReceivingFlow";
export function ReceiptRecovery({ flow, loadOperationId }: { flow: ReturnType<typeof useStoreReceivingFlow>; loadOperationId: string }) {
 return <section aria-label="Восстановление операции" className="store-app-recovery">
  {flow.pending && <p>Сохранённая операция ожидает подтверждения. Данные не меняются до выяснения результата.</p>}
  {flow.corrupt && <button type="button" title="Прочитать действительный результат с сервера; повреждённая запись не отправляется" data-help-id="receipt.reread" onClick={() => void flow.open(loadOperationId)}>Перечитать поставку</button>}
  {flow.pending && !flow.pending.confirmedRejection && <button type="button" title="Проверить квитанцию исходной операции без повторной отправки" data-help-id="receipt.status" disabled={flow.busy} onClick={() => void flow.checkStatus()}>Проверить результат</button>}
  {flow.pending && <button type="button" title="Повторить точное сохранённое тело с прежним номером операции" data-help-id="receipt.retry" disabled={flow.busy} onClick={() => void flow.retry()}>Повторить сохранённую операцию</button>}
  {flow.pending?.confirmedRejection && <button type="button" title="Перечитать состав и открыть исправление после доказанного отказа" data-help-id="receipt.correct" disabled={flow.busy} onClick={() => void flow.restart()}>Исправить данные после отказа</button>}
  {flow.message && <p role="status" className="store-app-message">{flow.message}</p>}
 </section>;
}
