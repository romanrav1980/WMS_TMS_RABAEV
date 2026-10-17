// Общая условная изометрическая сцена склада: зоны-этапы и объекты на них (волны, задания). Этап объекта определяет вызывающий
// по фактическим данным; сцена ничего не вычисляет и не выдумывает. Доступна с клавиатуры (Tab/Enter/Space).

export type IsoStage = { id: string; title: string; x: number; y: number; dashed?: boolean };
export type IsoTone = "plan" | "ok" | "bad" | "warn" | "muted";
export type IsoItem = { id: number | string; stage: string; tone: IsoTone; label: string; title: string };
type Props = { stages: IsoStage[]; items: IsoItem[]; selected: number | string | null; onSelect: (id: number | string) => void;
  ariaLabel: string; stageHelpId: string; itemHelpId: string; stageHelp: string; perStage?: number };

const W = 150, H = 96;
const TONE: Record<IsoTone, [string, string, string]> = {
  plan: ["#3d8bfd", "#2a62b5", "#3474d6"], ok: ["#2fbf71", "#1f8a51", "#25a160"], bad: ["#ef5b5b", "#aa3333", "#c44444"],
  warn: ["#f0a531", "#b07418", "#cf8c22"], muted: ["#7c8794", "#555e69", "#69727d"] };
// Шаг 120×66 больше полуразмеров площадки (93×29): соседние зоны не перекрываются.
const iso = (x: number, y: number) => ({ px: (x - y) * 120, py: (x + y) * 66 });

export function IsoStageScene({ stages, items, selected, onSelect, ariaLabel, stageHelpId, itemHelpId, stageHelp, perStage = 8 }: Props) {
  const by = new Map<string, IsoItem[]>();
  for (const it of items) (by.get(it.stage) ?? by.set(it.stage, []).get(it.stage)!).push(it);
  const pts = stages.map(st => iso(st.x, st.y));
  const minX = Math.min(...pts.map(p => p.px)) - W * 0.62 - 10, maxX = Math.max(...pts.map(p => p.px)) + W * 0.62 + 10;
  const minY = Math.min(...pts.map(p => p.py)) - 10, maxY = Math.max(...pts.map(p => p.py)) + H * 0.6 + 20;
  return <svg viewBox={`${minX} ${minY} ${maxX - minX} ${maxY - minY}`} role="img" aria-label={ariaLabel} style={{ width: "100%", height: "auto", maxHeight: 520, display: "block", marginTop: 34 }}>
    {stages.map(st => {
      const { px, py } = iso(st.x, st.y), list = by.get(st.id) ?? [];
      const hw = W * 0.62, hh = H * 0.3, d = H * 0.6;
      return <g key={st.id} data-help-id={stageHelpId + "." + st.id}>
        <title>{`${st.title}: ${list.length}. ${stageHelp}`}</title>
        <polygon points={`${px - hw},${py + hh} ${px},${py + d} ${px},${py + d + 10} ${px - hw},${py + hh + 10}`} fill="#0e1722" />
        <polygon points={`${px + hw},${py + hh} ${px},${py + d} ${px},${py + d + 10} ${px + hw},${py + hh + 10}`} fill="#172434" />
        <polygon points={`${px},${py} ${px + hw},${py + hh} ${px},${py + d} ${px - hw},${py + hh}`} fill={st.dashed ? "#1a2230" : "#1c2c40"} stroke="#2f4560" strokeDasharray={st.dashed ? "4 3" : undefined} />
        <text x={px} y={py + 15} textAnchor="middle" fill="#b9c8d8" fontSize="10.5">{st.title} · {list.length}</text>
        {list.slice(0, perStage).map((it, i) => {
          const cx = px - 42 + (i % 4) * 28, cy = py + 30 + Math.floor(i / 4) * 15, sel = selected === it.id, [top, left, right] = TONE[it.tone];
          return <g key={it.id} role="button" tabIndex={0} aria-pressed={sel} aria-label={it.label} data-help-id={itemHelpId} style={{ cursor: "pointer" }}
            onClick={() => onSelect(it.id)} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(it.id); } }}>
            <title>{it.title}</title>
            <polygon points={`${cx},${cy - 8} ${cx + 11},${cy - 2} ${cx},${cy + 4} ${cx - 11},${cy - 2}`} fill={top} stroke={sel ? "#fff" : "none"} strokeWidth="2" />
            <polygon points={`${cx - 11},${cy - 2} ${cx},${cy + 4} ${cx},${cy + 10} ${cx - 11},${cy + 4}`} fill={left} />
            <polygon points={`${cx + 11},${cy - 2} ${cx},${cy + 4} ${cx},${cy + 10} ${cx + 11},${cy + 4}`} fill={right} />
          </g>;
        })}
        {list.length > perStage && <text x={px + 66} y={py + 34} fill="#93a6ba" fontSize="10" textAnchor="end">+{list.length - perStage}</text>}
      </g>;
    })}
  </svg>;
}
