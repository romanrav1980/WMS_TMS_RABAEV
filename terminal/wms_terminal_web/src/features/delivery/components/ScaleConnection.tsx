import { useEffect } from "react";
import { useStoreWeighing } from "../useStoreWeighing";
import type { StorePreview, StoreCredentials } from "../contracts";
const readiness = { READY: "Настроены", INACTIVE: "Отключены", CALIBRATION_EXPIRED: "Истёк срок поверки", SENDER_UNAVAILABLE: "Не назначен рабочий шлюз", RECEIPT_NOT_ELIGIBLE: "Приёмка недоступна" };
export function ScaleConnection({ preview, credentials, disabled, onCapture, onAuthError }: {
 preview: StorePreview; credentials: StoreCredentials; disabled: boolean; onCapture: (key: string) => void; onAuthError: () => void;
}) {
 const scale = useStoreWeighing(preview, credentials, onAuthError);
 useEffect(() => onCapture(scale.capture?.capture_key ?? ""), [scale.capture?.capture_key, onCapture]);
 const waiting = !scale.rejected && !!scale.pending && (!scale.fact || scale.fact.state === "REQUESTED");
 return <section className="store-app-scale" aria-label="Внешние весы">
  <h3>Весы {scale.devices.length === 1 ? scale.devices[0].device_id : "магазина"}</h3>
  {scale.devices.length > 1 && <label>Прибор<select title="Выбрать настроенные весы этого магазина" data-help-id="scale.device" disabled={disabled || waiting || scale.busy || !!scale.capture} value={scale.device} onChange={event => scale.setDevice(event.target.value)}>
   <option value="">Выберите весы</option>{scale.devices.map(device => <option key={device.device_id} value={device.device_id} disabled={device.readiness !== "READY"}>{device.device_id} · {readiness[device.readiness]}</option>)}
  </select></label>}
  {scale.devices.length === 1 && scale.devices[0].readiness !== "READY" && <p className="store-app-message" role="status">{readiness[scale.devices[0].readiness]}</p>}
  {scale.capture ? <div className="store-app-weight-value" role="status"><strong>{scale.capture.gross_weight_kg} кг</strong><span>✓ Стабильный вес</span></div>
   : <><p className="store-app-hint">{waiting ? "Запрос передан. Ожидаем измерение от весов…" : "Проверьте ноль на пустых весах, затем поставьте груз и запросите вес."}</p>
    {!scale.devices.length && <p role="status">Нет настроенных весов. Обратитесь к ответственному за оборудование.</p>}
    <div className="store-app-inline-actions"><button type="button" className="store-app-primary" title="Отправить весам через API запрос измерения именно этого грузового места" data-help-id="scale.request" disabled={disabled || scale.busy || scale.corrupt || scale.rejected || !scale.devices.some(item => item.device_id === scale.device && item.readiness === "READY") || scale.fact?.state === "STALE"} onClick={() => void scale.request()}>{waiting ? "Повторить запрос весов" : "Получить вес"}</button>
     <button type="button" title="Перечитать настройки приборов; наличие настройки не доказывает связь со шлюзом" data-help-id="scale.refresh" disabled={disabled || scale.busy} onClick={() => void scale.refreshDevices()}>Обновить</button></div></>}
  {scale.message && !scale.capture && <p role="status" className="store-app-message">{scale.message}</p>}
  {(scale.rejected || (scale.fact && ["EXPIRED", "STALE"].includes(scale.fact.state))) && <button type="button" title="Сохранить прежний запрос в истории и открыть новый после подтверждённого отказа или истечения" data-help-id="scale.correct" disabled={disabled || scale.busy} onClick={scale.newMeasurement}>Новый запрос весов</button>}
  <details><summary title="Показать прибор, точность, время измерения и повторное взвешивание">Прибор и измерение</summary>
   <p className="store-app-hint">Вес поступает через API оборудования. Настройка прибора не доказывает связь; если ответа нет, проверьте его питание и подключение к серверу.</p>
   {scale.capture && <p className="store-app-hint">{scale.capture.device_id} · {scale.capture.received_at?.replace(/\.\d+/, "")}</p>}
   {scale.devices.filter(item => item.device_id === scale.device).map(item => <p className="store-app-hint" key={item.device_id}>Предел {item.capacity_kg} кг · шаг {item.resolution_kg} кг · поверка {item.calibration_ref}</p>)}
   {scale.fact?.state === "CAPTURED" && <button type="button" title="Начать новое измерение; прежний запрос сохранится в истории" data-help-id="scale.new" disabled={disabled || scale.busy} onClick={scale.newMeasurement}>Взвесить заново</button>}
  </details>
 </section>;
}
