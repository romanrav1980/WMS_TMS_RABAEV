/**
 * TopologyGridEditorPage.tsx — Страница создания топологии склада с нуля.
 *
 * Рабочий процесс:
 *   1. Задать размер сетки и ширину прохода
 *   2. Выделить столбцы → назначить роли (ЛЕВЫЕ / ПРАВЫЕ / ПРОХОД)
 *   3. Система автоматически находит аллеи (inferAisles)
 *   4. При необходимости скорректировать расстояния аллей
 *   5. Отметить мелкоштучные ячейки (split pick-face)
 *   6. Выбрать алгоритм маршрута → Рассчитать
 *   7. Сохранить черновик → открывается в TopologyAdminPage для валидации
 *
 * Производительность:
 *   - GridData/SelectionBitSet/OffscreenGridBuffer хранятся в useRef
 *     (не в useState) → React никогда не делает diff этих данных
 *   - Перерисовка canvas управляется вручную через markDirty
 *   - Панели слева и снизу — обычный React-DOM (обновляются редко)
 */

import { useCallback, useMemo, useRef, useState } from "react";
import {
  AisleDef,
  DEFAULT_SETTINGS,
  GridData,
  GridSettings,
  OffscreenGridBuffer,
  ROLE,
  RoleValue,
  SelectionBitSet,
  calcRouteLengthM,
  colLabel,
  inferAisles,
} from "../hooks/gridData";
import {
  RouteGenParams,
  RoutePattern,
  generateRoute,
} from "../hooks/useRouteGenerator";
import { GridCanvasEditor } from "./GridCanvasEditor";

// ---------------------------------------------------------------------------
// Константы
// ---------------------------------------------------------------------------

const API_BASE       = import.meta.env.VITE_API_BASE       || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

function apiHeaders(extra?: HeadersInit): HeadersInit {
  return { Authorization: `Basic ${btoa(API_BASIC_AUTH)}`, ...extra };
}

/** Пресеты для диалога мелкоштучного деления. */
const SLOT_PRESETS: Array<{ cols: number; rows: number; label: string }> = [
  { cols: 1, rows: 1, label: "1×1 (нет)" },
  { cols: 2, rows: 2, label: "2×2 (4 слота)" },
  { cols: 3, rows: 3, label: "3×3 (9 слотов)" },
  { cols: 2, rows: 4, label: "2×4 (8 слотов)" },
  { cols: 1, rows: 5, label: "1×5 (5 слотов)" },
];

const PATTERN_LABELS: Record<RoutePattern, string> = {
  Z:          "Z-образный",
  U:          "U-образный (рекомендуется)",
  SNAKE:      "Змейка",
  TWO_BLOCK:  "Двухблочный",
  ZONE_SWEEP: "По зонам",
  LINEAR:     "Ручной",
};

const PATTERN_HINTS: Record<RoutePattern, string> = {
  Z:          "Все аллеи насквозь, слева направо",
  U:          "U-поворот у дальнего торца — меньше ходьбы",
  SNAKE:      "S-образный, минимум разворотов на 180°",
  TWO_BLOCK:  "Склад пополам, два встречных потока",
  ZONE_SWEEP: "Сначала зона A, потом B, потом C...",
  LINEAR:     "Задать порядок вручную (drag-and-drop)",
};

// ---------------------------------------------------------------------------
// Типы локального состояния
// ---------------------------------------------------------------------------

/** Состояние диалога мелкоштучного деления. */
interface SlotDialogState {
  open: boolean;
  slotCols: number;
  slotRows: number;
}

/** Состояние диалога сохранения топологии. */
interface SaveDialogState {
  open: boolean;
  label: string;
  warehouseId: number;
  saving: boolean;
  error: string | null;
}

// ---------------------------------------------------------------------------
// Компонент
// ---------------------------------------------------------------------------

export function TopologyGridEditorPage({ onBack }: { onBack: () => void }) {
  // ---- Настройки сетки (меняются в форме сверху, до начала рисования) ----
  const [rows, setRows] = useState(50);
  const [cols, setCols] = useState(9);
  const [settings, setSettings] = useState<GridSettings>(DEFAULT_SETTINGS);

  // ---- Основные данные сетки хранятся в ref — не вызывают React-ре-рендер ----
  const gridRef       = useRef<GridData>(new GridData(rows, cols));
  const selectionRef  = useRef<SelectionBitSet>(new SelectionBitSet(rows * cols));
  const offscreenRef  = useRef<OffscreenGridBuffer>(new OffscreenGridBuffer(cols, rows));

  // ---- Аллеи — список, нужен для React-UI (левая панель, метки) ----
  const [aisles, setAisles] = useState<AisleDef[]>([]);

  // ---- Состояние UI (влияет на DOM — useState) ----
  const [selectionCount,  setSelectionCount]  = useState(0);
  const [routePattern,    setRoutePattern]    = useState<RoutePattern>("U");
  const [twoBlockSplit,   setTwoBlockSplit]   = useState(0.5);
  const [routeLength,     setRouteLength]     = useState<number | null>(null);
  const [showSequence,    setShowSequence]    = useState(false);
  const [slotDialog,      setSlotDialog]      = useState<SlotDialogState>({
    open: false, slotCols: 3, slotRows: 3,
  });
  const [saveDialog, setSaveDialog] = useState<SaveDialogState>({
    open:        false,
    label:       "Новая топология",
    warehouseId: 1,
    saving:      false,
    error:       null,
  });

  // Ref для вызова refresh снаружи (нужен GridCanvasEditor)
  const refreshCanvasRef = useRef<(() => void) | null>(null);

  // ---------------------------------------------------------------------------
  // Сброс сетки при изменении размеров
  // ---------------------------------------------------------------------------

  const handleResizeApply = useCallback(() => {
    gridRef.current      = new GridData(rows, cols);
    selectionRef.current = new SelectionBitSet(rows * cols);
    offscreenRef.current = new OffscreenGridBuffer(cols, rows);
    setAisles([]);
    setSelectionCount(0);
    setRouteLength(null);
    setShowSequence(false);
    offscreenRef.current.markDirty();
    refreshCanvasRef.current?.();
  }, [rows, cols]);

  // ---------------------------------------------------------------------------
  // Назначение ролей выделенным ячейкам
  // ---------------------------------------------------------------------------

  const assignRole = useCallback((role: RoleValue) => {
    const data = gridRef.current;
    const sel  = selectionRef.current;
    if (sel.count === 0) return;

    // Назначить роль всем выделенным ячейкам
    sel.forEach((i) => {
      data.roles[i] = role;
      // Снять привязку к аллее — inferAisles пересчитает
      data.aisleIdx[i] = -1;
    });

    // Пересчитать аллеи на основе новых ролей
    const newAisles = inferAisles(data, settings);
    setAisles(newAisles);

    // Сбросить маршрут (роли изменились)
    data.clearRoute();
    setRouteLength(null);
    setShowSequence(false);

    // Пометить offscreen устаревшим и перерисовать
    offscreenRef.current.markDirty();
    refreshCanvasRef.current?.();
  }, [settings]);

  /** Очистить роль выделенных ячеек (вернуть в EMPTY). */
  const clearRole = useCallback(() => assignRole(ROLE.EMPTY), [assignRole]);

  // ---------------------------------------------------------------------------
  // Мелкоштучное деление
  // ---------------------------------------------------------------------------

  const applySlotDivision = useCallback(() => {
    const { slotCols, slotRows } = slotDialog;
    const data = gridRef.current;
    const sel  = selectionRef.current;

    sel.forEach((i) => {
      // Деление применяется только к L/R ячейкам
      if (data.roles[i] === ROLE.LEFT || data.roles[i] === ROLE.RIGHT) {
        data.slotCols[i] = slotCols <= 1 ? 0 : slotCols;
        data.slotRows[i] = slotRows <= 1 ? 0 : slotRows;
      }
    });

    offscreenRef.current.markDirty();
    refreshCanvasRef.current?.();
    setSlotDialog((d) => ({ ...d, open: false }));
  }, [slotDialog]);

  // ---------------------------------------------------------------------------
  // Генерация маршрута
  // ---------------------------------------------------------------------------

  const handleGenerateRoute = useCallback(() => {
    const data = gridRef.current;
    if (aisles.length === 0) {
      alert("Сначала назначьте роли ячейкам и создайте аллеи.");
      return;
    }

    const params: RouteGenParams = {
      twoBlockSplit: twoBlockSplit,
      zoneSweepBase: "U",
      bayHeightM:    settings.bayHeightMeters,
    };

    const result = generateRoute(routePattern, data, aisles, params);
    setRouteLength(result.lengthMeters);
    setShowSequence(true);

    offscreenRef.current.markDirty();
    refreshCanvasRef.current?.();
  }, [aisles, routePattern, twoBlockSplit, settings]);

  // ---------------------------------------------------------------------------
  // Обновление расстояния аллеи
  // ---------------------------------------------------------------------------

  const updateAisleDistance = useCallback((aisleId: string, meters: number) => {
    setAisles((prev) =>
      prev.map((a) =>
        a.id === aisleId ? { ...a, distanceMeters: meters, customDistance: true } : a,
      ),
    );
  }, []);

  const recalcDefaultDistances = useCallback(() => {
    setAisles((prev) =>
      prev.map((a, i) => ({
        ...a,
        distanceMeters: i * settings.aisleWidthMeters,
        customDistance: false,
      })),
    );
  }, [settings.aisleWidthMeters]);

  // ---------------------------------------------------------------------------
  // Сохранение топологии
  // ---------------------------------------------------------------------------

  const handleSave = useCallback(async () => {
    const data = gridRef.current;
    setSaveDialog((d) => ({ ...d, saving: true, error: null }));

    // Собрать payload
    const cells: Array<{
      row: number; col: number; role: string;
      aisle_id: string | null;
      slot_division?: { cols: number; rows: number };
    }> = [];

    for (let i = 0; i < data.size; i++) {
      const role = data.roles[i];
      if (role === ROLE.EMPTY || role === ROLE.PASSAGE) continue;

      const r   = data.rowOf(i);
      const c   = data.colOf(i);
      const ai  = data.aisleIdx[i];
      const sc  = data.slotCols[i];
      const sr  = data.slotRows[i];

      cells.push({
        row:      r,
        col:      c,
        role:     role === ROLE.LEFT ? "left" : "right",
        aisle_id: ai >= 0 ? aisles[ai]?.id ?? null : null,
        ...(sc > 1 || sr > 1 ? { slot_division: { cols: sc || 1, rows: sr || 1 } } : {}),
      });
    }

    const pickSeqs: Array<{ row: number; col: number; pick_sequence: number }> = [];
    for (let i = 0; i < data.size; i++) {
      const s = data.pickSeqs[i];
      if (s >= 0) {
        pickSeqs.push({ row: data.rowOf(i), col: data.colOf(i), pick_sequence: s });
      }
    }

    const payload = {
      warehouse_id: saveDialog.warehouseId,
      label:        saveDialog.label,
      grid: {
        rows:    data.rows,
        cols:    data.cols,
        settings: {
          aisle_width_meters: settings.aisleWidthMeters,
          bay_height_meters:  settings.bayHeightMeters,
        },
        cells,
        aisles: aisles.map((a) => ({
          id:               a.id,
          label:            a.label,
          left_col:         a.leftCol,
          right_col:        a.rightCol,
          passage_col:      a.passageCol ?? null,
          distance_meters:  a.distanceMeters,
          custom_distance:  a.customDistance,
        })),
        route_pattern: routePattern,
        pick_sequences: pickSeqs,
      },
    };

    try {
      const resp = await fetch(`${API_BASE}/api/admin/topologies/from-grid`, {
        method:  "POST",
        headers: apiHeaders({ "Content-Type": "application/json" }),
        body:    JSON.stringify(payload),
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`${resp.status}: ${text}`);
      }

      const result = await resp.json() as { topology_id: number };
      setSaveDialog((d) => ({ ...d, saving: false, open: false }));
      // Вернуться в TopologyAdminPage и открыть только что созданную топологию
      onBack();
    } catch (e) {
      setSaveDialog((d) => ({
        ...d,
        saving: false,
        error:  e instanceof Error ? e.message : String(e),
      }));
    }
  }, [aisles, routePattern, saveDialog, settings, onBack]);

  // ---------------------------------------------------------------------------
  // Вычислить длину маршрута (при изменении aisles.distanceMeters)
  // ---------------------------------------------------------------------------

  const currentLengthM = useMemo(() => {
    if (!showSequence) return null;
    return calcRouteLengthM(gridRef.current, aisles, settings.bayHeightMeters);
  }, [aisles, showSequence, settings.bayHeightMeters]);

  const displayLength = currentLengthM ?? routeLength;

  // ---------------------------------------------------------------------------
  // Рендер
  // ---------------------------------------------------------------------------

  return (
    <div style={{
      display:       "grid",
      gridTemplateRows: "auto 1fr auto",
      gridTemplateColumns: "260px 1fr",
      height:        "100vh",
      background:    "var(--bg)",
      fontFamily:    "Inter, 'Segoe UI', Arial, sans-serif",
    }}>
      {/* ================================================================
          TOPBAR
          ================================================================ */}
      <div style={{
        gridColumn:    "1 / -1",
        display:       "flex",
        alignItems:    "center",
        gap:           12,
        padding:       "10px 18px",
        borderBottom:  "1px solid var(--line)",
        background:    "rgba(255,255,255,.94)",
        backdropFilter: "blur(10px)",
      }}>
        <button
          onClick={onBack}
          style={{ ...btnStyle, background: "var(--soft)", color: "var(--text)" }}
        >
          ← Назад
        </button>

        <span style={{ fontWeight: 800, fontSize: 16 }}>
          Редактор топологии склада
        </span>

        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          Сетка: {rows} × {cols} · Ячеек отбора: {gridRef.current.pickCellCount}
        </span>

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button
            onClick={() => setSaveDialog((d) => ({ ...d, open: true }))}
            style={{ ...btnStyle, background: "var(--blue)", color: "#fff" }}
            disabled={aisles.length === 0}
            title={aisles.length === 0 ? "Сначала назначьте аллеи" : "Сохранить черновик"}
          >
            💾 Сохранить черновик
          </button>
        </div>
      </div>

      {/* ================================================================
          ЛЕВАЯ ПАНЕЛЬ: инструменты + аллеи
          ================================================================ */}
      <div style={{
        gridRow:     2,
        borderRight: "1px solid var(--line)",
        background:  "var(--card)",
        display:     "flex",
        flexDirection: "column",
        overflow:    "hidden",
        fontSize:    13,
      }}>
        <div style={{ flex: 1, overflow: "auto", padding: "12px 14px" }}>

          {/* ---- Размер сетки ---- */}
          <Section title="Размер сетки">
            <LabelRow label="Строк (баев)">
              <NumInput value={rows} min={1} max={500}
                onChange={setRows} />
            </LabelRow>
            <LabelRow label="Столбцов">
              <NumInput value={cols} min={1} max={200}
                onChange={setCols} />
            </LabelRow>
            <LabelRow label="Ширина прохода (м)">
              <NumInput
                value={settings.aisleWidthMeters}
                min={0.5} max={20} step={0.5}
                onChange={(v) => setSettings((s) => ({ ...s, aisleWidthMeters: v }))}
              />
            </LabelRow>
            <LabelRow label="Высота бая (м)">
              <NumInput
                value={settings.bayHeightMeters}
                min={0.5} max={10} step={0.5}
                onChange={(v) => setSettings((s) => ({ ...s, bayHeightMeters: v }))}
              />
            </LabelRow>
            <button onClick={handleResizeApply} style={{ ...btnStyle, width: "100%", marginTop: 8 }}>
              Применить размер
            </button>
          </Section>

          {/* ---- Назначить роль ---- */}
          <Section title={`Назначить${selectionCount > 0 ? ` (${selectionCount} ячеек)` : ""}`}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
              <button
                onClick={() => assignRole(ROLE.LEFT)}
                disabled={selectionCount === 0}
                style={{ ...btnStyle, background: "#3B82F6", color: "#fff" }}
              >
                ◀ Левые
              </button>
              <button
                onClick={() => assignRole(ROLE.RIGHT)}
                disabled={selectionCount === 0}
                style={{ ...btnStyle, background: "#F97316", color: "#fff" }}
              >
                Правые ▶
              </button>
              <button
                onClick={() => assignRole(ROLE.PASSAGE)}
                disabled={selectionCount === 0}
                style={{ ...btnStyle, background: "#9CA3AF", color: "#fff" }}
              >
                ▓ Проход
              </button>
              <button
                onClick={clearRole}
                disabled={selectionCount === 0}
                style={{ ...btnStyle }}
              >
                ✕ Очистить
              </button>
            </div>
            <button
              onClick={() => setSlotDialog((d) => ({ ...d, open: true }))}
              disabled={selectionCount === 0}
              style={{ ...btnStyle, width: "100%", marginTop: 6 }}
              title="Разделить ячейку на мелкоштучные слоты"
            >
              🔲 Мелкоштучная...
            </button>
          </Section>

          {/* ---- Аллеи ---- */}
          <Section title="Аллеи">
            {aisles.length === 0 ? (
              <p style={{ color: "var(--muted)", fontSize: 12, margin: 0 }}>
                Назначьте соседние столбцы как «Левые» и «Правые» — аллеи определятся автоматически.
              </p>
            ) : (
              <>
                {aisles.map((aisle) => (
                  <AisleRow
                    key={aisle.id}
                    aisle={aisle}
                    onDistanceChange={(m) => updateAisleDistance(aisle.id, m)}
                  />
                ))}
                <button
                  onClick={recalcDefaultDistances}
                  style={{ ...btnStyle, width: "100%", marginTop: 6, fontSize: 11 }}
                >
                  ↺ Пересчитать расстояния автоматически
                </button>
              </>
            )}
          </Section>

          {/* ---- Алгоритм маршрута ---- */}
          <Section title="Алгоритм маршрута">
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {(Object.keys(PATTERN_LABELS) as RoutePattern[]).map((p) => (
                <label key={p} style={{
                  display:   "flex",
                  alignItems: "flex-start",
                  gap:       6,
                  cursor:    "pointer",
                  padding:   "4px 6px",
                  borderRadius: 6,
                  background: routePattern === p ? "var(--soft)" : "transparent",
                }}>
                  <input
                    type="radio"
                    name="routePattern"
                    value={p}
                    checked={routePattern === p}
                    onChange={() => setRoutePattern(p)}
                    style={{ marginTop: 2 }}
                  />
                  <span>
                    <b style={{ fontSize: 12 }}>{PATTERN_LABELS[p]}</b>
                    <br />
                    <span style={{ fontSize: 11, color: "var(--muted)" }}>
                      {PATTERN_HINTS[p]}
                    </span>
                  </span>
                </label>
              ))}
            </div>

            {routePattern === "TWO_BLOCK" && (
              <LabelRow label={`Точка разреза (${Math.round(twoBlockSplit * 100)}%)`}>
                <input
                  type="range" min={10} max={90} step={5}
                  value={Math.round(twoBlockSplit * 100)}
                  onChange={(e) => setTwoBlockSplit(Number(e.target.value) / 100)}
                  style={{ width: "100%" }}
                />
              </LabelRow>
            )}

            <button
              onClick={handleGenerateRoute}
              disabled={aisles.length === 0}
              style={{ ...btnStyle, width: "100%", marginTop: 8,
                background: "var(--green)", color: "#fff" }}
            >
              ▶ Рассчитать маршрут
            </button>

            {displayLength !== null && (
              <div style={{
                marginTop: 8, padding: "6px 10px",
                background: "#ECFDF5", borderRadius: 6, fontSize: 12, color: "#065F46",
              }}>
                Длина маршрута: <b>{Math.round(displayLength)} м</b>
                &nbsp;·&nbsp;
                <button
                  style={{ background: "none", border: "none", color: "#065F46",
                    cursor: "pointer", fontSize: 12, padding: 0, textDecoration: "underline" }}
                  onClick={() => setShowSequence((v) => !v)}
                >
                  {showSequence ? "Скрыть номера" : "Показать номера"}
                </button>
              </div>
            )}
          </Section>

        </div>{/* /scroll */}
      </div>{/* /left panel */}

      {/* ================================================================
          CANVAS-ОБЛАСТЬ
          ================================================================ */}
      <div style={{ gridRow: 2, position: "relative", overflow: "hidden" }}>
        <GridCanvasEditor
          data={gridRef.current}
          offscreen={offscreenRef.current}
          selection={selectionRef.current}
          aisles={aisles}
          showSequence={showSequence}
          onSelectionChange={setSelectionCount}
          onDataChange={() => {
            // Сохранить ref на функцию refresh для вызова из assignRole и т.д.
          }}
        />
        {/* Легенда поверх canvas */}
        <Legend />
      </div>

      {/* ================================================================
          НИЖНЯЯ СТРОКА СТАТУСА
          ================================================================ */}
      <div style={{
        gridColumn:  "1 / -1",
        gridRow:     3,
        display:     "flex",
        alignItems:  "center",
        gap:         16,
        padding:     "6px 18px",
        borderTop:   "1px solid var(--line)",
        background:  "var(--card)",
        fontSize:    12,
        color:       "var(--muted)",
      }}>
        <span>Сетка: {rows} × {cols}</span>
        <span>Ячеек отбора: {gridRef.current.pickCellCount}</span>
        <span>Аллей: {aisles.length}</span>
        <span>Выделено: {selectionCount}</span>
        {displayLength !== null && (
          <span>Маршрут: <b style={{ color: "var(--green)" }}>{Math.round(displayLength)} м</b></span>
        )}
        <span style={{ marginLeft: "auto" }}>
          Scroll: zoom · ПКМ/MMB: pan · Shift+заголовок: строка/столбец · Esc: снять выделение
        </span>
      </div>

      {/* ================================================================
          ДИАЛОГ МЕЛКОШТУЧНОГО ДЕЛЕНИЯ
          ================================================================ */}
      {slotDialog.open && (
        <DialogOverlay onClose={() => setSlotDialog((d) => ({ ...d, open: false }))}>
          <div style={{ padding: "20px 24px", minWidth: 280 }}>
            <h3 style={{ margin: "0 0 14px", fontSize: 15 }}>Мелкоштучное деление</h3>

            <LabelRow label="По ширине (cols)">
              <div style={{ display: "flex", gap: 4 }}>
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    onClick={() => setSlotDialog((d) => ({ ...d, slotCols: n }))}
                    style={{
                      ...btnStyle,
                      width: 32, height: 32,
                      background: slotDialog.slotCols === n ? "var(--blue)" : "var(--soft)",
                      color:      slotDialog.slotCols === n ? "#fff" : "var(--text)",
                    }}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </LabelRow>

            <LabelRow label="По высоте (rows)">
              <div style={{ display: "flex", gap: 4 }}>
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    onClick={() => setSlotDialog((d) => ({ ...d, slotRows: n }))}
                    style={{
                      ...btnStyle,
                      width: 32, height: 32,
                      background: slotDialog.slotRows === n ? "var(--blue)" : "var(--soft)",
                      color:      slotDialog.slotRows === n ? "#fff" : "var(--text)",
                    }}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </LabelRow>

            {/* Пресеты */}
            <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 6 }}>
              {SLOT_PRESETS.map((p) => (
                <button
                  key={p.label}
                  onClick={() => setSlotDialog((d) => ({ ...d, slotCols: p.cols, slotRows: p.rows }))}
                  style={{
                    ...btnStyle, fontSize: 11,
                    background:
                      slotDialog.slotCols === p.cols && slotDialog.slotRows === p.rows
                        ? "var(--blue)" : "var(--soft)",
                    color:
                      slotDialog.slotCols === p.cols && slotDialog.slotRows === p.rows
                        ? "#fff" : "var(--text)",
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Предпросмотр */}
            <div style={{ marginTop: 14 }}>
              <SlotPreview cols={slotDialog.slotCols} rows={slotDialog.slotRows} />
              <p style={{ margin: "6px 0 0", fontSize: 12, color: "var(--muted)", textAlign: "center" }}>
                {slotDialog.slotCols} × {slotDialog.slotRows} = {slotDialog.slotCols * slotDialog.slotRows} слот(ов)
              </p>
            </div>

            <div style={{ marginTop: 16, display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button
                onClick={() => setSlotDialog((d) => ({ ...d, open: false }))}
                style={btnStyle}
              >
                Отмена
              </button>
              <button
                onClick={applySlotDivision}
                style={{ ...btnStyle, background: "var(--blue)", color: "#fff" }}
              >
                Применить
              </button>
            </div>
          </div>
        </DialogOverlay>
      )}

      {/* ================================================================
          ДИАЛОГ СОХРАНЕНИЯ
          ================================================================ */}
      {saveDialog.open && (
        <DialogOverlay onClose={() => setSaveDialog((d) => ({ ...d, open: false }))}>
          <div style={{ padding: "20px 24px", minWidth: 320 }}>
            <h3 style={{ margin: "0 0 14px", fontSize: 15 }}>Сохранить топологию</h3>

            <LabelRow label="Название">
              <input
                type="text"
                value={saveDialog.label}
                onChange={(e) => setSaveDialog((d) => ({ ...d, label: e.target.value }))}
                style={{ ...inputStyle, width: "100%" }}
              />
            </LabelRow>
            <LabelRow label="ID склада">
              <NumInput
                value={saveDialog.warehouseId}
                min={1} max={9999}
                onChange={(v) => setSaveDialog((d) => ({ ...d, warehouseId: v }))}
              />
            </LabelRow>

            <div style={{ marginTop: 8, fontSize: 12, color: "var(--muted)" }}>
              Будет создана топология в статусе <b>DRAFT</b>.
              После сохранения откроется в TopologyAdminPage для валидации и публикации.
            </div>

            {saveDialog.error && (
              <div style={{ marginTop: 8, color: "var(--red)", fontSize: 12 }}>
                Ошибка: {saveDialog.error}
              </div>
            )}

            <div style={{ marginTop: 16, display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button
                onClick={() => setSaveDialog((d) => ({ ...d, open: false }))}
                style={btnStyle}
                disabled={saveDialog.saving}
              >
                Отмена
              </button>
              <button
                onClick={handleSave}
                style={{ ...btnStyle, background: "var(--blue)", color: "#fff" }}
                disabled={saveDialog.saving || !saveDialog.label.trim()}
              >
                {saveDialog.saving ? "Сохраняю..." : "Сохранить"}
              </button>
            </div>
          </div>
        </DialogOverlay>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Вспомогательные мини-компоненты
// ---------------------------------------------------------------------------

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        fontSize:    11,
        fontWeight:  850,
        color:       "var(--muted)",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        marginBottom: 8,
        paddingBottom: 4,
        borderBottom: "1px solid var(--line)",
      }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function LabelRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
      gap: 8, marginBottom: 6 }}>
      <span style={{ color: "var(--muted)", fontSize: 12, whiteSpace: "nowrap" }}>{label}</span>
      {children}
    </div>
  );
}

function NumInput({
  value, min, max, step = 1, onChange,
}: {
  value: number; min: number; max: number; step?: number;
  onChange: (v: number) => void;
}) {
  return (
    <input
      type="number"
      value={value}
      min={min}
      max={max}
      step={step}
      onChange={(e) => {
        const v = Number(e.target.value);
        if (v >= min && v <= max) onChange(v);
      }}
      style={{ ...inputStyle, width: 70, textAlign: "right" }}
    />
  );
}

function AisleRow({
  aisle,
  onDistanceChange,
}: {
  aisle: AisleDef;
  onDistanceChange: (m: number) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [val, setVal]         = useState(String(aisle.distanceMeters));

  return (
    <div style={{
      display:       "flex",
      alignItems:    "center",
      gap:           6,
      marginBottom:  4,
      fontSize:      12,
    }}>
      <span style={{
        background:   "#EFF6FF",
        color:        "#1D4ED8",
        borderRadius: 4,
        padding:      "1px 6px",
        fontWeight:   700,
        minWidth:     28,
        textAlign:    "center",
      }}>
        {aisle.id}
      </span>
      <span style={{ color: "var(--muted)", flex: 1 }}>
        L={colLabel(aisle.leftCol)} R={colLabel(aisle.rightCol)}
      </span>
      {editing ? (
        <input
          autoFocus
          type="number"
          value={val}
          min={0}
          step={0.5}
          style={{ ...inputStyle, width: 54 }}
          onChange={(e) => setVal(e.target.value)}
          onBlur={() => {
            const m = parseFloat(val);
            if (!isNaN(m) && m >= 0) onDistanceChange(m);
            setEditing(false);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") (e.target as HTMLInputElement).blur();
            if (e.key === "Escape") setEditing(false);
          }}
        />
      ) : (
        <span
          onClick={() => { setVal(String(aisle.distanceMeters)); setEditing(true); }}
          title="Нажмите для изменения"
          style={{
            cursor:       "pointer",
            color:        aisle.customDistance ? "var(--amber)" : "var(--muted)",
            textDecoration: "underline dotted",
            fontSize:     11,
          }}
        >
          {aisle.distanceMeters.toFixed(1)} м
          {aisle.customDistance ? " ✎" : ""}
        </span>
      )}
    </div>
  );
}

/** Предпросмотр мелкоштучного деления ячейки. */
function SlotPreview({ cols, rows }: { cols: number; rows: number }) {
  const W = 90, H = 70;
  const sw = W / cols, sh = H / rows;

  return (
    <div style={{
      width: W, height: H, border: "2px solid var(--blue)", borderRadius: 4,
      position: "relative", margin: "0 auto", background: "#DBEAFE",
    }}>
      {/* Вертикальные линии деления */}
      {Array.from({ length: cols - 1 }, (_, i) => (
        <div key={`v${i}`} style={{
          position:  "absolute",
          left:      (i + 1) * sw,
          top:       0,
          width:     1,
          height:    "100%",
          background: "rgba(255,255,255,0.7)",
        }} />
      ))}
      {/* Горизонтальные линии деления */}
      {Array.from({ length: rows - 1 }, (_, i) => (
        <div key={`h${i}`} style={{
          position:  "absolute",
          top:       (i + 1) * sh,
          left:      0,
          height:    1,
          width:     "100%",
          background: "rgba(255,255,255,0.7)",
        }} />
      ))}
    </div>
  );
}

/** Легенда в правом нижнем углу canvas-области. */
function Legend() {
  const items = [
    { color: "#3B82F6", label: "Левая (L)" },
    { color: "#F97316", label: "Правая (R)" },
    { color: "#E5E7EB", label: "Проход" },
    { color: "#FBBF24", label: "Выделена" },
    { color: "#065F46", label: "Маршрут" },
  ];
  return (
    <div style={{
      position:      "absolute",
      bottom:        28,
      right:         10,
      display:       "flex",
      gap:           10,
      padding:       "5px 10px",
      background:    "rgba(255,255,255,.88)",
      borderRadius:  8,
      border:        "1px solid var(--line)",
      fontSize:      11,
      pointerEvents: "none",
    }}>
      {items.map(({ color, label }) => (
        <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <div style={{
            width: 12, height: 12, borderRadius: 2,
            background: color,
            border: color === "#FBBF24" ? "2px solid #F59E0B" : undefined,
          }} />
          {label}
        </div>
      ))}
    </div>
  );
}

/** Модальное окно с затемнённым фоном. */
function DialogOverlay({
  children,
  onClose,
}: {
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div
      style={{
        position:   "fixed",
        inset:      0,
        zIndex:     1000,
        background: "rgba(0,0,0,.45)",
        display:    "grid",
        placeItems: "center",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{
        background:   "#fff",
        borderRadius: 12,
        boxShadow:    "var(--shadow)",
        minWidth:     280,
        maxWidth:     480,
      }}>
        {children}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Стили (inline, без CSS-файлов для изоляции)
// ---------------------------------------------------------------------------

const btnStyle: React.CSSProperties = {
  padding:      "6px 12px",
  border:       "1px solid var(--line)",
  borderRadius: 7,
  background:   "var(--card)",
  color:        "var(--text)",
  fontSize:     12,
  fontWeight:   700,
  cursor:       "pointer",
  whiteSpace:   "nowrap",
};

const inputStyle: React.CSSProperties = {
  padding:      "4px 8px",
  border:       "1px solid var(--line)",
  borderRadius: 6,
  fontSize:     12,
  color:        "var(--text)",
  background:   "#fff",
};
