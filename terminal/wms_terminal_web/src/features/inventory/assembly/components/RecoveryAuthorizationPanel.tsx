import { useState } from "react";
import { NativeHelp } from "../../../platform";
import { ASSEMBLY_ARTICLE_ID } from "../help";
import { savedAuthorization, authorizationSnapshot } from "../authorizationJournal";
import { readSaved } from "../savedCommands";
import { useReconciliation } from "../useReconciliation";
import type { AssemblyCredentials, RecoveryAuthorizeBody } from "../contracts";
const STATE_LABEL = { REQUESTED: "ожидает подтверждения контролёра", AUTHORIZED: "ожидает замера весов", COMPLETED: "сверка завершена", DISCREPANCY: "расхождение сохраняется" };
export function RecoveryAuthorizationPanel({ credentials, identity }: { credentials: AssemblyCredentials; identity: string }) {
  let saved: ReturnType<typeof savedAuthorization> = null, damaged = "";
  try { saved = savedAuthorization(credentials, identity); } catch (err) { damaged = err instanceof Error ? err.message : String(err); }
  const flow = useReconciliation(credentials, identity, authorizationSnapshot(saved));
  const [reason, setReason] = useState(""), [removed, setRemoved] = useState(false);
  const record = flow.record;
  if (record) try { saved = readSaved("recovery_authorize", { server: location.origin, actor: credentials.username, task_id: record.case_task_id }); } catch (err) { damaged = err instanceof Error ? err.message : String(err); }
  const own = record?.requester_id === credentials.username;
  const wrongTarget = saved && (saved.target_session !== record?.session_id || saved.target_reconciliation !== identity);
  const eligible = !!record && !own && (!flow.stale || !!saved) && !flow.authFailed && !flow.busy && !damaged && !wrongTarget;
  const submit = () => {
    if (!eligible || (!saved && (!removed || reason.trim().length < 8 || record.state !== "REQUESTED"))) return;
    void flow.authorize(saved ? saved.body as RecoveryAuthorizeBody : { operation_id: `ASM.AUTH.UI:${crypto.randomUUID()}`, reason: reason.trim(), unaccepted_goods_removed: true }, !!saved);
  };
  return <section className="asm-stage asm-recovery">
    <header className="asm-header"><h2>Сверка — контролёр</h2><NativeHelp articleId={ASSEMBLY_ARTICLE_ID} credentials={credentials} /></header>
    {!record && !flow.error && <p>Читаем серверную заявку…</p>}
    {flow.error && <p className="asm-err" role="alert">{flow.error} Проверьте состояние и сохранённую отправку перед новым действием.</p>}
    <button type="button" onClick={() => void flow.refresh()} disabled={flow.busy} title="Прочитать исходную сверку у сервера. GET404 не удаляет сохранённую отправку." data-help-id="assembly.recovery.controller-read">Прочитать результат</button>
    {record && <>
      <p>Задание {record.case_task_id} · оператор {record.requester_id} · {STATE_LABEL[record.state]}</p>
      {own && <p role="alert">Оператор этой заявки не может быть её контролёром. Выйдите и передайте проверку другому сотруднику с действующим допуском.</p>}
      {damaged && <p role="alert">{damaged}</p>}
      {wrongTarget && <p role="alert">Есть другая сохранённая сверка. <a href={`/assembly/?reconciliation_id=${encodeURIComponent(saved!.target_reconciliation!)}`} title="Перейти к исходной сохранённой сверке" data-help-id="assembly.recovery.original-link">Открыть исходную заявку</a></p>}
      {flow.stale && <p>Данные или допуск не подтверждены. Перечитайте заявку; сохранённую отправку можно повторить без изменений при действующем допуске.</p>}
      {record.state === "REQUESTED" && !saved && <>
        <p>Проверьте остановку сессии и удаление только непринятого товара. Принятый товар и тару не трогают; весы не обнуляют.</p>
        <label>Основание подтверждения<textarea value={reason} maxLength={500} onChange={e => setReason(e.target.value)} disabled={!eligible} title="Укажите основание проверки — от 8 до 500 символов" data-help-id="assembly.recovery.controller-reason" /></label>
        <label className="asm-consent"><input type="checkbox" checked={removed} onChange={e => setRemoved(e.target.checked)} disabled={!eligible} title="Подтверждаю фактическое удаление непринятого товара после остановки сессии" data-help-id="assembly.recovery.removed" />Непринятый товар удалён после подтверждённой остановки; принятый товар и тара сохранены.</label>
      </>}
      {(record.state === "REQUESTED" || saved) && <button type="button" onClick={submit} disabled={!eligible || (!saved && (!removed || reason.trim().length < 8))}
        title="Сохранить подтверждение текущего контролёра. Для завершения затем требуется отдельный замер шлюза; товарная проводка не выполняется." data-help-id="assembly.recovery.authorize">{saved ? "Повторить ту же отправку" : "Подтвердить и запросить замер"}</button>}
      {record.state === "AUTHORIZED" && !saved && <p>Подтверждение сохранено. Ожидаем реальный замер шлюза.</p>}
      {record.state === "COMPLETED" && <p>Сверка завершена. Старый непринятый шаг отменён без товарной проводки.</p>}
      {record.state === "DISCREPANCY" && <p>Вес не совпал с принятым состоянием. Сессия остаётся заблокированной; оператор создаёт новую заявку после разбора.</p>}
    </>}
  </section>;
}





