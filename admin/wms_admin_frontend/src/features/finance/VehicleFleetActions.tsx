export function VehicleFleetActions({onEdit,onDelete,onProfile}:{onEdit:()=>void;onDelete:()=>void;onProfile:()=>void}){
 return <><button type="button" className="fleet-edit-btn" title="Редактировать существующую карточку автомобиля" onClick={onEdit}>✏</button>
 <button type="button" title="Настроить класс, габариты и температурные возможности автомобиля" onClick={onProfile}>Профиль</button>
 <button type="button" className="fleet-del-btn" title="Удалить автомобиль из активного справочника по существующим правилам" onClick={onDelete}>✕</button></>;
}
