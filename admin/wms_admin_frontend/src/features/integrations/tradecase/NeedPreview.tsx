import { useState } from "react";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech, Time } from "./ui";

type Need = { document_version: number; recipient_title: string; sku_title: string; snapshot_at: string; period_from: string; period_until: string;
  forecast_kind: "MOVEMENT" | "CONSUMPTION"; topup_enabled: boolean; topup_horizon_days: number | null;
  forecast_quantity: string; target_quantity: string; available_quantity: string; in_transit_quantity: string; current_trip_quantity: string; planned_other_quantity: string; received_quantity: string;
  additional_quantity: string; additional_boxes: string; age_minutes: number; expired: boolean;
  supplies: { supply_id: string; version: number; base_quantity: string; accounted_as: string }[] };
const ACCOUNT: Record<string, string> = { IN_AVAILABLE: "уже в остатке", CANCELLED: "отменена", AFTER_HORIZON: "после расчётного периода", UNCONFIRMED: "не подтверждена",
  CURRENT_TRIP: "подтверждённый план", IN_TRANSIT: "в пути", PLANNED_OTHER_TRIP: "план другого рейса", DELIVERED: "доставлено", BEFORE_HORIZON: "до расчётного периода" };
const quantity = (v: string) => Number(v).toLocaleString("ru-RU", { maximumFractionDigits: 6 });

export function NeedPreview({ wh, id }: { wh: string; id: string }) {
  const [age, setAge] = useState(""), [requested, setRequested] = useState(""), [reload, setReload] = useState(0);
  const valid = /^\d+$/.test(age) && Number(age) >= 1 && Number(age) <= 1440;
  const read = useRead<Need>(requested ? `/api/tradecase/warehouses/${encodeURIComponent(wh)}/needs/${encodeURIComponent(id)}?max_age_minutes=${requested}` : null, reload);
  const result = requested === age && !read.loading && !read.error ? read.data : null;
  return <section aria-label="Расчёт потребности получателя">
    <h4>Потребность из данных получателя <HelpLink anchor="need" /></h4>
    <label>Допустимый возраст данных, мин <input type="number" min="1" max="1440" step="1" value={age} onChange={e => setAge(e.target.value)}
      title="Введите допустимый возраст снимка для этой проверки: от 1 до 1440 минут. Значение не сохраняется как норматив площадки." data-help-id="tradecase.need.age" /></label>
    <Act help={{ id: "tradecase.need.calculate", text: "Прочитать текущую версию снимка и рассчитать дополнительную потребность. Товар не резервируется.", anchor: "need" }}
      disabled={!valid || read.loading} onClick={() => { setRequested(age); setReload(n => n + 1); }}>Рассчитать потребность</Act>
    {read.loading && <p className="tc-note">Читаем снимок и входящие поставки…</p>}
    {read.error && <p className="tc-err" role="alert">{read.error}</p>}
    {result && <>
      <p>{result.recipient_title} · {result.sku_title}</p>
      <p>Период прогноза: <Time value={result.period_from} /> — <Time value={result.period_until} />.</p>
      <p>{result.topup_enabled ? `Добивка включена на период не более ${result.topup_horizon_days} дн.` : "Добивка отключена в настройках получателя."}</p>
      {result.forecast_kind !== "MOVEMENT" && <p className="tc-msg warn">Для добивки загрузите прогноз перемещений. Прогноз потребления не разрешает добивку.</p>}
      {result.expired ? <p className="tc-msg warn" role="alert">Снимок устарел: {quantity(String(result.age_minutes))} мин. Запросите свежие данные перед выбором добивки.</p>
        : <p className="tc-note">Возраст снимка: {quantity(String(result.age_minutes))} мин.</p>}
      <dl className="tc-fields">
        <dt>{result.forecast_kind === "MOVEMENT" ? "Прогноз перемещений" : "Прогноз потребления"}</dt><dd>{quantity(result.forecast_quantity)} шт.</dd>
        {result.forecast_kind !== "MOVEMENT" && <><dt>Целевой запас</dt><dd>{quantity(result.target_quantity)} шт.</dd><dt>Доступно у получателя</dt><dd>{quantity(result.available_quantity)} шт.</dd></>}
        <dt>Подтверждено в пути</dt><dd>{quantity(result.in_transit_quantity)} шт.</dd>
        {result.forecast_kind === "MOVEMENT" && <><dt>План других рейсов</dt><dd>{quantity(result.planned_other_quantity)} шт.</dd><dt>Уже доставлено за период</dt><dd>{quantity(result.received_quantity)} шт.</dd></>}
        <dt>Основной подвоз</dt><dd>{quantity(result.current_trip_quantity)} шт.</dd><dt>Дополнительная потребность</dt><dd><b>{quantity(result.additional_quantity)} шт. / {quantity(result.additional_boxes)} кор.</b></dd>
      </dl>
      <p>Сверьте основной подвоз с планом рейса. Перед выбором добивки проверьте свободный запас отправителя, маршрут и вместимость.</p>
      {result.supplies.length > 0 && <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Поставка</th><th>Версия</th><th>Количество, шт.</th><th>Учтена</th></tr></thead>
        <tbody>{result.supplies.map(s => <tr key={s.supply_id}><td>{s.supply_id}</td><td>{s.version}</td><td>{quantity(s.base_quantity)}</td><td>{ACCOUNT[s.accounted_as] ?? "требует проверки"}</td></tr>)}</tbody></table></div>}
      <Tech value={result} label="Расчёт: версии и источники" />
    </>}
  </section>;
}
