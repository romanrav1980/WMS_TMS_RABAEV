import { caseStage, isClosedWave, preparationComplete } from "./executionState";
import { IsoStageScene } from "../IsoStageScene";
import type { IsoStage } from "../IsoStageScene";
import type { Wave } from "../types";
import { shiftHelp } from "./help";
import type { WaveDetail } from "./types";

// Поток волн по этапам склада. Этап — по фактическим данным readiness/pick-readiness и статусам CASE-заданий волны;
// без прочитанных деталей и фактов сборки волна стоит в «детали не прочитаны», а не в выдуманном этапе.

export type Stage = "PREP" | "RELEASE" | "REPL" | "PICK" | "STAGE" | "PACKED" | "SHIPPED" | "CLEAR" | "UNREAD" | "ARCHIVE";
export const STAGES: (IsoStage & { id: Stage })[] = [
  { id: "PREP", title: "Подготовка (до запуска)", x: 0, y: 0 }, { id: "RELEASE", title: "Ждёт разрешения отбора", x: 1, y: 0 },
  { id: "REPL", title: "Пополнение отбора", x: 2, y: 0 }, { id: "PICK", title: "Сборка", x: 3, y: 0 },
  { id: "STAGE", title: "Размещение / недостачи", x: 0, y: 1 }, { id: "PACKED", title: "Собрано: контроль, погрузка", x: 1, y: 1 },
  { id: "SHIPPED", title: "Отгружено, волна не закрыта", x: 2, y: 1 }, { id: "CLEAR", title: "Открытых блокировок нет", x: 3, y: 1 },
  { id: "UNREAD", title: "Детали не прочитаны", x: 1, y: 2, dashed: true }, { id: "ARCHIVE", title: "Завершены / отменены", x: 2, y: 2 },
];
const BY_CASE = { PICKING: "PICK", AWAITING_SHIPMENT: "PACKED", SHIPPED: "SHIPPED" } as const;

/** cases — статусы CASE-заданий волны из полной (не обрезанной лимитом) выборки сборки; без них стадия сборки не угадывается. */
export function stageOf(w: Wave, d: WaveDetail | undefined, cases?: string[]): Stage {
  if (isClosedWave(w.status)) return "ARCHIVE";
  if (w.status === "PREVIEW") return "PREP";
  const actual = caseStage(cases ?? []);
  if (!preparationComplete(d) || !d?.readiness.data) return actual ? BY_CASE[actual] : "UNREAD";
  if (d.pick.data && !d.pick.data.released_at) return "RELEASE";
  const types = new Set(d.readiness.data.blockers.map(b => b.blocker_type));
  if (types.has("REPLENISHMENT")) return "REPL";
  if (types.has("CASE_PICK") || actual === "PICKING") return "PICK";
  if (types.size) return "STAGE";
  return actual ? BY_CASE[actual] : "CLEAR";
}

type Props = { waves: Wave[]; details: Map<number, WaveDetail>; riskyWaves: Set<number>; selected: number | null; onSelect: (id: number) => void; cases?: Map<number, string[]> };

export function WaveFlowScene({ waves, details, riskyWaves, selected, onSelect, cases }: Props) {
  const items = waves.map(w => {
    const risky = riskyWaves.has(w.pick_wave_id), stage = stageOf(w, details.get(w.pick_wave_id), cases?.get(w.pick_wave_id));
    return { id: w.pick_wave_id, stage, tone: risky ? "bad" as const : w.status === "PREVIEW" || !preparationComplete(details.get(w.pick_wave_id)) ? "plan" as const : "ok" as const,
      label: `Волна ${w.wave_code}`, title: `Волна ${w.wave_code} · ${STAGES.find(s => s.id === stage)?.title} · заказов ${w.order_count}, заданий ${w.task_count}${risky ? " · есть подтверждённые блокировки" : ""}. ${shiftHelp.wave.text}` };
  });
  return <IsoStageScene stages={STAGES} items={items} selected={selected} onSelect={id => onSelect(Number(id))} ariaLabel="Поток волн по этапам склада (условная схема)"
    stageHelpId={shiftHelp.stage.id} itemHelpId={shiftHelp.wave.id} stageHelp={shiftHelp.stage.text} />;
}
