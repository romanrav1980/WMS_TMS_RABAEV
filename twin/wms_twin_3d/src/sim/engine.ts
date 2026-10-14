import type { TwinState } from "../contracts/twin";
import { detectCollisions } from "./collisions";
import { simExecutors, simOperations } from "./ops";
import { createRng, type Rng } from "./rng";
import { createWorld } from "./seed";
import { spawnTrips, stepTrips } from "./transport";
import { planTasks, stepWarehouse } from "./warehouse";

// Мок-источник: детерминированная симуляция по шагам процессов WMS/TMS.
// Один шаг — не больше MAX_STEP секунд модельного времени, чтобы высокая скорость не «перепрыгивала» события.
const MAX_STEP = 1.5;
const COLLISION_PERIOD = 2;

export type Simulator = { world: TwinState; advance: (simSeconds: number) => void };

export function createSimulator(seed = 20261013): Simulator {
  const rng: Rng = createRng(seed);
  const world = createWorld(seed, rng);
  let sinceCollisions = 0;
  const stepOnce = (dt: number) => {
    world.simTime += dt;
    spawnTrips(world, rng);
    stepTrips(world, dt);
    planTasks(world);
    stepWarehouse(world, dt, rng);
    sinceCollisions += dt;
    if (sinceCollisions >= COLLISION_PERIOD) {
      detectCollisions(world, sinceCollisions);
      sinceCollisions = 0;
    }
    const hourAgo = world.simTime - 3600;
    while (world.counters.pickTimes.length && world.counters.pickTimes[0] < hourAgo) world.counters.pickTimes.shift();
  };
  // Прогрев: к открытию страницы смена уже идёт, на территории есть машины и задания.
  for (let t = 0; t < 50 * 60; t += MAX_STEP) stepOnce(MAX_STEP);
  return {
    world,
    advance(simSeconds: number) {
      let left = simSeconds;
      while (left > 1e-6) {
        const dt = Math.min(MAX_STEP, left);
        stepOnce(dt);
        left -= dt;
      }
      world.operations = simOperations(world);
      world.executors = simExecutors(world);
      world.version += 1;
    }
  };
}
