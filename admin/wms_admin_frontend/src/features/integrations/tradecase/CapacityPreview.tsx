import { useState } from "react";
import { listPath } from "./api";
import type { DocRow, Page } from "./api";
import { useRead } from "./useRead";
import { HelpLink, Tech, str } from "./ui";

type Capacity = { trip_version: number; planned_weight_kg: string; planned_volume_m3: string; free_weight_kg: string; free_volume_m3: string;
  box_limit_weight: number; box_limit_volume: number; box_limit_geometry: number | null; maximum_boxes: number | null; fitting_boxes: number | null;
  remaining_boxes: number | null; blocking_reason: string | null; loading_started: boolean; calculation_signature: string };

export function CapacityPreview({ wh, trip }: { wh: string; trip: string }) {
  const [sku, setSku] = useState(""), [boxes, setBoxes] = useState("60"), [path, setPath] = useState<string | null>(null), [reload, setReload] = useState(0);
  const products = useRead<Page<DocRow>>(listPath(wh, "SKU", null)), read = useRead<Capacity>(path, reload);
  const result = read.loading || read.error ? null : read.data;
  function calculate(e: React.FormEvent) { e.preventDefault(); const n = Number(boxes); if (!sku.trim() || !Number.isSafeInteger(n) || n < 1 || n > 100000) return;
    setPath(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(trip)}/capacity?` + new URLSearchParams({ sku_id: sku.trim(), requested_boxes: String(n) })); setReload(v => v + 1); }
  return <section className="tc-bind tc-capacity"><h4>Место под дополнительные короба <HelpLink anchor="capacity" /></h4>
    <p className="tc-note">Расчёт сопоставляет принятый план с массой и габаритами машины. Он не резервирует товар и не создаёт заказ добивки.</p>
    <form onSubmit={calculate}><label>Товар из заказа<input list="tc-capacity-products" value={sku} onChange={e => { setSku(e.target.value); setPath(null); }}
      maxLength={100} required title="Введите код товара из заказа; подсказка показывает товары первой страницы справочника" data-help-id="tradecase.capacity.sku" /></label>
      <datalist id="tc-capacity-products">{products.data?.items.map(p => <option key={p.document_id} value={p.document_id}>{str(p.payload.title)}</option>)}</datalist>
      <label>Запрошено коробов<input type="number" min={1} max={100000} step={1} value={boxes} onChange={e => { setBoxes(e.target.value); setPath(null); }} required
        title="Количество целых коробов для проверки вместимости; товар при расчёте не резервируется" data-help-id="tradecase.capacity.quantity" /></label>
      <button type="submit" disabled={read.loading || !sku.trim()} title="Рассчитать место по текущим заказам, упаковке и машине. Согласование и складские задания не создаются" data-help-id="tradecase.capacity.calculate">Рассчитать место</button></form>
    {read.loading && <p role="status">Считаем вместимость…</p>}{read.error && <p className="tc-err" role="alert">{read.error}</p>}
    {result && <div className="tc-capacity-result"><dl className="tc-fields">
      <dt>План рейса</dt><dd>{result.planned_weight_kg} кг · {result.planned_volume_m3} м³</dd>
      <dt>Осталось по плану</dt><dd>{result.free_weight_kg} кг · {result.free_volume_m3} м³</dd>
      <dt>Ограничение по массе / объёму / геометрии</dt><dd>{result.box_limit_weight} / {result.box_limit_volume} / {result.box_limit_geometry ?? "нет подтверждённой схемы укладки"} коробов</dd>
      {result.maximum_boxes !== null && <><dt>В пределах расчёта</dt><dd><b>{result.fitting_boxes}</b> коробов; вне предела {result.remaining_boxes}</dd></>}
    </dl>
      {result.blocking_reason && <p className="tc-msg warn">{result.loading_started ? "По рейсу началась погрузка. Добивка после начала погрузки этим расчётом не определяется." : "Для разных габаритов коробов требуется отдельная схема укладки; итоговое количество не рассчитано."}</p>}
      <p className="tc-note">Для согласования добивки отдельно проверьте укладку, свободный товар, получателя и срок доставки. Выполнение требует отдельного заказа SAP.</p><Tech value={result} /></div>}
  </section>;
}
