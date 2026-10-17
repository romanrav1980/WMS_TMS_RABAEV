import { useEffect, useRef } from "react";
import type { AssemblyStep } from "../contracts";

function beepOnce() {
  try {
    const ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    const osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.frequency.value = 880; osc.connect(gain); gain.connect(ctx.destination);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    osc.start(); osc.stop(ctx.currentTime + 0.15);
    osc.onended = () => ctx.close();
  } catch { /* звук недоступен — визуальный успех остаётся */ }
}

const LABEL: Record<AssemblyStep["state"], string> = {
  WAITING_BEFORE: "Подготовка весов…", ARMED: "", READY: "Проверяем вес…", APPLIED: "Укладка подтверждена", DISCREPANCY: "Расхождение", CANCELLED: "Шаг отменён после сверки",
};

/** Visual/audible success fires only on a real server APPLIED, once per step_id. Before ARMED the operator is never
 *  invited to place anything (WAITING_BEFORE shows no placement prompt at all). */
export function StepStage({ step, onPlaced, placing, paused, held }: { step: AssemblyStep; onPlaced: () => void; placing: boolean; paused?: boolean; held?: boolean }) {
  const celebrated = useRef<string | null>(null);
  useEffect(() => { if (step.state === "APPLIED" && celebrated.current !== step.step_id) { celebrated.current = step.step_id; beepOnce(); } }, [step.state, step.step_id]);

  return <div className={"asm-step asm-step-" + step.state.toLowerCase()} aria-live="polite">
    <div className="asm-step-big">
      <b>{step.article}</b><span>{step.quantity} шт</span>
    </div>
    {paused && <p className="asm-note">{held ? "Укладка остановлена. Выполните подтверждённые шаги сверки ниже." : "Ожидаем подтверждённое состояние. Новые физические действия приостановлены."}</p>}
    {!paused && step.state === "WAITING_BEFORE" && <p className="asm-wait">{LABEL.WAITING_BEFORE}</p>}
    {!paused && step.state === "ARMED" && <>
      <p className="asm-armed">Положите товар</p>
      {step.confirmation_mode === "BUTTON" && !step.button_intent && <button type="button" disabled={placing} onClick={onPlaced} title="Подтвердить, что товар физически положен" data-help-id="assembly.placed">
        {placing ? "…" : "Положил"}</button>}
      {step.confirmation_mode === "BUTTON" && step.button_intent && <p className="asm-note">Намерение зафиксировано, ждём подтверждения весов.</p>}
      {step.confirmation_mode === "AUTO" && <p className="asm-note">После стабилизации веса примется автоматически.</p>}
    </>}
    {!paused && step.state === "READY" && <p className="asm-ready">{LABEL.READY}</p>}
    {!paused && step.state === "APPLIED" && <p className="asm-applied">✓ {LABEL.APPLIED}</p>}
    {!paused && step.state === "CANCELLED" && <p className="asm-note">{LABEL.CANCELLED}. Товарная проводка по этому шагу не выполнена.</p>}
    {!paused && step.state === "DISCREPANCY" && <p className="asm-discrepancy" role="alert">{LABEL.DISCREPANCY}{step.block_reason ? ": " + step.block_reason : ""}</p>}
  </div>;
}



