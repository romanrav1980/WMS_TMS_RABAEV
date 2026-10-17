import type { HuNode, HuSnapshot } from "./huTreeModel";
import { huMassFacts } from "./huMassFacts";

/** Existing snapshot provenance only. The Python quality projection has no native adapter yet. */
export function HuMassFacts({ node, snapshot }: { node: HuNode; snapshot: HuSnapshot }) {
 const mass = huMassFacts(node, snapshot);
 return <section className="hu-mass-facts" aria-label="Основания массы выбранного места">
  <h4>Масса <span>отгрузочное измерение не передано</span></h4>
  {mass.facts.length > 0 ? <dl>{mass.facts.map(fact => <div key={fact.label}><dt>{fact.label}</dt><dd>{fact.value}<small>{fact.basis}</small></dd></div>)}</dl>
   : <p className="hu-tree-note">Масса выбранного места неизвестна.</p>}
  <details><summary title="Показать недостающие основания массы и ограничения текущего снимка; ничего не рассчитывает и не подтверждает QC"
   data-help-id="hu.mass.transparency" data-help-article="warehouse-hu-tree">Источники и ограничения</summary>
   <p>Ожидаемый GROSS текущего состава и отдельное отгрузочное измерение всего места не подтверждены этим снимком. Разница массы и допуск QC не рассчитываются.</p>
   {mass.missing.length > 0 && <ul>{mass.missing.map(reason => <li key={reason}>{reason}</li>)}</ul>}
   {mass.legacyTotal && <p>Справочный расчёт снимка: <b>{mass.legacyTotal}</b>. Не измеренная масса и не подтверждённый расчёт ожидаемого GROSS для QC.</p>}
   <p>Дочерние массы и тара здесь не суммируются. Температурная совместимость этим ответом не подтверждается.</p>
  </details>
 </section>;
}
