import { MarkedGoodsPanel } from "./MarkedGoodsPanel";
import { WeightEvidencePanel } from "./WeightEvidencePanel";
import { DiscrepancyFields } from "./DiscrepancyFields";
import { HelpHint } from "../help/HelpHint";
import type { StorePreview, StoreCredentials } from "../contracts";
import type { ReceiptForm } from "../useReceiptForm";

export function ReceiptVerification({ preview, credentials, form, disabled, storeId, onAuthError }: {
 preview: StorePreview; credentials: StoreCredentials; form: ReceiptForm; disabled: boolean; storeId: string; onAuthError: () => void;
}) {
 const mode = preview.mode, leaves = preview.snapshot.nodes.filter(node => node.kind === "STOCK");
 const article = mode === "PAPER_COUNT" ? "store-receiving-paper-count" : mode === "WEIGHT_PHOTO" ? "store-receiving-weight-photo" : "store-receiving-barcode";
 return <>
  <h2>{mode === "PAPER_COUNT" ? "Пересчитайте товар" : mode === "WEIGHT_PHOTO" ? "Взвесьте место" : "Проверьте состав"} <HelpHint helpId="delivery.mode" tip="Порядок проверки определён стратегией магазина" article={article} /></h2>
  {mode === "WEIGHT_PHOTO" && <WeightEvidencePanel preview={preview} credentials={credentials} disabled={disabled} onAuthError={onAuthError}
   onEvidence={value => { form.setWeightSource(value.source); form.setCaptureKey(value.captureKey); form.setManualKg(value.manualKg); form.setPhotoIds(value.photoIds); form.setAct(value.actConfirmed); }} />}
  {preview.requires_marked_recipient_flow && preview.marked_unit_control && <MarkedGoodsPanel control={preview.marked_unit_control}
   partialAllowed={!!preview.marked_partial_control} username={credentials.username} scopeKey={storeId + ":" + preview.load_operation_id + ":" + preview.composition_signature}
   disabled={disabled} onScans={form.setScans} onAggregates={form.setAggregates} onValidity={form.setScanValid} />}
  {mode === "PAPER_COUNT" && <label>Документ пересчёта<input title="Номер накладной или акта, по которому вы пересчитали товар" data-help-id="paper.reference" maxLength={200} disabled={disabled} value={form.paperReference} onChange={event => form.setPaperReference(event.target.value)} /></label>}
  <DiscrepancyFields leaves={leaves} rows={form.rows} onChange={form.setRows} disabled={disabled} forced={form.forceCounts}
   enabled={form.enabled || form.forceCounts} onToggle={form.setEnabled} note={form.note} onNote={form.setNote} helpArticle={article} />
  <details className="store-app-composition"><summary title="Посмотреть ожидаемые товары в этом грузовом месте">Состав · {leaves.length} строк</summary>
   <ul className="store-app-snapshot">{leaves.map(node => <li key={node.uid}>{node.article}: {node.quantity} {node.base_uom}</li>)}</ul>
  </details>
 </>;
}
