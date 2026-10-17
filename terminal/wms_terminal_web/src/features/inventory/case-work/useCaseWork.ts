import { useCaseRecovery } from "./useCaseRecovery";
import { recoveryIntent } from "./recoveryIntent";
import { readControl } from "../resource-intents/controlJournal";
import type { SavedControl } from "../resource-intents/controlJournal";
import { useCallback, useEffect, useRef, useState } from "react";
import type { AssemblyCredentials } from "../assembly/contracts";
import { validateAck, validateContext, validateSessions } from "./contracts";
import type { Context, Intent, Journal, Sessions } from "./contracts";
import { readJournal, withJournalLock, writeJournal } from "./journal";
import { request } from "./api";
import { useCaseActions } from "./useCaseActions";

export interface CaseWorkView { context: Context | null; sessions: Sessions | null; journal: Journal | null; busy: boolean; error: string; blocked: boolean; control: SavedControl | null }
const INITIAL: CaseWorkView = { context: null, sessions: null, journal: null, busy: false, error: "", blocked: true, control: null };
function message(error: unknown): string { return error instanceof Error ? error.message : "Нет подтверждённого ответа. Исходная операция сохранена."; }

export function useCaseWork(task: number | null, credentials: AssemblyCredentials | null) {
  const [view, setView] = useState<CaseWorkView>(INITIAL);
  const [refreshKey, setRefreshKey] = useState(0);
  const epoch = useRef(0), busy = useRef(false), controller = useRef<AbortController | null>(null);
  const valid = useCallback((version: number) => epoch.current === version && !controller.current?.signal.aborted, []);
  const publish = useCallback((version: number, patch: Partial<CaseWorkView>) => {
    if (valid(version)) setView(old => ({ ...old, ...patch }));
  }, [valid]);

  const contextRead = useCallback(async (version: number, signal: AbortSignal): Promise<void> => {
    if (!credentials || task === null) return;
    const context = validateContext(await request(`/api/case-pick/tasks/${task}/resource-context`, credentials, signal), task, credentials.username);
    if (!valid(version)) return;
    const sessions = validateSessions(await request(`/api/case-pick/tasks/${task}/resource-sessions`, credentials, signal), context);
    publish(version, { context, sessions });
  }, [credentials, task, publish, valid]);

  const resolve = useCallback(async (intent: Intent, version: number, signal: AbortSignal, post: boolean): Promise<void> => {
    if (!credentials || intent.server !== location.origin || intent.actor !== credentials.username) throw new Error("В журнале операция другой учётной записи или сервера. Войдите исходным оператором; запрос сохранён.");
    if (!valid(version)) return;
    if (post && await readControl(recoveryIntent(intent))) throw new Error("Сохранено прекращение исходного запроса. Повтор исходного действия заблокирован; прочитайте итог восстановления.");
    const data = await request(post ? intent.url : `/api/case-pick/resource-commands/${encodeURIComponent(intent.body.operation_id)}`, credentials, signal, post ? intent : undefined);
    if (!valid(version)) return;
    const ack = validateAck(data, intent);
    const saved = await readJournal();
    if (!valid(version)) return;
    if (!saved.journal.pending || JSON.stringify(saved.journal.pending) !== JSON.stringify(intent)) throw new Error("Журнал операции изменился. Ответ сохранённой операции нужно прочитать повторно.");
    const next: Journal = { schema: 1, pending: null, last: { intent, ack } };
    writeJournal(next, saved.raw);
    publish(version, { journal: next, control: null, context: null, sessions: null, error: "" });
  }, [credentials, publish, valid]);

  useEffect(() => {
    const version = ++epoch.current, abort = new AbortController();
    controller.current = abort; busy.current = true;
    setView({ ...INITIAL, busy: true });
    void (async () => {
      try {
        // blocked — только неисправный/нечитаемый журнал. Сбой чтения задания (сеть, 403) не должен запрещать
        // явный повтор исходной операции: её байты целы в журнале (C0113 review).
        let saved: Awaited<ReturnType<typeof readJournal>>;
        try { saved = await readJournal(); }
        catch (error) { publish(version, { error: message(error), blocked: true }); return; }
        if (!valid(version)) return;
        let control: SavedControl | null = null;
        try { if (saved.journal.pending) control = await readControl(recoveryIntent(saved.journal.pending)); }
        catch (error) { publish(version, { journal: saved.journal, error: message(error), blocked: true }); return; }
        publish(version, { journal: saved.journal, control, blocked: false });
        if (credentials && saved.journal.pending) {
          try { await withJournalLock(() => resolve(saved.journal.pending!, version, abort.signal, false)); }
          catch (error) { publish(version, { error: message(error) }); }
        }
        if (valid(version)) await contextRead(version, abort.signal);
      } catch (error) { publish(version, { error: message(error) }); }
      finally { if (valid(version)) { busy.current = false; publish(version, { busy: false }); } }
    })();
    const changed = (event: StorageEvent) => { if (event.key === null || event.key === "wms.case-work.journal.v1" || event.key?.startsWith("wms.metadata-intent-control.v1:")) setRefreshKey(key => key + 1); };
    window.addEventListener("storage", changed);
    return () => { abort.abort(); epoch.current++; busy.current = false; window.removeEventListener("storage", changed); };
  }, [credentials, task, refreshKey, contextRead, publish, resolve, valid]);

  const { retry, submit } = useCaseActions({ credentials, view, epoch, busy, controller, valid, publish, resolve, contextRead });

  const recovery = useCaseRecovery({ credentials, view, epoch, busy, controller, valid, publish, contextRead });
  return { ...view, ...recovery, submit, retry, refresh: () => setRefreshKey(key => key + 1) };
}
export type CaseWorkState = ReturnType<typeof useCaseWork>;
