import { reasonText } from "./reasonText";

export function ReasonNotice({ reason }: { reason: string | null }) {
  return <div className="cw-warning" role="status"><p>{reasonText(reason)}</p>
    {reason && <details className="cw-details"><summary title="Показать точную причину сервера для обращения к старшему смены" data-help-id="case-work.reason.diagnostics">Причина для диагностики</summary><code>{reason}</code></details>}
  </div>;
}
