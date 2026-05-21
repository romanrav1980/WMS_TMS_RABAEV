/**
 * useRouteGenerator.ts — Алгоритмы генерации мастер-маршрута обхода.
 *
 * Мастер-маршрут обходит ВСЕ ячейки отбора (L/R) ровно по одному разу.
 * Это статический порядок, записываемый в RRL_PICK_ROUTE_CELL.PICK_SEQUENCE.
 *
 * Доступные алгоритмы:
 *   Z          — прямой проход, аллея за аллеей (базовый)
 *   U          — U-поворот у дальнего торца каждой аллеи
 *   SNAKE      — змейка, минимум разворотов
 *   TWO_BLOCK  — склад разрезается пополам, два встречных потока
 *   ZONE_SWEEP — сначала обойти зону A, потом B, потом C...
 *   LINEAR     — ручной порядок (алгоритм не меняет pickSeqs, управляет UI)
 */

import {
  AisleDef,
  GridData,
  ROLE,
  calcRouteLengthM,
} from "./gridData";

// ---------------------------------------------------------------------------
// Тип алгоритма
// ---------------------------------------------------------------------------

export type RoutePattern =
  | "Z"
  | "U"
  | "SNAKE"
  | "TWO_BLOCK"
  | "ZONE_SWEEP"
  | "LINEAR";

export interface RouteGenParams {
  /** Доля склада для front-блока в TWO_BLOCK (0–1, по умолчанию 0.5). */
  twoBlockSplit?: number;
  /** Базовый паттерн внутри каждой зоны для ZONE_SWEEP. */
  zoneSweepBase?: "Z" | "U" | "SNAKE";
  /** Карта cell-index → zone_code для ZONE_SWEEP. */
  zoneMap?: Map<number, string>;
  /** Высота бая в метрах (для расчёта длины). */
  bayHeightM?: number;
}

export interface RouteGenResult {
  /** Суммарная длина маршрута в метрах (приблизительная). */
  lengthMeters: number;
  /** Число ячеек, получивших порядковый номер. */
  cellCount: number;
}

// ---------------------------------------------------------------------------
// Точка входа
// ---------------------------------------------------------------------------

/**
 * Запустить выбранный алгоритм, записать pick_sequence в data.pickSeqs.
 * Возвращает статистику результата.
 */
export function generateRoute(
  pattern: RoutePattern,
  data: GridData,
  aisles: AisleDef[],
  params: RouteGenParams = {},
): RouteGenResult {
  // Сортируем аллеи по расстоянию от начала склада (слева направо)
  const sorted = [...aisles].sort((a, b) => a.distanceMeters - b.distanceMeters);

  // Сброс предыдущих номеров
  data.clearRoute();

  switch (pattern) {
    case "Z":          genZ(data, sorted);                                              break;
    case "U":          genU(data, sorted);                                              break;
    case "SNAKE":      genSnake(data, sorted);                                          break;
    case "TWO_BLOCK":  genTwoBlock(data, sorted, params.twoBlockSplit ?? 0.5);          break;
    case "ZONE_SWEEP": genZoneSweep(data, sorted, params);                              break;
    case "LINEAR":     /* ручной — не трогаем pickSeqs */                               break;
  }

  const bayH = params.bayHeightM ?? 1.5;
  const lengthMeters = pattern === "LINEAR" ? 0 : calcRouteLengthM(data, aisles, bayH);
  const cellCount    = data.pickCellCount;

  return { lengthMeters, cellCount };
}

// ---------------------------------------------------------------------------
// Z-образный
// ---------------------------------------------------------------------------

/**
 * Z-образный (Sweep):
 *   Для каждой аллеи слева направо:
 *     → левый столбец сверху вниз
 *     → правый столбец сверху вниз
 *
 * Самый простой и предсказуемый паттерн.
 * Оптимален для равномерно заполненного склада.
 */
function genZ(data: GridData, sortedAisles: AisleDef[]): void {
  let seq = 0;
  for (const aisle of sortedAisles) {
    // Левый столбец сверху вниз
    for (let r = 0; r < data.rows; r++) {
      const i = r * data.cols + aisle.leftCol;
      if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
        data.pickSeqs[i] = seq++;
      }
    }
    // Правый столбец сверху вниз
    for (let r = 0; r < data.rows; r++) {
      const i = r * data.cols + aisle.rightCol;
      if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
        data.pickSeqs[i] = seq++;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// U-образный
// ---------------------------------------------------------------------------

/**
 * U-образный (Return):
 *   Для каждой аллеи слева направо:
 *     → левый столбец сверху вниз (бай 1 → N)
 *     → правый столбец снизу вверх (бай N → 1)
 *
 * Picker разворачивается у дальнего торца аллеи и не возвращается к входу
 * перед переходом в следующую аллею.
 * Экономит расстояние по сравнению с Z на ~5–10%.
 */
function genU(data: GridData, sortedAisles: AisleDef[]): void {
  let seq = 0;
  for (const aisle of sortedAisles) {
    // Левый столбец — вниз
    for (let r = 0; r < data.rows; r++) {
      const i = r * data.cols + aisle.leftCol;
      if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
        data.pickSeqs[i] = seq++;
      }
    }
    // Правый столбец — вверх
    for (let r = data.rows - 1; r >= 0; r--) {
      const i = r * data.cols + aisle.rightCol;
      if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
        data.pickSeqs[i] = seq++;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Змейка (SNAKE / S-shape)
// ---------------------------------------------------------------------------

/**
 * Змейка:
 *   Каждый следующий столбец начинается с того конца, где закончил предыдущий.
 *   Это минимизирует число разворотов на 180°.
 *
 * Пример для 2 аллей (4 столбца L1 R1 L2 R2):
 *   L1[1→N]↓  R1[N→1]↑  R2[1→N]↓  L2[N→1]↑  ...
 *
 * Обратите внимание: для аллеи A2 мы начинаем с R2 (туда), а потом L2 (обратно),
 * т.к. последний шаг предыдущей аллеи был у дальнего торца.
 */
function genSnake(data: GridData, sortedAisles: AisleDef[]): void {
  let seq    = 0;
  let goDown = true; // направление для первого столбца каждой аллеи

  for (const aisle of sortedAisles) {
    // Для змейки порядок столбцов внутри аллеи тоже чередуется
    const cols = goDown
      ? [aisle.leftCol, aisle.rightCol]
      : [aisle.rightCol, aisle.leftCol];

    for (const col of cols) {
      const rows = goDown
        ? range(0, data.rows)
        : range(data.rows - 1, -1, -1);

      for (const r of rows) {
        const i = r * data.cols + col;
        if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
          data.pickSeqs[i] = seq++;
        }
      }
      // После каждого столбца меняем направление
      goDown = !goDown;
    }
  }
}

// ---------------------------------------------------------------------------
// Двухблочный (TWO_BLOCK)
// ---------------------------------------------------------------------------

/**
 * Двухблочный:
 *   Склад разрезается горизонтально на front и back.
 *   Front-блок (баи 1..mid): аллеи слева направо, Z-паттерн сверху вниз.
 *   Back-блок  (баи mid..N): аллеи справа налево, Z-паттерн снизу вверх.
 *   Два потока встречаются в середине.
 *
 * Экономит расстояние ~15–20% на длинных складах (>30 баев).
 *
 * @param splitFraction Доля склада для front-блока (0.0–1.0, default 0.5)
 */
function genTwoBlock(
  data: GridData,
  sortedAisles: AisleDef[],
  splitFraction: number,
): void {
  let seq = 0;
  const mid = Math.ceil(data.rows * splitFraction);

  // Front-блок: аллеи слева направо, баи 0..mid-1, вниз
  for (const aisle of sortedAisles) {
    for (const col of [aisle.leftCol, aisle.rightCol]) {
      for (let r = 0; r < mid; r++) {
        const i = r * data.cols + col;
        if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
          data.pickSeqs[i] = seq++;
        }
      }
    }
  }

  // Back-блок: аллеи справа налево, баи rows-1..mid, вверх
  for (const aisle of [...sortedAisles].reverse()) {
    for (const col of [aisle.rightCol, aisle.leftCol]) {
      for (let r = data.rows - 1; r >= mid; r--) {
        const i = r * data.cols + col;
        if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
          data.pickSeqs[i] = seq++;
        }
      }
    }
  }
}

// ---------------------------------------------------------------------------
// По зонам (ZONE_SWEEP)
// ---------------------------------------------------------------------------

/**
 * По зонам:
 *   Сначала обходятся все ячейки зоны A, затем B, затем C (по алфавиту).
 *   Внутри каждой зоны применяется базовый паттерн (Z, U или SNAKE).
 *
 * Полезно для складов с температурными зонами или зонами по типу товара.
 * Если zoneMap не передана — degrade к Z.
 */
function genZoneSweep(
  data: GridData,
  sortedAisles: AisleDef[],
  params: RouteGenParams,
): void {
  const zoneMap  = params.zoneMap;
  const base     = params.zoneSweepBase ?? "U";

  if (!zoneMap || zoneMap.size === 0) {
    // Нет зон — применяем базовый паттерн ко всему складу
    const tmpData = { ...data, clearRoute: () => {} } as GridData;
    switch (base) {
      case "Z":    genZ(tmpData, sortedAisles);    break;
      case "U":    genU(tmpData, sortedAisles);    break;
      case "SNAKE": genSnake(tmpData, sortedAisles); break;
    }
    return;
  }

  // Получить уникальные коды зон, отсортировать
  const zones = [...new Set(zoneMap.values())].sort();
  let seq = 0;

  for (const zone of zones) {
    // Отобрать аллеи, у которых есть хотя бы одна ячейка данной зоны
    const zoneAisles = sortedAisles.filter((aisle) => {
      for (let r = 0; r < data.rows; r++) {
        const iL = r * data.cols + aisle.leftCol;
        const iR = r * data.cols + aisle.rightCol;
        if (zoneMap.get(iL) === zone || zoneMap.get(iR) === zone) return true;
      }
      return false;
    });

    // Обойти ячейки данной зоны в порядке базового паттерна
    for (const aisle of zoneAisles) {
      const colPairs: Array<[number, boolean]> = base === "U"
        ? [[aisle.leftCol, true], [aisle.rightCol, false]]
        : [[aisle.leftCol, true], [aisle.rightCol, true]];

      for (const [col, downward] of colPairs) {
        const rows = downward ? range(0, data.rows) : range(data.rows - 1, -1, -1);
        for (const r of rows) {
          const i = r * data.cols + col;
          if (
            (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) &&
            zoneMap.get(i) === zone
          ) {
            data.pickSeqs[i] = seq++;
          }
        }
      }
    }
  }

  // Ячейки без зоны — добавить в конец
  for (const aisle of sortedAisles) {
    for (const col of [aisle.leftCol, aisle.rightCol]) {
      for (let r = 0; r < data.rows; r++) {
        const i = r * data.cols + col;
        if (
          (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) &&
          data.pickSeqs[i] < 0 &&
          !zoneMap.has(i)
        ) {
          data.pickSeqs[i] = seq++;
        }
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Утилита range()
// ---------------------------------------------------------------------------

/** Аналог Python range(): генерирует массив целых чисел. */
function range(start: number, stop: number, step = 1): number[] {
  const result: number[] = [];
  if (step > 0) {
    for (let i = start; i < stop; i += step) result.push(i);
  } else {
    for (let i = start; i > stop; i += step) result.push(i);
  }
  return result;
}
