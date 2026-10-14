import { cameraCommand } from "../scene/CameraRig";
import { useTwin } from "../store/twinStore";

export function SceneToolbar() {
  const labels = useTwin((s) => s.labels);
  const setLabels = useTwin((s) => s.setLabels);
  const heatmap = useTwin((s) => s.heatmap);
  const toggleHeatmap = useTwin((s) => s.toggleHeatmap);
  const panelsHidden = useTwin((s) => s.panelsHidden);
  const togglePanels = useTwin((s) => s.togglePanels);
  return (
    <div className="scene-toolbar">
      <div className="tool-group">
        <button type="button" title="Приблизить" onClick={() => cameraCommand("zoomIn")}>＋</button>
        <button type="button" title="Отдалить" onClick={() => cameraCommand("zoomOut")}>－</button>
      </div>
      <div className="tool-group">
        <button type="button" title="Повернуть влево" onClick={() => cameraCommand("rotateLeft")}>⟲</button>
        <button type="button" title="Повернуть вправо" onClick={() => cameraCommand("rotateRight")}>⟳</button>
        <button type="button" title="Сбросить вид" onClick={() => cameraCommand("reset")}>⌂</button>
      </div>
      <div className="tool-card">
        <small>Подписи</small>
        <div className="seg">
          {(["fleet", "all", "none"] as const).map((l) => (
            <button type="button" key={l} className={labels === l ? "active" : ""} onClick={() => setLabels(l)}>
              {{ fleet: "Техника", all: "Все", none: "Нет" }[l]}
            </button>
          ))}
        </div>
      </div>
      <div className="tool-group">
        <button type="button" className={heatmap ? "active" : ""} title="Тепловая карта остатков в ячейках отбора" onClick={toggleHeatmap}>▦</button>
        <button type="button" className={panelsHidden ? "active" : ""} title="Скрыть/показать панели" onClick={togglePanels}>◫</button>
      </div>
    </div>
  );
}
