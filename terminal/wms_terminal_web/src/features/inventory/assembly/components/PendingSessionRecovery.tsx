import { useEffect, useRef, useState } from "react";
import { NativeHelp } from "../../../platform";
import { ASSEMBLY_ARTICLE_ID } from "../help";
import type { ReactNode } from "react";
import { pendingCommands } from "../savedCommands";
import type { SavedCommand } from "../savedCommands";
import { AbandonmentPanel } from "./AbandonmentPanel";
import { canAbandon, originalMatches, readAbandonment } from "../abandonment";
import type { AbandonControl } from "../abandonment";
import { retryRecoveryRequest } from "../recoveryCommands";
import { readSession, retrySaved, validSession } from "../commands";
import type { AssemblyCredentials, AssemblySession } from "../contracts";
import type { JournalMeta } from "../journal";

const LABEL = { open_session: "открытие сессии", open_step: "открытие укладки", finish: "завершение", case_close: "закрытие сборки", recovery_request: "остановка для сверки", recovery_authorize: "подтверждение контролёра" };
/** No automatic POST. GET404 never discards intent; only exact acknowledged retry resolves it. */
export function PendingSessionRecovery({ credentials, meta, onResolved, onAbandoned, children }: {
  credentials: AssemblyCredentials; meta: JournalMeta; onResolved: (session: AssemblySession) => void; onAbandoned: () => void; children: () => ReactNode;
}) {
  const [busy, setBusy] = useState(false), [note, setNote] = useState("");
  const [, journalChanged] = useState(0), [accessDenied, setAccessDenied] = useState(false);
  useEffect(() => { const changed = () => journalChanged(value => value + 1); window.addEventListener("storage", changed); return () => window.removeEventListener("storage", changed); }, []);
  const live = useRef(true);
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  let commands: SavedCommand[] = [], damaged = "", control: AbandonControl | null = null;
  try { commands = pendingCommands(meta); control = readAbandonment(meta);
    if (control && !commands.some(command => originalMatches(control!, command))) commands.push(control.original);
  } catch (err) { damaged = err instanceof Error ? err.message : String(err); }
  const act = async (command: SavedCommand, retry: boolean) => {
    if (busy) return;
    setBusy(true); setNote("");
    try {
      if (retry) {
        const result = command.kind === "recovery_request" ? await retryRecoveryRequest(credentials, meta, command) : await retrySaved(credentials, meta, command);
        if (live.current) onResolved(result);
      } else {
        const result = validSession(await readSession(credentials, command.target_session), credentials, command.target_session, meta.task_id);
        if (live.current) setNote(`Сервер: ${result.state}. Исходная команда сохранена. Для сверки точного тела повторите ту же отправку.`);
      }
    } catch (err) {
      if (live.current && [401, 403].includes((err as { status?: number }).status ?? 0)) setAccessDenied(true);
      if (live.current) setNote((err as { status?: number }).status === 404
        ? "Результат пока не виден. Исходная отправка могла ещё не завершиться. Команда сохранена."
        : err instanceof Error ? err.message : String(err));
    } finally { if (live.current) setBusy(false); }
  };
  if (!damaged && commands.length === 0 && !control) return children();
  return <div className="asm-err-box" role="alert">
    <p>{damaged || "Есть сохранённая незавершённая команда. Новые действия заблокированы до сверки исходной отправки."}</p>
    <NativeHelp articleId={ASSEMBLY_ARTICLE_ID} credentials={credentials} />
    {accessDenied && <p>Допуск изменён. Войдите заново под своей учётной записью. Сохранённые команды не удалены.</p>}
    {note && <p className="asm-note">{note}</p>}
    {commands.map(command => <div key={command.kind}>
      <p>{LABEL[command.kind]} · сессия {command.target_session}</p>
      <button type="button" disabled={busy || accessDenied || !!damaged} onClick={() => void act(command, false)} title="Прочитать исходную сессию. Чтение не удаляет команду и не создаёт новую." data-help-id="assembly.recover-read">Прочитать результат</button>
      <button type="button" disabled={busy || accessDenied || !!damaged || (!!control && !originalMatches(control, command))} onClick={() => void act(command, true)} title="Повторить сохранённое тело по исходному адресу без новых идентификаторов." data-help-id="assembly.recover-retry">Повторить ту же отправку</button>
      {!damaged && canAbandon(command) && (!control || originalMatches(control, command)) && <AbandonmentPanel credentials={credentials} meta={meta} command={command} control={control}
        busyElsewhere={busy || accessDenied} onBusy={setBusy} onDenied={() => setAccessDenied(true)} onChanged={() => journalChanged(value => value + 1)} onDone={() => { setBusy(false); journalChanged(value => value + 1); onAbandoned(); }} />}
    </div>)}
  </div>;
}







