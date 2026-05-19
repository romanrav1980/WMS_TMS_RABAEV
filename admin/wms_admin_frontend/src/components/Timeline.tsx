import { SHIFT_MINUTES, clock } from "../demoData";
import { collisionTitle } from "../replay/reducer";
import type { WarehouseEvent } from "../types";

const collisionColors: Record<string, string> = {
  PICK_FACE_EMPTY: "#ee3e37",
  PICK_FACE_QUEUE: "#ef4444",
  REACH_RESOURCE_SHORTAGE: "#b91c1c",
  ROUTE_COMPLETION_DELAY: "#f97316",
  REACHTRUCK_CROSSING: "#7c3aed",
  REACHTRUCK_PICKER_PASS: "#a855f7",
  REACHTRUCK_BLOCK: "#dc2626",
  DOCK_QUEUE: "#f59e0b",
  AISLE_CONGESTION: "#eab308"
};

export function Timeline({ minute, playing, speed, events, onMinute, onPlayToggle, onSpeed }: {
  minute: number;
  playing: boolean;
  speed: number;
  events: WarehouseEvent[];
  onMinute: (minute: number) => void;
  onPlayToggle: () => void;
  onSpeed: (speed: number) => void;
}) {
  const markers = events
    .filter((event) => ["WAVE_REPLENISHMENT_PREP_STARTED", "WAVE_LAUNCHED", "COLLISION", "PICK_FACE_EMPTY_AT_ARRIVAL", "ROUTE_COMPLETION_DELAYED", "PALLET_STAGED_TO_DOCK", "CLIENT_READY", "PALLET_LOADING_STARTED"].includes(event.event_type))
    .slice(0, 260);
  const collisionBuckets = buildCollisionBuckets(events);
  return (
    <footer className="timeline-panel">
      <div className="timeline-controls">
        <button className={`play-button ${playing ? "" : "paused"}`} type="button" onClick={onPlayToggle}>{playing ? "Pause" : "Play"}</button>
        <button className="mini-control" type="button" onClick={() => onMinute(Math.max(0, minute - 5))}>‹</button>
        <button className="mini-control" type="button" onClick={() => onMinute(Math.min(SHIFT_MINUTES, minute + 5))}>›</button>
        <select value={speed} onChange={(event) => onSpeed(Number(event.target.value))}>
          <option value={1}>x1</option>
          <option value={5}>x5</option>
          <option value={10}>x10</option>
          <option value={60}>x60</option>
        </select>
        <button className="live-button" type="button" onClick={() => onMinute(SHIFT_MINUTES)}>LIVE</button>
      </div>
      <div className="timeline-track-wrap">
        <div className="timeline-ticks">{Array.from({ length: 13 }, (_, index) => <span key={index}>{clock(index * 60)}</span>)}</div>
        <div className="timeline-markers">
          {markers.map((event, index) => <i key={`${event.minute}-${index}`} className={`timeline-marker ${["COLLISION", "PICK_FACE_EMPTY_AT_ARRIVAL", "ROUTE_COMPLETION_DELAYED"].includes(event.event_type) ? "red" : event.event_type === "WAVE_LAUNCHED" ? "green" : "blue"}`} style={{ left: `${(event.minute / SHIFT_MINUTES) * 100}%` }} />)}
        </div>
        <div className="collision-density">
          {collisionBuckets.map((bucket) => (
            <div key={bucket.start} className="collision-bucket" title={bucket.title}>
              {bucket.parts.map((part) => <span key={part.type} style={{ height: `${part.height}%`, background: part.color }} />)}
              {bucket.total > 0 && <b>{bucket.total}</b>}
            </div>
          ))}
        </div>
        <input type="range" min={0} max={SHIFT_MINUTES} step={1} value={minute} onChange={(event) => onMinute(Number(event.target.value))} />
        <b className="time-badge" style={{ left: `${(minute / SHIFT_MINUTES) * 100}%` }}>{clock(minute)}</b>
      </div>
      <button className="mini-control" type="button">□</button>
    </footer>
  );
}

function buildCollisionBuckets(events: WarehouseEvent[]) {
  const bucketMinutes = 30;
  const bucketCount = SHIFT_MINUTES / bucketMinutes;
  const buckets = Array.from({ length: bucketCount }, (_, index) => ({
    start: index * bucketMinutes,
    counts: new Map<string, number>()
  }));
  for (const event of events) {
    if (event.event_type !== "COLLISION" || !event.collision_type) continue;
    const index = Math.min(bucketCount - 1, Math.max(0, Math.floor(event.minute / bucketMinutes)));
    const bucket = buckets[index];
    bucket.counts.set(event.collision_type, (bucket.counts.get(event.collision_type) || 0) + 1);
  }
  const maxTotal = Math.max(1, ...buckets.map((bucket) => Array.from(bucket.counts.values()).reduce((sum, value) => sum + value, 0)));
  return buckets.map((bucket) => {
    const total = Array.from(bucket.counts.values()).reduce((sum, value) => sum + value, 0);
    const parts = Array.from(bucket.counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 4)
      .map(([type, count]) => ({
        type,
        count,
        color: collisionColors[type] || "#64748b",
        height: Math.max(10, Math.round((count / Math.max(1, total)) * Math.min(100, 18 + (total / maxTotal) * 82)))
      }));
    const title = total
      ? `${clock(bucket.start)}-${clock(bucket.start + bucketMinutes)}\n${Array.from(bucket.counts.entries()).sort((a, b) => b[1] - a[1]).map(([type, count]) => `${collisionTitle(type)}: ${count}`).join("\n")}`
      : `${clock(bucket.start)}-${clock(bucket.start + bucketMinutes)}: нет коллизий`;
    return { start: bucket.start, total, parts, title };
  });
}
