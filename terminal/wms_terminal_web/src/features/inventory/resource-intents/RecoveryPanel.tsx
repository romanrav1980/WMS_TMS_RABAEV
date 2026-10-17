import { useId, useState } from "react";
import type { ReactNode } from "react";
export function RecoveryPanel({ busy, own, blocked, control, read, abandon, helpSlot }: {
 busy: boolean; own: boolean; blocked: boolean; control: { operation_id: string; reason: string } | null;
 read: () => Promise<void>; abandon: (reason: string) => Promise<void>; helpSlot?: ReactNode;
}) {
 const [reason, setReason] = useState(""), [confirmed, setConfirmed] = useState(false), id = useId();
 const ready = own && !busy && !blocked;
 return <details className="cw-details"><summary title="Открыть безопасное восстановление неизвестного metadata запроса; исходное действие не сбрасывается" data-help-id="metadata-intent.recovery.open">Запрос не должен выполняться?</summary>
  {helpSlot}
  <p>Сервер может неизменно прекратить только ещё не записанный запрос. Уже записанный результат будет прочитан отдельно. Это не отмена задания и не возврат товара.</p>
  {control ? <><p>Запрос прекращения сохранён. Исходное действие больше не повторяется. При потере ответа используйте чтение или точный повтор прекращения.</p><code>{control.operation_id}</code><p>{control.reason}</p></>
   : <><label className="cw-field" htmlFor={id}>Причина прекращения<textarea id={id} value={reason} rows={2} maxLength={500} disabled={!ready}
    title="Объяснить, почему сохранённое назначение или запуск не должны исполняться; минимум 8 значимых символов" data-help-id="metadata-intent.reason" onChange={event => setReason(event.target.value)} /></label>
    <label><input type="checkbox" checked={confirmed} disabled={!ready} onChange={event => setConfirmed(event.target.checked)}
     title="Подтвердить явное прекращение исходного запроса; новое действие станет доступно только после точной серверной квитанции" data-help-id="metadata-intent.confirm" /> Прекратить именно сохранённый запрос</label></>}
  <div className="cw-actions"><button type="button" disabled={!ready} onClick={() => void read()} title="Прочитать исходную квитанцию или native подтверждение прекращения; 404 оставляет запрос заблокированным" data-help-id="metadata-intent.resolution.read">Прочитать итог восстановления</button>
   <button type="button" disabled={!ready || (!control && (!confirmed || Array.from(reason.trim()).length < 8))} onClick={() => void abandon(control?.reason ?? reason)}
    title={control ? "Повторить неизменный сохранённый запрос прекращения с прежним operation_id и original_wire" : "Сохранить отдельный запрос прекращения и отправить серверу; исходное действие остаётся заблокированным до подтверждения"}
    data-help-id="metadata-intent.abandon.submit">{control ? "Повторить прекращение" : "Запросить прекращение"}</button></div>
 </details>;
}
