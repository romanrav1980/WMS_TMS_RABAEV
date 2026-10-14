import { useEffect, useRef, type ReactNode, type RefObject } from "react";
import { clipToDay, DAY_MIN, offAxisOps, planText, spanOf, type GanttTimed } from "./TransportGanttTime";
import "./TransportGantt.css";

// C-0034: шкала выбранных суток 00:00–24:00, полосы операций с обрезкой по полуночи и список операций вне шкалы.
export const PX_MIN   = 1.5;  // pixels per minute
export const ROW_H    = 52;   // vehicle row height px
export const HEADER_H = 44;   // time axis header height px
export const CHART_W  = DAY_MIN * PX_MIN; // 2160px
export const minToPx = (min: number) => min * PX_MIN;
const hhmm = (min: number) => `${String(Math.floor(min / 60)).padStart(2, "0")}:${String(min % 60).padStart(2, "0")}`;

export function TimeAxisRow() {
  const ticks: ReactNode[] = [];
  for (let min = 0; min <= DAY_MIN; min += 30) {
    const x = minToPx(min), isHour = min % 60 === 0;
    ticks.push(
      <g key={min}>
        <line x1={x} y1={isHour ? HEADER_H - 22 : HEADER_H - 10} x2={x} y2={HEADER_H} stroke="#cbd5e1" strokeWidth={isHour ? 1.5 : 1} />
        {isHour && <text x={Math.min(Math.max(x, 16), CHART_W - 16)} y={HEADER_H - 26} textAnchor="middle" fontSize={11} fill="#64748b" fontFamily="inherit">{hhmm(min)}</text>}
      </g>
    );
  }
  return <>{ticks}</>;
}

export function GridLines({ rowCount }: { rowCount: number }) {
  const lines: ReactNode[] = [];
  for (let min = 0; min <= DAY_MIN; min += 60) {
    const x = minToPx(min);
    lines.push(<line key={min} x1={x} y1={0} x2={x} y2={HEADER_H + rowCount * ROW_H} stroke="#e2e8f0" strokeWidth={1} strokeDasharray={min % 120 === 0 ? "none" : "2,3"} />);
  }
  for (let i = 0; i <= rowCount; i++) {
    const y = HEADER_H + i * ROW_H;
    lines.push(<line key={`h${i}`} x1={0} y1={y} x2={CHART_W} y2={y} stroke="#f1f5f9" strokeWidth={1} />);
  }
  return <>{lines}</>;
}

type BlockOp = GanttTimed & { operation_code: string; fact_start: string | null };
// Полоса операции; часть за пределами суток обрезается, продолжение отмечается треугольником у края.
export function OpBlock<T extends BlockOp>({ op, day, rowY, color, label, onHover, onLeave, onClick, onContextMenu }: {
  op: T; day: string; rowY: number; color: string; label: string;
  onHover: (e: React.MouseEvent<SVGRectElement>, op: T) => void; onLeave: () => void;
  onClick: (op: T) => void; onContextMenu: (e: React.MouseEvent, op: T) => void;
}) {
  const span = spanOf(op, day), clip = span && clipToDay(span);
  if (!clip) return null;
  const x = minToPx(clip.start), w = Math.max((clip.end - clip.start) * PX_MIN, 2);
  const y = rowY + 6, h = ROW_H - 12, mid = y + h / 2, hasFact = op.fact_start !== null;
  const note = (clip.before ? " · начата в предыдущие сутки" : "") + (clip.after ? " · продолжается в следующие сутки" : "");
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} rx={3} fill={color} opacity={hasFact ? 1 : 0.75}
        stroke={hasFact ? "rgba(0,0,0,.25)" : "none"} strokeWidth={1} style={{ cursor: "pointer" }}
        aria-label={`${label} ${planText(op, day)}${note}`}
        onMouseEnter={(e) => onHover(e, op)} onMouseLeave={onLeave} onClick={() => onClick(op)}
        onContextMenu={(e) => onContextMenu(e as unknown as React.MouseEvent, op)} />
      {clip.before && <polygon className="gantt-cont" points={`${x + 7},${mid - 6} ${x + 1},${mid} ${x + 7},${mid + 6}`} />}
      {clip.after && <polygon className="gantt-cont" points={`${x + w - 7},${mid - 6} ${x + w - 1},${mid} ${x + w - 7},${mid + 6}`} />}
      {w > 32 && <text x={x + w / 2} y={mid + 4} textAnchor="middle" fontSize={10} fill="#fff" fontWeight="600" fontFamily="inherit"
        style={{ pointerEvents: "none", userSelect: "none" }}>{label}</text>}
    </g>
  );
}

// Начальная прокрутка один раз на дату (обновление данных той же даты не сбивает позицию пользователя).
export function useInitialGanttScroll(ref: RefObject<HTMLDivElement | null>, day: string, ready: boolean, targetMin: () => number) {
  const done = useRef("");
  useEffect(() => {
    if (!ready || !ref.current || done.current === day) return;
    done.current = day;
    ref.current.scrollLeft = Math.max(0, minToPx(targetMin()) - 120);
  }, [ref, day, ready, targetMin]);
}

type ListOp = BlockOp & { op_id: number; tt_id: number };
// Операции текущей выборки, которых нет на шкале: без даты — неполные данные; вне суток — с датой. Каждая открывает карточку рейса.
export function GanttOffAxis<T extends ListOp>({ rows, day, labelOf, onOpen }: {
  rows: { vehicle_num: string; operations: T[] }[]; day: string; labelOf: (code: string) => string; onOpen: (op: T) => void;
}) {
  const items = rows.flatMap((v) => offAxisOps(v.operations, day).map((x) => ({ ...x, vehicle_num: v.vehicle_num })));
  const missing = items.filter((x) => x.reason === "missing").length;
  return (
    <div className="gantt-offaxis">
      <p className="gantt-offaxis-note">Сутки выбранной даты 00:00–24:00; время как в API, без пересчёта часового пояса. Показаны рейсы даты и пересекающие сутки операции;
        ◂ ▸ — операция начата в предыдущие или продолжается в следующие сутки.</p>
      {items.length > 0 && <details open={missing > 0}>
        <summary>{missing > 0 ? `Неполные данные — без плановой даты: ${missing}` : "Вне шкалы"}{items.length > missing ? ` · вне выбранных суток: ${items.length - missing}` : ""}</summary>
        <ul>{items.map(({ item, reason, vehicle_num }) => (
          <li key={item.op_id}>
            <button type="button" onClick={() => onOpen(item)}>Рейс #{item.tt_id} · {vehicle_num} · {labelOf(item.operation_code)} · {reason === "missing" ? "дата не задана" : planText(item, day)}</button>
          </li>))}</ul>
      </details>}
    </div>
  );
}
