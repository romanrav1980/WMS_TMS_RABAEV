import { help } from "../help";

type Err = { message: string; confirmed: boolean; uncertain: boolean } | null;

/** Uncertain (network/503) errors offer "read first" before any retry — never presented as success or failure. */
export function CommandError({ error, onRetry, onReadFirst, onDismiss }: { error: Err; onRetry: () => void; onReadFirst: () => void; onDismiss: () => void }) {
  if (!error) return null;
  return <div className="asm-err-box" role="alert">
    <p>{error.uncertain ? "Восстановление связи. " : ""}{error.message}</p>
    <div className="asm-err-actions">
      {error.uncertain && <button type="button" onClick={onReadFirst} title={help.readFirst.title} data-help-id={help.readFirst.id}>Прочитать результат</button>}
      <button type="button" onClick={onRetry} title={help.retry.title} data-help-id={help.retry.id}>Повторить то же самое</button>
      <button type="button" onClick={onDismiss} title={help.dismiss.title} data-help-id={help.dismiss.id}>Скрыть</button>
    </div>
  </div>;
}
