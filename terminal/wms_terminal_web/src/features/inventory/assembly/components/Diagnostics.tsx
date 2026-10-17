import { help } from "../help";
import type { AssemblySession, AssemblyStep } from "../contracts";

/** Device ids, calibration, policy versions and raw clocks belong here, not the primary screen (contract C-0110/AK06-D). */
export function Diagnostics({ session, step }: { session: AssemblySession; step: AssemblyStep | null }) {
  return <details className="asm-diag">
    <summary title={help.diagnostics.title} data-help-id={help.diagnostics.id}>Диагностика</summary>
    <dl>
      <dt>Сессия</dt><dd>{session.session_id} · {session.state}</dd>
      <dt>Пост</dt><dd>{session.device_id} · {session.post_cell}</dd>
      <dt>Версия содержимого</dt><dd>{session.content_version}</dd>
      <dt>Тара</dt><dd>{session.tare_capture_key} · {session.tare_weight_kg} кг</dd>
      <dt>Последний вес</dt><dd>{session.last_weight_kg ?? "нет данных"}</dd>
      <dt>Истекает</dt><dd>{session.expires_at ?? "не задано"}</dd>
      {session.block_reason && <><dt>Блокировка</dt><dd>{session.block_reason}</dd></>}
      {step && <>
        <dt>Шаг</dt><dd>{step.step_id} · операция {step.operation_id}</dd>
        <dt>До/после</dt><dd>{step.before_weight_kg ?? "—"} → {step.after_weight_kg ?? "—"} (Δ {step.delta_kg ?? "—"})</dd>
        <dt>Границы Δ</dt><dd>мин {step.min_delta_kg ?? "—"}, ожидание {step.expected_delta_min_kg ?? "—"}–{step.expected_delta_max_kg ?? "—"}</dd>
        <dt>Проведено в учёт</dt><dd>{step.stock_posted ? "да" : "нет"}</dd>
      </>}
    </dl>
  </details>;
}
