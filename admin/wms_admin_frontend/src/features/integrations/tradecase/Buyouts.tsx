import { useState } from "react";
import { buyoutUnitsPath, tcHelp } from "./api";
import type { Buyout, BuyoutUnit, UnitPage } from "./api";
import type { Names } from "./Lists";
import { useRead } from "./useRead";
import { Act, BUYOUT, HelpLink, Tech, Time, str } from "./ui";

const named = (names: Names, kind: string, id: string) => { const t = names.get(kind + ":" + id); return t ? `${t} (${id})` : id; };
/** Состояние выкупа без обещаний: PENDING — запрос принят складом, ответ СКМ не получен (очередь ≠ отправка провайдеру). */
export const buyoutState = (b: Buyout) => b.pending_units > 0 ? <span className="tc-chip">Есть ожидающие коды</span>
  : b.rejected_units > 0 && b.confirmed_units === 0 ? <span className="tc-chip bad">отказ СКМ</span>
  : b.rejected_units > 0 ? <span className="tc-chip bad">частично отказано</span> : <span className="tc-chip ok">подтверждено СКМ</span>;
const counts = (b: Buyout) => <><span className="tc-chip ok">{b.confirmed_units}</span> / <span className="tc-chip">{b.pending_units}</span> / <span className={"tc-chip" + (b.rejected_units ? " bad" : "")}>{b.rejected_units}</span></>;

export function BuyoutList({ rows, names, selected, onOpen }: { rows: Buyout[]; names: Names; selected: string; onOpen: (id: string) => void }) {
  return <div className="tc-scroll"><table className="tc-table"><thead><tr><th>Выкуп</th><th>Основание / строка</th><th>Товар</th><th>Собственник</th><th>Момент</th>
    <th>Коды: подтверждено / ожидает / отклонено</th><th>Состояние</th><th>Разделение</th><th /></tr></thead>
    <tbody>{rows.map(b => <tr key={b.buyout_id} className={b.buyout_id === selected ? "is-selected" : ""}><td><b>{b.buyout_id}</b></td><td>{b.basis_order_id} / {b.basis_line_id}</td>
      <td>{named(names, "SKU", b.sku_id)}</td><td>{named(names, "OWNER", b.source_owner_id)} → {named(names, "OWNER", b.target_owner_id)}</td><td>{BUYOUT[b.buyout_mode] ?? b.buyout_mode}</td>
      <td>{counts(b)}</td><td>{buyoutState(b)}</td><td>{b.composition_checked ? (b.requires_sorting ? "нужно" : "не нужно") : "в карточке"}</td>
      <td><Act help={tcHelp.openBuyout} onClick={() => onOpen(b.buyout_id)}>Открыть</Act></td></tr>)}</tbody></table></div>;
}

/** Карточка выкупа: всегда свежий DETAIL (квитанция команды может быть старее текущего состояния) и коды по курсору. */
export function BuyoutView({ wh, card, names }: { wh: string; card: Buyout; names: Names }) {
  const [cursors, setCursors] = useState<(string | null)[]>([null]), after = cursors[cursors.length - 1];
  const units = useRead<UnitPage<BuyoutUnit>>(buyoutUnitsPath(wh, card.buyout_id, after));
  return <>
    <p className="tc-note">Выкуп меняет собственника только после ответа СКМ по каждому коду. Физическое количество не меняется.</p>
    <dl className="tc-fields">
      <dt>Основание</dt><dd>заказ {card.basis_order_id}, строка {card.basis_line_id}, версия {card.basis_version}</dd>
      <dt>Товар / МРЦ</dt><dd>{named(names, "SKU", card.sku_id)} · МРЦ {str(card.mrc)}</dd>
      <dt>Собственник</dt><dd>{named(names, "OWNER", card.source_owner_id)} → {named(names, "OWNER", card.target_owner_id)}</dd>
      <dt>Момент выкупа</dt><dd>{BUYOUT[card.buyout_mode] ?? card.buyout_mode}</dd>
      <dt>Коды</dt><dd>запрошено {card.requested_units}: подтверждено {card.confirmed_units}, ожидает {card.pending_units}, отклонено {card.rejected_units} · {buyoutState(card)}</dd>
      <dt>Ответ СКМ</dt><dd>{card.external_document_id ? "документ СКМ " + card.external_document_id : "ответ ещё не получен; запрос в очереди склада не означает отправку провайдеру"}</dd>
      <dt>Разделение паллеты</dt><dd>{!card.composition_checked ? "не проверено — перечитайте карточку" : card.requires_sorting ? <b>нужно: на паллете остаётся товар другого собственника <HelpLink anchor="sort" label="Как разделить" /></b> : "не нужно"}</dd>
      <dt>Создан</dt><dd><Time value={card.created_at} /></dd>
    </dl>
    <h4>Коды выкупа</h4>
    {units.error ? <p className="tc-err" role="alert">{units.error}</p> : units.loading && !units.data ? <p className="tc-note">Читаем коды…</p> : units.data && <div className="tc-scroll"><table className="tc-table">
      <thead><tr><th>Паллета</th><th>Адрес</th><th>Ответ СКМ</th><th>Причина отказа</th><th>Удержание под выкуп</th></tr></thead>
      <tbody>{units.data.items.map(u => <tr key={u.physical_unit_key}><td>{u.pallet_identifier}</td><td>{str(u.cell)}</td>
        <td>{u.outcome === "CONFIRMED" ? <span className="tc-chip ok">подтверждён</span> : u.outcome === "REJECTED" ? <span className="tc-chip bad">отклонён</span> : <span className="tc-chip">ожидает</span>}</td>
        <td>{str(u.reason)}</td><td>{u.buyout_hold ? "да" : "нет"}</td></tr>)}</tbody></table></div>}
    <div className="tc-pager">{cursors.length > 1 && <Act help={tcHelp.first} onClick={() => setCursors([null])}>⟲ К началу</Act>}
      {units.data?.has_more && units.data.next_after && <Act help={tcHelp.moreUnits} onClick={() => setCursors(c => [...c, units.data!.next_after])}>Далее →</Act>}</div>
    <Tech value={card} />
  </>;
}
