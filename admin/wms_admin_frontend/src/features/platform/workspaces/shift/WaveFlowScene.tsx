import { preparationComplete } from "./executionState";
import { IsoStageScene } from "../IsoStageScene";
import type { IsoStage } from "../IsoStageScene";
import type { Wave } from "../types";
import { shiftHelp } from "./help";
import type { WaveDetail } from "./types";

// Поток волн по этапам склада. Этап — по фактическим данным readiness/pick-readiness; без прочитанных деталей волна стоит
// в «детали не прочитаны», а не в выдуманном этапе.

export type Stage = "PREP" | "RELEASE" | "REPL" | "PICK" | "STAGE" | "CLEAR" | "UNREAD";
export const STAGES: (IsoStage & { id: Stage })[] = [
  { id: "PREP", title: "Подготовка (до запуска)", x: 0, y: 0 }, { id: "RELEASE", title: "Ждёт разрешения отбора", x: 1, y: 0 },
  { id: "REPL", title: "Пополнение отбора", x: 2, y: 0 }, { id: "PICK", title: "Сборка", x: 0, y: 1 },
  { id: "STAGE", title: "Размещение / недостачи", x: 1, y: 1 }, { id: "CLEAR", title: "Открытых блокировок нет", x: 2, y: 1 },
  { id: "UNREAD", title: "Детали не прочитаны", x: 3, y: 0.5, dashed: true },
];

export function stageOf(w: Wave, d: WaveDetail | undefined): Stage {
  if (w.status === "PREVIEW") return "PREP";
  if (!preparationComplete(d) || !d?.readiness.data) return "UNREAD";
  if (d.pick.data && !d.pick.data.released_at) return "RELEASE";
  const types = new Set(d.readiness.data.blockers.map(b => b.blocker_type));
  if (types.has("REPLENISHMENT")) return "REPL";
  if (types.has("CASE_PICK")) return "PICK";
  if (types.size) return "STAGE";
  return "CLEAR";
}

type Props = { waves: Wave[]; details: Map<number, WaveDetail>; riskyWaves: Set<number>; selected: number | null; onSelect: (id: number) => void };

export function WaveFlowScene({ waves, details, riskyWaves, selected, onSelect }: Props) {
  const items = waves.map(w => {
    const risky = riskyWaves.has(w.pick_wave_id);
    return { id: w.pick_wave_id, stage: stageOf(w, details.get(w.pick_wave_id)), tone: risky ? "bad" as const : w.status === "PREVIEW" || !preparationComplete(details.get(w.pick_wave_id)) ? "plan" as const : "ok" as const,
      label: `Волна ${w.wave_code}`, title: `Волна ${w.wave_code} · ${w.status} · заказов ${w.order_count}, заданий ${w.task_count}${risky ? " · есть подтверждённые блокировки" : ""}. ${shiftHelp.wave.text}` };
  });
  return <IsoStageScene stages={STAGES} items={items} selected={selected} onSelect={id => onSelect(Number(id))} ariaLabel="Поток волн по этапам склада (условная схема)"
    stageHelpId={shiftHelp.stage.id} itemHelpId={shiftHelp.wave.id} stageHelp={shiftHelp.stage.text} />;
}
