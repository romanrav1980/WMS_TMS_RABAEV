import { HelpHint } from "../help/HelpHint";
import type { StoreSummary } from "../contracts";

export function StoreSelector({ stores, hasMore, onSelect, onLogout }: {
 stores: StoreSummary[]; hasMore: boolean; onSelect: (storeId: string) => void; onLogout: () => void;
}) {
 return <section className="store-app-screen" aria-label="Выбор магазина">
  <header className="store-app-header"><div className="store-app-heading"><span className="store-app-eyebrow">Приёмка магазина</span><h1>Ваши магазины</h1></div>
   <button type="button" data-help-id="session.logout" title="Выйти из приложения и закрыть сессию" onClick={onLogout}>Выйти</button></header>
  <div className="store-app-section-heading"><p>Выберите место работы</p>
   <HelpHint helpId="store.select" tip="Откроются поставки выбранного назначенного магазина" article="store-receiving-app" /></div>
  <ul className="store-app-list">{stores.map((store) => <li key={store.store_id}>
   <button type="button" title="Открыть поставки этого магазина" data-help-id="store.select.open" className="store-app-list-item" onClick={() => onSelect(store.store_id)}>
    <strong>{store.address}</strong><span className="store-app-muted">{modeLabel(store.receipt_mode)}</span><span className="store-app-card-link">Открыть поставки →</span>
   </button></li>)}</ul>
  {!stores.length && <div className="store-app-empty"><strong>Магазины не назначены</strong><p>Попросите администратора назначить магазин и способ приёмки.</p></div>}
  {hasMore && <p className="store-app-muted">Показаны первые {stores.length} магазинов. Список ограничен сервером; уточните назначение у администратора.</p>}
 </section>;
}

function modeLabel(mode: StoreSummary["receipt_mode"]): string {
 if (mode === "BARCODE") return "Сканирование кодов";
 if (mode === "WEIGHT_PHOTO") return "Взвешивание и фото";
 return "Пересчёт по накладной";
}
