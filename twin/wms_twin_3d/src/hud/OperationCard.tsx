import { useEffect, useState } from "react";
import { type OperationDetail, fetchOperationDetail } from "../adapters/tmsLive";
import type { TwinExecutor, TwinOperation, TwinState } from "../contracts/twin";
import { useTwin } from "../store/twinStore";
import { PHASE_LABEL, POSITION_LABEL, kindLabel, phaseTone } from "../ui/opsFormat";
import { Chip, Row } from "./DetailCards";

// Паспорт складской операции (§4 спецификации): исходный тип/статус, контекст, груз, источник/назначение,
// исполнитель, план/факт/остаток, время, причина блокировки. Неизвестное показывается как «—».
export function OperationCard({ op, w }: { op: TwinOperation; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const detail = useOperationDetail(op, w);
  const view = detail?.caseOp ?? op;
  const progress = detail?.progress;
  const place = (l?: TwinOperation["from"]) => (l?.cell ? `${l.cell}${l.wareId ? ` · склад ${l.wareId}` : ""}${l.bound ? "" : " · нет на схеме"}` : "—");
  return (
    <>
      <div className="card-chips">
        <Chip tone={phaseTone(view.phase)}>{PHASE_LABEL[view.phase]}</Chip>
        <Chip tone="idle">{view.source.rawStatus || "—"}</Chip>
        <Chip tone={view.source.mode === "LIVE" ? "ok" : "warn"}>{view.source.mode}</Chip>
      </div>
      {(view.blockedReason || view.lastError) && <p className="reason">{view.blockedReason ?? view.lastError}</p>}
      {view.progress && (
        <div className="progress-line">
          <span>{view.progress.done}/{view.progress.total} {view.progress.label}</span>
          <span className="bar"><span className="bar-fill tone-ok" style={{ width: `${(view.progress.done / Math.max(1, view.progress.total)) * 100}%` }} /></span>
        </div>
      )}
      <Row k="Тип" v={`${kindLabel(view.subtype)} (${view.subtype})`} />
      <Row k="Источник данных" v={`${view.source.entity} #${view.source.id}`} />
      {view.context.sourceDoc && <Row k="Основание" v={view.context.sourceDoc} />}
      {view.context.waveCode && <Row k="Волна" v={view.context.waveCode} />}
      {view.context.orderNo && <Row k="Заказ" v={view.context.orderNo} />}
      {view.context.customer && <Row k="Адресат" v={view.context.customer} />}
      {view.context.stNumber && <Row k="СТ" v={w.sts[view.context.stNumber] ? <button type="button" className="link" onClick={() => select({ kind: "st", id: view.context.stNumber! })}>{view.context.stNumber}</button> : view.context.stNumber} />}
      {view.context.tripId && <Row k="Рейс" v={w.trips.some((t) => t.id === view.context.tripId) ? <button type="button" className="link" onClick={() => select({ kind: "trip", id: view.context.tripId! })}>{view.context.tripId}</button> : view.context.tripId} />}
      <Row k="Груз" v={[view.loadUnit.kind, view.loadUnit.uid, view.loadUnit.sscc && `SSCC ${view.loadUnit.sscc}`].filter(Boolean).join(" · ") || "—"} />
      {view.loadUnit.palletType && <Row k="Тип паллеты" v={view.loadUnit.palletType} />}
      {view.loadUnit.contentVersion && <Row k="Версия состава" v={view.loadUnit.contentVersion} />}
      {view.kind === "MOVE" && <Row k="Откуда" v={place(view.from)} />}
      <Row k={view.kind === "MOVE" ? "Куда" : "Текущая ячейка"} v={place(view.to)} />
      <Row k="План" v={qty(view.quantity.planned, view.quantity.unit)} />
      <Row k="Подтверждено" v={qty(progress ? String(progress.confirmed_quantity ?? "") : view.quantity.confirmed, view.quantity.unit)} />
      {progress && <Row k="Остаток семейства" v={qty(String(progress.remaining_quantity ?? ""), String(progress.unit_code ?? view.quantity.unit ?? ""))} />}
      {view.quantity.mode && <Row k="Режим" v={view.quantity.mode} />}
      <Row k="Исполнитель" v={executorText(view, w)} />
      {detail?.sync && <Row k="Доменная синхронизация" v={String(detail.sync.sync_status ?? "—")} />}
      <Row k="Создано" v={view.times.created ?? "—"} />
      {view.times.started && <Row k="Начато" v={view.times.started} />}
      {view.times.finished && <Row k="Завершено" v={view.times.finished} />}
      {view.times.cancelled && <Row k="Отменено" v={view.times.cancelled} />}
      <Row k="Наблюдение" v={`${view.source.observedAt}${view.source.mode === "LIVE" ? " (время сервера без зоны — как в WMS)" : ""}`} />
      <Row k="Траектория" v={view.routeBasis === "CALCULATED" ? "расчётная" : "не наблюдается — показано только намерение"} />
      {view.lines && view.lines.length > 0 && (
        <div className="sublist">
          <small>Строки ({view.lines.length})</small>
          {view.lines.map((l) => (
            <button type="button" key={l.id} className="subrow" onClick={() => l.bound && l.cell && select({ kind: "cell", id: l.cell })}>
              <b>{l.cell ?? "—"}</b>
              <span>{l.sku ?? "—"} · {l.picked ?? "?"}/{l.planned ?? "?"}{l.bound ? "" : " · нет на схеме"}</span>
              <Chip tone={l.status === "DONE" || l.status === "PICKED" ? "ok" : "idle"}>{l.status || "—"}</Chip>
            </button>
          ))}
        </div>
      )}
      {detail?.error && <p className="muted">Подробности: {detail.error}</p>}
      {detail?.raw && (
        <details className="raw">
          <summary>Исходные поля ({Object.keys(detail.raw).length})</summary>
          <pre>{JSON.stringify(detail.raw, null, 1)}</pre>
        </details>
      )}
    </>
  );
}

const qty = (v?: string, unit?: string) => (v ? `${v}${unit ? ` ${unit}` : ""}` : "—");

function executorText(op: TwinOperation, w: TwinState) {
  const e = op.executor;
  const ex = w.executors.find((x) => x.id === `RES:${e.resourceId}` || x.id === e.resourceId);
  const parts = [ex?.name ?? e.label, e.assignedTo && `пользователь ${e.assignedTo}`, e.equipmentId && `техника ${e.equipmentId}`, e.sessionId && `сессия ${e.sessionId}`].filter(Boolean);
  return parts.length ? parts.join(" · ") : "не назначен";
}

function useOperationDetail(op: TwinOperation, w: TwinState) {
  const [detail, setDetail] = useState<OperationDetail | undefined>();
  useEffect(() => {
    setDetail(undefined);
    if (op.source.mode !== "LIVE") return;
    let alive = true;
    void fetchOperationDetail(op, new Set(w.cells.map((c) => c.id))).then((d) => { if (alive) setDetail(d); });
    return () => { alive = false; };
    // Подробности перечитываются при выборе другой операции или смене исходного статуса (§14).
  }, [op.key, op.source.rawStatus]);
  return detail;
}

export function ExecutorCard({ ex, w }: { ex: TwinExecutor; w: TwinState }) {
  const select = useTwin((s) => s.select);
  const ops = w.operations.filter((o) => o.executor.resourceId && (`RES:${o.executor.resourceId}` === ex.id || o.executor.resourceId === ex.id));
  return (
    <>
      <div className="card-chips">
        <Chip tone={ex.positionBasis === "OBSERVED_CELL" ? "ok" : ex.positionBasis === "SIMULATED" ? "warn" : "idle"}>{POSITION_LABEL[ex.positionBasis]}</Chip>
        {ex.sessionStatus && <Chip tone="info">сессия {ex.sessionStatus}</Chip>}
      </div>
      <Row k="Тип" v={ex.kind} />
      <Row k="Код" v={ex.code} />
      <Row k="Статус" v={ex.status || "—"} />
      {ex.wareId && <Row k="Склад" v={ex.wareId} />}
      {ex.equipmentCode && <Row k="Техника" v={ex.equipmentCode} />}
      <Row k="Последняя ячейка" v={ex.lastCell ? `${ex.lastCell}${ex.lastPositionAt ? ` · ${ex.lastPositionAt}` : ""}` : "—"} />
      {ex.heartbeatAt && <Row k="Heartbeat" v={ex.heartbeatAt} />}
      {ex.activeTaskId && <Row k="Текущее задание" v={ex.activeTaskId} />}
      <div className="sublist">
        <small>Операции исполнителя</small>
        {ops.length === 0 && <span className="muted">Нет в снимке</span>}
        {ops.map((o) => (
          <button type="button" key={o.key} className="subrow" onClick={() => select({ kind: "operation", id: o.key })}>
            <b>{o.key}</b>
            <span>{kindLabel(o.subtype)}</span>
            <Chip tone={phaseTone(o.phase)}>{o.source.rawStatus}</Chip>
          </button>
        ))}
      </div>
    </>
  );
}
