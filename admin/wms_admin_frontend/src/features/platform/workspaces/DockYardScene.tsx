import type { KeyboardEvent } from "react";
import { wsHelp } from "./help";
import { tripTone } from "./types";
import type { Selection, Trip } from "./types";

// Изометрическая схема РЦ по живым рейсам: ворота — фактические DOCK рейсов даты, машины — рейсы. Геометрия здания условная.
const S = 22, OX = 0, OY = 0, GAP = 3.4;
const iso = (x: number, y: number, z = 0): [number, number] => [OX + (x - y) * S * 0.866, OY + (x + y) * S * 0.5 - z * S];
const pts = (...p: [number, number, number][]) => p.map(([x, y, z]) => iso(x, y, z).join(",")).join(" ");
const TONE = { plan: "#3d8bfd", ship: "#2fbf71", closed: "#7c8794", other: "#f0a531" } as const;

function Box({ x, y, z = 0, w, d, h, top, left, right }: { x: number; y: number; z?: number; w: number; d: number; h: number; top: string; left: string; right: string }) {
  return <g>
    <polygon points={pts([x, y + d, z], [x + w, y + d, z], [x + w, y + d, z + h], [x, y + d, z + h])} fill={left} />
    <polygon points={pts([x + w, y, z], [x + w, y + d, z], [x + w, y + d, z + h], [x + w, y, z + h])} fill={right} />
    <polygon points={pts([x, y, z + h], [x + w, y, z + h], [x + w, y + d, z + h], [x, y + d, z + h])} fill={top} />
  </g>;
}

function Truck({ trip, x, y, selected, onSelect, lift = 0 }: { trip: Trip; x: number; y: number; selected: boolean; onSelect: () => void; lift?: number }) {
  const color = TONE[tripTone(trip.CONDITION)];
  const ready = trip.READY_PERC == null ? "готовность: нет данных" : `готовность склада ${trip.READY_PERC}%`;
  const [lx, ly] = iso(x + 0.7, y + 4.2, 2.4 + lift);
  const key = (e: KeyboardEvent) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(); } };
  return <g role="button" tabIndex={0} aria-label={`Рейс ${trip.ID}, ${trip.TRANSPORT ?? "машина не назначена"}, ${trip.CONDITION ?? "состояние неизвестно"}, ${ready}`}
    data-help-id={trip.DOCK ? wsHelp.dock.id : wsHelp.yardTrip.id} className="ops-truck" onClick={onSelect} onKeyDown={key} style={{ cursor: "pointer" }}>
    <title>{`Рейс ${trip.ID} · ${trip.TRANSPORT ?? "—"} · ${trip.CONDITION ?? "—"} · ${ready}${trip.DOCK ? " · ворота " + trip.DOCK : " · без ворот"}`}</title>
    <Box x={x} y={y} w={1.4} d={3.2} h={1.6} top="#d8e1ea" left="#9fb0c2" right="#b9c7d5" />
    <Box x={x} y={y + 3.2} w={1.4} d={1} h={1.3} top={color} left={color} right={color} />
    {selected && <polygon points={pts([x - 0.3, y - 0.3, 0], [x + 1.7, y - 0.3, 0], [x + 1.7, y + 4.5, 0], [x - 0.3, y + 4.5, 0])} fill="none" stroke="#8ec5ff" strokeWidth={2} strokeDasharray="4 3" />}
    <g transform={`translate(${lx},${ly})`}>
      <rect x={-4} y={-13} rx={6} width={Math.max(64, String(trip.TRANSPORT ?? trip.ID).length * 7 + 18)} height={18} fill="rgba(13,20,29,.88)" stroke={color} />
      <circle cx={5} cy={-4} r={3} fill={color} />
      <text x={12} y={0} fontSize={11} fill="#e6eef6">{trip.TRANSPORT ?? `рейс ${trip.ID}`}</text>
    </g>
  </g>;
}

export function DockYardScene({ trips, selection, onSelect, title }: { trips: Trip[]; selection: Selection; onSelect: (s: Selection) => void; title: string }) {
  const docks = Array.from(new Set(trips.map(t => t.DOCK).filter((d): d is string => Boolean(d)))).sort();
  const slots = Math.max(docks.length, 6);
  const W = slots * GAP + 1.2, D = 9, H = 3;
  const yard = trips.filter(t => !t.DOCK);
  const selected = (t: Trip) => selection?.kind === "trip" && selection.id === t.ID;
  // viewBox по фактическим углам площадки, чтобы схема занимала всю панель.
  const corners = [iso(-2, -2), iso(W + 3, -2), iso(W + 3, D + 16), iso(-2, D + 16), iso(0, 0, H + 1)];
  const minX = Math.min(...corners.map(c => c[0])) - 20, maxX = Math.max(...corners.map(c => c[0])) + 20;
  const minY = Math.min(...corners.map(c => c[1])) - 30, maxY = Math.max(...corners.map(c => c[1])) + 10;
  return <svg viewBox={`${minX} ${minY} ${maxX - minX} ${maxY - minY}`} width="100%" height="100%" role="img" aria-label={title} preserveAspectRatio="xMidYMid meet">
    <polygon points={pts([-2, -2, 0], [W + 3, -2, 0], [W + 3, D + 16, 0], [-2, D + 16, 0])} fill="#1a2533" />
    {Array.from({ length: slots }, (_, i) => <line key={"lane" + i} x1={iso(0.6 + i * GAP + 0.7, D + 1)[0]} y1={iso(0.6 + i * GAP + 0.7, D + 1)[1]}
      x2={iso(0.6 + i * GAP + 0.7, D + 6)[0]} y2={iso(0.6 + i * GAP + 0.7, D + 6)[1]} stroke="#2f4055" strokeDasharray="6 6" />)}
    <polygon points={pts([-1.5, D + 8, 0], [W + 2, D + 8, 0], [W + 2, D + 15, 0], [-1.5, D + 15, 0])} fill="#202d3d" stroke="#2f4055" />
    <text x={iso(-1.5, D + 15)[0] + 6} y={iso(-1.5, D + 15)[1] + 18} fontSize={13} fill="#93a6ba">Двор: рейсы без ворот</text>
    <Box x={0} y={0} w={W} d={D} h={H} top="#2b3b50" left="#34475f" right="#3d5270" />
    {Array.from({ length: 5 }, (_, i) => <line key={"roof" + i} x1={iso(0.5, 1 + i * 1.7, H)[0]} y1={iso(0.5, 1 + i * 1.7, H)[1]} x2={iso(W - 0.5, 1 + i * 1.7, H)[0]} y2={iso(W - 0.5, 1 + i * 1.7, H)[1]} stroke="#3e5470" />)}
    <text x={iso(W / 2, D / 2, H)[0]} y={iso(W / 2, D / 2, H)[1]} textAnchor="middle" fontSize={15} fontWeight={700} fill="#c9d8e8">{title}</text>
    {Array.from({ length: slots }, (_, i) => {
      const x = 0.6 + i * GAP, dock = docks[i], trip = dock ? trips.find(t => t.DOCK === dock) : undefined;
      const [tx, ty] = iso(x + 0.7, D, 0);
      return <g key={"dock" + i}>
        <polygon points={pts([x, D, 0], [x + 1.6, D, 0], [x + 1.6, D, 1.9], [x, D, 1.9])} fill={trip ? "#0d141d" : "#24364b"} stroke="#4b6380" />
        <text x={tx} y={ty + 16} textAnchor="middle" fontSize={10} fill="#93a6ba">{dock ?? `ворота ${i + 1}`}</text>
        {trip && <Truck trip={trip} x={x + 0.1} y={D + 0.6} lift={i % 2 ? 1.2 : 0} selected={selected(trip)} onSelect={() => onSelect({ kind: "trip", id: trip.ID })} />}
        {dock && trips.filter(t => t.DOCK === dock).length > 1 && <text x={tx} y={ty + 30} textAnchor="middle" fontSize={11} fill="#ffd38a">ещё {trips.filter(t => t.DOCK === dock).length - 1} на воротах</text>}
      </g>;
    })}
    {yard.slice(0, 8).map((trip, i) => <Truck key={trip.ID} trip={trip} x={-0.8 + i * GAP} y={D + 9.5} lift={i % 2 ? 1.2 : 0} selected={selected(trip)} onSelect={() => onSelect({ kind: "trip", id: trip.ID })} />)}
    {yard.length > 8 && <text x={iso(W, D + 12)[0]} y={iso(W, D + 12)[1]} fontSize={12} fill="#ffd38a">ещё {yard.length - 8} без ворот</text>}
  </svg>;
}
