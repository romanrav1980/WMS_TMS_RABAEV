import { useState } from "react";
import { HelpHint } from "../help/HelpHint";
import type { DeliveryListItem } from "../contracts";
import { deliveryStateLabel, departureHint, filterDeliveries, isReceived, shortDeparture, type DeliveryFilter } from "../listNavigation";

interface DeliveriesListProps {
 storeAddress: string; items: DeliveryListItem[]; busy: boolean; message: string; hasMore: boolean;
 onOpen: (loadOperationId: string) => void; onRefresh: () => void; onLoadMore: () => void;
 onBack: (() => void) | null; onLogout: () => void; onScan?: () => void;
}

function DeliveryCard({ item, busy, onOpen }: { item: DeliveryListItem; busy: boolean; onOpen: (id: string) => void }) {
 const received = isReceived(item);
 return <li><button type="button" className="store-app-list-item store-app-delivery-card"
  title={received ? "Открыть сохранённый акт приёмки поставки" : "Открыть поставку и начать приёмку"}
  data-help-id="deliveries.open" disabled={busy} onClick={() => onOpen(item.load_operation_id)}>
  <span className="store-app-card-heading"><strong>Рейс {item.trip_id}</strong>
   <span className={`store-app-badge ${received ? "is-received" : "is-waiting"}`}>{deliveryStateLabel(item)}</span></span>
  <span className="store-app-place">Место {item.root_key}</span>
  <span className="store-app-card-meta"><span>{item.gross_weight_kg === null ? "Вес не указан" : `${item.gross_weight_kg.toLocaleString("ru-RU")} кг`}</span>
   <span title={departureHint(item)}>{shortDeparture(item)} {item.time_status !== "AWARE" && <span aria-label={departureHint(item)}>ⓘ</span>}</span>
   <span className="store-app-card-link">{received ? "Акт" : "Принять"} →</span></span>
 </button></li>;
}

function DeliveryTabs({ filter, items, onChange }: { filter: DeliveryFilter; items: DeliveryListItem[]; onChange: (value: DeliveryFilter) => void }) {
 const tabs: Array<[DeliveryFilter, string, number]> = [
  ["waiting", "К приёмке", items.filter((item) => !isReceived(item)).length],
  ["accepted", "Принятые", items.filter(isReceived).length], ["all", "Все", items.length],
 ];
 return <div className="store-app-tabs" role="group" aria-label="Состояние загруженных поставок">
  {tabs.map(([value, label, count]) => <button key={value} type="button" aria-pressed={filter === value}
   title={`Показать «${label}» среди загруженных поставок`} data-help-id={`deliveries.filter.${value}`}
   onClick={() => onChange(value)}>{label} <span>{count}</span></button>)}
 </div>;
}

export function DeliveriesList({ storeAddress, items, busy, message, hasMore, onOpen, onRefresh, onLoadMore, onBack, onLogout, onScan }: DeliveriesListProps) {
 const [filter, setFilter] = useState<DeliveryFilter>("waiting");
 const [query, setQuery] = useState("");
 const visible = filterDeliveries(items, filter, query);
 return <section className="store-app-screen store-app-deliveries" aria-label="Поставки магазина">
  <header className="store-app-header">
   <div className="store-app-heading"><span className="store-app-eyebrow">Приёмка магазина</span><h1>Поставки</h1>
    <p className="store-app-store-name" title={storeAddress}>{storeAddress}</p></div>
   <div className="store-app-header-actions">
    {onBack && <button type="button" data-help-id="store.change" title="Выбрать другой назначенный магазин" onClick={onBack}>Магазин</button>}
    <button type="button" data-help-id="session.logout" title="Выйти из приложения и закрыть сессию" onClick={onLogout}>Выйти</button>
   </div>
  </header>
  <div className="store-app-list-toolbar">
   <button type="button" className="store-app-primary" data-help-id="deliveries.scan" disabled={busy || !onScan}
    title={onScan ? "Отсканировать код места и найти поставку" : "Сканирование поставки пока не подключено"} onClick={onScan}>Сканировать поставку</button>
   <button type="button" className="store-app-icon-button" data-help-id="deliveries.refresh" title="Обновить поставки с сервера" disabled={busy} onClick={onRefresh} aria-label="Обновить поставки">↻</button>
   <HelpHint helpId="deliveries.list" tip="Как найти поставку и начать приёмку" article="store-receiving-app" />
  </div>
  <DeliveryTabs filter={filter} items={items} onChange={setFilter} />
  <label className="store-app-search">Найти рейс или место
   <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Номер рейса или код места"
    title="Поиск только среди уже загруженных поставок" data-help-id="deliveries.search" aria-describedby="store-search-scope" />
  </label>
  <p id="store-search-scope" className="store-app-list-scope">Найдено {visible.length} из {items.length} загруженных{hasMore ? "; есть ещё на сервере" : ""}.</p>
  {busy && <p role="status" className="store-app-muted">Обновляем поставки…</p>}
  {!busy && !visible.length && <div className="store-app-empty"><strong>{filter === "waiting" && !query ? "Среди загруженных нет ожидающих поставок" : "Поставки не найдены"}</strong>
   <p>{hasMore ? "Загрузите следующую страницу или измените фильтр." : "Проверьте фильтр или обновите список."}</p></div>}
  <ul className="store-app-list">{visible.map((item) => <DeliveryCard key={item.load_operation_id} item={item} busy={busy} onOpen={onOpen} />)}</ul>
  {hasMore && <button type="button" className="store-app-load-more" data-help-id="deliveries.more" title="Загрузить следующую страницу и добавить к текущему поиску" disabled={busy} onClick={onLoadMore}>Загрузить ещё поставки</button>}
  {message && <p role="status" className="store-app-message">{message}</p>}
 </section>;
}
