import type { StorePreview } from "./contracts";

export function StoreBoxMassPanel({ preview }: { preview: StorePreview }) {
 const boxes = preview.physical_boxes ?? [];
 if (!boxes.length) return null;
 return <section aria-label="Измеренные коробки">
  <h4>Измеренные коробки при отгрузке</h4>
  <table><thead><tr><th>Идентификатор коробки</th><th>Брутто, кг</th><th>Тара, кг</th><th>Нетто, кг</th><th>Источник</th></tr></thead>
   <tbody>{boxes.map(box => <tr key={box.box_uid}>
    <td>{box.sscc || box.box_uid}</td><td>{box.gross_weight_kg}</td>
    <td>{box.tare_weight_kg ?? "—"}</td><td>{box.net_weight_kg ?? "—"}</td>
    <td>{box.origin === "WAREHOUSE_SCALE_QC" ? "Весы и складской контроль" : "Подтверждённое измерение"}
     {box.device_mode === "TEST" && <strong> · Тестовое измерение</strong>}
     {box.coverage_complete === false && <strong> · Неполный состав</strong>}
    </td>
   </tr>)}</tbody></table>
 </section>;
}
