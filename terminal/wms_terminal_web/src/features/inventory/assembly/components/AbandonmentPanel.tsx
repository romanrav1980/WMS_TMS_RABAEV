import { useEffect, useRef, useState } from "react";
import { createAbandonment, resolveAbandonment } from "../abandonment";
import type { AbandonControl, AbandonableCommand } from "../abandonment";
import type { AssemblyCredentials } from "../contracts";
import type { JournalMeta } from "../journal";

export function AbandonmentPanel({ credentials, meta, command, control, busyElsewhere, onDone, onChanged, onBusy, onDenied }: {
  credentials: AssemblyCredentials; meta: JournalMeta; command: AbandonableCommand;
  control: AbandonControl | null; busyElsewhere: boolean; onDone: () => void; onChanged: () => void; onBusy: (busy: boolean) => void; onDenied: () => void;
}) {
  const [reason, setReason] = useState(""), [busy, setBusy] = useState(false), [note, setNote] = useState("");
  const live = useRef(true);
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  const act = async (readOnly: boolean) => {
    if (busy || busyElsewhere) return;
    setBusy(true); onBusy(true); setNote("");
    try {
      await resolveAbandonment(credentials, meta, control ?? createAbandonment(command, reason), readOnly);
      if (live.current) onDone();
    } catch (err) {
      if (live.current && [401, 403].includes((err as { status?: number }).status ?? 0)) onDenied();
      if (live.current) setNote((err as { status?: number }).status === 404
        ? "Отмена пока не видна. Исходная команда и запрос отмены сохранены; автоматической отправки нет."
        : (err as { status?: number }).status === 409
          ? "Сервер не разрешил отмену. Если сессия или шаг уже созданы, прочитайте результат и повторите исходную команду для сверки; при расхождении используйте штатную сверку весов. Обе записи сохранены."
          : err instanceof Error ? err.message : String(err));
    } finally {
      if (live.current) { setBusy(false); onBusy(false); onChanged(); }
    }
  };
  return <section className="asm-recovery">
    <h3>Отменить неприменённую попытку</h3>
    <p>Сервер проверит, что сессия или шаг ещё не созданы, и запретит позднее выполнение исходного запроса. Созданная укладка этим действием не отменяется.</p>
    {control ? <p>Запрос отмены сохранён. Повтор сохраняет его исходные идентификаторы, причину и тело.</p> :
      <label>Причина отмены<textarea title="Укажите причину запрета позднего исполнения ещё не созданной попытки; созданный товарный факт не отменяется" value={reason} minLength={8} maxLength={500} disabled={busy || busyElsewhere} onChange={event => setReason(event.target.value)} data-help-id="assembly.abandon.reason" /></label>}
    {note && <p role="status">{note}</p>}
    {control && <button type="button" disabled={busy || busyElsewhere} onClick={() => void act(true)} title="Прочитать сохранённый результат отмены. Только совпадающий ABANDONED разрешает убрать исходный журнал." data-help-id="assembly.abandon.read">Прочитать отмену</button>}
    <button type="button" disabled={busy || busyElsewhere || (!control && reason.trim().length < 8)} onClick={() => void act(false)} title="Явно запросить native запрет позднего исполнения только ещё не созданной сессии или укладки. Товар не отменяется." data-help-id="assembly.abandon.submit">{control ? "Повторить ту же отмену" : "Запросить отмену попытки"}</button>
  </section>;
}



