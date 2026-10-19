import { tcHelp } from "./api";
import type { Tab } from "./api";

/** Компактная изометрическая схема процесса. Это схема, а не цифровой двойник: активны только реализованные
 *  основания (заказы, рейсы); склад, сборка и экспедиция в T02 не показывают фактических операций. */
const STEPS: { label: string; tab?: Tab; help?: { id: string; text: string } }[] = [
  { label: "Основание", tab: "ORDER", help: tcHelp.flowBasis }, { label: "Склад", tab: "STOCK", help: tcHelp.flowStock }, { label: "Сборка" }, { label: "Экспедиция" },
  { label: "Рейс", tab: "TRIP", help: tcHelp.flowTrip },
];

export function Flow({ onTab }: { onTab: (tab: Tab) => void }) {
  return <figure className="tc-flow" aria-label="Схема процесса СНС/BLC">
    <svg viewBox="0 0 560 104" role="img" aria-label="Основание → Склад → Сборка → Экспедиция → Рейс">
      {STEPS.map((s, i) => {
        const x = 20 + i * 108, active = Boolean(s.tab);
        const tile = <g key={s.label} className={"tc-tile" + (active ? " is-active" : "")} transform={`translate(${x} 14)`}>
          <polygon points="40,0 80,18 40,36 0,18" /><polygon className="side" points="0,18 40,36 40,46 0,28" /><polygon className="side2" points="80,18 40,36 40,46 80,28" />
          <text x="40" y="66" textAnchor="middle">{s.label}</text>

          {i < STEPS.length - 1 && <path d="M86 18 h18" className="tc-arrow" />}
        </g>;
        return active ? <a key={s.label} href="#" role="button" aria-label={s.label + ": открыть"} data-help-id={s.help!.id} onClick={e => { e.preventDefault(); onTab(s.tab!); }}>
          <title>{s.help!.text}</title>{tile}</a> : tile;
      })}
    </svg>
    <figcaption>Откройте основание, запас склада или рейс. Сборка и экспедиция в этой версии не подключены; координаты и фактические операции не рисуются.</figcaption>
  </figure>;
}
