import { useTwin } from "../store/twinStore";
import { fmt } from "../ui/format";
import { computeKpi } from "../ui/kpi";
import { isOpenPhase } from "../adapters/tmsOperations";

export function KpiRow() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const select = useTwin((s) => s.select);
  const setBottomTab = useTwin((s) => s.setBottomTab);
  const k = computeKpi(world);
  const live = world.mode === "live";
  const sts = Object.values(world.sts);
  const planned = world.trips.filter((t) => t.phase === "planned");
  const lateLive = planned.filter((t) => t.risk === "late").length;
  const openOps = world.operations.filter((o) => isOpenPhase(o.phase));
  const moves = openOps.filter((o) => o.kind === "MOVE");
  const picks = openOps.filter((o) => o.kind === "PICK");
  return (
    <div className="kpi-row">
      {live ? (
        <Kpi icon="⇄" label="Перемещения: открыто" value={String(moves.length)} note={`в работе ${moves.filter((o) => o.phase === "STARTED" || o.phase === "PARTIAL").length} · ошибок ${moves.filter((o) => o.phase === "FAILED").length}`} onClick={() => setBottomTab("ops")} />
      ) : (
        <Kpi icon="✋" label="Строк отбора / час" value={fmt(k.linesPerHour)} note={`${fmt(k.linesPicked)} за смену · СТ в работе ${k.stInWork}`} />
      )}
      {live ? (
        <>
          <Kpi icon="⛟" label="Рейсы спланированы" value={String(planned.length)} note={`${world.trips.filter((t) => t.phase === "done").length} отгружено · ${planned.filter((t) => t.gateId).length} с воротами`} onClick={() => setBottomTab("docks")} />
          <Kpi icon="⏱" label="Просрочены к отгрузке" value={String(lateLive)} note="спланирован, окно SHIPMENT_TIME+60 мин прошло" tone={lateLive ? "crit" : "ok"} />
          <Kpi icon="✋" label="Сборка CASE: открыто" value={String(picks.length)} note={`в работе ${picks.filter((o) => o.phase === "STARTED" || o.phase === "PARTIAL").length} · блок ${picks.filter((o) => o.phase === "BLOCKED").length} · СТ ${sts.length}`} onClick={() => setBottomTab("ops")} />
        </>
      ) : (
        <>
          <Kpi icon="⛟" label="ТС на территории" value={String(k.trucksOnSite)} note={`${k.trucksQueued} в очереди · ${k.trucksTransit} в пути`} tone={k.trucksQueued ? "warn" : undefined} onClick={() => setBottomTab("docks")} />
          <Kpi icon="⏱" label="Постановка в окно" value={k.dockedCount ? `${k.onTimePct.toFixed(1)}%` : "—"} note={`${k.dockedCount} постановок · ${k.lateCount} с опозданием`} tone={k.onTimePct < 90 ? "warn" : "ok"} />
          <Kpi icon="▤" label="SLA пополнения" value={world.counters.replDone ? `${k.replSla.toFixed(0)}%` : "—"} note={`очередь ${k.replQueue} · пустых ячеек ${k.facesEmpty}`} tone={k.facesEmpty ? "warn" : undefined} />
        </>
      )}
      <Kpi
        icon="⚠"
        label="Коллизии"
        value={String(k.collisionsActive)}
        note={`${k.collisionsCritical} критич. · потери ${k.lostMinutes.toFixed(0)} мин`}
        tone={k.collisionsCritical ? "crit" : k.collisionsActive ? "warn" : "ok"}
        onClick={() => {
          const first = world.collisions.find((c) => c.active);
          if (first) select({ kind: "collision", id: first.key });
          setBottomTab("events");
        }}
      />
    </div>
  );
}

function Kpi({ icon, label, value, note, tone, onClick }: { icon: string; label: string; value: string; note: string; tone?: string; onClick?: () => void }) {
  return (
    <button type="button" className={`kpi ${tone ? `tone-${tone}` : ""}`} onClick={onClick} disabled={!onClick}>
      <span className="kpi-icon">{icon}</span>
      <span className="kpi-body">
        <small>{label}</small>
        <b>{value}</b>
        <em>{note}</em>
      </span>
    </button>
  );
}
