import { useState } from "react";
import { isOpenPhase } from "../adapters/tmsOperations";
import type { TwinOperation, TwinState } from "../contracts/twin";
import { useTwin } from "../store/twinStore";
import { PHASE_LABEL, kindLabel, phaseTone } from "../ui/opsFormat";

type Scope = "open" | "all";
type Kind = "all" | "MOVE" | "PICK";

const isBound = (o: TwinOperation) => !!(o.from?.bound || o.to?.bound || o.lines?.some((l) => l.bound));

// Список складских операций снимка: исходный статус + фаза адаптера, привязка к схеме, план/факт.
export function OperationsTab({ w }: { w: TwinState }) {
  const select = useTwin((s) => s.select);
  const selected = useTwin((s) => s.selected);
  const [scope, setScope] = useState<Scope>("open");
  const [kind, setKind] = useState<Kind>("all");
  const [unboundOnly, setUnboundOnly] = useState(false);
  const list = w.operations
    .filter((o) => (scope === "open" ? isOpenPhase(o.phase) : true))
    .filter((o) => (kind === "all" ? true : o.kind === kind))
    .filter((o) => (unboundOnly ? !isBound(o) : true))
    .slice(0, 200);
  const st = w.opsStats;
  return (
    <div className="ops-tab">
      <div className="ops-filters">
        <div className="seg">
          <button type="button" className={scope === "open" ? "active" : ""} onClick={() => setScope("open")}>Открытые</button>
          <button type="button" className={scope === "all" ? "active" : ""} onClick={() => setScope("all")}>Все</button>
        </div>
        <div className="seg">
          {(["all", "MOVE", "PICK"] as Kind[]).map((k) => (
            <button type="button" key={k} className={kind === k ? "active" : ""} onClick={() => setKind(k)}>{{ all: "Все типы", MOVE: "Перемещения", PICK: "Сборка" }[k]}</button>
          ))}
        </div>
        <label className="check">
          <input type="checkbox" checked={unboundOnly} onChange={(e) => setUnboundOnly(e.target.checked)} /> только без привязки к схеме
        </label>
      </div>
      {w.mode === "live" && (
        <p className="ops-stats">
          Склад {w.layout.wareId ?? "?"}: {w.operations.length} операций в снимке · других складов отфильтровано {st.otherWarehouses} · открытых без привязки к схеме {st.unbound}
          {st.limitReached && " · выдача ограничена 500 строками — это не весь склад"}
        </p>
      )}
      <table className="ops-table">
        <thead>
          <tr><th>Операция</th><th>Тип</th><th>Статус WMS</th><th>Фаза</th><th>Откуда → куда</th><th>План / факт</th><th>Исполнитель</th></tr>
        </thead>
        <tbody>
          {list.map((o) => (
            <tr key={o.key} className={selected?.kind === "operation" && selected.id === o.key ? "selected" : ""} onClick={() => select({ kind: "operation", id: o.key })}>
              <td><b>{o.key}</b></td>
              <td>{kindLabel(o.subtype)}</td>
              <td>{o.source.rawStatus || "—"}</td>
              <td><span className={`chip tone-${phaseTone(o.phase)}`}>{PHASE_LABEL[o.phase]}</span></td>
              <td>
                {o.kind === "MOVE" ? `${o.from?.cell ?? "—"} → ${o.to?.cell ?? "—"}` : o.progress ? `${o.progress.done}/${o.progress.total} строк` : "—"}
                {!isBound(o) && <span className="unbound"> · нет на схеме</span>}
              </td>
              <td>{o.quantity.planned ?? "—"} / {o.quantity.confirmed ?? "—"} {o.quantity.unit ?? ""}</td>
              <td>{o.executor.label ?? o.executor.assignedTo ?? (o.executor.resourceId ? `RES:${o.executor.resourceId}` : "—")}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {list.length === 0 && <p className="muted pad">Нет операций по фильтру</p>}
    </div>
  );
}
