import { HelpButton } from "../help/HelpButton";
import { accessHelp } from "./help";
import type { PendingState } from "./metadataCommand";
import type { CommandMessage } from "./useMetadataCommands";

/** Незавершённая команда и сообщение последнего результата. Повтор отправляет точное сохранённое тело. */
export function PendingCommandBanner({ pending, busy, message, onCheck, onRetry, onArchive, help = accessHelp }: {
  pending: PendingState; busy: boolean; message: CommandMessage; onCheck: () => void; onRetry: () => void; onArchive: () => void;
  help?: Pick<typeof accessHelp, "pendingCheck" | "pendingRetry" | "pendingArchive">;
}) {
  return <>
    {pending.kind === "valid" && <section className="aa-pending" role="region" aria-label="Незавершённая команда">
      <strong>Незавершённая команда: {pending.command.label}</strong>
      <span>Тип {pending.command.command_type} · operation_id <code>{pending.command.operation_id}</code> · создана {new Date(pending.command.created_at).toLocaleString("ru-RU")}</span>
      <span>Пока исход не подтверждён, новые изменения заблокированы, чтобы не создать противоречие.</span>
      <div className="aa-actions">
        <HelpButton help={help.pendingCheck} onClick={onCheck} unavailable={busy && "идёт запрос"}>Проверить квитанцию</HelpButton>
        <HelpButton help={help.pendingRetry} onClick={onRetry} unavailable={busy && "идёт запрос"}>Повторить ту же команду</HelpButton>
      </div>
    </section>}
    {pending.kind === "damaged" && <section className="aa-pending aa-bad" role="alert">
      <strong>Сохранённая команда повреждена.</strong>
      <span>Новые изменения заблокированы. Проверьте состояние объектов на сервере, затем уберите запись в архив.</span>
      <HelpButton help={help.pendingArchive} onClick={onArchive}>В архив</HelpButton>
    </section>}
    {message && <p className={"aa-msg aa-" + message.tone} role={message.tone === "ok" ? "status" : "alert"}>{message.text}</p>}
  </>;
}
