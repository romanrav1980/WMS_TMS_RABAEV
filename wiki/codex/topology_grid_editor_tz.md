# ТЗ: Редактор топологии склада (Excel-подобный сеточный редактор)

**Версия:** 1.2  
**Дата:** 2026-05-21  
**Статус:** Черновик  

---

## 1. Цель и контекст

### Проблема

Текущий `TopologyAdminPage` отображает **уже созданную** топологию (SVG-вьювер), но не позволяет создать её с нуля. Диспетчер должен открыть чистый лист и нарисовать схему склада так, как он видит её на плане помещения.

### Решение

Отдельная страница — **сеточный редактор** в стиле Excel. Строки = баи (секции по глубине), столбцы = поперечные позиции. Пользователь раскрашивает ячейки сетки, назначает им роли, задаёт расстояния между аллеями, отмечает мелкоштучные участки, затем система строит объекты `RRL_TOPOLOGY_*` и назначает порядок обхода.

### Из чего состоит склад в терминах сетки

```
      Col 1   Col 2   Col 3   Col 4   Col 5   Col 6   Col 7
Row 1 [ R-A1 ][ L-A1 ][ПРОХОД][ R-A2 ][ L-A2 ][ПРОХОД][ R-A3 ]
Row 2 [ R-A1 ][ L-A1 ][ПРОХОД][ R-A2 ][ L-A2 ][ПРОХОД][ R-A3 ]
...
Row N [ R-A1 ][ L-A1 ][ПРОХОД][ R-A2 ][ L-A2 ][ПРОХОД][ R-A3 ]
```

- **R-Ax** — правая сторона аллеи Ax (`side_code = 'R'`)
- **L-Ax** — левая сторона аллеи Ax (`side_code = 'L'`)
- **ПРОХОД** — межстеллажный коридор
- Пара [R][L] = один `RRL_TOPOLOGY_AISLE`

---

## 2. Требования к производительности и выбор технологий

### 2.1 Ключевое требование

> Редактор должен работать без ощутимых задержек на сетках до **15 000 ячеек отбора**.
> Любое взаимодействие (выделение, назначение роли, прокрутка, зум) — не более **16 мс** (60 fps).

Типичная большая сетка: 200 строк × 75 столбцов = 15 000 ячеек, из которых ~50% — L/R-ячейки отбора.

### 2.2 Почему HTML `<table>` не подходит

| Проблема | HTML table (15 000 td) | Canvas 2D |
|----------|------------------------|-----------|
| DOM-ноды | 15 000+ элементов | 1 элемент `<canvas>` |
| Event listeners | ~15 000 | 1 на canvas |
| React reconciliation при изменении роли | O(N) diff | нет (manual redraw) |
| Скролл | браузерный, медленный на 15 K | pan через transform matrix |
| Зум | CSS scale (blurry) | pixel-perfect transform |
| Перерисовка при выделении | reflow + repaint всего DOM | `fillRect` только изменённых ячеек |
| Память (16 K объектов React) | ~8 MB | ~80 KB (TypedArrays) |

Вывод: единственная технология, которая гарантирует 60 fps при 15 000 ячейках — **Canvas 2D**.

### 2.3 Архитектура рендера: OffscreenCanvas + два видимых слоя

```
┌──────────────────────────────────────────────────────────┐
│  OffscreenCanvas (невидимый, размер всего склада)        │
│  Содержимое: ВСЕ ячейки в натуральном масштабе          │
│  Перерисовывается: только при изменении ролей            │
│  Частота: редко (пользователь поднял кнопку мыши)        │
│  Размер: totalCols×CELL_W × totalRows×CELL_H            │
│  Пример: 75×20 × 200×20 = 1500×4000 px                  │
├──────────────────────────────────────────────────────────┤
│  canvas#grid-static   (z-index: 1, видимый)             │
│  Содержимое: ctx.drawImage(offscreen) + заголовки       │
│  Перерисовывается: при зуме, пане, изменении ролей      │
│  Метод: один drawImage() вместо N×fillRect()            │
│  Время: ~0.5–1 ms вне зависимости от числа ячеек        │
├──────────────────────────────────────────────────────────┤
│  canvas#grid-dynamic  (z-index: 2, position: absolute)  │
│  Содержимое: drag-прямоугольник, hover, стрелки маршрута│
│  Перерисовывается: каждый pointermove                    │
│  Время: < 1 ms (только геометрические примитивы)        │
└──────────────────────────────────────────────────────────┘
```

Ключевая идея: зум и пан не пересчитывают 15 000 ячеек — они делают `drawImage` из готового offscreen-буфера с новым transform. Пересчёт offscreen происходит только когда пользователь реально что-то изменил (назначил роль, пересчитал маршрут).

### 2.4 Хранение состояния: TypedArrays

Вместо массива объектов `GridCell[][]` — компактные типизированные массивы:

```typescript
class GridData {
  readonly rows: number;
  readonly cols: number;

  // Упакованные данные: row * cols + col → индекс
  roles:    Uint8Array;   // 0=empty 1=left 2=right 3=passage
  aisleIdx: Int16Array;   // -1=нет, иначе индекс в aisles[]
  pickSeqs: Int32Array;   // -1=нет, иначе PICK_SEQUENCE
  slotCols: Uint8Array;   // 0=нет деления, 1–5
  slotRows: Uint8Array;   // 0=нет деления, 1–5

  constructor(rows: number, cols: number) {
    this.rows = rows;
    this.cols = cols;
    const n = rows * cols;
    this.roles    = new Uint8Array(n);
    this.aisleIdx = new Int16Array(n).fill(-1);
    this.pickSeqs = new Int32Array(n).fill(-1);
    this.slotCols = new Uint8Array(n);
    this.slotRows = new Uint8Array(n);
  }

  idx(row: number, col: number): number {
    return (row - 1) * this.cols + (col - 1);
  }
}
// Память: 15 000 ячеек × 9 байт ≈ 135 KB. Для сравнения: объекты — ~6 MB
```

### 2.5 Выделение: BitSet вместо `Set<string>`

```typescript
class SelectionBitSet {
  private bits: Uint32Array;
  constructor(size: number) {
    this.bits = new Uint32Array(Math.ceil(size / 32));
  }
  has(idx: number): boolean {
    return !!(this.bits[idx >>> 5] & (1 << (idx & 31)));
  }
  set(idx: number): void  { this.bits[idx >>> 5] |=  (1 << (idx & 31)); }
  clr(idx: number): void  { this.bits[idx >>> 5] &= ~(1 << (idx & 31)); }
  toggle(idx: number): void {
    if (this.has(idx)) this.clr(idx); else this.set(idx);
  }
  clearAll(): void { this.bits.fill(0); }
  // Итерация: for(let i=0; i<size; i++) if(selection.has(i)) ...
}
// Память: 15 000 ячеек → 469 байт. Set<string> с теми же ячейками → ~1.5 MB
```

### 2.6 Рендер с отсечением невидимых ячеек

При любом масштабе рисуются только ячейки, попадающие в текущий viewport:

```typescript
function computeVisibleRange(
  transform: DOMMatrix,
  canvasW: number,
  canvasH: number,
  cellW: number,
  cellH: number,
  totalRows: number,
  totalCols: number,
): { r1: number; r2: number; c1: number; c2: number } {
  // Инвертировать transform → получить grid-координаты углов viewport
  const inv = transform.inverse();
  const toGrid = (cx: number, cy: number) => ({
    x: inv.a * cx + inv.c * cy + inv.e,
    y: inv.b * cx + inv.d * cy + inv.f,
  });
  const tl = toGrid(0, 0);
  const br = toGrid(canvasW, canvasH);

  return {
    r1: Math.max(0, Math.floor(tl.y / cellH)),
    r2: Math.min(totalRows - 1, Math.ceil(br.y / cellH)),
    c1: Math.max(0, Math.floor(tl.x / cellW)),
    c2: Math.min(totalCols - 1, Math.ceil(br.x / cellW)),
  };
}
// При zoom=1, canvas 1280×800, cell 20×20:
//   видно 64×40 = 2560 ячеек из 15 000 → рисуем только их
// При zoom=0.25 (весь склад виден):
//   видно все 15 000 ячеек, но cell=5px → только fillRect (без текста)
```

### 2.7 Level of Detail (LOD) по масштабу

| Масштаб | Размер ячейки | Что рисовать |
|---------|---------------|--------------|
| < 0.3 | < 6 px | только `fillRect` (цвет роли) |
| 0.3–0.6 | 6–12 px | цвет + контур ячейки |
| 0.6–1.0 | 12–20 px | цвет + контур + код аллеи |
| > 1.0 | > 20 px | полный: цвет + текст бая + sequence + слоты |

```typescript
function drawCell(
  ctx: CanvasRenderingContext2D,
  r: number, c: number,
  data: GridData,
  sel: SelectionBitSet,
  zoom: number,
  cellW: number,
  cellH: number,
): void {
  const i = data.idx(r + 1, c + 1);
  const role = data.roles[i];
  if (role === 0) return; // empty — не рисовать

  const x = c * cellW;
  const y = r * cellH;

  ctx.fillStyle = ROLE_COLORS[role];
  ctx.fillRect(x, y, cellW - 1, cellH - 1);

  if (sel.has(i)) {
    ctx.strokeStyle = '#FBBF24';
    ctx.lineWidth = 2 / zoom; // контур не зависит от масштаба
    ctx.strokeRect(x + 1, y + 1, cellW - 3, cellH - 3);
  }

  if (zoom >= 0.6 && cellW >= 12) {
    // Код аллеи
    const aisleIdx = data.aisleIdx[i];
    if (aisleIdx >= 0) {
      ctx.fillStyle = 'rgba(255,255,255,0.7)';
      ctx.font = `${Math.floor(cellH * 0.4)}px monospace`;
      ctx.fillText(/* aisle label */ '', x + 2, y + cellH * 0.6);
    }
  }

  if (zoom >= 1.0 && cellW >= 20) {
    // Номер sequence
    const seq = data.pickSeqs[i];
    if (seq >= 0) {
      ctx.fillStyle = '#065F46';
      ctx.font = `bold ${Math.floor(cellH * 0.35)}px sans-serif`;
      ctx.fillText(String(seq), x + cellW * 0.5, y + cellH * 0.5);
    }
    // Мелкоштучная сетка
    const sc = data.slotCols[i];
    const sr = data.slotRows[i];
    if (sc > 1 || sr > 1) drawSlotGrid(ctx, x, y, cellW, cellH, sc || 1, sr || 1, zoom);
  }
}
```

### 2.8 Обновление только грязных регионов

```typescript
const dirtySet = new Set<number>(); // индексы изменённых ячеек

function markDirty(indices: number[]): void {
  for (const i of indices) dirtySet.add(i);
  scheduleRepaint();
}

let rafId = 0;
function scheduleRepaint(): void {
  if (rafId) return;
  rafId = requestAnimationFrame(() => {
    rafId = 0;
    if (dirtySet.size > 500) {
      // Много изменений — полная перерисовка быстрее
      drawFullGrid();
    } else {
      // Перерисовать только изменённые ячейки
      for (const i of dirtySet) drawSingleCell(i);
    }
    dirtySet.clear();
  });
}
// 500 — эмпирический порог: полная перерисовка 15K клеток ~8 ms,
// поштучная на 500 ячеек ~6 ms. При > 500 выгоднее один проход.
```

### 2.9 OffscreenCanvas — обязательный элемент реализации

`OffscreenCanvas` — обязательный компонент архитектуры, не опция. Без него zoom/pan при полностью видимом складе (15 000 ячеек) будет занимать 8–20 ms, что нарушает требование 16 ms / 60 fps.

#### Жизненный цикл offscreen-буфера

```typescript
class OffscreenGridBuffer {
  private canvas: OffscreenCanvas;
  private ctx: OffscreenCanvasRenderingContext2D;
  private dirty = true;

  constructor(
    private readonly totalCols: number,
    private readonly totalRows: number,
    private readonly cellW: number,
    private readonly cellH: number,
  ) {
    this.canvas = new OffscreenCanvas(totalCols * cellW, totalRows * cellH);
    this.ctx = this.canvas.getContext('2d')!;
  }

  markDirty(): void {
    this.dirty = true;
  }

  /** Перерисовать offscreen, если были изменения. Вызывается перед drawImage. */
  ensureFresh(data: GridData, aisles: AisleDef[]): void {
    if (!this.dirty) return;
    this.dirty = false;

    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Рисуем ВСЕ ячейки без клиппинга — один полный проход
    for (let r = 0; r < data.rows; r++) {
      for (let c = 0; c < data.cols; c++) {
        const i = data.idx(r + 1, c + 1);
        const role = data.roles[i];
        if (role === 0) continue;

        const x = c * this.cellW;
        const y = r * this.cellH;

        ctx.fillStyle = ROLE_COLORS[role];
        ctx.fillRect(x, y, this.cellW - 1, this.cellH - 1);

        // Мелкоштучная сетка
        const sc = data.slotCols[i];
        const sr = data.slotRows[i];
        if (sc > 1 || sr > 1) {
          drawSlotGrid(ctx, x, y, this.cellW, this.cellH, sc, sr, 1.0);
        }

        // Текст (sequence): рисуем всегда в offscreen,
        // видимость определится zoom-ом при drawImage
        const seq = data.pickSeqs[i];
        if (seq >= 0) {
          ctx.fillStyle = '#065F46';
          ctx.font = `bold ${Math.floor(this.cellH * 0.4)}px sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(String(seq), x + this.cellW / 2, y + this.cellH / 2);
        }
      }
    }
  }

  /** Нарисовать на видимом canvas с учётом текущего transform */
  drawTo(
    targetCtx: CanvasRenderingContext2D,
    transform: DOMMatrix,
    canvasW: number,
    canvasH: number,
  ): void {
    targetCtx.save();
    targetCtx.clearRect(0, 0, canvasW, canvasH);
    targetCtx.setTransform(transform);
    // Один вызов вместо тысяч fillRect
    targetCtx.drawImage(this.canvas, 0, 0);
    targetCtx.restore();
  }

  get offscreen(): OffscreenCanvas {
    return this.canvas;
  }
}
```

#### Когда вызывать `markDirty()`

| Действие пользователя | Нужно ли markDirty? |
|-----------------------|---------------------|
| Назначить роль ячейкам | **Да** |
| Задать мелкоштучное деление | **Да** |
| Пересчитать маршрут (новые sequence) | **Да** |
| Зум / пан | Нет (только drawTo с новым transform) |
| Drag-выделение | Нет (только dynamic canvas) |
| Изменить расстояние аллеи | Нет (не влияет на пиксели ячеек) |

#### Полный цикл перерисовки

```typescript
function scheduleRepaint(reason: 'roles' | 'zoom' | 'selection'): void {
  if (reason === 'roles') {
    offscreenBuffer.markDirty();
  }
  if (rafId.current) return;
  rafId.current = requestAnimationFrame(() => {
    rafId.current = 0;
    const ctx = staticCanvas.current!.getContext('2d')!;

    // 1. Обновить offscreen (нет-оп если не dirty)
    offscreenBuffer.ensureFresh(gridData.current, aisles.current);

    // 2. Скомпозировать на видимый canvas — всегда один drawImage
    offscreenBuffer.drawTo(ctx, transform.current, canvasW, canvasH);

    // 3. Поверх нарисовать sticky-заголовки (игнорируют transform)
    drawHeaders(ctx, transform.current);
  });
}
```

#### Совместимость

`OffscreenCanvas` поддерживается в Chrome 69+, Firefox 105+, Edge 79+. Safari поддерживает с версии 16.4 (2023). Для корпоративных проектов на современных браузерах — полностью безопасно.

Если нужна поддержка старых браузеров: fallback — обычный `<canvas>` за пределами DOM (`document.createElement('canvas')`), API идентичен.

```typescript
const offscreenSupported = typeof OffscreenCanvas !== 'undefined';
const bufferCanvas = offscreenSupported
  ? new OffscreenCanvas(w, h)
  : Object.assign(document.createElement('canvas'), { width: w, height: h });
```

### 2.10 Оценка производительности

| Операция | Ожидаемое время | Метод измерения |
|----------|-----------------|-----------------|
| Первый рендер offscreen (15 000 ячеек) | < 20 ms | `performance.mark` |
| Zoom / pan → `drawImage` offscreen | **< 1 ms** | `performance.mark` |
| Drag-выделение (dynamic canvas) | < 1 ms / кадр | DevTools FPS |
| Выделение прямоугольника 500 ячеек | < 8 ms | `performance.mark` |
| Назначение роли 1000 ячеек → ensureFresh | < 20 ms | `performance.mark` |
| Генерация маршрута (U, 7 500 ячеек) | < 50 ms | `performance.mark` |
| Zoom при Retina DPR=2 | **< 2 ms** | `performance.mark` |

Тест производительности запускается как часть CI (Jest + jsdom-canvas mock):
```typescript
it('renders 15000 cells in < 20ms', () => {
  const grid = new GridData(200, 75);
  // заполнить тестовыми ролями
  const t0 = performance.now();
  drawFullGrid(mockCtx, grid, identityTransform, viewport);
  expect(performance.now() - t0).toBeLessThan(20);
});
```

---

## 3. Концепция UI

### 3.1 Общий вид страницы

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [← Назад]   Новая топология / "Склад A"   [Сохранить черновик] [Вал.] │
├──────────────────┬──────────────────────────────────────────────────────┤
│  ИНСТРУМЕНТЫ     │                    СЕТКА (Canvas 2D)                 │
│                  │  ┌────────────────────────────────────────────────┐  │
│  Строк:  [200 ↕] │  │  A    B    C    D    E    F    G   ...         │  │
│  Столбцов:[75 ↕] │  │ ━━━━━A1━━━━━        ━━━━━A2━━━━━              │  │
│                  │  │  ░░   ██   ██   ░░   ░░   ██   ██   ░░        │  │
│  Инструмент:     │  │  ░░   ██   ██   ░░   ░░   ██   ██   ░░        │  │
│  ○ Выделить      │  │  ░░   ██  [🔲]  ░░   ░░   ██   ██   ░░        │  │
│  ○ Стереть       │  │                                                │  │
│                  │  │  ... 200 строк × 75 столбцов = 15 000 ячеек   │  │
│  Назначить:      │  └────────────────────────────────────────────────┘  │
│  [ЛЕВЫЕ]         ├──────────────────────────────────────────────────────┤
│  [ПРАВЫЕ]        │  ПАНЕЛЬ ДЕЙСТВИЙ (при выделении)                     │
│  [ПРОХОД]        │  Выделено: 200 ячеек (столбец B, строки 1–200)      │
│  [Очистить]      │  [← ЛЕВЫЕ] [ПРАВЫЕ →] [▓ ПРОХОД] [🔲 Мелкоштучная]│
│                  │  [✕ Очистить роль]                                   │
│  ──────────      ├──────────────────────────────────────────────────────┤
│  Маршрут:        │  АЛЛЕИ                                               │
│  [U-образный ▼]  │  A1: L=B R=C   dist=3.5м  [✎]                       │
│                  │  A2: L=F R=G   dist=7.0м  [↺]                       │
│  [Рассчитать]    │  Ширина прохода: [3.5 м]  [Пересчитать]             │
│  Маршрут: 1248 м │                                                      │
└──────────────────┴───────────────────────────────────────────────────────┘
```

### 3.2 Цветовая кодировка

| Роль | fillStyle | Примечание |
|------|-----------|------------|
| Пусто | не рисовать (фон canvas) | экономия draw calls |
| Левая (L) | `#3B82F6` | синий |
| Правая (R) | `#F97316` | оранжевый |
| Проход | `#E5E7EB` с штриховкой | серый |
| Выделена | жёлтый strokeRect контур `#FBBF24` | поверх любого цвета |
| Маршрут | зелёный текст `#065F46` | номер sequence |
| Мелкоштучная | + внутренняя сетка тонкими линиями | при zoom ≥ 1 |

---

## 4. Модель данных сетки

### 4.1 Хранение в React-компоненте

Состояние, меняющееся при каждом событии, держать в `useRef` — **не** в `useState`. React re-render не нужен при изменении ролей; нужна только перерисовка canvas.

```typescript
const gridData    = useRef<GridData>(new GridData(rows, cols));
const selection   = useRef<SelectionBitSet>(new SelectionBitSet(rows * cols));
const transform   = useRef<DOMMatrix>(new DOMMatrix());
const aisles      = useRef<AisleDef[]>([]);
const routeSeqs   = useRef<Int32Array>(new Int32Array(rows * cols).fill(-1));

// useState только для вещей, влияющих на React-дерево:
const [uiState, setUiState] = useState({
  selectionCount: 0,
  routeLengthM: 0,
  aisleList: [] as AisleDef[],  // для левой панели
  apiState: 'idle' as 'idle' | 'saving' | 'error',
});
```

### 4.2 Маппинг сетки → Oracle

| GridData поле | Oracle-объект |
|---------------|---------------|
| `roles[i] = 1 / 2` | `RRL_TOPOLOGY_CELL.SIDE_CODE = 'L'/'R'` |
| `aisleIdx[i]` → `aisles[idx]` | `RRL_TOPOLOGY_AISLE` |
| `(i / cols) + 1` = row | `RRL_TOPOLOGY_CELL.BAY_NO` |
| `(i % cols) + 1` → label | `RRL_TOPOLOGY_CELL.SECTION_CODE` |
| `aisles[idx].distanceMeters` | `RRL_TOPOLOGY_AISLE.DISTANCE_FROM_START_M` |
| `pickSeqs[i]` | `RRL_PICK_ROUTE_CELL.PICK_SEQUENCE` |
| `slotCols[i] × slotRows[i]` | `RRL_TOPOLOGY_PICK_FACE_SLOT` записи |

---

## 5. Механика выделения

### 5.1 Pointer events на canvas

```typescript
const canvasRef = useRef<HTMLCanvasElement>(null);

useEffect(() => {
  const canvas = canvasRef.current!;
  canvas.addEventListener('pointerdown',  handlePointerDown,  { passive: true });
  canvas.addEventListener('pointermove',  handlePointerMove,  { passive: true });
  canvas.addEventListener('pointerup',    handlePointerUp);
  canvas.addEventListener('wheel',        handleWheel, { passive: false });
  return () => { /* removeEventListener */ };
}, []);

function canvasToCell(e: PointerEvent): { r: number; c: number } | null {
  const rect = canvasRef.current!.getBoundingClientRect();
  const cx = (e.clientX - rect.left) * devicePixelRatio;
  const cy = (e.clientY - rect.top)  * devicePixelRatio;
  const inv = transform.current.inverse();
  const gx = inv.a * cx + inv.c * cy + inv.e;
  const gy = inv.b * cx + inv.d * cy + inv.f;
  const c = Math.floor(gx / CELL_W);
  const r = Math.floor(gy / CELL_H);
  if (r >= 0 && r < gridData.current.rows && c >= 0 && c < gridData.current.cols) {
    return { r, c };
  }
  return null;
}
```

### 5.2 Режимы взаимодействия

**Клик** → выделить/снять одну ячейку (toggle через BitSet).

**Drag** → прямоугольное выделение:
- `pointerdown` → `dragStart = canvasToCell(e)`
- `pointermove` → обновить `dragEnd`, перерисовать dynamic canvas (только прямоугольник)
- `pointerup` → применить: для каждой ячейки в прямоугольнике `selection.set(idx)`

**Ctrl + drag** → аддитивный режим (не сбрасывать текущее выделение).

**Shift + клик на заголовке столбца** → выделить весь столбец (200 ячеек × 1 цикл BitSet).

**Escape** → `selection.clearAll()`, `scheduleRepaint()`.

### 5.3 Заголовки строк и столбцов

Заголовки рисуются на том же статическом canvas в фиксированных регионах с `ctx.save() / ctx.restore()` и `ctx.setTransform(1,0,0,1,0,0)` (игнорируют zoom/pan), что даёт sticky-эффект без DOM.

```typescript
function drawHeaders(ctx: CanvasRenderingContext2D, transform: DOMMatrix): void {
  const { rows, cols } = gridData.current;
  const zoom = transform.a; // scale factor
  const panX = transform.e;
  const panY = transform.f;
  
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0); // сброс transform
  
  // Заголовки столбцов (строка 0)
  ctx.fillStyle = '#F3F4F6';
  ctx.fillRect(HEADER_W, 0, canvasW - HEADER_W, HEADER_H);
  for (let c = 0; c < cols; c++) {
    const x = HEADER_W + c * CELL_W * zoom + panX;
    if (x < HEADER_W || x > canvasW) continue;
    ctx.fillStyle = '#374151';
    ctx.fillText(colLabel(c), x + CELL_W * zoom / 2, HEADER_H / 2);
  }
  
  // Заголовки строк (столбец 0)
  for (let r = 0; r < rows; r++) {
    const y = HEADER_H + r * CELL_H * zoom + panY;
    if (y < HEADER_H || y > canvasH) continue;
    ctx.fillStyle = '#374151';
    ctx.fillText(String(r + 1).padStart(3, '0'), HEADER_W / 2, y + CELL_H * zoom / 2);
  }
  
  ctx.restore();
}
```

---

## 6. Привязка ячеек к аллеям

### 6.1 Автоопределение

```typescript
function inferAisles(data: GridData, settings: GridSettings): AisleDef[] {
  const aisles: AisleDef[] = [];
  let aisleIdx = 0;
  
  for (let c = 0; c < data.cols - 1; c++) {
    // Проверить, что весь столбец c имеет роль 'left', c+1 — 'right'
    const colRole = dominantRole(data, c);     // most frequent non-empty role
    const nextRole = dominantRole(data, c + 1);
    
    if ((colRole === 1 && nextRole === 2) || (colRole === 2 && nextRole === 1)) {
      const dist = aisleIdx * settings.aisleWidthMeters;
      aisles.push({
        id: `A${aisleIdx + 1}`,
        label: `Аллея ${aisleIdx + 1}`,
        leftCol:  colRole === 1 ? c : c + 1,
        rightCol: colRole === 2 ? c : c + 1,
        distanceMeters: dist,
        customDistance: false,
      });
      aisleIdx++;
    }
  }
  return aisles;
}
```

### 6.2 Управление аллеями в UI

Список в нижней части (не в canvas — обычный React-список, меняется редко):

```
АЛЛЕИ:
  A1  L=B  R=C   dist= 3.5 м  [✎ Задать вручную]  [✕]
  A2  L=F  R=G   dist= 7.0 м  [↺ авто]            [✕]
  [+ Добавить аллею вручную]
```

---

## 7. Расстояния между аллеями

### 7.1 Формула по умолчанию

```
distanceMeters[i] = (i − 1) × aisleWidthMeters
```

При `aisleWidthMeters = 3.5 м`: A1=0.0, A2=3.5, A3=7.0, A4=10.5...

### 7.2 Ручная корректировка

Кнопка `✎` → поле ввода в метрах, `customDistance = true`.
Кнопка `Пересчитать всё` → сброс всех `customDistance` к формуле.

### 7.3 Межаллейная матрица расстояний (для алгоритмов маршрута)

```typescript
function buildInterAisleCostMatrix(aisles: AisleDef[]): Float32Array {
  const n = aisles.length;
  const matrix = new Float32Array(n * n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      matrix[i * n + j] = Math.abs(aisles[i].distanceMeters - aisles[j].distanceMeters);
    }
  }
  return matrix;
}
```

### 7.4 Oracle DDL (миграция 046)

```sql
DECLARE v NUMBER;
BEGIN
  SELECT COUNT(*) INTO v FROM user_tab_columns
  WHERE table_name='RRL_TOPOLOGY_AISLE' AND column_name='DISTANCE_FROM_START_M';
  IF v = 0 THEN
    EXECUTE IMMEDIATE '
      ALTER TABLE RABAEV.RRL_TOPOLOGY_AISLE ADD (
        DISTANCE_FROM_START_M  NUMBER(8,2) DEFAULT NULL,
        AISLE_WIDTH_M          NUMBER(5,2) DEFAULT 3.5,
        AISLE_LABEL            VARCHAR2(100)
      )';
  END IF;
END;
/
```

---

## 8. Мелкоштучные ячейки (Split Pick-Face)

### 8.1 Концепция

Физическое место (например, 800×1800 мм) делится на `slotCols × slotRows` слотов:

```
3×3 = 9 слотов:      2×4 = 8 слотов:
┌──┬──┬──┐           ┌──┬──┐
│А1│А2│А3│           │А1│А2│
├──┼──┼──┤           ├──┼──┤
│Б1│Б2│Б3│           │Б1│Б2│
├──┼──┼──┤           ├──┼──┤
│В1│В2│В3│           │В1│В2│
└──┴──┴──┘           ├──┼──┤
                     │Г1│Г2│
                     └──┴──┘
```

### 8.2 Назначение в редакторе

1. Выделить ячейки → `[🔲 Мелкоштучная...]`
2. Диалог с пресетами + ввод:
   ```
   ┌────────────────────────────────────┐
   │  Мелкоштучное деление             │
   │  По ширине:  [1][2][3][4][5]      │
   │  По высоте:  [1][2][3][4][5]      │
   │  Пресеты: [2×2] [3×3] [2×4] [1×5]│
   │  = 9 слотов                       │
   │  [Применить]  [Отмена]            │
   └────────────────────────────────────┘
   ```
3. `data.slotCols[i] = sc; data.slotRows[i] = sr;`
4. `markDirty([i])`

### 8.3 Рендер мелкоштучной ячейки на canvas

```typescript
function drawSlotGrid(
  ctx: CanvasRenderingContext2D,
  x: number, y: number,
  cellW: number, cellH: number,
  sc: number, sr: number,
  zoom: number,
): void {
  ctx.strokeStyle = 'rgba(255,255,255,0.5)';
  ctx.lineWidth = 0.5 / zoom;
  const sw = cellW / sc;
  const sh = cellH / sr;
  for (let ci = 1; ci < sc; ci++) {
    ctx.beginPath();
    ctx.moveTo(x + ci * sw, y);
    ctx.lineTo(x + ci * sw, y + cellH);
    ctx.stroke();
  }
  for (let ri = 1; ri < sr; ri++) {
    ctx.beginPath();
    ctx.moveTo(x,         y + ri * sh);
    ctx.lineTo(x + cellW, y + ri * sh);
    ctx.stroke();
  }
}
```

### 8.4 Oracle DDL — RRL_TOPOLOGY_PICK_FACE_SLOT

```sql
DECLARE v NUMBER;
BEGIN
  SELECT COUNT(*) INTO v FROM user_tables WHERE table_name='RRL_TOPOLOGY_PICK_FACE_SLOT';
  IF v = 0 THEN
    EXECUTE IMMEDIATE '
      CREATE TABLE RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT (
        SLOT_ID   NUMBER(10)  PRIMARY KEY,
        CELL_ID   NUMBER(10)  NOT NULL
                  REFERENCES RABAEV.RRL_TOPOLOGY_CELL(CELL_ID),
        SLOT_COL  NUMBER(2)   NOT NULL,
        SLOT_ROW  NUMBER(2)   NOT NULL,
        SLOT_CODE VARCHAR2(10),
        IS_ACTIVE NUMBER(1)   DEFAULT 1,
        CONSTRAINT uq_slot UNIQUE (CELL_ID, SLOT_COL, SLOT_ROW)
      )';
    EXECUTE IMMEDIATE
      'CREATE SEQUENCE RABAEV.RRL_TOPOLOGY_PICK_FACE_SLOT_SEQ START WITH 1 INCREMENT BY 1';
  END IF;
END;
/
```

---

## 9. Алгоритмы порядка обхода

### Контекст

Маршрут топологии — **мастер-маршрут**: каждая L/R-ячейка получает уникальный `PICK_SEQUENCE`. Алгоритм обходит **все** ячейки отбора ровно по одному разу (гамильтонов путь по складскому графу).

### 9.1 Сводная таблица

| Алгоритм | Код | Длина маршрута | Когда использовать |
|----------|-----|----------------|---------------------|
| Z-образный | `Z` | базовая | Стандартный прямоугольный склад |
| U-образный | `U` | ≈ базовая | Товары тяготеют к одному торцу |
| Змейка | `SNAKE` | ≈ базовая | Минимум разворотов, длинные аллеи |
| Двухблочный | `TWO_BLOCK` | −10…20% от базовой | Длинный склад (>30 баев) |
| По зонам | `ZONE_SWEEP` | зависит от зон | Зонированный склад |
| Ёлочка | `FISHBONE` | −15% (теоретически) | Диагональные перекрёстные проходы |
| Ручной | `LINEAR` | любая | Нестандартная планировка |

### 9.2 Z-образный

```
→ A1_L[01…N] → A1_R[01…N] → A2_L[01…N] → A2_R[01…N] → …
```

```typescript
function generateZ(aisles: AisleDef[], data: GridData): void {
  let seq = 0;
  for (const aisle of sortByDistance(aisles)) {
    for (const col of [aisle.leftCol, aisle.rightCol]) {
      for (let row = 0; row < data.rows; row++) {
        const i = data.idx(row + 1, col + 1);
        if (data.roles[i] !== 0) data.pickSeqs[i] = seq++;
      }
    }
  }
}
```

### 9.3 U-образный

```
→ A1_L[01→N] ↓  разворот  → A1_R[N→01] ↑  → A2_L[01→N] ↓ …
```

```typescript
function generateU(aisles: AisleDef[], data: GridData): void {
  let seq = 0;
  for (const aisle of sortByDistance(aisles)) {
    for (let row = 0; row < data.rows; row++) {
      const i = data.idx(row + 1, aisle.leftCol + 1);
      if (data.roles[i]) data.pickSeqs[i] = seq++;
    }
    for (let row = data.rows - 1; row >= 0; row--) {
      const i = data.idx(row + 1, aisle.rightCol + 1);
      if (data.roles[i]) data.pickSeqs[i] = seq++;
    }
  }
}
```

### 9.4 Змейка (SNAKE)

Следующий столбец начинается с того конца, где закончил предыдущий:

```typescript
function generateSnake(aisles: AisleDef[], data: GridData): void {
  let seq = 0;
  let goDown = true;
  for (const aisle of sortByDistance(aisles)) {
    for (const col of [aisle.leftCol, aisle.rightCol]) {
      const rows = goDown
        ? Array.from({ length: data.rows }, (_, r) => r)
        : Array.from({ length: data.rows }, (_, r) => data.rows - 1 - r);
      for (const row of rows) {
        const i = data.idx(row + 1, col + 1);
        if (data.roles[i]) data.pickSeqs[i] = seq++;
      }
      goDown = !goDown;
    }
  }
}
```

### 9.5 Двухблочный (TWO_BLOCK)

```
Front (баи 1…N/2), аллеи слева направо:   Z-паттерн
Back  (баи N/2+1…N), аллеи справа налево: Z-паттерн с разворотом
Встреча в середине
```

```typescript
function generateTwoBlock(aisles: AisleDef[], data: GridData, splitFraction = 0.5): void {
  let seq = 0;
  const mid = Math.ceil(data.rows * splitFraction);
  const sorted = sortByDistance(aisles);

  for (const aisle of sorted) {
    for (const col of [aisle.leftCol, aisle.rightCol]) {
      for (let row = 0; row < mid; row++) {
        const i = data.idx(row + 1, col + 1);
        if (data.roles[i]) data.pickSeqs[i] = seq++;
      }
    }
  }
  for (const aisle of [...sorted].reverse()) {
    for (const col of [aisle.rightCol, aisle.leftCol]) {
      for (let row = data.rows - 1; row >= mid; row--) {
        const i = data.idx(row + 1, col + 1);
        if (data.roles[i]) data.pickSeqs[i] = seq++;
      }
    }
  }
}
```

### 9.6 По зонам (ZONE_SWEEP)

Сначала все ячейки зоны A (по возрастанию `zone_code`), внутри зоны — базовый паттерн (Z/U/SNAKE):

```typescript
function generateZoneSweep(
  aisles: AisleDef[],
  data: GridData,
  zoneMap: Map<number, string>, // idx → zoneCode
  basePattern: 'Z' | 'U' | 'SNAKE' = 'U',
): void {
  const zones = [...new Set(zoneMap.values())].sort();
  let seq = 0;
  for (const zone of zones) {
    const zoneAisles = aisles.filter(a => aisleInZone(a, zone, zoneMap, data));
    // Запустить basePattern только на ячейках этой зоны
    seq = runPatternInZone(basePattern, zoneAisles, data, zone, zoneMap, seq);
  }
}
```

### 9.7 Ёлочка (FISHBONE) — заглушка

Применимо только если в планировке есть диагональные коридоры (роль `'diagonal_passage'`). В текущей версии — fallback на SNAKE. Полная реализация — следующий этап.

### 9.8 Расчёт длины маршрута

```typescript
function calcRouteLengthM(
  data: GridData,
  aisles: AisleDef[],
  cellHeightM = 1.5,
): number {
  // Собрать массив [idx] по порядку seq
  const ordered: number[] = new Array(data.rows * data.cols);
  let maxSeq = -1;
  for (let i = 0; i < data.pickSeqs.length; i++) {
    const s = data.pickSeqs[i];
    if (s >= 0) { ordered[s] = i; maxSeq = Math.max(maxSeq, s); }
  }
  
  let total = 0;
  const aisleDist = buildInterAisleCostMatrix(aisles);
  const n = aisles.length;
  
  for (let s = 1; s <= maxSeq; s++) {
    const from = ordered[s - 1];
    const to   = ordered[s];
    const r1 = Math.floor(from / data.cols);
    const c1 = from % data.cols;
    const r2 = Math.floor(to / data.cols);
    const c2 = to % data.cols;
    const ai1 = data.aisleIdx[from];
    const ai2 = data.aisleIdx[to];
    
    if (ai1 === ai2 || ai1 < 0 || ai2 < 0) {
      total += Math.abs(r1 - r2) * cellHeightM;
    } else {
      const exit  = Math.min(r1, data.rows - 1 - r1) * cellHeightM;
      const cross = aisleDist[ai1 * n + ai2];
      const entry = r2 * cellHeightM;
      total += exit + cross + entry;
    }
  }
  return total;
}
```

### 9.9 UI выбора алгоритма

```
Алгоритм обхода (все ячейки):
○ Z-образный    — все аллеи насквозь, слева направо
● U-образный    — U-поворот у дальнего торца         ← default
○ Змейка        — S-образный, минимум разворотов
○ Двухблочный   — front/back, встреча в середине
○ По зонам      — сначала зона A, потом B, потом C
○ Ёлочка        — диагональные проходы (fishbone)
○ Ручной        — drag-and-drop список

Параметры:
  Высота бая: [1.5 м]    Точка разреза (Two-Block): [50%]
  Базовый паттерн зон: [U ▼]

Длина маршрута: 1 248 м   [Пересчитать]
```

---

## 10. Рабочий процесс (Use Case)

```
1. Открыть /admin/topology/new
   └─ Задать: Склад, Имя, Строк, Столбцов, Ширина прохода

2. Нарисовать схему (canvas)
   ├─ Drag по столбцу B → [ЛЕВЫЕ]  → синие ячейки
   ├─ Drag по столбцу C → [ПРАВЫЕ] → оранжевые
   ├─ Drag по столбцу D → [ПРОХОД] → серые штрихи
   ├─ Повторить для A2 (F, G, H)
   └─ inferAisles → A1 и A2 в панели аллей

3. Скорректировать расстояния (необязательно)

4. Отметить мелкоштучные ячейки
   └─ Выделить ячейки → [🔲 Мелкоштучная...] → 3×3

5. Выбрать алгоритм маршрута → [Рассчитать]
   └─ Видеть: числа в ячейках, длина 1248 м

6. [Сохранить черновик] → POST /api/admin/topologies/from-grid
   └─ Редирект на TopologyAdminPage?topology_id=42

7. [Валидировать] → [Опубликовать]
```

---

## 11. API-эндпоинты

### POST `/api/admin/topologies/from-grid`

```json
{
  "warehouse_id": 1,
  "label": "Склад A, 2026-Q2",
  "grid": {
    "rows": 200, "cols": 75,
    "settings": { "aisle_width_meters": 3.5 },
    "cells": [
      { "row": 1, "col": 2, "role": "left",  "aisle_id": "A1" },
      { "row": 3, "col": 2, "role": "left",  "aisle_id": "A1",
        "slot_division": { "cols": 3, "rows": 3 } }
    ],
    "aisles": [
      { "id": "A1", "label": "Аллея 1", "left_col": 2, "right_col": 3,
        "passage_col": 4, "distance_meters": 3.5, "custom_distance": false }
    ],
    "route_pattern": "U",
    "pick_sequences": [
      { "row": 1, "col": 2, "pick_sequence": 0 }
    ]
  }
}
```

**Response:** `{ "topology_id": 42, "status": "DRAFT", "cell_count": 7500, "slot_count": 27 }`

### GET `/api/admin/topologies/{id}/as-grid`

Возвращает GridState для повторного открытия в редакторе.

---

## 12. Сервисный слой (Python)

```python
async def create_topology_from_grid(
    db: oracledb.AsyncConnection,
    warehouse_id: int,
    label: str,
    grid: GridPayload,
    user_id: int,
) -> dict:
    topology_id = await _next_val(db, "RRL_WAREHOUSE_TOPOLOGY_SEQ")
    await db.execute("""
        INSERT INTO RABAEV.RRL_WAREHOUSE_TOPOLOGY
          (TOPOLOGY_ID, WAREHOUSE_ID, LABEL, STATUS, CREATED_BY, CREATED_AT)
        VALUES (:1, :2, :3, 'DRAFT', :4, SYSDATE)
    """, [topology_id, warehouse_id, label, user_id])

    aisle_id_map: dict[str, int] = {}
    for aisle in grid.aisles:
        db_id = await _next_val(db, "RRL_TOPOLOGY_AISLE_SEQ")
        aisle_id_map[aisle.id] = db_id
        await db.execute("""
            INSERT INTO RABAEV.RRL_TOPOLOGY_AISLE
              (AISLE_ID, TOPOLOGY_ID, AISLE_CODE, AISLE_LABEL,
               DISTANCE_FROM_START_M, AISLE_WIDTH_M)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, [db_id, topology_id, aisle.id, aisle.label,
              aisle.distance_meters, grid.settings.aisle_width_meters])

    cell_lookup: dict[tuple, int] = {}
    slot_count = 0
    for cell in grid.cells:
        if cell.role not in ('left', 'right'):
            continue
        cell_id = await _next_val(db, "RRL_TOPOLOGY_CELL_SEQ")
        cell_lookup[(cell.row, cell.col)] = cell_id
        await db.execute("""
            INSERT INTO RABAEV.RRL_TOPOLOGY_CELL
              (CELL_ID, TOPOLOGY_ID, AISLE_ID, BAY_NO, SECTION_CODE,
               SIDE_CODE, IS_PICK_FACE, ACTIVE)
            VALUES (:1, :2, :3, :4, :5, :6, 1, 1)
        """, [cell_id, topology_id, aisle_id_map.get(cell.aisle_id),
              cell.row, _col_label(cell.col),
              'L' if cell.role == 'left' else 'R'])

        if cell.slot_division and (cell.slot_division.cols > 1 or cell.slot_division.rows > 1):
            await _create_pick_face_slots(
                db, cell_id, cell.slot_division.cols, cell.slot_division.rows)
            slot_count += cell.slot_division.cols * cell.slot_division.rows

    if grid.pick_sequences:
        route_id = await _next_val(db, "RRL_PICK_ROUTE_SEQ")
        await db.execute("""
            INSERT INTO RABAEV.RRL_PICK_ROUTE
              (ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_PATTERN, STATUS)
            VALUES (:1, :2, 'MAIN', :3, 'DRAFT')
        """, [route_id, topology_id, grid.route_pattern or 'U'])
        for s in grid.pick_sequences:
            cell_id = cell_lookup.get((s.row, s.col))
            if cell_id:
                await db.execute("""
                    INSERT INTO RABAEV.RRL_PICK_ROUTE_CELL
                      (ROUTE_CELL_ID, ROUTE_ID, TOPOLOGY_CELL_ID, PICK_SEQUENCE)
                    VALUES (RRL_PICK_ROUTE_CELL_SEQ.NEXTVAL, :1, :2, :3)
                """, [route_id, cell_id, s.pick_sequence])

    await db.commit()
    return {
        "topology_id": topology_id,
        "status": "DRAFT",
        "cell_count": len(cell_lookup),
        "slot_count": slot_count,
    }
```

---

## 13. React-компоненты

### 13.1 Структура

```
TopologyGridEditorPage.tsx               ← роут /admin/topology/new
├── GridEditorToolbar.tsx                ← размер, инструменты (React UI)
├── GridCanvasEditor.tsx                 ← два <canvas>, все pointer events
│   ├── useGridData.ts                   ← GridData + SelectionBitSet в useRef
│   ├── useCanvasRenderer.ts             ← drawFullGrid, drawSingleCell, scheduleRepaint
│   ├── usePointerInteraction.ts         ← hit-test, drag, zoom/pan
│   └── useRouteGenerator.ts            ← Z/U/SNAKE/TWO_BLOCK/ZONE_SWEEP алгоритмы
├── AisleManagerPanel.tsx                ← список аллей, расстояния (React, меняется редко)
├── SelectionActionBar.tsx               ← панель действий при выделении (React)
├── SlotDivisionDialog.tsx               ← диалог мелкоштучного деления
├── RouteAlgorithmPanel.tsx              ← выбор алгоритма, длина маршрута
└── GridEditorSaveModal.tsx              ← диалог сохранения
```

### 13.2 GridCanvasEditor — скелет

```tsx
export function GridCanvasEditor({ rows, cols }: Props) {
  const staticCanvas  = useRef<HTMLCanvasElement>(null);
  const dynamicCanvas = useRef<HTMLCanvasElement>(null);
  const gridData      = useRef(new GridData(rows, cols));
  const selection     = useRef(new SelectionBitSet(rows * cols));
  const transform     = useRef(new DOMMatrix());
  const dirty         = useRef(new Set<number>());
  const rafId         = useRef(0);

  const scheduleRepaint = useCallback(() => {
    if (rafId.current) return;
    rafId.current = requestAnimationFrame(() => {
      rafId.current = 0;
      const ctx = staticCanvas.current!.getContext('2d')!;
      if (dirty.current.size > 500) {
        drawFullGrid(ctx, gridData.current, selection.current,
                     transform.current, CELL_W, CELL_H);
      } else {
        for (const i of dirty.current) {
          drawSingleCell(ctx, i, gridData.current, selection.current,
                         transform.current, CELL_W, CELL_H);
        }
      }
      dirty.current.clear();
    });
  }, []);

  // ... pointer handlers, zoom handler

  return (
    <div style={{ position: 'relative', overflow: 'hidden', width: '100%', height: '100%' }}>
      <canvas ref={staticCanvas}  style={{ position: 'absolute', zIndex: 1 }} />
      <canvas ref={dynamicCanvas} style={{ position: 'absolute', zIndex: 2 }} />
    </div>
  );
}
```

### 13.3 Зум и пан

```typescript
function handleWheel(e: WheelEvent): void {
  e.preventDefault();
  const factor = e.deltaY < 0 ? 1.1 : 0.9;
  const rect = staticCanvas.current!.getBoundingClientRect();
  const cx = (e.clientX - rect.left) * devicePixelRatio;
  const cy = (e.clientY - rect.top)  * devicePixelRatio;
  // Масштабировать вокруг точки курсора
  transform.current = new DOMMatrix()
    .translate(cx, cy)
    .scale(factor)
    .translate(-cx, -cy)
    .multiply(transform.current);
  // Ограничить zoom: min 0.1, max 8.0
  const scale = transform.current.a;
  if (scale < 0.1 || scale > 8.0) { /* откатить */ }
  dirty.current.add(-1); // -1 = signal for full repaint
  scheduleRepaint();
}
```

---

## 14. Критерии приёмки

| # | Критерий | Метод |
|---|----------|-------|
| **ПРОИЗВОДИТЕЛЬНОСТЬ** | | |
| 1 | Первый рендер offscreen 15 000 ячеек < 20 ms | Jest perf test |
| 2 | Zoom / pan → drawImage offscreen < 1 ms | Jest perf test |
| 3 | Zoom при Retina DPR=2 стабильно 60 fps | DevTools FPS |
| 4 | Drag-выделение: dynamic canvas < 1 ms/кадр | DevTools FPS |
| 5 | Назначение роли 1000 ячеек (ensureFresh) < 20 ms | Jest perf test |
| 6 | Генерация маршрута (U, 7500 ячеек) < 50 ms | Jest perf test |
| 7 | OffscreenCanvas.markDirty не вызывается при zoom/pan | Code review |
| 8 | Память: GridData + offscreen 15 K ячеек < 50 MB heap | Chrome Memory |
| **ФУНКЦИОНАЛЬНОСТЬ** | | |
| 7 | Сетка задаётся 1×1 до 200×75 | UI |
| 8 | Drag рисует прямоугольник, все ячейки в нём выделяются | Manual |
| 9 | Shift+клик на заголовке = выделить весь столбец/строку | Manual |
| 10 | Sticky заголовки при прокрутке/зуме | Visual |
| 11 | inferAisles правильно объединяет L+R | Unit test |
| 12 | Расстояния по умолчанию = aisleIdx × width | Unit test |
| 13 | custom distance сохраняет флаг customDistance=true | Unit test |
| 14 | Диалог мелкоштучного деления показывает предпросмотр | Visual |
| 15 | 3×3 деление создаёт 9 строк RRL_TOPOLOGY_PICK_FACE_SLOT | DB |
| **АЛГОРИТМЫ МАРШРУТА** | | |
| 16 | Z: seq растёт сверху вниз, аллеи слева направо | Unit test |
| 17 | U: левый столбец 1→N, правый N→1 | Unit test |
| 18 | SNAKE: каждый следующий столбец меняет направление | Unit test |
| 19 | TWO_BLOCK: баи 1..N/2 получают меньший seq, чем N/2+1..N | Unit test |
| 20 | Все паттерны обходят 100% L/R-ячеек без пропусков | Unit test |
| 21 | calcRouteLengthM для 1-аллейного склада = (rows-1)×cellH×2 | Unit test |
| **ИНТЕГРАЦИЯ** | | |
| 22 | POST /from-grid создаёт DRAFT в Oracle | API test |
| 23 | GET /as-grid возвращает GridState для повторного открытия | API test |
| 24 | Validate после сохранения: 0 ошибок для корректной сетки | API test |
| 25 | Permission guard: без TOPOLOGY_EDIT — 403 | Manual |

---

## 15. Оценка трудоёмкости

| Задача | Дней |
|--------|------|
| GridData (TypedArrays) + SelectionBitSet | 0.5 |
| Canvas рендер: drawFullGrid, LOD, грязные регионы | 2 |
| Sticky заголовки строк/столбцов на canvas | 0.5 |
| Pointer events: click, drag-select, zoom/pan | 1.5 |
| Назначение ролей + AisleManagerPanel | 1 |
| Расстояния между аллеями | 0.5 |
| Алгоритмы Z/U/SNAKE + calcRouteLengthM | 0.5 |
| Алгоритмы TWO_BLOCK/ZONE_SWEEP | 0.5 |
| FISHBONE заглушка | 0.5 |
| Ручной LINEAR (drag-and-drop список) | 1 |
| RouteAlgorithmPanel + метрика длины | 0.5 |
| Мелкоштучные ячейки (диалог + canvas рендер) | 1 |
| API from-grid + as-grid (Python) + слоты | 1.5 |
| Миграция 046 (AISLE_LABEL, DISTANCE_M, PICK_FACE_SLOT) | 0.5 |
| Интеграция с TopologyAdminPage (редирект, кнопка) | 0.5 |
| Unit + performance tests | 1.5 |
| **Итого** | **12.5 дней** |
