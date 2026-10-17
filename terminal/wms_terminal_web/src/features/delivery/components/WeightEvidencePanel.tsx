import { useEffect, useRef, useState } from "react";
import { ScaleConnection } from "./ScaleConnection";
import { useStorePhotos } from "../useStorePhotos";
import { HelpHint } from "../help/HelpHint";
import { manualWeightHelp, normalizeManualKg, previewDelta } from "../manualWeight";
import type { WeightSource } from "../manualWeight";
import type { StoreCredentials, StorePreview } from "../contracts";

export type WeightEvidenceValue = { source: WeightSource; captureKey: string; manualKg: string | null; photoIds: string[]; actConfirmed: boolean };

/** Вес и фото. По умолчанию вес вводит пользователь (C0116); электронные весы — отдельный источник с прежним API.
 *  Переключение источника очищает только ещё не отправленный выбор: во время ожидания исхода панель отключена. */
export function WeightEvidencePanel({ preview, credentials, disabled, onEvidence, onAuthError }: {
 preview: StorePreview; credentials: StoreCredentials; disabled: boolean;
 onEvidence: (value: WeightEvidenceValue) => void; onAuthError: () => void;
}) {
 const photos = useStorePhotos(preview, credentials, onAuthError);
 const fileInput = useRef<HTMLInputElement>(null), view = useRef("FRONT");
 const [source, setSource] = useState<WeightSource>("MANUAL");
 const [capture, setCapture] = useState(""), [manualText, setManualText] = useState(""), [act, setAct] = useState(false);
 const manualKg = source === "MANUAL" ? normalizeManualKg(manualText) : null;
 const evidenceKey = photos.evidence.join(":");
 useEffect(() => { onEvidence({ source, captureKey: source === "SCALE" ? capture : "", manualKg, photoIds: photos.evidence, actConfirmed: act }); }, [source, capture, manualKg, evidenceKey, act]);
 function choose(next: WeightSource) {
  if (disabled || next === source) return;
  setSource(next); setCapture(""); setManualText(""); // прежний выбор другого источника не уходит в команду
 }
 function takePhoto(side: string) { view.current = side; fileInput.current?.click(); }
 const delta = manualKg ? previewDelta(manualKg, preview.shipping_gross_weight_kg) : null;
 return <fieldset className="store-app-weight" disabled={disabled}>
  <legend>Вес и фото <HelpHint helpId="weight.evidence" tip="Вес брутто места: вводите с весов вручную или получите от электронных весов; фото подтверждают состояние места" article="store-receiving-weight-photo" /></legend>
  <div className="store-app-weight-plan"><span>Отгружено</span><strong>{preview.shipping_gross_weight_kg} кг</strong><span>Допуск ±{preview.shipping_weight_tolerance_kg ?? "не задан"} кг</span></div>
  {!preview.shipping_weight_tolerance_kg && <p className="store-app-message" role="status">Нет подтверждённого допуска веса. Приёмка заблокирована — обратитесь в логистику.</p>}
  <div className="store-app-source" role="radiogroup" aria-label="Источник веса">
   <button type="button" role="radio" aria-checked={source === "MANUAL"} className={source === "MANUAL" ? "is-active" : ""} data-help-id="weight.source.manual"
    title="Ввести вес брутто, который показывают весы магазина. Сервер сохранит его как «введено пользователем»" onClick={() => choose("MANUAL")}>Ввести вес</button>
   <button type="button" role="radio" aria-checked={source === "SCALE"} className={source === "SCALE" ? "is-active" : ""} data-help-id="weight.source.scale"
    title="Получить вес от подключённых электронных весов через API оборудования (если весы настроены)" onClick={() => choose("SCALE")}>Электронные весы</button>
   <a className="store-app-help-link" href={manualWeightHelp(source === "MANUAL" ? "store" : "integrated")} target="_blank" rel="noopener"
    title="Открыть справку о весе в новой вкладке; введённые данные приёмки сохраняются" data-help-id="weight.help">Справка</a>
  </div>
  {source === "MANUAL" ? <section className="store-app-manual" aria-label="Вес, введённый пользователем">
   <label>Вес брутто по весам, кг
    <input inputMode="decimal" autoComplete="off" value={manualText} placeholder="например 12,450" maxLength={30}
     onChange={event => setManualText(event.target.value)} title="Вес брутто всего места вместе с тарой, как показывают весы. Десятичный разделитель — запятая или точка" data-help-id="weight.manual.value" />
   </label>
   {manualText && !manualKg && <p role="alert" className="store-app-message">Введите положительное число килограммов, например 12,450.</p>}
   {manualKg && <p className="store-app-hint" role="status">Будет передано {manualKg} кг · введено пользователем{delta ? ` · разница с отгрузкой ${delta} кг (предварительно; допуск проверит сервер)` : ""}.</p>}
  </section>
   : <ScaleConnection preview={preview} credentials={credentials} disabled={disabled} onCapture={setCapture} onAuthError={onAuthError} />}
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
  <details><summary title="Показать вариант пересчёта при весовом расхождении" data-help-id="weight.act.toggle">Если вес не сошёлся</summary><label className="store-app-check"><input type="checkbox" title="Открыть обязательный построчный пересчёт и зафиксировать приёмку по акту" data-help-id="weight.act" checked={act} disabled={disabled} onChange={event => setAct(event.target.checked)} />Принимаю по акту с пересчётом</label></details>
 </fieldset>;
}
