import { useCallback, useEffect, useState } from "react";
import { archiveDamaged, describeRefusal, newOperationId, readPending, readReceipt, savePending, sendPending } from "./metadataCommand";
import type { MetadataDomain, PendingCommand, PendingState, SendOutcome } from "./metadataCommand";
import type { CommandReceipt } from "./types";

const LOCK_UNAVAILABLE = "Браузер не поддерживает блокировку между вкладками: отправка запрещена, чтобы две вкладки не отправили команды одновременно. Откройте экран в современном браузере.";

/** Межвкладочный lock на «записать в журнал + отправить» (C-0068). localStorage сам не даёт атомарного CAS;
 *  последний барьер — operation_id и expected_version на сервере. Без navigator.locks отправка запрещена. */
async function exclusive(domain: string, work: () => Promise<void>, blocked: (text: string) => void): Promise<void> {
  const locks = (navigator as Navigator & { locks?: LockManager }).locks;
  if (!locks) { blocked(LOCK_UNAVAILABLE); return; }
  await locks.request(`retailcase.${domain}.command`, { ifAvailable: true }, async lock => {
    if (!lock) { blocked("Команда уже отправляется в другой вкладке — дождитесь её результата."); return; }
    await work();
  });
}

export type CommandMessage = { tone: "ok" | "bad" | "warn"; text: string } | null;

/** Сценарий команд метаданных для экрана: одна незавершённая команда на домен, повтор/квитанция/архив. */
export function useMetadataCommands(domain: MetadataDomain, onDone: (receipt: CommandReceipt, command: PendingCommand) => void) {
  const [pending, setPending] = useState<PendingState>(() => readPending(domain));
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<CommandMessage>(null);

  // Другая вкладка могла записать/снять команду: обновляем баннер по событию storage.
  useEffect(() => {
    const onStorage = (event: StorageEvent) => { if (event.key === null || event.key.startsWith(`retailcase.${domain}.`)) setPending(readPending(domain)); };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [domain]);

  const apply = useCallback((outcome: SendOutcome, command: PendingCommand) => {
    const label = command.label;
    setPending(readPending(domain));
    if (outcome.kind === "done") {
      setMessage({ tone: "ok", text: `${label}: сохранено, версия ${outcome.receipt.version}${outcome.receipt.replayed ? " (повтор вернул сохранённый результат)" : ""}.` });
      onDone(outcome.receipt, command);
    } else if (outcome.kind === "refused") setMessage({ tone: "bad", text: `${label}: отказ сервера. ${describeRefusal(outcome)}` });
    else setMessage({ tone: "warn", text: `${label}: ${outcome.message}. Команда сохранена — проверьте квитанцию или повторите.` });
  }, [domain, onDone]);

  const submit = useCallback(async (commandType: string, payload: Record<string, unknown>, label: string, prefix: string, endpoint?: string) => {
    await exclusive(domain, async () => {
    if (readPending(domain).kind !== "none") { setPending(readPending(domain)); setMessage({ tone: "warn", text: "Сначала завершите незавершённую команду." }); return; }
    const command = { domain, operation_id: newOperationId(prefix), command_type: commandType, payload, label, created_at: new Date().toISOString(), ...(endpoint ? { endpoint } : {}) };
    let raw: string;
    try { raw = savePending(command); } catch (error) { setMessage({ tone: "bad", text: String(error instanceof Error ? error.message : error) }); return; }
    setPending({ kind: "valid", command, raw }); setBusy(true); setMessage(null);
    try { apply(await sendPending(command, raw), command); } finally { setBusy(false); }
    }, text => setMessage({ tone: "warn", text }));
  }, [apply, domain]);

  const retry = useCallback(async () => {
    await exclusive(domain, async () => {
      const state = readPending(domain);
      if (state.kind !== "valid") return;
      setBusy(true);
      try { apply(await sendPending(state.command, state.raw), state.command); } finally { setBusy(false); }
    }, text => setMessage({ tone: "warn", text }));
  }, [apply, domain]);

  const check = useCallback(async () => {
    const state = readPending(domain);
    if (state.kind !== "valid") return;
    setBusy(true);
    try { apply(await readReceipt(state.command, state.raw), state.command); } finally { setBusy(false); }
  }, [apply, domain]);

  const archive = useCallback(() => {
    const state = readPending(domain);
    if (state.kind !== "damaged") return;
    if (!window.confirm("Перенести повреждённую запись в архив браузера? Сначала убедитесь, что изменение на сервере не нужно повторять.")) return;
    setMessage(archiveDamaged(domain, state.raw) ? { tone: "ok", text: "Запись перенесена в архив." } : { tone: "bad", text: "Архив не создан: запись изменилась или хранилище недоступно." });
    setPending(readPending(domain));
  }, [domain]);

  return { pending, busy, message, setMessage, submit, retry, check, archive, blocked: pending.kind !== "none" };
}
