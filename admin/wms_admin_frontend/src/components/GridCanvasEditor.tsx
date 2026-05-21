/**
 * GridCanvasEditor.tsx — Сеточный Canvas-редактор топологии склада.
 *
 * Архитектура двух слоёв:
 *   canvas#grid-static  — offscreen-буфер → drawImage: роли ячеек, маршрут.
 *                         Перерисовывается только при изменении данных (редко).
 *   canvas#grid-dynamic — drag-прямоугольник, hover, выделение.
 *                         Перерисовывается на каждый pointermove (60 fps).
 *
 * Взаимодействие:
 *   - Клик → выделить/снять ячейку
 *   - Drag → прямоугольное выделение
 *   - Ctrl+клик/drag → аддитивное выделение
 *   - Shift+клик на заголовке столбца → выделить весь столбец
 *   - Shift+клик на заголовке строки → выделить всю строку
 *   - Scroll → zoom (0.1× – 8×)
 *   - Middle-click drag → pan
 *   - Escape → снять выделение
 *
 * Производительность:
 *   - 15 000 ячеек → zoom/pan < 1 ms (один drawImage)
 *   - Смена роли → ensureFresh() < 20 ms (полный проход offscreen)
 *   - Drag-выделение → < 1 ms/кадр (dynamic canvas)
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  AisleDef,
  CELL_H,
  CELL_W,
  HEADER_COL_H,
  HEADER_ROW_W,
  AISLE_LABEL_H,
  GridData,
  OffscreenGridBuffer,
  ROLE,
  ROLE_COLORS,
  SelectionBitSet,
  colLabel,
} from "../hooks/gridData";

// ---------------------------------------------------------------------------
// Константы рендера
// ---------------------------------------------------------------------------

const MIN_ZOOM = 0.1;
const MAX_ZOOM = 8.0;

/** Цвет выделения ячейки (контур). */
const SEL_COLOR    = "#FBBF24";  // янтарный
/** Цвет drag-прямоугольника. */
const DRAG_FILL    = "rgba(251,191,36,0.15)";
const DRAG_STROKE  = "#F59E0B";
/** Цвет hover-подсветки. */
const HOVER_FILL   = "rgba(255,255,255,0.25)";
/** Цвет заголовков строк/столбцов. */
const HEADER_BG    = "#F3F4F6";
const HEADER_TEXT  = "#374151";
const HEADER_BORDER = "#D1D5DB";
/** Цвет меток аллей. */
const AISLE_LABEL_BG = "#EFF6FF";
const AISLE_LABEL_TEXT = "#1D4ED8";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

export interface GridCanvasEditorProps {
  /** Данные сетки (TypedArrays). Меняется через ref, не через состояние. */
  data: GridData;
  /** Offscreen-буфер. Создаётся снаружи, чтобы переживать ре-рендеры. */
  offscreen: OffscreenGridBuffer;
  /** Битсет выделения. */
  selection: SelectionBitSet;
  /** Список аллей для меток над столбцами. */
  aisles: AisleDef[];
  /** Показывать ли номера pick_sequence в ячейках. */
  showSequence: boolean;
  /**
   * Вызывается когда выделение изменилось.
   * Передаёт новое число выделенных ячеек (для обновления панели действий).
   */
  onSelectionChange: (count: number) => void;
  /**
   * Вызывается когда данные ячеек изменились (роль, слоты).
   * Сигнализирует родителю о необходимости пометить offscreen dirty.
   */
  onDataChange: () => void;
}

// ---------------------------------------------------------------------------
// Компонент
// ---------------------------------------------------------------------------

export function GridCanvasEditor({
  data,
  offscreen,
  selection,
  aisles,
  showSequence,
  onSelectionChange,
  onDataChange,
}: GridCanvasEditorProps) {
  // Рефы на два canvas-элемента
  const staticRef  = useRef<HTMLCanvasElement>(null);
  const dynamicRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Трансформация zoom+pan (DOMMatrix масштабирует только grid-область,
  // без учёта sticky-заголовков)
  const transformRef = useRef<DOMMatrix>(new DOMMatrix());

  // Состояние drag-выделения: {r1,c1} → {r2,c2}
  const dragRef = useRef<{
    active: boolean;
    startR: number; startC: number;
    curR: number;   curC: number;
    additive: boolean;
  } | null>(null);

  // Состояние pan (средняя кнопка или space+drag)
  const panRef = useRef<{ startX: number; startY: number; origin: DOMMatrix } | null>(null);

  // Индекс ячейки под курсором (для hover)
  const hoverRef = useRef<number>(-1);

  // ID анимационного кадра
  const staticRafRef  = useRef<number>(0);
  const dynamicRafRef = useRef<number>(0);

  // Флаг: нужна ли перерисовка static-слоя
  const staticDirtyRef = useRef<boolean>(true);

  // ---------------------------------------------------------------------------
  // Размеры canvas с учётом DPR
  // ---------------------------------------------------------------------------

  const [canvasSize, setCanvasSize] = useState({ w: 800, h: 600 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setCanvasSize({ w: Math.round(width), h: Math.round(height) });
    });
    ro.observe(container);
    return () => ro.disconnect();
  }, []);

  const dpr = window.devicePixelRatio || 1;
  const physW = canvasSize.w * dpr;
  const physH = canvasSize.h * dpr;

  // Применить DPR к canvas при изменении размера
  useEffect(() => {
    for (const ref of [staticRef, dynamicRef]) {
      const el = ref.current;
      if (!el) continue;
      el.width  = physW;
      el.height = physH;
      // CSS-размер совпадает с размером контейнера
      el.style.width  = `${canvasSize.w}px`;
      el.style.height = `${canvasSize.h}px`;
    }
    // После изменения размера — перерисовать всё
    markStaticDirty();
  }, [physW, physH]);

  // ---------------------------------------------------------------------------
  // Планирование перерисовок
  // ---------------------------------------------------------------------------

  /** Запланировать перерисовку static-слоя (роли, маршрут). */
  const markStaticDirty = useCallback(() => {
    staticDirtyRef.current = true;
    if (staticRafRef.current) return;
    staticRafRef.current = requestAnimationFrame(() => {
      staticRafRef.current = 0;
      repaintStatic();
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /** Запланировать перерисовку dynamic-слоя (drag, hover, выделение). */
  const scheduleDynamicRepaint = useCallback(() => {
    if (dynamicRafRef.current) return;
    dynamicRafRef.current = requestAnimationFrame(() => {
      dynamicRafRef.current = 0;
      repaintDynamic();
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------------------------------------------------------------------------
  // Перерисовка static-слоя
  // ---------------------------------------------------------------------------

  function repaintStatic() {
    const canvas = staticRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.save();
    ctx.scale(dpr, dpr);  // единицы — CSS-пиксели

    // 1. Скомпозировать offscreen с текущим zoom+pan (один drawImage)
    offscreen.ensureFresh(data, aisles, showSequence);
    const t = transformRef.current;

    ctx.clearRect(0, 0, canvasSize.w, canvasSize.h);
    ctx.save();
    // Сместить на HEADER_ROW_W, HEADER_COL_H + AISLE_LABEL_H, чтобы grid
    // начинался правее и ниже заголовков
    ctx.translate(HEADER_ROW_W, HEADER_COL_H + AISLE_LABEL_H);
    ctx.setTransform(
      t.a, t.b, t.c, t.d,
      t.e + HEADER_ROW_W,
      t.f + HEADER_COL_H + AISLE_LABEL_H,
    );
    offscreen.drawTo(ctx, t, physW / dpr, physH / dpr);
    ctx.restore();

    // 2. Нарисовать контуры выделения поверх ячеек
    drawSelectionOverlay(ctx, t);

    // 3. Sticky-заголовки (игнорируют zoom, всегда видны)
    drawHeaders(ctx, t);

    ctx.restore();
    staticDirtyRef.current = false;
  }

  /** Нарисовать жёлтые контуры выделенных ячеек. */
  function drawSelectionOverlay(ctx: CanvasRenderingContext2D, t: DOMMatrix) {
    if (selection.count === 0) return;

    const zoom = t.a;
    ctx.save();
    ctx.strokeStyle = SEL_COLOR;
    ctx.lineWidth   = Math.max(1.5, 2 / zoom);

    for (let i = 0; i < data.size; i++) {
      if (!selection.has(i)) continue;
      const r = Math.floor(i / data.cols);
      const c = i % data.cols;
      const sx = c * CELL_W * zoom + t.e + HEADER_ROW_W;
      const sy = r * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;
      ctx.strokeRect(sx + 1, sy + 1, CELL_W * zoom - 2, CELL_H * zoom - 2);
    }
    ctx.restore();
  }

  /** Нарисовать sticky-заголовки строк и столбцов. */
  function drawHeaders(ctx: CanvasRenderingContext2D, t: DOMMatrix) {
    const zoom = t.a;
    const panX = t.e;
    const panY = t.f;

    ctx.save();
    ctx.font = `${Math.max(9, Math.min(12, CELL_W * zoom * 0.5))}px monospace`;
    ctx.textAlign    = "center";
    ctx.textBaseline = "middle";

    // ---- Угол (пересечение строк и столбцов) ----
    ctx.fillStyle = HEADER_BG;
    ctx.fillRect(0, 0, HEADER_ROW_W, HEADER_COL_H + AISLE_LABEL_H);

    // ---- Заголовки столбцов (A, B, C...) ----
    ctx.fillStyle = HEADER_BG;
    ctx.fillRect(HEADER_ROW_W, AISLE_LABEL_H, canvasSize.w, HEADER_COL_H);

    ctx.fillStyle = HEADER_TEXT;
    for (let c = 0; c < data.cols; c++) {
      const x = c * CELL_W * zoom + panX + HEADER_ROW_W + CELL_W * zoom / 2;
      if (x < HEADER_ROW_W || x > canvasSize.w) continue;
      ctx.fillText(colLabel(c), x, AISLE_LABEL_H + HEADER_COL_H / 2);
    }

    // Линия под заголовками
    ctx.strokeStyle = HEADER_BORDER;
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(HEADER_ROW_W, AISLE_LABEL_H + HEADER_COL_H);
    ctx.lineTo(canvasSize.w, AISLE_LABEL_H + HEADER_COL_H);
    ctx.stroke();

    // ---- Метки аллей (полоса над заголовками столбцов) ----
    ctx.fillStyle = AISLE_LABEL_BG;
    ctx.fillRect(HEADER_ROW_W, 0, canvasSize.w, AISLE_LABEL_H);

    ctx.fillStyle  = AISLE_LABEL_TEXT;
    ctx.font       = `bold ${Math.max(8, Math.min(11, CELL_W * zoom * 0.45))}px sans-serif`;

    for (const aisle of aisles) {
      const x1 = aisle.leftCol  * CELL_W * zoom + panX + HEADER_ROW_W;
      const x2 = (aisle.rightCol + 1) * CELL_W * zoom + panX + HEADER_ROW_W;
      if (x2 < HEADER_ROW_W || x1 > canvasSize.w) continue;

      const mx = (x1 + x2) / 2;
      ctx.fillText(aisle.label, mx, AISLE_LABEL_H / 2);

      // Горизонтальная линия под меткой аллеи
      ctx.strokeStyle = AISLE_LABEL_TEXT;
      ctx.lineWidth   = 1;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(Math.max(HEADER_ROW_W, x1),  AISLE_LABEL_H - 1);
      ctx.lineTo(Math.min(canvasSize.w, x2),   AISLE_LABEL_H - 1);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // ---- Заголовки строк (01, 02, 03...) ----
    ctx.fillStyle = HEADER_BG;
    ctx.fillRect(0, HEADER_COL_H + AISLE_LABEL_H, HEADER_ROW_W, canvasSize.h);

    ctx.fillStyle = HEADER_TEXT;
    ctx.font      = `${Math.max(8, Math.min(10, CELL_H * zoom * 0.55))}px monospace`;
    ctx.textAlign = "right";

    for (let r = 0; r < data.rows; r++) {
      const y = r * CELL_H * zoom + panY + HEADER_COL_H + AISLE_LABEL_H + CELL_H * zoom / 2;
      if (y < HEADER_COL_H + AISLE_LABEL_H || y > canvasSize.h) continue;
      ctx.fillText(String(r + 1).padStart(3, "0"), HEADER_ROW_W - 4, y);
    }

    // Вертикальная линия правее заголовков строк
    ctx.strokeStyle = HEADER_BORDER;
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(HEADER_ROW_W, HEADER_COL_H + AISLE_LABEL_H);
    ctx.lineTo(HEADER_ROW_W, canvasSize.h);
    ctx.stroke();

    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Перерисовка dynamic-слоя (drag-прямоугольник, hover)
  // ---------------------------------------------------------------------------

  function repaintDynamic() {
    const canvas = dynamicRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, canvasSize.w, canvasSize.h);

    const t    = transformRef.current;
    const zoom = t.a;

    // Hover-подсветка
    if (hoverRef.current >= 0) {
      const i = hoverRef.current;
      const r = Math.floor(i / data.cols);
      const c = i % data.cols;
      const sx = c * CELL_W * zoom + t.e + HEADER_ROW_W;
      const sy = r * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;

      if (data.roles[i] !== ROLE.EMPTY) {
        ctx.fillStyle = HOVER_FILL;
        ctx.fillRect(sx, sy, CELL_W * zoom, CELL_H * zoom);
      }
    }

    // Drag-прямоугольник выделения
    if (dragRef.current?.active) {
      const d = dragRef.current;
      const x1 = Math.min(d.startC, d.curC) * CELL_W * zoom + t.e + HEADER_ROW_W;
      const y1 = Math.min(d.startR, d.curR) * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;
      const x2 = (Math.max(d.startC, d.curC) + 1) * CELL_W * zoom + t.e + HEADER_ROW_W;
      const y2 = (Math.max(d.startR, d.curR) + 1) * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;

      ctx.fillStyle   = DRAG_FILL;
      ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
      ctx.strokeStyle = DRAG_STROKE;
      ctx.lineWidth   = 1.5;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    }

    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Hit-test: экранные координаты → (row, col) 0-based
  // ---------------------------------------------------------------------------

  function canvasToCell(
    clientX: number, clientY: number,
  ): { r: number; c: number } | null {
    const canvas = staticRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    // Перевести в CSS-пиксели относительно canvas
    const cx = clientX - rect.left;
    const cy = clientY - rect.top;

    // Убрать отступ заголовков
    const gx = cx - HEADER_ROW_W;
    const gy = cy - HEADER_COL_H - AISLE_LABEL_H;
    if (gx < 0 || gy < 0) return null;

    // Применить обратную трансформацию
    const t   = transformRef.current;
    const inv = t.inverse();
    const wx  = inv.a * gx + inv.c * gy + inv.e;
    const wy  = inv.b * gx + inv.d * gy + inv.f;

    const c = Math.floor(wx / CELL_W);
    const r = Math.floor(wy / CELL_H);

    if (r >= 0 && r < data.rows && c >= 0 && c < data.cols) {
      return { r, c };
    }
    return null;
  }

  /** Определить, кликнул ли пользователь по заголовку строки (левая полоса). */
  function isRowHeader(clientX: number, clientY: number): number | null {
    const canvas = staticRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const cx = clientX - rect.left;
    const cy = clientY - rect.top;
    if (cx >= 0 && cx < HEADER_ROW_W && cy >= HEADER_COL_H + AISLE_LABEL_H) {
      const t    = transformRef.current;
      const gy   = cy - HEADER_COL_H - AISLE_LABEL_H;
      const wy   = (gy - t.f) / t.a;
      const r    = Math.floor(wy / CELL_H);
      if (r >= 0 && r < data.rows) return r;
    }
    return null;
  }

  /** Определить, кликнул ли пользователь по заголовку столбца (верхняя полоса). */
  function isColHeader(clientX: number, clientY: number): number | null {
    const canvas = staticRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const cx = clientX - rect.left;
    const cy = clientY - rect.top;
    if (
      cx >= HEADER_ROW_W &&
      cy >= AISLE_LABEL_H &&
      cy < HEADER_COL_H + AISLE_LABEL_H
    ) {
      const t  = transformRef.current;
      const gx = cx - HEADER_ROW_W;
      const wx = (gx - t.e) / t.a;
      const c  = Math.floor(wx / CELL_W);
      if (c >= 0 && c < data.cols) return c;
    }
    return null;
  }

  // ---------------------------------------------------------------------------
  // Pointer-события
  // ---------------------------------------------------------------------------

  const handlePointerDown = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    // Клик по заголовку строки (Shift — выделить всю строку)
    if (e.shiftKey) {
      const row = isRowHeader(e.clientX, e.clientY);
      if (row !== null) {
        selection.selectRow(row, data.cols, e.ctrlKey || e.metaKey);
        onSelectionChange(selection.count);
        markStaticDirty();
        return;
      }
      // Клик по заголовку столбца
      const col = isColHeader(e.clientX, e.clientY);
      if (col !== null) {
        selection.selectCol(col, data.rows, data.cols, e.ctrlKey || e.metaKey);
        onSelectionChange(selection.count);
        markStaticDirty();
        return;
      }
    }

    // Middle-click или Space+click → pan
    if (e.button === 1) {
      panRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        origin: new DOMMatrix(transformRef.current.toString()),
      };
      e.currentTarget.setPointerCapture(e.pointerId);
      return;
    }

    const cell = canvasToCell(e.clientX, e.clientY);
    if (!cell) return;

    const { r, c } = cell;
    const i        = r * data.cols + c;
    const additive = e.ctrlKey || e.metaKey;

    if (!additive) {
      // Простой клик без Ctrl — начать drag-выделение
      selection.clearAll();
    }

    // Запустить drag-режим
    dragRef.current = {
      active:   true,
      startR:   r, startC: c,
      curR:     r, curC:   c,
      additive,
    };

    // Немедленно выделить стартовую ячейку
    selection.set(i);
    onSelectionChange(selection.count);
    markStaticDirty();
    scheduleDynamicRepaint();

    e.currentTarget.setPointerCapture(e.pointerId);
  }, [data, selection, onSelectionChange, markStaticDirty, scheduleDynamicRepaint]);

  const handlePointerMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    // Pan
    if (panRef.current) {
      const dx = e.clientX - panRef.current.startX;
      const dy = e.clientY - panRef.current.startY;
      const o  = panRef.current.origin;
      transformRef.current = new DOMMatrix([
        o.a, o.b, o.c, o.d,
        o.e + dx, o.f + dy,
      ]);
      markStaticDirty();
      return;
    }

    const cell = canvasToCell(e.clientX, e.clientY);
    const newHover = cell ? cell.r * data.cols + cell.c : -1;

    if (newHover !== hoverRef.current) {
      hoverRef.current = newHover;
      scheduleDynamicRepaint();
    }

    // Drag-выделение
    if (dragRef.current?.active && cell) {
      dragRef.current.curR = cell.r;
      dragRef.current.curC = cell.c;
      scheduleDynamicRepaint();
    }
  }, [data, markStaticDirty, scheduleDynamicRepaint]);

  const handlePointerUp = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    // Завершить pan
    if (panRef.current) {
      panRef.current = null;
      return;
    }

    // Применить прямоугольное выделение
    if (dragRef.current?.active) {
      const d = dragRef.current;
      selection.selectRect(
        d.startR, d.startC,
        d.curR, d.curC,
        data.cols,
        d.additive,
      );
      dragRef.current = null;
      onSelectionChange(selection.count);
      markStaticDirty();
      scheduleDynamicRepaint();
    }
  }, [data, selection, onSelectionChange, markStaticDirty, scheduleDynamicRepaint]);

  /** Zoom колесом мыши вокруг точки курсора. */
  const handleWheel = useCallback((e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();

    const factor  = e.deltaY < 0 ? 1.12 : 1 / 1.12;
    const canvas  = staticRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    // Центр зума — позиция курсора в grid-пространстве (без заголовков)
    const cx = e.clientX - rect.left - HEADER_ROW_W;
    const cy = e.clientY - rect.top  - HEADER_COL_H - AISLE_LABEL_H;

    const t        = transformRef.current;
    const newScale = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, t.a * factor));
    const realFactor = newScale / t.a;

    // Зум относительно точки курсора: translate(cx,cy) · scale · translate(-cx,-cy)
    transformRef.current = new DOMMatrix([
      newScale,
      0, 0,
      newScale,
      t.e + cx * (1 - realFactor),
      t.f + cy * (1 - realFactor),
    ]);

    markStaticDirty();
  }, [markStaticDirty]);

  /** Escape — снять выделение. */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        selection.clearAll();
        dragRef.current = null;
        onSelectionChange(0);
        markStaticDirty();
        scheduleDynamicRepaint();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selection, onSelectionChange, markStaticDirty, scheduleDynamicRepaint]);

  // ---------------------------------------------------------------------------
  // Публичные методы через ref (для панели действий)
  // Вызываются из TopologyGridEditorPage
  // ---------------------------------------------------------------------------

  /** Пометить offscreen устаревшим и перерисовать (после смены роли). */
  const refresh = useCallback(() => {
    offscreen.markDirty();
    markStaticDirty();
    onDataChange();
  }, [offscreen, markStaticDirty, onDataChange]);

  // Экспортируем refresh через imperativeHandle — не нужен, просто вызываем из пропсов.
  // Родитель вызывает refresh напрямую через проп.

  // ---------------------------------------------------------------------------
  // Первый рендер и перерисовка при смене showSequence
  // ---------------------------------------------------------------------------

  useEffect(() => {
    offscreen.markDirty();
    markStaticDirty();
  }, [showSequence, offscreen, markStaticDirty]);

  useEffect(() => {
    markStaticDirty();
  }, [aisles, markStaticDirty]);

  // ---------------------------------------------------------------------------
  // JSX
  // ---------------------------------------------------------------------------

  return (
    <div
      ref={containerRef}
      style={{
        position:  "relative",
        width:     "100%",
        height:    "100%",
        overflow:  "hidden",
        cursor:    panRef.current ? "grabbing" : "crosshair",
        userSelect: "none",
      }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onWheel={handleWheel}
    >
      {/* Static-слой: ячейки, маршрут, выделение, заголовки */}
      <canvas
        ref={staticRef}
        style={{ position: "absolute", top: 0, left: 0, zIndex: 1 }}
      />
      {/* Dynamic-слой: drag-прямоугольник, hover */}
      <canvas
        ref={dynamicRef}
        style={{
          position:       "absolute",
          top:            0,
          left:           0,
          zIndex:         2,
          pointerEvents:  "none",  // события идут на container, не на dynamic-canvas
        }}
      />

      {/* Подсказка в правом нижнем углу */}
      <div style={{
        position:   "absolute",
        bottom:     8,
        right:      12,
        fontSize:   11,
        color:      "#94A3B8",
        pointerEvents: "none",
        userSelect: "none",
      }}>
        Scroll: zoom · MMB drag: pan · Shift+клик заголовка: выделить строку/столбец
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Хелперы для внешнего использования
// ---------------------------------------------------------------------------

/**
 * Нарисовать стрелки порядка обхода (overlay маршрута).
 * Вызывается снаружи на dynamic-canvas когда пользователь смотрит маршрут.
 *
 * @param ctx      Контекст dynamic-canvas (уже масштабирован под DPR)
 * @param data     Данные сетки
 * @param t        Текущий transform
 * @param canvasW  Ширина canvas в CSS-пикселях
 * @param canvasH  Высота canvas в CSS-пикселях
 */
export function drawRouteArrows(
  ctx: CanvasRenderingContext2D,
  data: GridData,
  t: DOMMatrix,
  canvasW: number,
  canvasH: number,
): void {
  const zoom = t.a;
  if (zoom < 0.4) return; // при малом масштабе стрелки нечитаемы

  // Собрать упорядоченные ячейки
  let maxSeq = -1;
  for (let i = 0; i < data.size; i++) {
    if (data.pickSeqs[i] > maxSeq) maxSeq = data.pickSeqs[i];
  }
  if (maxSeq < 0) return;

  const ordered = new Int32Array(maxSeq + 1).fill(-1);
  for (let i = 0; i < data.size; i++) {
    const s = data.pickSeqs[i];
    if (s >= 0) ordered[s] = i;
  }

  ctx.save();
  ctx.strokeStyle = "rgba(5, 150, 105, 0.7)";
  ctx.lineWidth   = Math.max(1, 1.5 * zoom);
  ctx.setLineDash([3, 3]);

  for (let s = 1; s <= maxSeq; s++) {
    const from = ordered[s - 1];
    const to   = ordered[s];
    if (from < 0 || to < 0) continue;

    const r1 = Math.floor(from / data.cols);
    const c1 = from % data.cols;
    const r2 = Math.floor(to   / data.cols);
    const c2 = to   % data.cols;

    const x1 = (c1 + 0.5) * CELL_W * zoom + t.e + HEADER_ROW_W;
    const y1 = (r1 + 0.5) * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;
    const x2 = (c2 + 0.5) * CELL_W * zoom + t.e + HEADER_ROW_W;
    const y2 = (r2 + 0.5) * CELL_H * zoom + t.f + HEADER_COL_H + AISLE_LABEL_H;

    // Пропустить стрелки вне viewport
    if (
      (x1 < HEADER_ROW_W && x2 < HEADER_ROW_W) ||
      (x1 > canvasW       && x2 > canvasW)       ||
      (y1 < HEADER_COL_H  && y2 < HEADER_COL_H)  ||
      (y1 > canvasH       && y2 > canvasH)
    ) continue;

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    // Наконечник стрелки
    drawArrowHead(ctx, x1, y1, x2, y2, 5 * zoom);
  }

  ctx.setLineDash([]);
  ctx.restore();
}

function drawArrowHead(
  ctx: CanvasRenderingContext2D,
  x1: number, y1: number,
  x2: number, y2: number,
  size: number,
): void {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  ctx.save();
  ctx.translate(x2, y2);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(-size, -size / 2);
  ctx.lineTo(-size,  size / 2);
  ctx.closePath();
  ctx.fillStyle = "rgba(5, 150, 105, 0.7)";
  ctx.fill();
  ctx.restore();
}

/**
 * Тип для передачи цветов ролей снаружи в легенду.
 * Экспортируется для использования в TopologyGridEditorPage.
 */
export { ROLE_COLORS };
