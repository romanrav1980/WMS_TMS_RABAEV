import { useCallback } from "react";
import type { AssemblyCredentials } from "../assembly/contracts";
import { recoveryRequest, RecoveryError, resolutionPath } from "../resource-intents/api";
import { ControlJournalError, readControl, saveControl, saveProof } from "../resource-intents/controlJournal";
import { validateAbandoned, validateResolution } from "../resource-intents/contracts";
import type { RecoveryProof } from "../resource-intents/contracts";
import { validateAck } from "./contracts";
import { recoveryIntent } from "./recoveryIntent";
import { readJournal, withJournalLock, writeJournal } from "./journal";
import type { Intent, Journal } from "./contracts";
import type { CaseWorkView } from "./useCaseWork";
interface Ports {
 credentials: AssemblyCredentials | null; view: CaseWorkView; epoch: { current: number }; busy: { current: boolean };
 controller: { current: AbortController | null }; valid: (version: number) => boolean;
 publish: (version: number, patch: Partial<CaseWorkView>) => void;
 contextRead: (version: number, signal: AbortSignal) => Promise<void>;
}
export function useCaseRecovery({ credentials, view, epoch, busy, controller, valid, publish, contextRead }: Ports) {
 const run = useCallback(async (mode: "read" | "abandon", reason = ""): Promise<void> => {
  if (busy.current || !credentials || view.blocked) return;
  busy.current = true; const version = epoch.current, signal = controller.current!.signal;
  publish(version, { busy: true, error: "", context: null, sessions: null });
  try {
   await withJournalLock(async () => {
    const saved = await readJournal(), intent = saved.journal.pending;
    if (!intent) throw new Error("Исходная операция уже разрешена. Обновите задание.");
    if (intent.actor !== credentials.username || intent.server !== location.origin) throw new Error("Войдите исходным оператором на исходном сервере. Операции остаются сохранены.");
    const original = recoveryIntent(intent); let control = await readControl(original); let proof: RecoveryProof;
    if (!valid(version)) return;
    if (mode === "abandon") {
     control = control ?? await saveControl(original, reason);
     if (!valid(version)) return;
     publish(version, { control });
     // A retained terminal proof is read from the server again, never used to resend a control.
     if (control.proof) proof = validateResolution(await recoveryRequest(resolutionPath(original), credentials, signal), original);
     else {
      const data = await recoveryRequest("/abandonments", credentials, signal, control.wire);
      proof = { status: "ABANDONED", abandonment: validateAbandoned(data, original, control) };
     }
    } else {
     try {
      if (!control) throw new RecoveryError("No local control", 404);
      const data = await recoveryRequest("/abandonments/" + encodeURIComponent(control.body.operation_id), credentials, signal);
      proof = { status: "ABANDONED", abandonment: validateAbandoned(data, original, control) };
     } catch (error) {
      if (!(error instanceof RecoveryError) || error.status !== 404) throw error;
      proof = validateResolution(await recoveryRequest(resolutionPath(original), credentials, signal), original);
     }
    }
    if (!valid(version)) return;
    if (proof.status === "RECORDED") validateAck(proof.original_receipt, intent);
    await saveProof(original, proof);
    if (!valid(version)) return;
    await applyProof(intent, proof, version);
   });
   if (valid(version)) await contextRead(version, signal);
  } catch (error) { publish(version, { ...(error instanceof ControlJournalError ? { blocked: true } : {}), error: error instanceof Error ? error.message : "Результат восстановления неизвестен. Запрос сохранён." }); }
  finally { if (valid(version)) { busy.current = false; publish(version, { busy: false }); } }
 }, [credentials, view.blocked, epoch, busy, controller, valid, publish, contextRead]);
 async function applyProof(intent: Intent, proof: RecoveryProof, version: number): Promise<void> {
  const saved = await readJournal(); if (!valid(version)) return;
  if (JSON.stringify(saved.journal.pending) !== JSON.stringify(intent)) throw new Error("Исходный журнал изменился. Прочитайте серверную квитанцию повторно.");
  const next: Journal = proof.status === "RECORDED"
   ? { schema: 1, pending: null, last: { intent, ack: validateAck(proof.original_receipt, intent) } }
   : { ...saved.journal, pending: null, abandoned: { intent, proof: proof.abandonment } };
  writeJournal(next, saved.raw); publish(version, { journal: next, control: null, context: null, sessions: null, error: "" });
 }
 return { readRecovery: () => run("read"), abandon: (reason: string) => run("abandon", reason) };
}
