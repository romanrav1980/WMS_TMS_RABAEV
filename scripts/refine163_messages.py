from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"admin/wms_admin_frontend/src/components/PlannerPreflight.tsx"
s=p.read_text(encoding="utf-8")
a=s.index('export function PlannerPreflight')
s=s[:a]+'''const REASONS: Record<string, string> = {
  PLAN_ST_NOT_FOUND: "СТ отсутствует в текущих данных",
  PLAN_ST_FOREIGN_OR_SHIPPED: "СТ уже отгружена или назначена другому рейсу",
  PLAN_VEHICLE_ID_PLATE_CONFLICT: "Сохранённая машина не соответствует текущему госномеру",
  PLAN_CURRENT_VEHICLE_NOT_FOUND: "Машина отсутствует",
  PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED: "Машина заблокирована либо её вместимость не задана",
  PLAN_PALLET_CAPACITY_EXCEEDED: "Превышена паллетная вместимость",
  PLAN_WEIGHT_CAPACITY_EXCEEDED: "Превышена грузоподъёмность",
  PLAN_DECLARED_WEIGHT_REQUIRED: "Плановая масса части товара отсутствует",
  PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT: "Тип машины или гидроборт не соответствует адресу",
  PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED: "Машина превышает ограничение адреса по тоннажу",
  PLAN_STRICT_TIME_SCHEDULE_REQUIRED: "Строгие временные окна требуют подтверждённого расписания",
  PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED: "Рейс отменён, отгружен или передан в биллинг",
};

function reason(code?: string): string | undefined {
  return code ? REASONS[code] || code : undefined;
}

'''+s[a:]
s=s.replace('source_blockers.map(item => `${item.code}${item.st_number ? ": " + item.st_number : ""}`)','source_blockers.map(item => `${reason(item.code)}${item.st_number ? ": " + item.st_number : ""}`)')
s=s.replace('route.capacity_and_type.code, route.current_native_application.code,','reason(route.capacity_and_type.code), reason(route.current_native_application.code),')
p.write_text(s,encoding="utf-8")
