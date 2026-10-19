import { tcHelp } from "./api";
import type { DocCard, Kind, MsgCard, Payload } from "./api";
import type { Names } from "./Lists";
import { KIND_NAME, resultChip } from "./Lists";
import { Act, BUYOUT, HelpLink, OSG, ORDER_KIND, Tech, Time, UOM, str, yes } from "./ui";

const arr = (v: unknown) => (Array.isArray(v) ? v : []) as Payload[];
const named = (names: Names, kind: string, id: unknown) => { const v = str(id); const t = names.get(kind + ":" + v); return t ? `${t} (${v})` : v; };
const Row = ({ k, v }: { k: string; v: React.ReactNode }) => <><dt>{k}</dt><dd>{v}</dd></>;
type Open = (kind: Kind, id: string) => void;

/** Карточка документа. Принятое основание ≠ физическое исполнение: сборка, выкуп и погрузка здесь не показываются. */
export function DocumentView({ card, names, onOpen, bind }: { card: DocCard; names: Names; onOpen: Open; bind?: React.ReactNode }) {
  const p = card.payload;
  return <>
    <p className="tc-note">Основание принято, версия {card.document_version}. {card.entity_type === "NEED" ? "Сверьте получателя, товар и период." : card.entity_type === "ORDER" || card.entity_type === "TRIP" ? "Проверьте строки и плановую дату." : "Сверьте данные документа."}{p.cancelled === true ? " Документ отменён источником." : ""}</p>
    <dl className="tc-fields">{fields(card.entity_type, p, names)}</dl>
    {card.entity_type === "ORDER" && <OrderLines lines={arr(p.lines)} names={names} />}
    {card.entity_type === "TRIP" && <TripOrders orders={arr(p.orders)} onOpen={onOpen} />}
    {bind}
    <Tech value={{ warehouse_id: card.warehouse_id, source_id: card.source_id, entity_type: card.entity_type, document_version: card.document_version, payload: p }} />
  </>;
}

function fields(kind: Kind, p: Payload, names: Names) {
  switch (kind) {
    case "ORDER": return <><Row k="Получатель" v={named(names, "RECIPIENT", p.recipient_id)} /><Row k="Вид заказа" v={ORDER_KIND[str(p.order_kind)] ?? str(p.order_kind)} />
      <Row k="Отгрузка (план)" v={<Time value={p.planned_ship_at} />} />{p.parent_trip_id ? <Row k="Основной рейс" v={str(p.parent_trip_id)} /> : null}</>;
    case "TRIP": return <><Row k="Машина" v={str(p.vehicle_id)} /><Row k="Источник плана" v={str(p.planning_source)} /><Row k="Выезд (план)" v={<Time value={p.planned_departure_at} />} />
      <Row k="Вместимость" v={`${str(p.capacity_kg)} кг · ${str(p.capacity_m3)} м³`} /><Row k="Маршрут" v="точки маршрута в этой версии не передаются" /></>;
    case "RECIPIENT": return <><Row k="Название" v={str(p.title)} /><Row k="Собственник после выкупа" v={named(names, "OWNER", p.target_owner_id)} />
      <Row k="Допустимые собственники-источники" v={arr(p.permitted_source_owners).map(o => named(names, "OWNER", o)).join(", ") || "—"} />
      <Row k="Момент выкупа" v={BUYOUT[str(p.buyout_mode)] ?? str(p.buyout_mode)} /><Row k="ОСГ" v={`${OSG[str(p.osg_basis)] ?? str(p.osg_basis)}, не меньше ${str(p.min_osg_days)} дн.`} />
      <Row k="Срок доставки, дн." v={str(p.lead_time_days)} /><Row k="Частичный отбор / отгрузка / вскрытие короба" v={`${yes(p.allow_partial_pick)} / ${yes(p.allow_partial_ship)} / ${yes(p.allow_broken_box)}`} />
      <Row k="Активен" v={yes(p.active)} /></>;
    case "NEED": return <><Row k="Получатель" v={named(names, "RECIPIENT", p.recipient_id)} /><Row k="Товар" v={named(names, "SKU", p.sku_id)} /><Row k="Снимок на" v={<Time value={p.snapshot_at} />} /><Row k="Период" v={<><Time value={p.period_from} /> — <Time value={p.period_until} /></>} /></>;
    case "SKU": return <><Row k="Название" v={str(p.title)} /><Row k="Базовая единица" v={UOM[str(p.base_uom)] ?? str(p.base_uom)} /><Row k="В коробе, шт." v={str(p.units_per_box)} />
      <Row k="Разрешённые МРЦ" v={arr(p.permitted_mrc).join(", ") || "—"} /><Row k="Активен" v={yes(p.active)} /></>;
    case "SUPPLY": return <><Row k="Идентификатор паллеты" v={str(p.pallet_identifier)} /><Row k="Товар" v={named(names, "SKU", p.sku_id)} />
      <Row k="Собственник" v={named(names, "OWNER", p.owner_id)} /><Row k="МРЦ" v={str(p.mrc)} /><Row k="Партия поставщика" v={str(p.supplier_batch)} />
      <Row k="Срок годности" v={str(p.expiry_date)} /><Row k="Заказ SAP / строка" v={`${str(p.sap_order_id)} / ${str(p.sap_line_id)}`} />
      <Row k="Состав" v={`${arr(p.codes).length} кодов маркировки (сами коды — в технических сведениях)`} /></>;
    default: return <><Row k="Название" v={str(p.title)} /><Row k="Активен" v={yes(p.active)} /></>;
  }
}

function OrderLines({ lines, names }: { lines: Payload[]; names: Names }) {
  return <><h4>Строки заказа <HelpLink anchor="order" label="Что проверить" /></h4><div className="tc-scroll"><table className="tc-table">
    <thead><tr><th>Строка</th><th>Товар</th><th>Собственник → получатель</th><th>МРЦ</th><th>Количество</th><th>Мин. ОСГ, дн.</th></tr></thead>
    <tbody>{lines.map(l => <tr key={str(l.line_id)}><td>{str(l.line_id)}</td><td>{named(names, "SKU", l.sku_id)}</td>
      <td>{named(names, "OWNER", l.source_owner_id)} → {named(names, "OWNER", l.target_owner_id)}</td><td>{str(l.mrc)}</td>
      <td>{str(l.quantity)} {UOM[str(l.uom)] ?? str(l.uom)}</td><td>{str(l.min_osg_days)}</td></tr>)}</tbody></table></div></>;
}

function TripOrders({ orders, onOpen }: { orders: Payload[]; onOpen: Open }) {
  return <><h4>Состав рейса по основаниям</h4><ul className="tc-list">{orders.map(o => <li key={str(o.order_id) + ":" + str(o.line_id)}>
    Заказ <b>{str(o.order_id)}</b>, строка {str(o.line_id)}: {str(o.quantity)} <Act help={tcHelp.related} onClick={() => onOpen("ORDER", str(o.order_id))}>Открыть заказ</Act></li>)}</ul></>;
}

const REASONS: Record<string, string> = {
  STALE_VERSION: "пришла устаревшая версия документа", VERSION_CONFLICT: "эта версия уже принята с другим содержимым",
  VERSION_CONTENT_CONFLICT: "эта версия уже принята с другим содержимым", EVENT_CONTENT_CONFLICT: "сообщение с тем же номером уже получено с другим содержимым",
  CANCELLED_DOCUMENT_REQUIRES_NEW_ID: "отменённый документ не изменяется — нужен новый номер документа",
  ORDER_QUANTITY_ALREADY_ASSIGNED: "количество строки заказа уже распределено в рейс", ORDER_LINE_MISSING: "в рейсе указана строка заказа, которой нет",
  ORDER_ASSIGNED_NEEDS_CHANGE: "строка уже назначена в рейс — изменение оформляется через изменение рейса",
  ASSIGNED_LINE_REMOVAL_REQUIRES_CHANGE: "строка уже назначена в рейс — удаление оформляется через изменение рейса",
  FIRST_SCAN_REQUIRES_REVERSE: "по заказу уже начата работа на складе — нужны обратные движения", MRC_NOT_PERMITTED: "МРЦ не разрешена для товара",
  OSG_BELOW_RECIPIENT: "минимальный остаточный срок годности ниже требования получателя", SOURCE_OWNER_NOT_PERMITTED: "собственник-источник не разрешён получателю",
  TARGET_OWNER_MISMATCH: "собственник-получатель не совпадает с профилем получателя", PLANNING_SOURCE_MISMATCH: "источник плана рейса не совпадает с настройкой площадки",
  BROKEN_BOX_NOT_ALLOWED: "получателю запрещено вскрытие короба: количество должно быть кратно целому коробу",
  PARTIAL_SHIPMENT_NOT_ALLOWED: "получателю запрещена частичная отгрузка: включите в рейс всю строку заказа",
  NEED_IDENTITY_CHANGED: "у снимка изменены получатель, товар или период — источник должен передать новый номер снимка",
  NEED_RECIPIENT_VERSION_CHANGED: "профиль получателя изменился — запросите снимок с актуальной версией",
  NEED_SKU_VERSION_CHANGED: "упаковка товара изменилась — запросите снимок с актуальной версией",
  SOURCE_MISMATCH: "сообщение пришло не от активного источника площадки", SITE_DISABLED: "приём на площадке выключен",
};
/** Понятная причина отказа; сам код остаётся в технических сведениях. */
function reason(code: unknown): string {
  const c = str(code), [head, kind, id] = c.split(":");
  if (head === "MASTER_MISSING" || head === "MASTER_INACTIVE") return (head === "MASTER_MISSING" ? "в справочнике склада нет записи: " : "запись справочника неактивна: ") + (KIND_NAME[kind] ?? kind).toLowerCase() + (id ? " " + id : "");
  return REASONS[c] ?? "документ отклонён по правилу приёма";
}

/** Карточка сообщения обмена: «принято/отклонено» отдельно от доставки ответа и внешнего подтверждения. */
export function MessageView({ card, onOpen }: { card: MsgCard; onOpen: Open }) {
  const r = card.result, kind = r.entity_type as Kind, id = str(r.document_id);
  return <>
    <dl className="tc-fields">
      <Row k="Документ" v={<>{KIND_NAME[kind] ?? kind} <b>{id}</b>, версия {str(r.version)} {r.status === "ACCEPTED" && <Act help={tcHelp.related} onClick={() => onOpen(kind, id)}>Открыть документ</Act>}</>} />
      <Row k="Приём на складе" v={resultChip(r.status)} />
      {r.status === "REJECTED" && <Row k="Причина отказа" v={<>{reason(r.code)}. Передайте номер документа, версию и код из технических сведений ответственному за источник ({card.source_id}). <HelpLink anchor="exchange" label="Как" /></>} />}
      {r.replayed === true && <Row k="Повтор" v="повтор уже полученного сообщения — новый документ не создан" />}
      <Row k="Остатки" v={r.stock_changed === false ? "не менялись" : str(r.stock_changed)} />
      <Row k="Физическое исполнение" v={r.physical_execution === "NOT_STARTED" ? "не начато" : str(r.physical_execution)} />
      <Row k="Ответ источнику" v={r.external_delivery === "PENDING" ? "в очереди на отправку" : str(r.external_delivery)} />
      <Row k="Внешнее подтверждение" v={r.external_business === "NOT_CONFIRMED" ? "внешний ответ не получен" : str(r.external_business)} />
      <Row k="Время" v={<Time value={r.occurred_at} />} />
    </dl>
    <Tech value={{ request: card.request, result: r }} label="Исходное сообщение и технический результат" />
  </>;
}
