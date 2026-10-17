import type { WarehouseWeighState } from "../useWarehouseWeigh";
import type { ShipmentBindState } from "../useShipmentBind";
import { useEffect, useState } from "react";
import { NativeHelp } from "../../../platform";
import { ASSEMBLY_ARTICLE_ID } from "../help";
import { CommandError } from "./CommandError";
import { RecoveryPanel } from "./RecoveryPanel";
import { Diagnostics } from "./Diagnostics";
import { FinishPanel } from "./FinishPanel";
import { NewStepForm } from "./NewStepForm";
import { StepStage } from "./StepStage";
import type { AssemblyContext, AssemblyCredentials } from "../contracts";
import type { AssemblySessionState } from "../useAssemblySession";

const STAGE = ["Подача", "Человек", "Сборочная тара"];

/** Runtime screen: compact task/operator header, a visual feed→operator→container scheme, then the large active
 *  step. Diagnostics (device ids, calibration, clocks) are collapsed, not on the primary surface. */
export function AssemblyStage({ context, credentials, state, weigh, binding, refreshContext, contextFresh }: { context: AssemblyContext; credentials: AssemblyCredentials; state: AssemblySessionState; weigh: WarehouseWeighState; binding: ShipmentBindState; refreshContext: () => void; contextFresh: boolean }) {
  const [finishing, setFinishing] = useState(false);
  useEffect(() => { if (binding.entry || weigh.entry?.body.purpose === "FINAL_GROSS") setFinishing(true); }, [binding.entry, weigh.entry]);
  useEffect(() => { if (state.session?.state === "FINALIZED") setFinishing(false); }, [state.session?.state]);
  const physicalBlocked = weigh.blocked || binding.blocked || !contextFresh;
  const { session, currentStep, unresolved, busy, error, stale, place, startStep, retrySame, readBeforeRetry, dismissError } = state;
  if (!session) return null;
  const blocked = session.state === "BLOCKED";
  const caseClosed = ["WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"].includes(context.task_state);
  const closeEligible = caseClosed || (context.lines.length > 0 && context.lines.every(line => line.status ? ["PICKED", "SHORT_PICKED", "CANCELLED"].includes(line.status) : Number(line.remaining_quantity) === 0));
  const idleSession = !physicalBlocked && session.state === "OPEN" && !blocked && !unresolved && !stale && !busy && context.content_version === session.content_version;
  const canStartNew = idleSession && ["IN_PROGRESS", "PARTIAL", "WAIT_REPLENISHMENT"].includes(context.task_state);

  return <div className="asm-stage">
    <header className="asm-header">
      <div><b>Задание {context.task_id}</b><span>{session.operator_id} · {session.post_cell}</span></div>
      <NativeHelp articleId={ASSEMBLY_ARTICLE_ID} credentials={credentials} />
    </header>
    {context.stations.find(s => s.device_id === session.device_id)?.device_mode === "TEST" && <p className="asm-chip asm-test">ТЕСТОВЫЙ ПОСТ — физическое оборудование не подтверждено</p>}
    <div className="asm-scheme" aria-hidden="true">{STAGE.map((s, i) => <span key={s} className={"asm-scheme-step" + (i === 2 && currentStep ? " active" : "")}>{s}</span>)}</div>
    {stale && <div className="asm-err-box" role="alert"><p>Данные не подтверждены: {stale.message} Действия приостановлены.</p><button type="button" onClick={() => void readBeforeRetry()} title="Проверить текущую сессию и допуск у сервера" data-help-id="assembly.refresh-stale">Проверить связь и допуск</button></div>}
    {blocked && <p className="asm-discrepancy" role="alert">Сессия заблокирована{session.block_reason ? ": " + session.block_reason : ""}.</p>}
    <CommandError error={error && error.kind !== "finish" ? error : null} onRetry={retrySame} onReadFirst={readBeforeRetry} onDismiss={dismissError} />
    {currentStep && <StepStage step={currentStep} onPlaced={place} placing={!!busy || !!stale || blocked || physicalBlocked} paused={!!busy || !!stale || blocked || physicalBlocked} held={blocked && !busy && !stale} />}
    {context.content_version !== session.content_version && <p className="asm-note">Перечитываем актуальный состав задания. Новая укладка временно недоступна.</p>}
    {!currentStep && !blocked && session.state === "OPEN" && <p className="asm-note">Укладок ещё не было в этой сессии.</p>}
    {canStartNew && !finishing && <NewStepForm context={context} session={session} busy={busy === "open_step"} onStart={startStep} />}
    {!finishing && idleSession && !closeEligible && <p className="asm-note">В задании остаются незавершённые строки. Сначала завершите отбор или штатное решение по недобору.</p>}
    {!finishing && idleSession && closeEligible && <button type="button" onClick={() => setFinishing(true)} title="Перейти к завершению укладки" data-help-id="assembly.finish-open">Завершить укладку</button>}
    {finishing && !stale && <FinishPanel context={context} weigh={weigh} binding={binding} refreshContext={refreshContext} credentials={credentials} session={session} station={context.stations.find(s => s.device_id === session.device_id)} taskState={context.task_state} closeEligible={closeEligible} contextFresh={contextFresh} sessionState={state} onClose={() => setFinishing(false)} />}
    {session.state === "FINALIZED" && <p className="asm-applied">✓ Укладка завершена. Контроль — отдельный существующий процесс.</p>}
    <RecoveryPanel session={session} step={currentStep} disabled={!!busy || !!stale || session.state === "FINALIZED"} onRequest={state.requestRecovery} />
    <Diagnostics session={session} step={currentStep} />
  </div>;
}






