import type { WarehouseWeighState } from "../useWarehouseWeigh";
export function WeighProgress({ workflow, active }: { workflow: WarehouseWeighState; active: boolean }) {
  const { entry, state, error, busy, denied, loadAllowed, remainingSeconds } = workflow;
  if (!entry && !state && !error) return null;
  const purpose = entry?.body.purpose ?? state?.purpose;
  const waitingZero = active && !error && !denied && state?.current_context === "CURRENT" && state.measurement_stage === "WAITING_ZERO" && ["REQUESTED","CLAIMED"].includes(state.state);
  return <section className="asm-weigh-card" aria-label="Запрос к весам" aria-live="polite">
    <h3>{purpose === "FINAL_GROSS" ? "Финальный вес" : "Вес пустой тары"}</h3>
    {loadAllowed && active ? <p className="asm-weigh-go">Ноль подтверждён. {purpose === "FINAL_GROSS" ? "Поставьте полную тару" : "Поставьте пустую тару"} на платформу и не касайтесь её. Окно: {remainingSeconds} с.</p>
      : state?.state === "CAPTURED" ? <p className="asm-applied">Замер получен сервером.</p>
      : waitingZero ? <p className="asm-note">Освободите платформу и дождитесь подтверждённого нуля. Пока не устанавливайте {purpose === "FINAL_GROSS" ? "полную тару" : "пустую тару"}.</p>
      : <p className="asm-note">Остановитесь: текущее окно загрузки не подтверждено. Перечитайте результат. Прошлое подтверждение нуля не разрешает ставить груз.</p>}
    {state && ["EXPIRED","STALE"].includes(state.state) && <p className="asm-note">Запрос больше не действует. Новый запрос создаётся отдельным действием.</p>}
    {error && <p className="asm-err" role="alert">{error}</p>}
    {denied && <p>Допуск изменён. Войдите заново; исходный запрос сохранён.</p>}
    {entry && <div className="asm-finish-actions"><button type="button" disabled={busy || denied} onClick={workflow.refresh} title="Прочитать исходный запрос. Чтение не отправляет новый запрос и не удаляет неизвестный результат." data-help-id="assembly.weigh-read">Проверить результат</button>
      <button type="button" disabled={busy || denied} onClick={workflow.retry} title="Повторить только сохранённое тело с прежним request_id. Новое измерение под другим ID не создаётся." data-help-id="assembly.weigh-retry">Повторить ту же отправку</button></div>}
  </section>;
}
