// UI-модель общего Ганта ресурсов (C0074). Серверный DTO — RESOURCE_TIMELINE_API_V1 (Codex), переводится в эту модель
// адаптером timelineAdapter.ts. Поля, которых нет в ответе, считаются неизвестными, а не нулём/«свободно».

export type ResourceType = "REACH_TRUCK" | "PICKER" | "DOCK" | "VEHICLE" | "OTHER";
export const RESOURCE_TYPES: { id: ResourceType; label: string; short: string }[] = [
  { id: "REACH_TRUCK", label: "Ричтраки", short: "Ричтрак" },
  { id: "PICKER", label: "Комплектовщики", short: "Комплектовщик" },
  { id: "DOCK", label: "Ворота", short: "Ворота" },
  { id: "VEHICLE", label: "Машины", short: "Машина" },
  { id: "OTHER", label: "Прочие ресурсы", short: "Ресурс" },
];

/** Переход к реальному экрану-владельцу; права проверяет он. */
export type ObjectLink = { page: string; params?: Record<string, string | number> } | null;

/** Интервал доступности по источнику. PLANNED — план выхода (не подтверждённое присутствие), ON_SHIFT — подтверждённая смена.
 *  Отсутствие интервала = неизвестно. */
export type AvailabilityState = "ON_SHIFT" | "PLANNED" | "OFF_SHIFT" | "DOWN" | "UNKNOWN";
export type Availability = { start_at: string; finish_at: string | null; state: AvailabilityState; source: string; reason: string | null };

export type TimelineResource = {
  resource_key: string; resource_type: ResourceType; resource_id: string | number;
  code: string; name: string | null; warehouse_id: number; warehouse_name?: string | null; zone_code: string | null;
  /** Исходный вид ресурса сервера и состояние в реестре (не во времени): BLOCKED, ACTIVE и т.п. */
  kind_raw?: string; source_state?: string | null;
  availability: Availability[];
  /** Последний наблюдённый сигнал (сессия, телеметрия). Без сигнала — null, а не «свободен».
   *  session_id — тот же id, что в /api/resources/sessions (resource_session_view); реальный ключ для перехода «сессия → ресурс», не придуманный. */
  last_signal: { state: string; observed_at: string; source: string; session_id: number | null } | null;
  qualifications: string[] | null;
  link: ObjectLink;
};

export type EventQuantity = { value: string; uom: string };
export type TimelineEvent = {
  event_id: string; event_kind: string; title: string; status: string | null;
  wave_id: number | null; task_id: number | string | null; trip_id: number | null;
  plan_start_at: string | null; plan_finish_at: string | null;
  fact_start_at: string | null; fact_finish_at: string | null;
  quantity: EventQuantity | null; source: string; link: ObjectLink;
  /** Окончание факта неизвестно у источника; терминальный статус без окончания не продлевается до «сейчас». */
  finish_unresolved?: boolean; terminal?: boolean;
  /** Старое местное время без пояса — только показ в карточке, на ось не ставится. */
  legacy_time?: Record<string, string | null> | null;
  time_status?: string; details?: [string, string][];
};

/** Одна работа (event_id) может занимать несколько ресурсов: отдельные привязки, одно событие. */
export type BindingRole = "EXECUTOR" | "EQUIPMENT" | "DOCK" | "VEHICLE";
export type TimelineBinding = { binding_id: string; event_id: string; resource_key: string; role: BindingRole;
  basis: "PLAN" | "FACT"; start_at: string | null; finish_at: string | null };

export type SourceStatus = "OK" | "ERROR" | "NO_ACCESS" | "NOT_MAPPED";
export type TimelineSource = { source: string; title?: string; status: SourceStatus; read_at: string | null;
  row_count: number | null; limit: number | null; truncated: boolean; message: string | null };

export type ResourceTimeline = {
  warehouse: { warehouse_id: number; name: string | null; time_zone: string | null; time_zone_source: string | null };
  window: { start_at: string; finish_at: string };
  read_at: string;
  resources: TimelineResource[];
  events: TimelineEvent[];
  bindings: TimelineBinding[];
  sources: TimelineSource[];
  /** Кандидаты пересечений от сервера (OVERLAP_REVIEW). Если есть — используются вместо расчёта в браузере. */
  overlaps?: { resource_key: string; basis: "PLAN" | "FACT"; event_ids: string[] }[];
  overlap_limit?: number;
};

/** Выбранный объект общий для сцены, Ганта, списка и карточки. */
export type GanttSelection = { kind: "resource"; key: string } | { kind: "event"; id: string } | null;
