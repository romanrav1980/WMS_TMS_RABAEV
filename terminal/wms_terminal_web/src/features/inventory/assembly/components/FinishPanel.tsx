import { useEffect, useRef, useState } from "react";
import { ScanField } from "../../../platform";
import { rawApiGet } from "../api";
import { CommandError } from "./CommandError";
import { ShipmentBinding } from "./ShipmentBinding";
import { help } from "../help";
import { extractFinalCandidates } from "../finalCandidates";
import { terminalWeigh } from "../physicalContracts";
import type { AssemblyContext, AssemblyCredentials, AssemblySession, AssemblyStation, FinalCaptureCandidate } from "../contracts";
import type { AssemblySessionState } from "../useAssemblySession";
import type { WarehouseWeighState } from "../useWarehouseWeigh";
import type { ShipmentBindState } from "../useShipmentBind";
type Props = { contextFresh: boolean; context: AssemblyContext; credentials: AssemblyCredentials; session: AssemblySession; station: AssemblyStation | undefined; taskState: string; closeEligible: boolean; sessionState: AssemblySessionState; weigh: WarehouseWeighState; binding: ShipmentBindState; refreshContext: () => void; onClose: () => void };
export function FinishPanel({ context, credentials, session, station, taskState, closeEligible, sessionState, weigh, binding, refreshContext, onClose, contextFresh }: Props) {
  const [candidates, setCandidates] = useState<FinalCaptureCandidate[] | null>(null), [loadError, setLoadError] = useState("");
  const epoch = useRef(0), [picked, setPicked] = useState<string | null>(null), [container, setContainer] = useState("");
  const [, tick] = useState(0);
  const load = () => {
    const attempt = ++epoch.current; setPicked(null); setCandidates(null); setLoadError("");
    rawApiGet<unknown>(`/api/inventory/warehouse-scales/final-captures?task=${session.task_id}`, credentials)
      .then(data => { if (epoch.current === attempt) setCandidates(extractFinalCandidates(data, session, station, context)); })
      .catch(err => { if (epoch.current === attempt) setLoadError(err instanceof Error ? err.message : String(err)); });
  };
  useEffect(() => { load(); return () => { epoch.current += 1; }; }, [session.session_id, session.content_version, credentials, station, context.final_composition_signature, weigh.state?.capture_key]);
  useEffect(() => { const timer = setInterval(() => tick(v => v + 1), 1000); return () => clearInterval(timer); }, []);
  const caseClosed = ["WAIT_CONTROL", "CONTROL_IN_PROGRESS", "CONTROLLED", "READY_TO_SHIP"].includes(taskState);
  const bound = context.shipment_binding_state === "BOUND" && context.final_signature_domain === "ASM_FINAL" && context.final_signature_version === 3 && !!context.final_composition_signature;
  const current = extractFinalCandidates(candidates, session, station, context), chosen = current.some(c => c.capture_key === picked) ? picked : null;
  const canRequest = !weigh.entry || !!weigh.state && terminalWeigh(weigh.state);
  const blocked = !contextFresh || context.content_version !== session.content_version || !!sessionState.busy || !!sessionState.stale || sessionState.unresolved || binding.blocked;
  const requestFinal = () => { if (!station || !bound || container !== session.scan_container) return;
    weigh.start({ request_id: `ASM.FINAL:${crypto.randomUUID()}`, device_id: session.device_id, purpose: "FINAL_GROSS", case_task_id: session.task_id,
      expected_content_version: session.content_version, scan_container: container, zero_progress_required: true, tare_capture_key: session.tare_capture_key, expected_composition_signature: context.final_composition_signature! });
  };
  return <section className="asm-finish-panel" role="dialog" aria-label="Завершение укладки">
    <h2>Завершение укладки</h2>
    {!caseClosed && <><p className="asm-note">1. Закройте сборку. Сервер проверит строки и физический состав.</p><button type="button" disabled={!closeEligible || blocked || weigh.blocked} onClick={sessionState.closeCase}
      title="Штатно закрыть текущую сборку после проверки строк и физического состава. Исходная команда сохраняется для точного повтора." data-help-id="assembly.case-close-submit">Закрыть сборку</button></>}
    {caseClosed && <><p className="asm-note">Сборка закрыта сервером. Привяжите подготовленную отгрузку и получите отдельный финальный вес.</p><ScanField label="Идентификатор паллеты / полной сборочной тары" value={container} onChange={setContainer} />
      {container && container !== session.scan_container && <p className="asm-err">Скан не совпадает с тарой текущей сессии.</p>}
      <ShipmentBinding context={context} container={container} workflow={binding} disabled={blocked || weigh.blocked} />
      {!bound && context.shipment_binding_state === "BOUND" && <p className="asm-note">Отгрузка привязана. Перечитайте состав; текущая ASM identity ещё не подтверждена.</p>}
      <button type="button" disabled={blocked || !bound || !canRequest || weigh.busy || weigh.denied || (!!weigh.error && !weigh.entry) || container !== session.scan_container} onClick={requestFinal}
        title="Сохранить отдельный запрос FINAL_GROSS для текущего состава и той же измеренной тары. Освободите платформу, затем дождитесь подтверждённого нуля." data-help-id="assembly.final-request">Взвесить полную тару</button></>}
    <button type="button" onClick={() => { refreshContext(); load(); }} title="Перечитать текущее задание, привязку и финальные замеры. Запрос к весам не создаётся." data-help-id="assembly.finish-reload">Обновить состав и замеры</button>
    {loadError && <p className="asm-err" role="alert">{loadError}</p>}
    {caseClosed && candidates != null && current.length === 0 && <p className="asm-note">Нужен отдельный свежий финальный замер текущей ASM сборки. Вес последней укладки и отгрузочный QC не заменяют его.</p>}
    <div className="asm-pick-list" role="radiogroup" aria-label="Финальный замер">{current.map(c => <button key={c.capture_key} type="button" role="radio" aria-checked={picked === c.capture_key}
      className={"asm-pick" + (picked === c.capture_key ? " selected" : "")} onClick={() => setPicked(c.capture_key)} title={help.finishPick.title} data-help-id={help.finishPick.id}><b>{c.weight_kg} кг</b><small>Финальный вес этой сборки</small></button>)}</div>
    <CommandError error={sessionState.error?.kind === "finish" ? sessionState.error : null} onRetry={sessionState.retrySame} onReadFirst={sessionState.readBeforeRetry} onDismiss={sessionState.dismissError} />
    <div className="asm-finish-actions"><button type="button" disabled={!caseClosed || !chosen || blocked || weigh.blocked || !!loadError} onClick={() => chosen && sessionState.finish({ final_capture_key: chosen })}
      title={help.finishConfirm.title} data-help-id={help.finishConfirm.id}>{sessionState.busy === "finish" ? "Завершаем…" : "Завершить укладку"}</button>
      <button type="button" onClick={onClose} title="Вернуться к сборке. Сохранённые запросы весов и привязки остаются для сверки." data-help-id="assembly.finish-cancel">Назад</button></div>
  </section>;
}


