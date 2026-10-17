import { useWarehouseWeigh } from "./useWarehouseWeigh";
import { useShipmentBind } from "./useShipmentBind";
import { WeighProgress } from "./components/WeighProgress";
import { BindingRecovery } from "./components/ShipmentBinding";
import { useEffect, useMemo, useState } from "react";
import { LoginGate } from "./components/LoginGate";
import { CommandError } from "./components/CommandError";
import { StationSetup } from "./components/StationSetup";
import { AssemblyStage } from "./components/AssemblyStage";
import { RecoveryAuthorizationPanel } from "./components/RecoveryAuthorizationPanel";
import { TaskPicker } from "./components/TaskPicker";
import { PendingSessionRecovery } from "./components/PendingSessionRecovery";
import { useAssemblyAuth } from "./useAssemblyAuth";
import { useAssemblyContext } from "./useAssemblyContext";
import { useAssemblySession } from "./useAssemblySession";
import type { AssemblyContext, AssemblyCredentials } from "./contracts";
import "./styles.css";

function initialTaskId(): number | null {
  const raw = new URLSearchParams(location.search).get("task_id");
  const n = raw ? Number(raw) : NaN;
  return Number.isInteger(n) && n > 0 ? n : null;
}

/** One assigned CASE task owns setup→session→steps→finish; remounted per task_id so stale state never leaks across tasks. */
function TaskRuntime({ credentials, context, refreshContext, contextFresh }: { credentials: AssemblyCredentials; context: AssemblyContext; refreshContext: () => void; contextFresh: boolean }) {
  const state = useAssemblySession(credentials, context.task_id, context.active_session, refreshContext);
  const meta = useMemo(() => ({ server: location.origin, actor: credentials.username, task_id: context.task_id }), [credentials.username, context.task_id]);
  const weigh = useWarehouseWeigh(credentials, meta, refreshContext), binding = useShipmentBind(credentials, meta, refreshContext);
  useEffect(() => { if (state.session && state.session.content_version !== context.content_version) refreshContext(); }, [state.session?.content_version, context.content_version, refreshContext]);
  return state.meta ? <PendingSessionRecovery credentials={credentials} meta={state.meta} onResolved={state.adoptSession} onAbandoned={state.afterAbandonment}>
    {() => <><WeighProgress workflow={weigh} active={contextFresh && (state.session?.state === "OPEN" || ["IN_PROGRESS","PARTIAL","WAIT_REPLENISHMENT"].includes(context.task_state))} /><BindingRecovery workflow={binding} />{state.session ? <AssemblyStage context={context} credentials={credentials} state={state} contextFresh={contextFresh} weigh={weigh} binding={binding} refreshContext={refreshContext} /> :
      <><CommandError error={state.error} onRetry={state.retrySame} onReadFirst={state.readBeforeRetry} onDismiss={state.dismissError} />
      <StationSetup context={context} credentials={credentials} refreshContext={refreshContext} weigh={weigh} busy={state.busy === "open_session" || !!state.stale || binding.blocked || !contextFresh} onOpenSession={state.startSession} /></>}</>}
  </PendingSessionRecovery> : null;
}

export function AssemblyScaleApp() {
  const auth = useAssemblyAuth();
  const [taskId, setTaskId] = useState<number | null>(initialTaskId);
  const [reconciliationId] = useState(() => new URLSearchParams(location.search).get("reconciliation_id"));
  const ctx = useAssemblyContext(auth.credentials, reconciliationId ? null : taskId);

  if (!auth.credentials) return <LoginGate auth={auth} purpose={reconciliationId ? "Вход контролёра сверки" : undefined} />;
  if (reconciliationId) return <div className="asm-app"><RecoveryAuthorizationPanel key={`${auth.credentials.username}:${reconciliationId}`} credentials={auth.credentials} identity={reconciliationId} />
    <button type="button" onClick={auth.logout} title="Выйти из учётной записи контролёра" data-help-id="assembly.logout">Выйти</button>
    <a href="/assembly/" title="Вернуться к выбору назначенного задания. Потребуется вход своей учётной записью." data-help-id="assembly.recovery.back">К заданиям</a></div>;
  if (taskId == null) return <TaskPicker initial={null} onOpen={setTaskId} />;

  return <div className="asm-app">
    <button type="button" className="asm-logout" onClick={() => setTaskId(null)} title="Выбрать другое задание" data-help-id="assembly.task-id.change">← другое задание</button>
    {ctx.loading && <p className="asm-note">Загрузка задания {taskId}…</p>}
    {ctx.error && <div className="asm-err-box" role="alert"><p>{ctx.error}</p><button type="button" onClick={ctx.refresh} title="Повторить чтение задания" data-help-id="assembly.context.retry">Повторить</button></div>}
    {ctx.context && ctx.context.task_id === taskId && !ctx.loading && <TaskRuntime key={`${auth.credentials.username}:${taskId}`} credentials={auth.credentials} context={ctx.context} contextFresh={!ctx.error} refreshContext={ctx.refreshMetadata} />}
    <button type="button" className="asm-logout" onClick={auth.logout} title="Выйти из этого поста" data-help-id="assembly.logout">Выйти</button>
  </div>;
}




