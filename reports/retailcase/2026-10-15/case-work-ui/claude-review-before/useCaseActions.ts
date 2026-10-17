import { useCallback } from "react";
import type { AssemblyCredentials } from "../assembly/contracts";
import { canonical, sha256 } from "./contracts";
import type { Command, Intent, Journal, Session } from "./contracts";
import { readJournal, withJournalLock, writeJournal } from "./journal";
import { CaseWorkError } from "./api";
import type { CaseWorkView } from "./useCaseWork";

interface ActionPorts {
  credentials: AssemblyCredentials | null; view: CaseWorkView;
  epoch: { current: number }; busy: { current: boolean }; controller: { current: AbortController | null };
  valid: (version: number) => boolean; publish: (version: number, patch: Partial<CaseWorkView>) => void;
  resolve: (intent: Intent, version: number, signal: AbortSignal, post: boolean) => Promise<void>;
  contextRead: (version: number, signal: AbortSignal) => Promise<void>;
}
function message(error: unknown): string { return error instanceof Error ? error.message : "Нет подтверждённого ответа. Исходная операция сохранена."; }
export function useCaseActions({ credentials, view, epoch, busy, controller, valid, publish, resolve, contextRead }: ActionPorts) {
  const retry = useCallback(async (): Promise<void> => {
    if (busy.current || !credentials || view.blocked) return;
    busy.current = true; const version = epoch.current, signal = controller.current!.signal;
    publish(version, { busy: true, error: "", context: null, sessions: null });
    try {
      await withJournalLock(async () => {
        const saved = await readJournal();
        if (!saved.journal.pending) throw new Error("Исходная операция уже разрешена. Обновите задание.");
        try { await resolve(saved.journal.pending, version, signal, false); }
        catch (error) {
          if (!(error instanceof CaseWorkError) || error.status !== 404) throw error;
          if (valid(version)) await resolve(saved.journal.pending, version, signal, true);
        }
      });
      if (valid(version)) await contextRead(version, signal);
    } catch (error) { publish(version, { error: message(error) }); }
    finally { if (valid(version)) { busy.current = false; publish(version, { busy: false }); } }
  }, [credentials, view.blocked, publish, resolve, valid, contextRead]);

  const submit = useCallback(async (session: Session, reason: string): Promise<void> => {
    if (busy.current || !credentials || !view.context || !view.sessions || !view.journal || view.blocked || view.journal.pending) return;
    const context = view.context;
    if (!view.sessions.items.some(row => row.resource_session_id === session.resource_session_id && row.ready)
      || !["NEW", "ASSIGNED"].includes(context.status || "") || Array.from(reason.trim()).length < 8 || Array.from(reason).length > 500) return;
    busy.current = true; const version = epoch.current, signal = controller.current!.signal;
    publish(version, { busy: true, error: "" });
    try {
      await withJournalLock(async () => {
        const saved = await readJournal();
        if (!valid(version)) return;
        if (saved.journal.pending) throw new Error("Сначала прочитайте результат ранее сохранённой операции.");
        const body: Command = { operation_id: crypto.randomUUID(), action: context.status === "NEW" ? "CLAIM" : "START",
          expected_assignment_version: context.assignment_version, resource_session_id: session.resource_session_id,
          resource_id: session.resource_id, equipment_id: session.equipment_id, reason };
        const wire = canonical(body), hash = await sha256(wire);
        if (!valid(version)) return;
        const intent: Intent = { actor: credentials.username, task_id: context.task_id, server: location.origin,
          url: `/api/case-pick/tasks/${context.task_id}/resource-commands`, wire, request_sha256: hash, body, created_at: new Date().toISOString() };
        const journal: Journal = { ...saved.journal, pending: intent };
        try { writeJournal(journal, saved.raw); }
        catch (error) { publish(version, { blocked: true }); throw error; }
        publish(version, { journal, context: null, sessions: null });
        await resolve(intent, version, signal, true);
      });
      if (valid(version)) await contextRead(version, signal);
    } catch (error) { publish(version, { error: message(error) }); }
    finally { if (valid(version)) { busy.current = false; publish(version, { busy: false }); } }
  }, [credentials, view, valid, publish, resolve, contextRead]);

  return { retry, submit };
}
