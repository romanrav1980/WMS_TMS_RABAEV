import { useEffect } from "react";
import { useStoreReceivingFlow } from "../useStoreReceivingFlow";
import { useReceiptForm } from "../useReceiptForm";
import { ScanField } from "../../platform";
import { UnloadingStep } from "./UnloadingStep";
import { ReceiptSummary } from "./ReceiptSummary";
import { ReceiptVerification } from "./ReceiptVerification";
import { ReceiptRecovery } from "./ReceiptRecovery";
import { HelpHint } from "../help/HelpHint";
import { ArrivalPanel } from "./ArrivalPanel";
import type { StoreCredentials } from "../contracts";

const steps = ["Место", "Проверка", "Подтверждение"];
export function DeliveryDetail({ storeId, credentials, loadOperationId, onBack, onAuthError, initialScan = "" }: {
 storeId: string; credentials: StoreCredentials; loadOperationId: string; onBack: () => void; onAuthError: () => void; initialScan?: string;
}) {
 const flow = useStoreReceivingFlow(storeId, credentials, onAuthError), form = useReceiptForm(flow.preview, initialScan);
 useEffect(() => { void flow.open(loadOperationId); }, [loadOperationId]); // this mounted detail owns its request lifecycle
 if (flow.lastReceipt) return <ReceiptSummary result={flow.lastReceipt} onNext={onBack} />;
 const preview = flow.preview;
 if (!preview) return <section className="store-app-screen"><button type="button" title="Вернуться к поставкам магазина" data-help-id="delivery.back" onClick={onBack}>← Поставки</button><p role="status">{flow.message || "Открываем поставку…"}</p></section>;
 const disabled = flow.busy || !!flow.pending || flow.stalePreview || flow.corrupt || preview.already_received;
 const permitted = form.placeReady && form.evidenceReady && !disabled;
 const current = flow.pending || flow.corrupt ? 2 : form.step;
 const modeName = preview.mode === "PAPER_COUNT" ? "Пересчёт" : preview.mode === "WEIGHT_PHOTO" ? "Вес и фото" : "Сканирование";
 function submit() {
  if (!permitted) return;
  void flow.confirm({ scanPlace: form.commandScanPlace!, beforeCameras: form.beforeCameras, unloading: form.unloading,
   observations: form.enabled || form.forceCounts ? form.rows : undefined, caseNote: form.enabled || form.forceCounts ? form.note : undefined,
   scans: form.scans.length ? form.scans : undefined, aggregationScans: form.aggregates.length ? form.aggregates : undefined,
   scaleCaptureKey: preview!.mode === "WEIGHT_PHOTO" && form.weightSource === "SCALE" ? form.captureKey : undefined,
   manualWeightKg: preview!.mode === "WEIGHT_PHOTO" && form.weightSource === "MANUAL" && form.manualKg ? form.manualKg : undefined, photoIds: preview!.mode === "WEIGHT_PHOTO" ? form.photoIds : undefined,
   weightActConfirmed: preview!.mode === "WEIGHT_PHOTO" && form.act ? true : undefined, paperReference: preview!.mode === "PAPER_COUNT" ? form.paperReference.trim() : undefined });
 }
 return <section className="store-app-screen" aria-label="Приёмка поставки">
  <header className="store-app-header"><button type="button" className="store-app-quiet" title="Вернуться к поставкам, сохранив ожидающую отправленную команду" data-help-id="delivery.back" onClick={onBack}>← Поставки</button><HelpHint helpId="receipt.guide" tip="Пошаговая приёмка магазина" article="store-receiving-app" /></header>
  <div><h1 className="store-app-title">Приёмка</h1><p className="store-app-hint">{preview.store_address} · {modeName}</p><strong className="store-app-place-code">{preview.root_scan_identifier}</strong></div>
  <ArrivalPanel load={loadOperationId} store={storeId} credentials={credentials} disabled={flow.busy} onAuthError={onAuthError} />
  {preview.already_received ? <p role="status">Место уже принято. Исходный акт пока недоступен. Новая приёмка заблокирована.</p> : <>
   <nav className="store-app-stepper" aria-label="Шаги приёмки">{steps.map((name, index) => <button type="button" key={name}
    className="store-app-step" data-help-id={"receipt.step." + index} title={"Открыть шаг: " + name} aria-current={current === index ? "step" : undefined}
    disabled={disabled || index > form.step} onClick={() => form.setStep(index)}>{index + 1}. {name}</button>)}</nav>
   <div hidden={current !== 0} className="store-app-step-content">
    <h2>Считайте код места</h2><ScanField label="Идентификатор паллеты или места" value={form.scanPlace} onChange={form.setScanPlace} disabled={disabled} autoFocus />
    {form.scanPlace && !form.placeMatches && <p role="alert" className="store-app-message">Код не совпадает с этой поставкой. Проверьте этикетку или вернитесь к списку.</p>}
    <label className="store-app-check"><input type="checkbox" title="Подтвердить фактическую установку места перед камерами магазина" data-help-id="receipt.camera-position" checked={form.beforeCameras} disabled={disabled} onChange={event => form.setBeforeCameras(event.target.checked)} />Место перед камерами наблюдения</label>
    <details><summary title="Отметить время начала и фактические условия выгрузки">Выгрузка {preview.unloading ? "· начата" : "· отметить начало"}</summary><UnloadingStep preview={preview} credentials={credentials}
     scanPlace={form.commandScanPlace ?? ""} beforeCameras={form.beforeCameras} disabled={disabled} onDetails={form.setUnloading} onPending={form.setUnloadPending}
     onStarted={() => void flow.open(loadOperationId)} onAuthError={onAuthError} /></details>
   </div>
   <div hidden={current !== 1} className="store-app-step-content"><ReceiptVerification preview={preview} credentials={credentials} form={form} disabled={disabled} storeId={storeId} onAuthError={onAuthError} /></div>
   <div hidden={current !== 2} className="store-app-step-content"><h2>Проверьте итог</h2><dl><dt>Грузовое место</dt><dd>{preview.root_scan_identifier}</dd><dt>Способ приёмки</dt><dd>{modeName}</dd><dt>Строк состава</dt><dd>{form.rows.length}</dd></dl>
    {form.paperReference && <p>Документ: {form.paperReference}</p>}{preview.mode === "WEIGHT_PHOTO" && form.weightSource === "MANUAL" && form.manualKg && <p>Вес {form.manualKg} кг · введено пользователем · фото: {form.photoIds.length}</p>}{preview.mode === "WEIGHT_PHOTO" && form.weightSource === "SCALE" && form.captureKey && <p>Вес получен от электронных весов · фото: {form.photoIds.length}</p>}
    <p>{form.enabled || form.forceCounts ? "Будут переданы фактические количества и указанные расхождения." : "Подтверждаете получение полного состава по стратегии магазина."}</p></div>
   <ReceiptRecovery flow={flow} loadOperationId={loadOperationId} />
   {!flow.pending && !flow.corrupt && <footer className="store-app-footer">
    {current > 0 && <button type="button" title="Вернуться на предыдущий шаг и проверить ввод" data-help-id="receipt.previous" disabled={flow.busy} onClick={() => form.setStep(current - 1)}>Назад</button>}
    {current < 2 ? <button type="button" className="store-app-primary" title="Перейти к следующему шагу после обязательной проверки" data-help-id="receipt.next" disabled={disabled || (current === 0 ? !form.placeReady : !form.evidenceReady)} onClick={() => form.setStep(current + 1)}>Продолжить</button>
     : <button type="button" className="store-app-primary" title="Сохранить команду и отправить фактическую приёмку на сервер" data-help-id="receipt.confirm" disabled={!permitted} onClick={submit}>Подтвердить приёмку</button>}
   </footer>}
  </>}
 </section>;
}
