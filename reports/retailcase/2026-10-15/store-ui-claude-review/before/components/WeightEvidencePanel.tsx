import { useEffect, useRef, useState } from "react";
import { ScaleConnection } from "./ScaleConnection";
import { useStorePhotos } from "../useStorePhotos";
import { HelpHint } from "../help/HelpHint";
import type { StoreCredentials, StorePreview } from "../contracts";

export function WeightEvidencePanel({ preview, credentials, disabled, onEvidence, onAuthError }: {
 preview: StorePreview; credentials: StoreCredentials; disabled: boolean;
 onEvidence: (captureKey: string, photoIds: string[], actConfirmed: boolean) => void; onAuthError: () => void;
}) {
 const photos = useStorePhotos(preview, credentials, onAuthError);
 const fileInput = useRef<HTMLInputElement>(null), view = useRef("FRONT");
 const [capture, setCapture] = useState(""), [act, setAct] = useState(false);
 const evidenceKey = photos.evidence.join(":");
 useEffect(() => { onEvidence(capture, photos.evidence, act); }, [capture, evidenceKey, act]);
 function takePhoto(side: string) { view.current = side; fileInput.current?.click(); }
 return <fieldset className="store-app-weight" disabled={disabled}>
  <legend>Вес и фото <HelpHint helpId="weight.evidence" tip="Вес приходит от прибора через API; фото подтверждают состояние места" article="store-receiving-weight-photo" /></legend>
  <div className="store-app-weight-plan"><span>Отгружено</span><strong>{preview.shipping_gross_weight_kg} кг</strong><span>Допуск ±{preview.shipping_weight_tolerance_kg ?? "не задан"} кг</span></div>
  {!preview.shipping_weight_tolerance_kg && <p className="store-app-message" role="status">Нет подтверждённого допуска веса. Приёмка заблокирована — обратитесь в логистику.</p>}
  <ScaleConnection preview={preview} credentials={credentials} disabled={disabled} onCapture={setCapture} onAuthError={onAuthError} />
  <section aria-label="Фотографии грузового места"><h3>Фото с трёх сторон <span className="store-app-hint">{photos.evidence.length}/3</span></h3>
   <div className="store-app-photo-grid">{photos.visible.map(side => <button type="button" key={side.code} className={side.photo ? "store-app-photo is-complete" : "store-app-photo"}
    title={"Сфотографировать место: " + side.label.toLowerCase() + "; файл отправится в архив"} data-help-id={"photo." + side.code.toLowerCase()} disabled={disabled || photos.busy} onClick={() => takePhoto(side.code)}>
    <span aria-hidden="true">{side.photo ? "✓" : "＋"}</span>{side.label}<small>{side.photo ? "Сохранено · переснять" : "Сделать фото"}</small></button>)}</div>
   <input type="file" ref={fileInput} hidden accept="image/jpeg,image/png" capture="environment" aria-label="Фото грузового места" onChange={event => { const file = event.target.files?.[0]; if (file) void photos.upload(file, view.current); event.target.value = ""; }} />
   {photos.busy && <p role="status">Сохраняем фотографию…</p>}
   {photos.message && <p role="status" className="store-app-hint">{photos.message}</p>}
   {photos.retry && <button type="button" title="Повторно передать тот же файл и ракурс после потери связи" data-help-id="photo.retry" disabled={photos.busy || disabled} onClick={() => void photos.upload(photos.retry!.file, photos.retry!.view)}>Повторить отправку фото</button>}
   <button type="button" className="store-app-quiet" title="Перечитать фото, уже сохранённые сервером для этого места" data-help-id="photo.refresh" disabled={photos.busy || disabled} onClick={() => void photos.refresh()}>Обновить фото</button>
  </section>
  <details><summary title="Показать вариант пересчёта при весовом расхождении">Если вес не сошёлся</summary><label className="store-app-check"><input type="checkbox" title="Открыть обязательный построчный пересчёт и зафиксировать приёмку по акту" data-help-id="weight.act" checked={act} disabled={disabled} onChange={event => setAct(event.target.checked)} />Принимаю по акту с пересчётом</label></details>
 </fieldset>;
}
