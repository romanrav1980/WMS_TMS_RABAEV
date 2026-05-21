/**
 * gridData.ts — Слой данных сеточного редактора топологии склада.
 *
 * Все структуры данных намеренно хранятся в TypedArrays, а не в объектах JavaScript,
 * чтобы 15 000 ячеек занимали ~135 KB вместо ~6 MB и не нагружали GC.
 *
 * Ключевые классы:
 *   GridData          — компактное хранилище ролей и атрибутов каждой ячейки
 *   SelectionBitSet   — битовый набор для выделения ячеек (469 байт на 15 000 ячеек)
 *   OffscreenGridBuffer — кэш-слой: рисует всё один раз, отдаёт через drawImage
 */

// ---------------------------------------------------------------------------
// Роли ячеек (хранятся в Uint8Array, значения 0–3)
// ---------------------------------------------------------------------------

/** Числовые коды ролей. Uint8 → экономим память. */
export const ROLE = {
  EMPTY:   0 as const,
  LEFT:    1 as const,  // левая сторона аллеи (side_code='L')
  RIGHT:   2 as const,  // правая сторона аллеи (side_code='R')
  PASSAGE: 3 as const,  // межстеллажный коридор (не хранит товар)
} as const;

export type RoleValue = 0 | 1 | 2 | 3;

/** Цвета ролей для Canvas fillStyle. */
export const ROLE_COLORS: Record<number, string> = {
  [ROLE.LEFT]:    "#3B82F6",  // синий
  [ROLE.RIGHT]:   "#F97316",  // оранжевый
  [ROLE.PASSAGE]: "#E5E7EB",  // светло-серый
};

/** Человекочитаемые метки ролей для UI. */
export const ROLE_LABELS: Record<number, string> = {
  [ROLE.LEFT]:    "Левая (L)",
  [ROLE.RIGHT]:   "Правая (R)",
  [ROLE.PASSAGE]: "Проход",
};

// ---------------------------------------------------------------------------
// Определение аллеи (пара столбцов L+R и их проход)
// ---------------------------------------------------------------------------

export interface AisleDef {
  /** Временный локальный ID: 'A1', 'A2', ... */
  id: string;
  /** Отображаемое название аллеи. */
  label: string;
  /** 0-based индекс столбца левой стороны. */
  leftCol: number;
  /** 0-based индекс столбца правой стороны. */
  rightCol: number;
  /** 0-based индекс столбца прохода (может отсутствовать). */
  passageCol?: number;
  /**
   * Абсолютное расстояние аллеи от начала склада, в метрах.
   * По умолчанию = aisleIndex × aisleWidthMeters.
   */
  distanceMeters: number;
  /** Если true — расстояние задано пользователем вручную, не пересчитывается автоматически. */
  customDistance: boolean;
}

// ---------------------------------------------------------------------------
// Настройки сетки
// ---------------------------------------------------------------------------

export interface GridSettings {
  /** Ширина одного межстеллажного прохода, метры. По умолчанию 3.5. */
  aisleWidthMeters: number;
  /** Высота одного бая (строки), метры. Используется для расчёта длины маршрута. */
  bayHeightMeters: number;
}

export const DEFAULT_SETTINGS: GridSettings = {
  aisleWidthMeters: 3.5,
  bayHeightMeters:  1.5,
};

// ---------------------------------------------------------------------------
// GridData — компактное хранилище ячеек
// ---------------------------------------------------------------------------

/**
 * GridData хранит атрибуты всех ячеек в параллельных TypedArray.
 * Индекс ячейки: i = (row-1)*cols + (col-1), где row и col — 1-based.
 *
 * Память для 15 000 ячеек:
 *   roles    Uint8Array  × 1 байт = 15 KB
 *   aisleIdx Int16Array  × 2 байт = 30 KB
 *   pickSeqs Int32Array  × 4 байт = 60 KB
 *   slotCols Uint8Array  × 1 байт = 15 KB
 *   slotRows Uint8Array  × 1 байт = 15 KB
 *   Итого ≈ 135 KB (vs ~6 MB для массива объектов)
 */
export class GridData {
  readonly rows: number;
  readonly cols: number;

  /** Роль каждой ячейки: 0=empty, 1=left, 2=right, 3=passage */
  readonly roles: Uint8Array;

  /**
   * Индекс аллеи в массиве aisles[] для каждой ячейки.
   * -1 означает «не привязана к аллее».
   */
  readonly aisleIdx: Int16Array;

  /**
   * Порядковый номер обхода (PICK_SEQUENCE) для каждой ячейки.
   * -1 означает «маршрут ещё не рассчитан».
   */
  readonly pickSeqs: Int32Array;

  /** Деление ячейки по ширине (мелкоштучные слоты): 0 или 1 = нет деления, 2–5. */
  readonly slotCols: Uint8Array;

  /** Деление ячейки по высоте (мелкоштучные слоты): 0 или 1 = нет деления, 2–5. */
  readonly slotRows: Uint8Array;

  constructor(rows: number, cols: number) {
    this.rows     = rows;
    this.cols     = cols;
    const n       = rows * cols;
    this.roles    = new Uint8Array(n);
    this.aisleIdx = new Int16Array(n).fill(-1);
    this.pickSeqs = new Int32Array(n).fill(-1);
    this.slotCols = new Uint8Array(n);
    this.slotRows = new Uint8Array(n);
  }

  /** Перевод 1-based (row, col) → плоский индекс массива. */
  idx(row: number, col: number): number {
    return (row - 1) * this.cols + (col - 1);
  }

  /** Обратное преобразование: плоский индекс → 1-based row. */
  rowOf(i: number): number {
    return Math.floor(i / this.cols) + 1;
  }

  /** Обратное преобразование: плоский индекс → 1-based col. */
  colOf(i: number): number {
    return (i % this.cols) + 1;
  }

  /** Общее число ячеек. */
  get size(): number {
    return this.rows * this.cols;
  }

  /** Число ячеек с ролью LEFT или RIGHT (ячейки отбора). */
  get pickCellCount(): number {
    let n = 0;
    for (let i = 0; i < this.size; i++) {
      if (this.roles[i] === ROLE.LEFT || this.roles[i] === ROLE.RIGHT) n++;
    }
    return n;
  }

  /** Сброс всех pickSeqs в -1 (при пересчёте маршрута). */
  clearRoute(): void {
    this.pickSeqs.fill(-1);
  }

  /**
   * Создаёт глубокую копию данных.
   * Используется при отмене изменений (undo) и для передачи в воркер.
   */
  clone(): GridData {
    const copy = new GridData(this.rows, this.cols);
    copy.roles.set(this.roles);
    copy.aisleIdx.set(this.aisleIdx);
    copy.pickSeqs.set(this.pickSeqs);
    copy.slotCols.set(this.slotCols);
    copy.slotRows.set(this.slotRows);
    return copy;
  }
}

// ---------------------------------------------------------------------------
// SelectionBitSet — битовый набор для выделения ячеек
// ---------------------------------------------------------------------------

/**
 * SelectionBitSet хранит состояние «выделена / не выделена» для каждой ячейки
 * в виде битового массива (1 бит на ячейку).
 *
 * Память: 15 000 ячеек → 469 байт.
 * Для сравнения: Set<string> с теми же ключами → ~1.5 MB.
 *
 * Операции has/set/clr работают за O(1) через битовые сдвиги.
 */
export class SelectionBitSet {
  private readonly bits: Uint32Array;
  private readonly capacity: number;
  private _count = 0;

  constructor(capacity: number) {
    this.capacity = capacity;
    // Каждое Uint32 хранит 32 ячейки. Округляем вверх.
    this.bits = new Uint32Array(Math.ceil(capacity / 32));
  }

  /** Проверить, выделена ли ячейка с данным индексом. */
  has(i: number): boolean {
    return !!(this.bits[i >>> 5] & (1 << (i & 31)));
  }

  /** Выделить ячейку. */
  set(i: number): void {
    if (!this.has(i)) {
      this.bits[i >>> 5] |= (1 << (i & 31));
      this._count++;
    }
  }

  /** Снять выделение с ячейки. */
  clr(i: number): void {
    if (this.has(i)) {
      this.bits[i >>> 5] &= ~(1 << (i & 31));
      this._count--;
    }
  }

  /** Переключить выделение ячейки. */
  toggle(i: number): void {
    if (this.has(i)) this.clr(i); else this.set(i);
  }

  /** Снять выделение со всех ячеек. */
  clearAll(): void {
    this.bits.fill(0);
    this._count = 0;
  }

  /** Число выделенных ячеек. */
  get count(): number {
    return this._count;
  }

  /**
   * Выделить все ячейки в прямоугольнике (0-based индексы включительно).
   * @param additive Если true — добавить к текущему выделению, не сбрасывать.
   */
  selectRect(
    r1: number, c1: number,
    r2: number, c2: number,
    cols: number,
    additive: boolean,
  ): void {
    if (!additive) this.clearAll();
    const rowMin = Math.min(r1, r2);
    const rowMax = Math.max(r1, r2);
    const colMin = Math.min(c1, c2);
    const colMax = Math.max(c1, c2);
    for (let r = rowMin; r <= rowMax; r++) {
      for (let c = colMin; c <= colMax; c++) {
        this.set(r * cols + c);
      }
    }
  }

  /** Выделить весь столбец (0-based). */
  selectCol(col: number, rows: number, cols: number, additive: boolean): void {
    if (!additive) this.clearAll();
    for (let r = 0; r < rows; r++) this.set(r * cols + col);
  }

  /** Выделить всю строку (0-based). */
  selectRow(row: number, cols: number, additive: boolean): void {
    if (!additive) this.clearAll();
    const base = row * cols;
    for (let c = 0; c < cols; c++) this.set(base + c);
  }

  /** Итерация по всем выделенным индексам. Удобен для назначения ролей. */
  forEach(cb: (i: number) => void): void {
    for (let w = 0; w < this.bits.length; w++) {
      let word = this.bits[w];
      while (word) {
        // Найти позицию младшего установленного бита
        const bit = word & (-word);
        const i = w * 32 + Math.log2(bit) | 0;
        if (i < this.capacity) cb(i);
        word ^= bit; // убрать этот бит
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Размеры ячеек на canvas (константы)
// ---------------------------------------------------------------------------

/** Ширина одной ячейки на canvas, пиксели (при zoom=1). */
export const CELL_W = 22;

/** Высота одной ячейки на canvas, пиксели (при zoom=1). */
export const CELL_H = 18;

/** Ширина колонки заголовков строк (bay numbers) в пикселях. */
export const HEADER_ROW_W = 40;

/** Высота строки заголовков столбцов (column labels) в пикселях. */
export const HEADER_COL_H = 28;

/** Высота полосы с метками аллей над заголовками столбцов. */
export const AISLE_LABEL_H = 18;

// ---------------------------------------------------------------------------
// OffscreenGridBuffer — кэш рендера для zoom/pan без пересчёта ячеек
// ---------------------------------------------------------------------------

/**
 * OffscreenGridBuffer — ключевая оптимизация для 15 000 ячеек.
 *
 * Проблема: при zoom/pan нужно перерисовывать все видимые ячейки на каждый кадр.
 * При 15 000 ячеек и полном отзуме это 15 000 fillRect ≈ 8–20 ms → < 60 fps.
 *
 * Решение: хранить полный рендер склада в offscreen-буфере.
 * При zoom/pan — один drawImage() ≈ 0.5–1 ms, независимо от числа ячеек.
 * Пересчёт offscreen происходит только при изменении ролей (редкая операция).
 *
 * Поддержка: OffscreenCanvas — Chrome 69+, Firefox 105+, Safari 16.4+.
 * Fallback для старых браузеров: обычный <canvas> за пределами DOM.
 */
export class OffscreenGridBuffer {
  private readonly canvas: OffscreenCanvas | HTMLCanvasElement;
  private readonly ctx: OffscreenCanvasRenderingContext2D | CanvasRenderingContext2D;

  /** true → нужна перерисовка offscreen перед следующим drawImage */
  private dirty = true;

  private readonly totalW: number;
  private readonly totalH: number;

  constructor(
    private readonly cols: number,
    private readonly rows: number,
  ) {
    this.totalW = cols * CELL_W;
    this.totalH = rows * CELL_H;

    // Предпочитаем OffscreenCanvas; fallback — обычный canvas вне DOM
    if (typeof OffscreenCanvas !== "undefined") {
      this.canvas = new OffscreenCanvas(this.totalW, this.totalH);
    } else {
      const el = document.createElement("canvas");
      el.width  = this.totalW;
      el.height = this.totalH;
      this.canvas = el;
    }

    this.ctx = this.canvas.getContext("2d") as
      OffscreenCanvasRenderingContext2D | CanvasRenderingContext2D;
  }

  /**
   * Пометить буфер устаревшим.
   * Вызывать при каждом изменении ролей, слотов или pick_sequence.
   */
  markDirty(): void {
    this.dirty = true;
  }

  /**
   * Если буфер устарел — перерисовать все ячейки склада.
   * Вызывается один раз перед каждой серией drawTo()-вызовов.
   *
   * @param data      Текущие данные сетки
   * @param aisles    Список аллей (для меток при zoom ≥ 0.6)
   * @param showSeq   Показывать ли номера pick_sequence
   */
  ensureFresh(
    data: GridData,
    _aisles: AisleDef[],
    showSeq: boolean,
  ): void {
    if (!this.dirty) return;
    this.dirty = false;

    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.totalW, this.totalH);

    // -----------------------------------------------------------------------
    // Единственный полный проход по всем ячейкам.
    // При markDirty (назначение роли, пересчёт маршрута) это происходит один раз,
    // затем многократно используется при zoom/pan через drawImage.
    // -----------------------------------------------------------------------
    for (let r = 0; r < data.rows; r++) {
      for (let c = 0; c < data.cols; c++) {
        const i    = r * data.cols + c;
        const role = data.roles[i];

        // Пустые ячейки не рисуем — экономим draw calls
        if (role === ROLE.EMPTY) continue;

        const x = c * CELL_W;
        const y = r * CELL_H;

        // Фон ячейки
        ctx.fillStyle = ROLE_COLORS[role];
        ctx.fillRect(x, y, CELL_W - 1, CELL_H - 1);

        // Мелкоштучная внутренняя сетка (рисуется всегда в offscreen,
        // видимость определяется масштабом при drawImage)
        const sc = data.slotCols[i];
        const sr = data.slotRows[i];
        if (sc > 1 || sr > 1) {
          drawSlotGridCtx(ctx, x, y, CELL_W - 1, CELL_H - 1, sc || 1, sr || 1);
        }

        // Номер pick_sequence (зелёный текст в центре ячейки)
        if (showSeq) {
          const seq = data.pickSeqs[i];
          if (seq >= 0) {
            ctx.fillStyle    = "#065F46";
            ctx.font         = `bold ${Math.floor(CELL_H * 0.5)}px sans-serif`;
            ctx.textAlign    = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(String(seq + 1), x + CELL_W / 2, y + CELL_H / 2);
          }
        }
      }
    }
  }

  /**
   * Скомпозировать offscreen-буфер на видимый canvas с учётом transform.
   * Один drawImage заменяет тысячи fillRect при zoom/pan.
   *
   * @param targetCtx Контекст видимого canvas
   * @param transform Текущая матрица zoom + pan
   * @param canvasW   Физическая ширина видимого canvas (с учётом DPR)
   * @param canvasH   Физическая высота видимого canvas
   */
  drawTo(
    targetCtx: CanvasRenderingContext2D,
    transform: DOMMatrix,
    canvasW: number,
    canvasH: number,
  ): void {
    targetCtx.save();
    targetCtx.clearRect(0, 0, canvasW, canvasH);
    targetCtx.setTransform(transform);
    targetCtx.drawImage(this.canvas as CanvasImageSource, 0, 0);
    targetCtx.restore();
  }

  /** Размеры буфера (для отладки). */
  get size(): { w: number; h: number } {
    return { w: this.totalW, h: this.totalH };
  }
}

// ---------------------------------------------------------------------------
// Вспомогательные функции
// ---------------------------------------------------------------------------

/**
 * Нарисовать внутреннюю сетку мелкоштучного деления ячейки.
 * Используется как в OffscreenGridBuffer, так и при рендере в dynamic-слое.
 */
export function drawSlotGridCtx(
  ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D,
  x: number, y: number,
  w: number, h: number,
  slotCols: number,
  slotRows: number,
): void {
  ctx.save();
  ctx.strokeStyle = "rgba(255,255,255,0.55)";
  ctx.lineWidth   = 0.8;

  const sw = w / slotCols;
  const sh = h / slotRows;

  // Вертикальные линии деления по ширине
  for (let ci = 1; ci < slotCols; ci++) {
    ctx.beginPath();
    ctx.moveTo(x + ci * sw, y);
    ctx.lineTo(x + ci * sw, y + h);
    ctx.stroke();
  }

  // Горизонтальные линии деления по высоте
  for (let ri = 1; ri < slotRows; ri++) {
    ctx.beginPath();
    ctx.moveTo(x,     y + ri * sh);
    ctx.lineTo(x + w, y + ri * sh);
    ctx.stroke();
  }
  ctx.restore();
}

/**
 * Преобразовать 0-based номер столбца в буквенный код ('A', 'B', ..., 'Z', 'AA', ...).
 * Используется для заголовков столбцов и SECTION_CODE в Oracle.
 */
export function colLabel(col: number): string {
  let result = "";
  let n = col + 1; // 1-based
  while (n > 0) {
    n--;
    result = String.fromCharCode(65 + (n % 26)) + result;
    n = Math.floor(n / 26);
  }
  return result;
}

/**
 * Автоопределение аллей из текущего состояния сетки.
 * Ищет соседние столбцы с доминирующими ролями LEFT и RIGHT.
 *
 * Логика: если в столбце c большинство непустых ячеек имеют role=LEFT,
 * а в столбце c+1 — role=RIGHT (или наоборот), они образуют аллею.
 */
export function inferAisles(data: GridData, settings: GridSettings): AisleDef[] {
  const aisles: AisleDef[] = [];

  // Определить доминирующую роль каждого столбца
  const colDominantRole = (col: number): RoleValue => {
    let leftCount = 0, rightCount = 0;
    for (let r = 0; r < data.rows; r++) {
      const role = data.roles[r * data.cols + col];
      if (role === ROLE.LEFT)  leftCount++;
      if (role === ROLE.RIGHT) rightCount++;
    }
    if (leftCount === 0 && rightCount === 0) return ROLE.EMPTY;
    return leftCount >= rightCount ? ROLE.LEFT : ROLE.RIGHT;
  };

  let aisleIndex = 0;
  for (let c = 0; c < data.cols - 1; c++) {
    const cur  = colDominantRole(c);
    const next = colDominantRole(c + 1);

    // Ищем пары LEFT+RIGHT или RIGHT+LEFT
    if (
      (cur === ROLE.LEFT  && next === ROLE.RIGHT) ||
      (cur === ROLE.RIGHT && next === ROLE.LEFT)
    ) {
      // Найти соседний столбец-проход (если есть)
      let passageCol: number | undefined;
      if (c + 2 < data.cols && colDominantRole(c + 2) === ROLE.EMPTY) {
        // Проверяем, что столбец c+2 помечен как PASSAGE
        let passageCount = 0;
        for (let r = 0; r < data.rows; r++) {
          if (data.roles[r * data.cols + (c + 2)] === ROLE.PASSAGE) passageCount++;
        }
        if (passageCount > data.rows / 3) passageCol = c + 2;
      }

      aisles.push({
        id:              `A${aisleIndex + 1}`,
        label:           `Аллея ${aisleIndex + 1}`,
        leftCol:         cur === ROLE.LEFT ? c : c + 1,
        rightCol:        cur === ROLE.RIGHT ? c : c + 1,
        passageCol,
        distanceMeters:  aisleIndex * settings.aisleWidthMeters,
        customDistance:  false,
      });

      // Привязать ячейки обоих столбцов к этой аллее
      for (let r = 0; r < data.rows; r++) {
        const iL = r * data.cols + (cur === ROLE.LEFT ? c : c + 1);
        const iR = r * data.cols + (cur === ROLE.RIGHT ? c : c + 1);
        data.aisleIdx[iL] = aisleIndex;
        data.aisleIdx[iR] = aisleIndex;
      }

      aisleIndex++;
      // Перепрыгиваем c+1, чтобы не обрабатывать правый столбец как левый следующей пары
      c++;
    }
  }

  return aisles;
}

/**
 * Построить матрицу межаллейных расстояний (n×n).
 * cost[i*n + j] = расстояние в метрах от аллеи i до аллеи j.
 * Используется алгоритмами маршрутизации.
 */
export function buildInterAisleMatrix(aisles: AisleDef[]): Float32Array {
  const n = aisles.length;
  const m = new Float32Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      m[i * n + j] = Math.abs(aisles[i].distanceMeters - aisles[j].distanceMeters);
    }
  }
  return m;
}

/**
 * Пересчитать длину маршрута в метрах по текущим pick_sequences.
 *
 * @param data         Данные сетки с заполненными pickSeqs
 * @param aisles       Список аллей с расстояниями
 * @param bayHeightM   Физическая высота бая в метрах
 * @returns            Суммарная длина маршрута в метрах
 */
export function calcRouteLengthM(
  data: GridData,
  aisles: AisleDef[],
  bayHeightM: number,
): number {
  const n = data.size;

  // Собрать упорядоченный массив индексов: ordered[seq] = cellIndex
  let maxSeq = -1;
  for (let i = 0; i < n; i++) {
    if (data.pickSeqs[i] > maxSeq) maxSeq = data.pickSeqs[i];
  }
  if (maxSeq < 0) return 0;

  const ordered = new Int32Array(maxSeq + 1).fill(-1);
  for (let i = 0; i < n; i++) {
    const s = data.pickSeqs[i];
    if (s >= 0) ordered[s] = i;
  }

  const interAisle = buildInterAisleMatrix(aisles);
  const na = aisles.length;
  let total = 0;

  for (let s = 1; s <= maxSeq; s++) {
    const from = ordered[s - 1];
    const to   = ordered[s];
    if (from < 0 || to < 0) continue;

    const r1 = Math.floor(from / data.cols);
    const r2 = Math.floor(to   / data.cols);
    const ai1 = data.aisleIdx[from];
    const ai2 = data.aisleIdx[to];

    if (ai1 === ai2 || ai1 < 0 || ai2 < 0) {
      // Та же аллея — движение по глубине
      total += Math.abs(r1 - r2) * bayHeightM;
    } else {
      // Разные аллеи: выйти к торцу + пройти поперёк + войти в новую аллею
      const exitDist  = Math.min(r1, data.rows - 1 - r1) * bayHeightM;
      const crossDist = interAisle[ai1 * na + ai2];
      const entryDist = r2 * bayHeightM;
      total += exitDist + crossDist + entryDist;
    }
  }

  return total;
}
