import { useState } from "react";
import { ScanField } from "../../../platform";
import { help } from "../help";
import type { AssemblyContext, AssemblySession, OpenStepBody } from "../contracts";

/** Opens the next step. Disabled entirely while session is blocked or a previous step is unresolved (caller gates that). */
export function NewStepForm({ context, session, busy, onStart }: { context: AssemblyContext; session: AssemblySession; busy: boolean; onStart: (body: OpenStepBody) => void }) {
  const [lineId, setLineId] = useState<number | null>(null);
  const [quantity, setQuantity] = useState("");
  const [sourceCell, setSourceCell] = useState("");
  const [product, setProduct] = useState("");
  const [container, setContainer] = useState("");
  const [consent, setConsent] = useState(false);
  const line = context.lines.find(l => l.case_line_id === lineId) ?? null;
  const qtyValid = /^[1-9][0-9]{0,8}$/.test(quantity) && !!line && Number(quantity) <= Number(line.remaining_quantity);
  const needsConsent = session.confirmation_mode === "AUTO";
  const sourceValid = !!sourceCell && sourceCell.length <= 60 && (!line?.source_cell || sourceCell === line.source_cell);
  const productValid = !!product && product.length <= 512 && (!line?.product_codes || [line.article, ...line.product_codes].includes(product));
  const canStart = line != null && line.policy_state === "CONFIGURED" && qtyValid && sourceValid && productValid && container.length <= 150 && container === session.scan_container && (!needsConsent || consent);

  const start = () => {
    if (!line || !canStart) return;
    onStart({ step_id: crypto.randomUUID(), operation_id: crypto.randomUUID(), case_line_id: line.case_line_id, quantity, scan_source_cell: sourceCell, scan_product: product, scan_container: container, expected_content_version: session.content_version, consent_to_auto: needsConsent && consent });
  };

  return <div className="asm-new-step">
    <h3>Следующая укладка</h3>
    <div className="asm-line-list" role="radiogroup" aria-label="Позиция задания">
      {context.lines.map(l => <button key={l.case_line_id} type="button" role="radio" aria-checked={l.case_line_id === lineId}
        disabled={busy || l.policy_state !== "CONFIGURED" || Number(l.remaining_quantity) <= 0}
        className={"asm-pick" + (l.case_line_id === lineId ? " selected" : "")} onClick={() => setLineId(l.case_line_id)}
        title={help.line.title} data-help-id={help.line.id}>
        <b>{l.article}</b><small>{l.name} · остаток {l.remaining_quantity} {l.base_uom}</small>
        {l.policy_state === "UNCONFIGURED" && <span className="asm-chip asm-warn">норматив массы не настроен</span>}
      </button>)}
    </div>
    {line && <>
      <label>Количество, шт
        <input disabled={busy} inputMode="numeric" value={quantity} onChange={e => setQuantity(e.target.value.replace(/\D/g, ""))}
          title={help.quantity.title} data-help-id={help.quantity.id} /></label>
      {quantity && !qtyValid && <p className="asm-note">Количество должно быть целым положительным и не превышать серверный остаток строки.</p>}
      <ScanField label="Ячейка источника" value={sourceCell} onChange={setSourceCell} disabled={busy} />
      <ScanField label="Товар" value={product} onChange={setProduct} disabled={busy} />
      <ScanField label="Сборочная тара (повторно)" value={container} onChange={setContainer} disabled={busy} />
      {container && container !== session.scan_container && <p className="asm-note">Идентификатор тары не совпадает с этой сессией.</p>}
      {sourceCell && !sourceValid && <p className="asm-note">Ячейка не совпадает с серверным источником строки.</p>}
      {product && !productValid && <p className="asm-note">Код товара не относится к выбранной позиции.</p>}
      {needsConsent && <label className="asm-consent"><input disabled={busy} type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}
        title={help.consent.title} data-help-id={help.consent.id} />
        Подтверждаю: после стабилизации веса укладка {line.article} в количестве {quantity || "…"} {line.base_uom} будет принята автоматически.</label>}
      <button type="button" disabled={!canStart || busy} onClick={start} title={help.startStep.title} data-help-id={help.startStep.id}>
        {busy ? "Открываем…" : "Начать укладку"}
      </button>
    </>}
  </div>;
}



