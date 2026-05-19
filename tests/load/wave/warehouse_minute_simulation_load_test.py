from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_OUT_DIR = "runtime/test-evidence/warehouse-minute-simulation"
RUN_PREFIX = "SIM"


@dataclass(frozen=True)
class Cell:
    cell_id: str
    aisle: int
    slot: int
    level: int
    x_m: float
    y_m: float
    role: str


@dataclass(frozen=True)
class Sku:
    sku_id: str
    abc_class: str
    pick_cell: str
    dynamic_allowed: bool
    box_volume: float
    box_weight: float
    pick_seconds_per_box: int


@dataclass
class Picker:
    resource_id: str
    boxes_per_hour: int
    trolley_capacity: int
    x_m: float = 0.0
    y_m: float = 0.0
    status: str = "IDLE"
    busy_until_minute: int = 0
    task_id: str | None = None
    wave_id: str | None = None
    client_id: str | None = None
    pallet_id: str | None = None
    picked_boxes: int = 0
    wait_minutes: int = 0
    walk_minutes: int = 0
    pick_minutes: int = 0


@dataclass
class Reachtruck:
    resource_id: str
    driver_id: str
    operations_per_hour: int
    x_m: float = 0.0
    y_m: float = 0.0
    status: str = "IDLE"
    busy_until_minute: int = 0
    task_id: str | None = None
    wave_id: str | None = None
    source_cell: str | None = None
    target_cell: str | None = None
    completed_ops: int = 0
    wait_minutes: int = 0
    travel_minutes: int = 0


@dataclass
class OrderLine:
    line_id: str
    client_id: str
    wave_id: str
    pallet_id: str
    sku_id: str
    qty_boxes: int
    pick_cell: str
    status: str = "WAITING"


@dataclass
class ClientOrder:
    client_id: str
    wave_id: str
    gate_id: str
    case_pallets: list[str]
    mono_pallets: list[str]
    lines: list[OrderLine]
    ready_minute: int | None = None
    shipped_minute: int | None = None


@dataclass
class ReplenishmentTask:
    task_id: str
    wave_id: str
    sku_id: str
    source_cell: str
    target_cell: str
    qty_boxes: int
    replenishment_mode: str = "PALLET_REPLENISHMENT"
    status: str = "QUEUED"
    assigned_to: str | None = None
    released_minute: int | None = None
    done_minute: int | None = None


@dataclass
class DockTask:
    task_id: str
    client_id: str
    wave_id: str
    gate_id: str
    pallet_id: str
    status: str = "WAITING"
    remaining_minutes: int = 60
    staged_minute: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Model-only warehouse minute simulation for WMS wave execution.")
    parser.add_argument("--clients", type=int, default=50)
    parser.add_argument("--waves", type=int, default=10)
    parser.add_argument("--clients-per-wave", type=int, default=5)
    parser.add_argument("--sku", type=int, default=1000)
    parser.add_argument("--pick-faces", type=int, default=1500)
    parser.add_argument("--pickers", type=int, default=10)
    parser.add_argument("--reachtrucks", type=int, default=5)
    parser.add_argument("--shift-start", default="08:00")
    parser.add_argument("--shift-hours", type=int, default=12)
    parser.add_argument("--replenishment-lead-minutes", type=int, default=60)
    parser.add_argument("--case-replenishment-per-hour", type=int, default=5)
    parser.add_argument("--pallet-drop-minutes", type=int, default=3)
    parser.add_argument("--pallet-exchange-minutes-min", type=int, default=2)
    parser.add_argument("--pallet-exchange-minutes-max", type=int, default=3)
    parser.add_argument("--dock-accumulation-minutes", type=int, default=60)
    parser.add_argument("--dock-shipping-minutes", type=int, default=60)
    parser.add_argument("--congestion-slowdown-factor", type=float, default=4.0)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--mode", choices=["model-only"], default="model-only")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    run_id = f"{RUN_PREFIX}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{args.seed}"
    out_dir = Path(args.out_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    simulation = WarehouseMinuteSimulation(args=args, rng=rng, run_id=run_id, out_dir=out_dir)
    report = simulation.run()
    print(json.dumps(report, ensure_ascii=False, indent=2))


class WarehouseMinuteSimulation:
    def __init__(self, args: argparse.Namespace, rng: random.Random, run_id: str, out_dir: Path) -> None:
        self.args = args
        self.rng = rng
        self.run_id = run_id
        self.out_dir = out_dir
        self.shift_minutes = args.shift_hours * 60
        self.shift_start = parse_clock(args.shift_start)
        self.events: list[dict[str, Any]] = []
        self.minute_rows: list[dict[str, Any]] = []
        self.collision_rows: list[dict[str, Any]] = []
        self.layout = self.build_layout()
        self.cells_by_id = {cell["cell_id"]: cell for cell in self.layout["cells"]}
        self.skus = self.build_skus()
        self.pick_face_capacity = self.build_pick_face_capacity()
        self.clients = self.build_clients_and_orders()
        self.pickers = self.build_pickers()
        self.reachtrucks = self.build_reachtrucks()
        self.pick_face_stock = self.build_initial_pick_stock()
        self.storage_stock = self.build_initial_storage_stock()
        self.replenishment_queue: list[ReplenishmentTask] = []
        self.dynamic_cell_sku: dict[str, str] = {}
        self.dock_queue: list[DockTask] = []
        self.active_waves: set[str] = set()
        self.completed_lines: set[str] = set()
        self.shipped_pallets: set[str] = set()
        self.empty_pick_face_probe: dict[str, int] = {}
        self.route_delay_probe: dict[str, int] = {}
        self.dock_stage_probe: dict[str, int] = {}
        self.wave_launch_minutes = {f"WAVE-SIM-{idx:02d}": (idx - 1) * 60 for idx in range(1, self.args.waves + 1)}
        self.replenishment_lead_minutes = args.replenishment_lead_minutes
        self.planned_replenishment_waves: set[str] = set()
        self.congested_segments: dict[str, int] = {}

    def run(self) -> dict[str, Any]:
        self.write_json("layout.json", self.layout)
        self.write_json("generated-orders.json", self.orders_payload())
        self.prestage_initial_wave_replenishment()
        self.write_json("generated-stock.json", self.stock_payload())

        for minute in range(self.shift_minutes + 1):
            self.launch_due_waves(minute)
            self.release_replenishment(minute)
            self.assign_reachtrucks(minute)
            self.assign_pickers(minute)
            self.progress_resources(minute)
            self.release_ready_dock_tasks(minute)
            self.progress_shipping(minute)
            self.detect_collisions(minute)
            self.capture_minute_metrics(minute)

        report = self.build_report()
        self.write_events()
        self.write_csv("timeline.csv", self.minute_rows)
        self.write_csv("metrics-by-minute.csv", self.minute_rows)
        self.write_csv("collision-report.csv", self.collision_rows)
        self.write_json("report.json", report)
        self.write_markdown_report(report)
        self.write_presentation(report)
        return report

    def build_layout(self) -> dict[str, Any]:
        aisles = 25
        slots = 60
        levels = 6
        cells: list[dict[str, Any]] = []
        gates: list[dict[str, Any]] = []
        dynamic_pick_faces: set[str] = set()
        duplicate_pick_faces: set[str] = set()
        pick_face_ids = [f"A{aisle:02d}-S{slot:03d}-L1" for aisle in range(1, aisles + 1) for slot in range(1, slots + 1)]
        dynamic_slots_per_aisle = max(1, round(slots * 0.10))
        for aisle in range(1, aisles + 1):
            for slot in range(slots - dynamic_slots_per_aisle + 1, slots + 1):
                dynamic_pick_faces.add(f"A{aisle:02d}-S{slot:03d}-L1")
        remaining = [cell_id for cell_id in pick_face_ids if cell_id not in dynamic_pick_faces]
        for cell_id in self.rng.sample(remaining, 200):
            duplicate_pick_faces.add(cell_id)
        for aisle in range(1, aisles + 1):
            y = (aisle - 1) * 4.0
            gates.append({"gate_id": f"G{aisle:02d}", "aisle": aisle, "x_m": 0.0, "y_m": y, "status": "AVAILABLE"})
            for slot in range(1, slots + 1):
                x = (slot - 1) * 1.5
                for level in range(1, levels + 1):
                    cell_id = f"A{aisle:02d}-S{slot:03d}-L{level}"
                    if level == 1 and cell_id in dynamic_pick_faces:
                        role = "DYNAMIC_PICK_FACE"
                    elif level == 1 and cell_id in duplicate_pick_faces:
                        role = "DUPLICATE_A_PICK_FACE"
                    elif level == 1:
                        role = "FIXED_PICK_FACE"
                    else:
                        role = "STORAGE"
                    cells.append(asdict(Cell(cell_id, aisle, slot, level, x, y, role)))
        return {
            "run_id": self.run_id,
            "warehouse": {
                "aisles": aisles,
                "slots_per_aisle": slots,
                "levels": levels,
                "aisle_length_m": 90,
                "aisle_spacing_m": 4,
                "slot_spacing_m": 1.5,
                "pick_faces": len(pick_face_ids),
                "dynamic_pick_face_policy": "10_PERCENT_END_OF_AISLE_URGENT_ONLY",
                "dynamic_pick_faces": len(dynamic_pick_faces),
                "dynamic_slots_per_aisle": dynamic_slots_per_aisle,
            },
            "gates": gates,
            "cells": cells,
        }

    def build_skus(self) -> dict[str, Sku]:
        fixed_cells = [cell for cell in self.layout["cells"] if cell["role"] in {"FIXED_PICK_FACE", "DUPLICATE_A_PICK_FACE"}]
        fixed_cells.sort(key=lambda row: (row["x_m"], row["aisle"]))
        skus: dict[str, Sku] = {}
        for idx in range(1, self.args.sku + 1):
            sku_id = f"SKU-{idx:04d}"
            if idx <= round(self.args.sku * 0.10):
                abc_class = "A"
                candidate = fixed_cells[(idx - 1) % max(1, round(len(fixed_cells) * 0.25))]
                pick_seconds = self.rng.randint(15, 28)
            elif idx <= round(self.args.sku * 0.40):
                abc_class = "B"
                start = round(len(fixed_cells) * 0.25)
                span = max(1, round(len(fixed_cells) * 0.45))
                candidate = fixed_cells[start + ((idx - 1) % span)]
                pick_seconds = self.rng.randint(18, 35)
            else:
                abc_class = "C"
                start = round(len(fixed_cells) * 0.60)
                span = max(1, len(fixed_cells) - start)
                candidate = fixed_cells[start + ((idx - 1) % span)]
                pick_seconds = self.rng.randint(22, 42)
            skus[sku_id] = Sku(
                sku_id=sku_id,
                abc_class=abc_class,
                pick_cell=candidate["cell_id"],
                dynamic_allowed=abc_class in {"A", "C"},
                box_volume=round(self.rng.uniform(0.006, 0.035), 4),
                box_weight=round(self.rng.uniform(0.4, 8.5), 2),
                pick_seconds_per_box=pick_seconds,
            )
        return skus

    def build_clients_and_orders(self) -> dict[str, ClientOrder]:
        clients: dict[str, ClientOrder] = {}
        sku_ids = list(self.skus)
        weights = [60 if self.skus[sku].abc_class == "A" else 20 if self.skus[sku].abc_class == "B" else 4 for sku in sku_ids]
        for client_idx in range(1, self.args.clients + 1):
            wave_no = 1 + ((client_idx - 1) // self.args.clients_per_wave)
            wave_id = f"WAVE-SIM-{wave_no:02d}"
            client_id = f"C{client_idx:03d}"
            gate_no = 1 + ((client_idx - 1) % 25)
            case_pallet_count = self.rng.randint(5, 10)
            mono_pallet_count = self.rng.randint(5, 10) if client_idx <= 20 else 0
            case_pallets = [f"{client_id}-CP-{idx:02d}" for idx in range(1, case_pallet_count + 1)]
            mono_pallets = [f"{client_id}-MP-{idx:02d}" for idx in range(1, mono_pallet_count + 1)]
            lines: list[OrderLine] = []
            for pallet_idx, pallet_id in enumerate(case_pallets, start=1):
                line_count = self.rng.randint(20, 30)
                pallet_skus = self.rng.choices(sku_ids, weights=weights, k=line_count)
                for line_idx, sku_id in enumerate(pallet_skus, start=1):
                    line_id = f"{pallet_id}-L{line_idx:03d}"
                    qty = self.rng.randint(1, 6)
                    lines.append(OrderLine(line_id, client_id, wave_id, pallet_id, sku_id, qty, self.skus[sku_id].pick_cell))
            clients[client_id] = ClientOrder(client_id, wave_id, f"G{gate_no:02d}", case_pallets, mono_pallets, lines)
        return clients

    def build_pickers(self) -> list[Picker]:
        speeds = [60, 75, 90, 105, 120, 135, 150, 165, 180, 120]
        capacities = [1, 1, 1, 2, 2, 2, 3, 3, 3, 2]
        return [Picker(f"P{idx:02d}", speeds[(idx - 1) % len(speeds)], capacities[(idx - 1) % len(capacities)]) for idx in range(1, self.args.pickers + 1)]

    def build_reachtrucks(self) -> list[Reachtruck]:
        ops = [15, 17, 18, 20, 22]
        return [
            Reachtruck(
                f"RT{idx:02d}",
                f"RTD{idx:02d}",
                ops[(idx - 1) % len(ops)],
                x_m=-4.0,
                y_m=(idx - 1) * 18.0,
            )
            for idx in range(1, self.args.reachtrucks + 1)
        ]

    def build_initial_pick_stock(self) -> dict[str, int]:
        stock: dict[str, int] = {}
        for sku in self.skus.values():
            if sku.abc_class == "A":
                qty = self.rng.randint(360, 600)
            elif sku.abc_class == "B":
                qty = self.rng.randint(150, 360)
            else:
                qty = self.rng.randint(0, 160)
            capacity = self.pick_face_capacity.get(sku.pick_cell, 160)
            stock[sku.pick_cell] = min(capacity, stock.get(sku.pick_cell, 0) + qty)
        return stock

    def build_pick_face_capacity(self) -> dict[str, int]:
        capacity: dict[str, int] = {}
        for sku in self.skus.values():
            if sku.abc_class == "A":
                capacity[sku.pick_cell] = 600
            elif sku.abc_class == "B":
                capacity[sku.pick_cell] = 360
            else:
                capacity[sku.pick_cell] = 160
        for cell in self.layout["cells"]:
            if cell["role"] == "DYNAMIC_PICK_FACE":
                capacity.setdefault(cell["cell_id"], 120)
        return capacity

    def build_initial_storage_stock(self) -> dict[str, list[dict[str, Any]]]:
        demand_by_sku: dict[str, int] = {sku_id: 0 for sku_id in self.skus}
        for client in self.clients.values():
            for line in client.lines:
                demand_by_sku[line.sku_id] += line.qty_boxes
            for _ in client.mono_pallets:
                mono_sku = self.rng.choice(list(self.skus))
                demand_by_sku[mono_sku] += self.rng.randint(80, 120)
        storage_cells = [cell for cell in self.layout["cells"] if cell["role"] == "STORAGE"]
        stock: dict[str, list[dict[str, Any]]] = {}
        for idx, (sku_id, demand) in enumerate(demand_by_sku.items(), start=1):
            sku = self.skus[sku_id]
            pick_qty = self.pick_face_stock.get(sku.pick_cell, 0)
            needed = max(0, demand - pick_qty) + self.rng.randint(120, 400)
            pallets = max(1, math.ceil(needed / 100))
            rows = []
            for pallet_idx in range(1, pallets + 1):
                cell = storage_cells[(idx * 17 + pallet_idx * 13) % len(storage_cells)]
                rows.append(
                    {
                        "uid_pallet": f"PAL-{sku_id}-{pallet_idx:03d}",
                        "sku_id": sku_id,
                        "cell_id": cell["cell_id"],
                        "qty_boxes": 100,
                        "batch": f"B-{sku_id}-{pallet_idx:03d}",
                        "expiry_days": self.rng.randint(60, 360),
                    }
                )
            stock[sku_id] = rows
        return stock

    def launch_due_waves(self, minute: int) -> None:
        for wave_id, launch_minute in self.wave_launch_minutes.items():
            prep_minute = max(0, launch_minute - self.replenishment_lead_minutes)
            if minute == prep_minute and wave_id not in self.planned_replenishment_waves:
                self.planned_replenishment_waves.add(wave_id)
                self.emit(minute, "WAVE_REPLENISHMENT_PREP_STARTED", wave_id=wave_id, launch_minute=launch_minute, lead_minutes=launch_minute - minute)
                self.plan_replenishment_for_wave(minute, wave_id)
                self.plan_mono_pallet_moves(minute, wave_id)
            if minute == launch_minute:
                self.active_waves.add(wave_id)
                clients = [client for client in self.clients.values() if client.wave_id == wave_id]
                self.emit(minute, "WAVE_LAUNCHED", wave_id=wave_id, message=f"Запущена волна {wave_id}", clients=len(clients))

    def prestage_initial_wave_replenishment(self) -> None:
        wave_id = "WAVE-SIM-01"
        demand: dict[str, int] = {}
        for client in self.clients.values():
            if client.wave_id != wave_id:
                continue
            for line in client.lines:
                demand[line.sku_id] = demand.get(line.sku_id, 0) + line.qty_boxes
        touched = 0
        for sku_id, qty in demand.items():
            sku = self.skus[sku_id]
            current = self.pick_face_stock.get(sku.pick_cell, 0)
            trigger = 80 if sku.abc_class == "A" else 50 if sku.abc_class == "B" else 20
            capacity = self.pick_face_capacity.get(sku.pick_cell, qty + trigger)
            if current < qty + trigger:
                self.pick_face_stock[sku.pick_cell] = min(capacity, qty + trigger)
                touched += 1
        self.planned_replenishment_waves.add(wave_id)
        self.emit(-1, "PRE_SHIFT_REPLENISHMENT_DONE", wave_id=wave_id, adjusted_pick_faces=touched)

    def plan_replenishment_for_wave(self, minute: int, wave_id: str) -> None:
        demand: dict[str, int] = {}
        for client in self.clients.values():
            if client.wave_id != wave_id:
                continue
            for line in client.lines:
                demand[line.sku_id] = demand.get(line.sku_id, 0) + line.qty_boxes
        for sku_id, qty in demand.items():
            sku = self.skus[sku_id]
            pick_qty = self.pick_face_stock.get(sku.pick_cell, 0)
            trigger = 80 if sku.abc_class == "A" else 50 if sku.abc_class == "B" else 20
            top_up_target = 560 if sku.abc_class == "A" else 320 if sku.abc_class == "B" else 130
            capacity = self.pick_face_capacity.get(sku.pick_cell, top_up_target)
            target_qty = min(capacity, max(qty + trigger, top_up_target))
            if pick_qty < target_qty:
                needed = target_qty - pick_qty
                pallets = math.ceil(needed / 100)
                for idx in range(pallets):
                    source = self.reserve_storage_pallet(sku_id)
                    if not source:
                        continue
                    target_cell = sku.pick_cell
                    task_qty = min(100, needed - idx * 100)
                    task = ReplenishmentTask(
                        task_id=f"RPL-{wave_id}-{sku_id}-{idx + 1:02d}",
                        wave_id=wave_id,
                        sku_id=sku_id,
                        source_cell=source["cell_id"],
                        target_cell=target_cell,
                        qty_boxes=task_qty,
                        replenishment_mode="CASE_REPLENISHMENT" if task_qty < 80 else "PALLET_REPLENISHMENT",
                    )
                    self.replenishment_queue.append(task)
        self.emit(minute, "REPLENISHMENT_PLANNED", wave_id=wave_id, tasks=sum(1 for task in self.replenishment_queue if task.wave_id == wave_id))

    def plan_mono_pallet_moves(self, minute: int, wave_id: str) -> None:
        for client in self.clients.values():
            if client.wave_id != wave_id:
                continue
            for pallet_id in client.mono_pallets:
                task = DockTask(
                    f"MONO-{pallet_id}",
                    client.client_id,
                    wave_id,
                    client.gate_id,
                    pallet_id,
                    "WAITING",
                    self.args.dock_shipping_minutes,
                    minute,
                )
                self.dock_queue.append(task)
                truck = min(self.reachtrucks, key=lambda row: row.completed_ops)
                self.emit(
                    minute,
                    "PALLET_STAGED_TO_DOCK",
                    wave_id=wave_id,
                    client_id=client.client_id,
                    gate_id=client.gate_id,
                    pallet_id=pallet_id,
                    staged_by="REACHTRUCK",
                    resource_id=truck.resource_id,
                )
                self.emit(minute, "MONO_PALLET_PLANNED", wave_id=wave_id, client_id=client.client_id, gate_id=client.gate_id, pallet_id=pallet_id)

    def release_replenishment(self, minute: int) -> None:
        active_target_cells = {task.target_cell for task in self.replenishment_queue if task.status in {"RELEASED", "IN_PROGRESS"}}
        for task in self.replenishment_queue:
            if task.status != "QUEUED":
                continue
            if task.target_cell in active_target_cells:
                continue
            task.status = "RELEASED"
            task.released_minute = minute
            active_target_cells.add(task.target_cell)
            self.emit(minute, "REPLENISHMENT_RELEASED", wave_id=task.wave_id, sku_id=task.sku_id, task_id=task.task_id, source_cell=task.source_cell, target_cell=task.target_cell)

    def assign_reachtrucks(self, minute: int) -> None:
        open_tasks = [task for task in self.replenishment_queue if task.status == "RELEASED"]
        for truck in self.reachtrucks:
            if truck.status != "IDLE" or not open_tasks:
                continue
            task = open_tasks.pop(0)
            source = self.cells_by_id[task.source_cell]
            target = self.cells_by_id[task.target_cell]
            distance = warehouse_route_distance(truck.x_m, truck.y_m, source["x_m"], source["y_m"]) + warehouse_route_distance(source["x_m"], source["y_m"], target["x_m"], target["y_m"])
            travel_minutes = max(1, math.ceil(distance / 166.7))
            source_handling_minutes = self.rng.randint(2, 3)
            target_drop_minutes = self.args.pallet_drop_minutes
            pallet_exchange_minutes = self.rng.randint(self.args.pallet_exchange_minutes_min, self.args.pallet_exchange_minutes_max) if self.pick_face_stock.get(task.target_cell, 0) > 0 else 0
            confirmation_minutes = 1
            technology_minutes = source_handling_minutes + target_drop_minutes + pallet_exchange_minutes + confirmation_minutes
            normative = math.ceil(60 / self.args.case_replenishment_per_hour) if task.replenishment_mode == "CASE_REPLENISHMENT" else math.ceil(60 / truck.operations_per_hour)
            duration = max(normative, travel_minutes + technology_minutes)
            truck.status = "MOVING_PALLET"
            truck.busy_until_minute = minute + duration
            truck.task_id = task.task_id
            truck.wave_id = task.wave_id
            truck.source_cell = task.source_cell
            truck.target_cell = task.target_cell
            truck.travel_minutes += travel_minutes
            task.status = "IN_PROGRESS"
            task.assigned_to = truck.resource_id
            self.emit(
                minute,
                "REACHTRUCK_TASK_STARTED",
                resource_id=truck.resource_id,
                wave_id=task.wave_id,
                task_id=task.task_id,
                source_cell=task.source_cell,
                target_cell=task.target_cell,
                duration_minutes=duration,
                travel_minutes=travel_minutes,
                source_handling_minutes=source_handling_minutes,
                target_drop_minutes=target_drop_minutes,
                pallet_exchange_minutes=pallet_exchange_minutes,
                confirmation_minutes=confirmation_minutes,
                replenishment_mode=task.replenishment_mode,
                equivalent_operations_per_hour=self.args.case_replenishment_per_hour if task.replenishment_mode == "CASE_REPLENISHMENT" else truck.operations_per_hour,
            )

    def assign_pickers(self, minute: int) -> None:
        for picker in self.pickers:
            if picker.status != "IDLE":
                continue
            line = self.next_pickable_line()
            if line:
                self.start_picker_line(minute, picker, line)
                continue
            blocked_line = self.next_waiting_line_with_empty_pick_face()
            if blocked_line:
                self.block_picker_on_empty_pick_face(minute, picker, blocked_line)
            else:
                picker.wait_minutes += 1

    def start_picker_line(self, minute: int, picker: Picker, line: OrderLine, include_walk: bool = True) -> None:
            cell = self.cells_by_id[line.pick_cell]
            distance = warehouse_route_distance(picker.x_m, picker.y_m, cell["x_m"], cell["y_m"]) if include_walk else 0
            walk_minutes = max(0 if not include_walk else 1, math.ceil(distance / 50.0)) if distance else 0
            speed_minutes = max(1, math.ceil((line.qty_boxes / picker.boxes_per_hour) * 60))
            if self.is_congested_location(cell["x_m"], cell["y_m"]):
                speed_minutes = math.ceil(speed_minutes * self.args.congestion_slowdown_factor)
                walk_minutes = math.ceil(walk_minutes * self.args.congestion_slowdown_factor)
            duration = walk_minutes + speed_minutes
            picker.status = "PICKING"
            picker.busy_until_minute = minute + duration
            picker.task_id = line.line_id
            picker.wave_id = line.wave_id
            picker.client_id = line.client_id
            picker.pallet_id = line.pallet_id
            picker.walk_minutes += walk_minutes
            picker.pick_minutes += speed_minutes
            line.status = "IN_PROGRESS"
            self.pick_face_stock[line.pick_cell] = self.pick_face_stock.get(line.pick_cell, 0) - line.qty_boxes
            if cell["role"] == "DYNAMIC_PICK_FACE" and self.pick_face_stock.get(line.pick_cell, 0) <= 0:
                self.dynamic_cell_sku.pop(line.pick_cell, None)
            self.emit(
                minute,
                "PICKER_TASK_STARTED",
                resource_id=picker.resource_id,
                wave_id=line.wave_id,
                client_id=line.client_id,
                pallet_id=line.pallet_id,
                sku_id=line.sku_id,
                cell=line.pick_cell,
                qty_boxes=line.qty_boxes,
                duration_minutes=duration,
                congestion_slowdown_factor=self.args.congestion_slowdown_factor if self.is_congested_location(cell["x_m"], cell["y_m"]) else 1,
            )

    def block_picker_on_empty_pick_face(self, minute: int, picker: Picker, line: OrderLine) -> None:
        reroute_cell = self.find_dynamic_cell_for_waiting_line(line)
        if reroute_cell:
            original_cell = line.pick_cell
            line.pick_cell = reroute_cell
            self.emit(
                minute,
                "PICK_LINE_REROUTED_TO_DYNAMIC_CELL",
                resource_id=picker.resource_id,
                wave_id=line.wave_id,
                client_id=line.client_id,
                pallet_id=line.pallet_id,
                sku_id=line.sku_id,
                original_cell=original_cell,
                reroute_cell=reroute_cell,
                reason="FIXED_PICK_FACE_EMPTY_DYNAMIC_CELL_HAS_URGENT_STOCK_FURTHER_ON_ROUTE",
            )
            self.start_picker_line(minute, picker, line)
            return

        cell = self.cells_by_id[line.pick_cell]
        picker.x_m = cell["x_m"]
        picker.y_m = cell["y_m"]
        picker.status = "WAITING_REPLENISHMENT"
        picker.busy_until_minute = minute + 1
        picker.task_id = line.line_id
        picker.wave_id = line.wave_id
        picker.client_id = line.client_id
        picker.pallet_id = line.pallet_id
        picker.wait_minutes += 1
        line.status = "WAITING_REPLENISHMENT"
        self.ensure_reactive_replenishment(minute, line)
        self.record_empty_pick_face_arrival(minute, picker, line)

    def record_empty_pick_face_arrival(self, minute: int, picker: Picker, line: OrderLine) -> None:
        last_probe = self.empty_pick_face_probe.get(line.line_id, -999)
        if minute - last_probe < 5:
            return
        self.empty_pick_face_probe[line.line_id] = minute
        available = self.pick_face_stock.get(line.pick_cell, 0)
        self.emit(
            minute,
            "PICK_FACE_EMPTY_AT_ARRIVAL",
            resource_id=picker.resource_id,
            wave_id=line.wave_id,
            client_id=line.client_id,
            pallet_id=line.pallet_id,
            sku_id=line.sku_id,
            cell=line.pick_cell,
            required_boxes=line.qty_boxes,
            available_boxes=available,
            capacity_boxes=self.pick_face_capacity.get(line.pick_cell, 0),
        )
        self.record_collision(
            minute,
            "PICK_FACE_EMPTY",
            cell=line.pick_cell,
            resource_id=picker.resource_id,
            wave_id=line.wave_id,
            client_id=line.client_id,
            sku_id=line.sku_id,
            required_boxes=line.qty_boxes,
            available_boxes=available,
            capacity_boxes=self.pick_face_capacity.get(line.pick_cell, 0),
            lost_minutes=1,
        )

    def ensure_reactive_replenishment(self, minute: int, line: OrderLine) -> None:
        already_open = any(
            task.sku_id == line.sku_id and task.status in {"QUEUED", "RELEASED", "IN_PROGRESS"}
            for task in self.replenishment_queue
        )
        if already_open:
            return
        source = self.reserve_storage_pallet(line.sku_id)
        if not source:
            return
        urgent_dynamic_cell = self.find_free_dynamic_cell_for_urgent_line(line)
        target_cell = urgent_dynamic_cell or line.pick_cell
        capacity = self.pick_face_capacity.get(target_cell, 100)
        current = max(0, self.pick_face_stock.get(target_cell, 0))
        free_capacity = capacity - current
        if free_capacity <= 0:
            return
        qty = min(100, free_capacity)
        task = ReplenishmentTask(
            task_id=f"RPL-REACTIVE-{line.wave_id}-{line.sku_id}-{minute:03d}",
            wave_id=line.wave_id,
            sku_id=line.sku_id,
            source_cell=source["cell_id"],
            target_cell=target_cell,
            qty_boxes=qty,
            replenishment_mode="CASE_REPLENISHMENT" if qty < 80 else "PALLET_REPLENISHMENT",
            status="QUEUED",
        )
        self.replenishment_queue.append(task)
        if urgent_dynamic_cell:
            self.dynamic_cell_sku[urgent_dynamic_cell] = line.sku_id
        self.emit(
            minute,
            "REACTIVE_REPLENISHMENT_PLANNED",
            wave_id=line.wave_id,
            client_id=line.client_id,
            pallet_id=line.pallet_id,
            sku_id=line.sku_id,
            task_id=task.task_id,
            source_cell=task.source_cell,
            target_cell=task.target_cell,
            qty_boxes=task.qty_boxes,
            reason="URGENT_DYNAMIC_CELL" if urgent_dynamic_cell else "PICK_FACE_CAPACITY_EXHAUSTED",
        )

    def progress_resources(self, minute: int) -> None:
        for truck in self.reachtrucks:
            if truck.status == "MOVING_PALLET" and minute >= truck.busy_until_minute:
                task = next((row for row in self.replenishment_queue if row.task_id == truck.task_id), None)
                if task:
                    task.status = "DONE"
                    task.done_minute = minute
                    self.pick_face_stock[task.target_cell] = self.pick_face_stock.get(task.target_cell, 0) + task.qty_boxes
                    target = self.cells_by_id[task.target_cell]
                    if target["role"] == "DYNAMIC_PICK_FACE":
                        self.dynamic_cell_sku[task.target_cell] = task.sku_id
                    truck.x_m = target["x_m"]
                    truck.y_m = target["y_m"]
                    truck.completed_ops += 1
                    self.emit(minute, "REPLENISHMENT_DONE", resource_id=truck.resource_id, wave_id=task.wave_id, task_id=task.task_id, sku_id=task.sku_id, source_cell=task.source_cell, target_cell=task.target_cell, qty_boxes=task.qty_boxes)
                truck.status = "IDLE"
                truck.task_id = None
                truck.wave_id = None
                truck.source_cell = None
                truck.target_cell = None
        for picker in self.pickers:
            if picker.status == "WAITING_REPLENISHMENT" and minute >= picker.busy_until_minute:
                line = self.find_line(picker.task_id)
                if line and self.pick_face_stock.get(line.pick_cell, 0) >= line.qty_boxes:
                    self.emit(
                        minute,
                        "PICK_FACE_REPLENISHED_FOR_WAITING_PICKER",
                        resource_id=picker.resource_id,
                        wave_id=line.wave_id,
                        client_id=line.client_id,
                        pallet_id=line.pallet_id,
                        sku_id=line.sku_id,
                        cell=line.pick_cell,
                    )
                    self.start_picker_line(minute, picker, line, include_walk=False)
                elif line:
                    picker.busy_until_minute = minute + 1
                    picker.wait_minutes += 1
                    self.record_empty_pick_face_arrival(minute, picker, line)
            if picker.status == "PICKING" and minute >= picker.busy_until_minute:
                line = self.find_line(picker.task_id)
                if line:
                    line.status = "DONE"
                    self.completed_lines.add(line.line_id)
                    cell = self.cells_by_id[line.pick_cell]
                    picker.x_m = cell["x_m"]
                    picker.y_m = cell["y_m"]
                    picker.picked_boxes += line.qty_boxes
                    self.emit(minute, "PICKER_TASK_DONE", resource_id=picker.resource_id, wave_id=line.wave_id, client_id=line.client_id, pallet_id=line.pallet_id, sku_id=line.sku_id, cell=line.pick_cell, qty_boxes=line.qty_boxes)
                picker.status = "IDLE"
                picker.task_id = None
                picker.wave_id = None
                picker.client_id = None
                picker.pallet_id = None

    def release_ready_dock_tasks(self, minute: int) -> None:
        for client in self.clients.values():
            if client.ready_minute is not None:
                continue
            self.detect_route_completion_delay(minute, client)
            if all(line.status == "DONE" for line in client.lines):
                client.ready_minute = minute
                for pallet_id in client.case_pallets:
                    staged_by = self.stage_case_pallet_to_dock(minute, client, pallet_id)
                    self.dock_queue.append(DockTask(
                        f"SHIP-{pallet_id}",
                        client.client_id,
                        client.wave_id,
                        client.gate_id,
                        pallet_id,
                        "WAITING",
                        self.args.dock_shipping_minutes,
                        minute,
                    ))
                    self.emit(
                        minute,
                        "PALLET_STAGED_TO_DOCK",
                        wave_id=client.wave_id,
                        client_id=client.client_id,
                        gate_id=client.gate_id,
                        pallet_id=pallet_id,
                        staged_by=staged_by["kind"],
                        resource_id=staged_by["resource_id"],
                    )
                self.emit(minute, "CLIENT_READY", wave_id=client.wave_id, client_id=client.client_id, gate_id=client.gate_id, pallets=len(client.case_pallets) + len(client.mono_pallets))

    def progress_shipping(self, minute: int) -> None:
        active_by_gate: dict[str, DockTask] = {}
        for task in self.dock_queue:
            if task.status == "LOADING":
                active_by_gate[task.gate_id] = task
                task.remaining_minutes -= 1
                if task.remaining_minutes <= 0:
                    task.status = "DONE"
                    self.shipped_pallets.add(task.pallet_id)
                    self.emit(minute, "PALLET_SHIPPED", wave_id=task.wave_id, client_id=task.client_id, gate_id=task.gate_id, pallet_id=task.pallet_id)
        for task in self.dock_queue:
            if task.status != "WAITING" or task.gate_id in active_by_gate:
                continue
            if minute - task.staged_minute < self.args.dock_accumulation_minutes:
                continue
            task.status = "LOADING"
            active_by_gate[task.gate_id] = task
            self.emit(minute, "PALLET_LOADING_STARTED", wave_id=task.wave_id, client_id=task.client_id, gate_id=task.gate_id, pallet_id=task.pallet_id)
        for client in self.clients.values():
            all_pallets = set(client.case_pallets + client.mono_pallets)
            if client.shipped_minute is None and all_pallets and all_pallets.issubset(self.shipped_pallets):
                client.shipped_minute = minute
                self.emit(minute, "CLIENT_SHIPPED", wave_id=client.wave_id, client_id=client.client_id, gate_id=client.gate_id)

    def detect_collisions(self, minute: int) -> None:
        pickers_by_cell: dict[str, list[Picker]] = {}
        for picker in self.pickers:
            if picker.status == "PICKING":
                line = self.find_line(picker.task_id)
                if line:
                    pickers_by_cell.setdefault(line.pick_cell, []).append(picker)
        for cell, pickers in pickers_by_cell.items():
            if len(pickers) > 1:
                self.record_collision(minute, "PICK_FACE_QUEUE", cell=cell, resources=[picker.resource_id for picker in pickers], lost_minutes=len(pickers) - 1)
        segment_load: dict[str, int] = {}
        for picker in self.pickers:
            if picker.status == "PICKING":
                key = segment_key(picker.x_m, picker.y_m)
                segment_load[key] = segment_load.get(key, 0) + 1
        for truck in self.reachtrucks:
            if truck.status == "MOVING_PALLET":
                key = segment_key(truck.x_m, truck.y_m)
                segment_load[key] = segment_load.get(key, 0) + 2
        for key, load in segment_load.items():
            if load > 4:
                self.record_collision(minute, "AISLE_CONGESTION", segment=key, load=load, lost_minutes=load - 4)
        active_targets = {truck.target_cell for truck in self.reachtrucks if truck.status == "MOVING_PALLET" and truck.target_cell}
        for picker in self.pickers:
            if picker.status != "PICKING":
                continue
            line = self.find_line(picker.task_id)
            if line and line.pick_cell in active_targets:
                self.record_collision(minute, "REACHTRUCK_BLOCK", cell=line.pick_cell, resource_id=picker.resource_id, lost_minutes=1)
        active_trucks = [truck for truck in self.reachtrucks if truck.status == "MOVING_PALLET"]
        for idx, first in enumerate(active_trucks):
            for second in active_trucks[idx + 1:]:
                if self.same_aisle_crossing(first, second):
                    aisle = round(first.y_m / 4) + 1
                    slot = max(1, round(((first.x_m + second.x_m) / 2) / 1.5) + 1)
                    self.record_collision(
                        minute,
                        "REACHTRUCK_CROSSING",
                        segment=f"A{aisle:02d}-SEG{max(1, slot // 7):02d}",
                        resources=[first.resource_id, second.resource_id],
                        lost_minutes=2,
                    )
        for truck in active_trucks:
            for picker in self.pickers:
                if picker.status == "PICKING" and self.reachtruck_passes_picker(truck, picker):
                    aisle = round(truck.y_m / 4) + 1
                    self.record_collision(
                        minute,
                        "REACHTRUCK_PICKER_PASS",
                        segment=f"A{aisle:02d}-SEG{max(1, round(truck.x_m / 10)):02d}",
                        resources=[truck.resource_id, picker.resource_id],
                        resource_id=truck.resource_id,
                        lost_minutes=1,
                    )
        waiting_repl = sum(1 for task in self.replenishment_queue if task.status == "QUEUED")
        if waiting_repl > 30:
            self.record_collision(minute, "REACH_RESOURCE_SHORTAGE", queued_tasks=waiting_repl, lost_minutes=min(10, waiting_repl // 10))
        waiting_dock = sum(1 for task in self.dock_queue if task.status == "WAITING")
        if waiting_dock > 25:
            self.record_collision(minute, "DOCK_QUEUE", queued_pallets=waiting_dock, lost_minutes=min(10, waiting_dock // 10))
        late_staging = sum(1 for task in self.dock_queue if task.status == "WAITING")
        if late_staging > 45:
            self.record_collision(minute, "PALLET_TO_DOCK_DELAY", queued_pallets=late_staging, lost_minutes=min(12, late_staging // 12))

    def capture_minute_metrics(self, minute: int) -> None:
        active_repl = sum(1 for task in self.replenishment_queue if task.status in {"RELEASED", "IN_PROGRESS"})
        queued_repl = sum(1 for task in self.replenishment_queue if task.status == "QUEUED")
        done_repl = sum(1 for task in self.replenishment_queue if task.status == "DONE")
        total_lines = sum(len(client.lines) for client in self.clients.values())
        done_lines = len(self.completed_lines)
        row = {
            "minute": minute,
            "clock": self.clock(minute),
            "active_waves": len(self.active_waves),
            "picker_busy": sum(1 for picker in self.pickers if picker.status != "IDLE"),
            "reachtruck_busy": sum(1 for truck in self.reachtrucks if truck.status != "IDLE"),
            "queued_replenishment": queued_repl,
            "active_replenishment": active_repl,
            "done_replenishment": done_repl,
            "done_pick_lines": done_lines,
            "total_pick_lines": total_lines,
            "dock_queue": sum(1 for task in self.dock_queue if task.status == "WAITING"),
            "shipped_pallets": len(self.shipped_pallets),
            "collisions": sum(1 for row in self.collision_rows if row["minute"] == minute),
            "lost_minutes": sum(row["lost_minutes"] for row in self.collision_rows if row["minute"] == minute),
        }
        self.minute_rows.append(row)

    def next_pickable_line(self) -> OrderLine | None:
        for client in self.clients.values():
            if client.wave_id not in self.active_waves:
                continue
            for line in client.lines:
                if line.status == "WAITING" and self.pick_face_stock.get(line.pick_cell, 0) >= line.qty_boxes:
                    return line
        return None

    def next_waiting_line_with_empty_pick_face(self) -> OrderLine | None:
        for client in self.clients.values():
            if client.wave_id not in self.active_waves:
                continue
            for line in client.lines:
                if line.status == "WAITING" and self.pick_face_stock.get(line.pick_cell, 0) < line.qty_boxes:
                    return line
        return None

    def detect_route_completion_delay(self, minute: int, client: ClientOrder) -> None:
        launch_minute = self.wave_launch_minutes.get(client.wave_id, 0)
        route_age = minute - launch_minute
        if route_age < 150:
            return
        done_lines = sum(1 for line in client.lines if line.status == "DONE")
        total_lines = max(1, len(client.lines))
        if done_lines == total_lines:
            return
        last_probe = self.route_delay_probe.get(client.client_id, -999)
        if minute - last_probe < 30:
            return
        self.route_delay_probe[client.client_id] = minute
        self.emit(
            minute,
            "ROUTE_COMPLETION_DELAYED",
            wave_id=client.wave_id,
            client_id=client.client_id,
            gate_id=client.gate_id,
            done_lines=done_lines,
            total_lines=total_lines,
            late_minutes=route_age - 150,
        )
        self.record_collision(
            minute,
            "ROUTE_COMPLETION_DELAY",
            wave_id=client.wave_id,
            client_id=client.client_id,
            gate_id=client.gate_id,
            lost_minutes=max(1, min(15, route_age - 150)),
        )

    def stage_case_pallet_to_dock(self, minute: int, client: ClientOrder, pallet_id: str) -> dict[str, str]:
        preferred_picker = next((picker for picker in self.pickers if picker.pallet_id == pallet_id), None)
        if preferred_picker:
            return {"kind": "PICKER", "resource_id": preferred_picker.resource_id}
        if self.rng.random() < 0.65:
            picker = self.rng.choice(self.pickers)
            return {"kind": "PICKER", "resource_id": picker.resource_id}
        truck = min(self.reachtrucks, key=lambda row: row.completed_ops)
        gate_no = int(client.gate_id.replace("G", ""))
        truck.x_m = -3
        truck.y_m = (gate_no - 1) * 4
        self.emit(
            minute,
            "REACHTRUCK_STAGED_PICKED_PALLET",
            resource_id=truck.resource_id,
            wave_id=client.wave_id,
            client_id=client.client_id,
            gate_id=client.gate_id,
            pallet_id=pallet_id,
        )
        return {"kind": "REACHTRUCK", "resource_id": truck.resource_id}

    def same_aisle_crossing(self, first: Reachtruck, second: Reachtruck) -> bool:
        return abs(first.y_m - second.y_m) <= 1.2 and abs(first.x_m - second.x_m) <= 12.0 and first.task_id != second.task_id

    def reachtruck_passes_picker(self, truck: Reachtruck, picker: Picker) -> bool:
        return abs(truck.y_m - picker.y_m) <= 1.2 and abs(truck.x_m - picker.x_m) <= 8.0

    def is_congested_location(self, x_m: float, y_m: float) -> bool:
        target_segment = segment_key(x_m, y_m)
        load = 0
        for picker in self.pickers:
            if picker.status == "PICKING" and segment_key(picker.x_m, picker.y_m) == target_segment:
                load += 1
        for truck in self.reachtrucks:
            if truck.status == "MOVING_PALLET" and segment_key(truck.x_m, truck.y_m) == target_segment:
                load += 2
            if truck.status == "MOVING_PALLET" and truck.target_cell:
                target = self.cells_by_id.get(truck.target_cell)
                if target and abs(target["y_m"] - y_m) <= 1.2 and abs(target["x_m"] - x_m) <= 8.0:
                    return True
        return load >= 4

    def reserve_storage_pallet(self, sku_id: str) -> dict[str, Any] | None:
        rows = self.storage_stock.get(sku_id, [])
        return rows.pop(0) if rows else None

    def find_free_dynamic_cell(self) -> str | None:
        dynamic_cells = [cell["cell_id"] for cell in self.layout["cells"] if cell["role"] == "DYNAMIC_PICK_FACE"]
        used_targets = {task.target_cell for task in self.replenishment_queue if task.status in {"QUEUED", "RELEASED", "IN_PROGRESS"}}
        for cell_id in dynamic_cells:
            if cell_id not in used_targets:
                return cell_id
        return None

    def find_free_dynamic_cell_for_urgent_line(self, line: OrderLine) -> str | None:
        current_cell = self.cells_by_id.get(line.pick_cell)
        if not current_cell:
            return None
        used_targets = {task.target_cell for task in self.replenishment_queue if task.status in {"QUEUED", "RELEASED", "IN_PROGRESS"}}
        candidates = []
        for cell in self.layout["cells"]:
            cell_id = cell["cell_id"]
            if cell["role"] != "DYNAMIC_PICK_FACE" or cell_id in used_targets:
                continue
            if self.dynamic_cell_sku.get(cell_id) or self.pick_face_stock.get(cell_id, 0) > 0:
                continue
            same_aisle_later = cell["aisle"] == current_cell["aisle"] and cell["slot"] >= current_cell["slot"]
            later_global_route = (cell["aisle"], cell["slot"]) > (current_cell["aisle"], current_cell["slot"])
            if same_aisle_later or later_global_route:
                candidates.append(cell)
        candidates.sort(key=lambda row: (row["aisle"] != current_cell["aisle"], row["aisle"], row["slot"]))
        return candidates[0]["cell_id"] if candidates else None

    def find_dynamic_cell_for_waiting_line(self, line: OrderLine) -> str | None:
        current_cell = self.cells_by_id.get(line.pick_cell)
        if not current_cell:
            return None
        candidates = []
        for cell in self.layout["cells"]:
            cell_id = cell["cell_id"]
            if cell["role"] != "DYNAMIC_PICK_FACE":
                continue
            if self.dynamic_cell_sku.get(cell_id) != line.sku_id:
                continue
            if self.pick_face_stock.get(cell_id, 0) < line.qty_boxes:
                continue
            same_aisle_later = cell["aisle"] == current_cell["aisle"] and cell["slot"] >= current_cell["slot"]
            later_global_route = (cell["aisle"], cell["slot"]) > (current_cell["aisle"], current_cell["slot"])
            if same_aisle_later or later_global_route:
                candidates.append(cell)
        candidates.sort(key=lambda row: (row["aisle"] != current_cell["aisle"], row["aisle"], row["slot"]))
        return candidates[0]["cell_id"] if candidates else None

    def find_line(self, line_id: str | None) -> OrderLine | None:
        if not line_id:
            return None
        for client in self.clients.values():
            for line in client.lines:
                if line.line_id == line_id:
                    return line
        return None

    def emit(self, minute: int, event_type: str, **payload: Any) -> None:
        self.events.append({"minute": minute, "clock": self.clock(minute), "event_type": event_type, **payload})

    def record_collision(self, minute: int, collision_type: str, lost_minutes: int, **payload: Any) -> None:
        row = {"minute": minute, "clock": self.clock(minute), "collision_type": collision_type, "lost_minutes": lost_minutes, **payload}
        self.collision_rows.append(row)
        self.emit(minute, "COLLISION", collision_type=collision_type, lost_minutes=lost_minutes, **payload)

    def clock(self, minute: int) -> str:
        return (self.shift_start + timedelta(minutes=minute)).strftime("%H:%M")

    def orders_payload(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "clients": [
                {
                    "client_id": client.client_id,
                    "wave_id": client.wave_id,
                    "gate_id": client.gate_id,
                    "case_pallets": client.case_pallets,
                    "mono_pallets": client.mono_pallets,
                    "lines": [asdict(line) for line in client.lines],
                }
                for client in self.clients.values()
            ],
        }

    def stock_payload(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "pick_face_stock": self.pick_face_stock,
            "pick_face_capacity": self.pick_face_capacity,
            "storage_stock": self.storage_stock,
            "sku": {sku_id: asdict(sku) for sku_id, sku in self.skus.items()},
        }

    def build_report(self) -> dict[str, Any]:
        total_lines = sum(len(client.lines) for client in self.clients.values())
        total_pick_boxes = sum(line.qty_boxes for client in self.clients.values() for line in client.lines)
        done_pick_boxes = sum(line.qty_boxes for client in self.clients.values() for line in client.lines if line.status == "DONE")
        shift_hours = self.shift_minutes / 60
        picker_box_capacity = int(sum(picker.boxes_per_hour for picker in self.pickers) * shift_hours)
        reachtruck_nominal_capacity = int(sum(truck.operations_per_hour for truck in self.reachtrucks) * shift_hours)
        case_replenishment_capacity = int(self.args.reachtrucks * self.args.case_replenishment_per_hour * shift_hours)
        case_replenishment_tasks = sum(1 for task in self.replenishment_queue if task.replenishment_mode == "CASE_REPLENISHMENT")
        pallet_replenishment_tasks = sum(1 for task in self.replenishment_queue if task.replenishment_mode == "PALLET_REPLENISHMENT")
        reroute_events = sum(1 for event in self.events if event["event_type"] == "PICK_LINE_REROUTED_TO_DYNAMIC_CELL")
        dynamic_pick_faces = [cell for cell in self.layout["cells"] if cell["role"] == "DYNAMIC_PICK_FACE"]
        layout_pick_faces = [cell for cell in self.layout["cells"] if cell["level"] == 1]
        end_of_aisle_dynamic_pick_faces = [
            cell for cell in dynamic_pick_faces
            if cell["slot"] > self.layout["warehouse"]["slots_per_aisle"] - self.layout["warehouse"]["dynamic_slots_per_aisle"]
        ]
        wave_completion: dict[str, int | None] = {}
        for wave_no in range(1, self.args.waves + 1):
            wave_id = f"WAVE-SIM-{wave_no:02d}"
            wave_clients = [client for client in self.clients.values() if client.wave_id == wave_id]
            shipped = [client.shipped_minute for client in wave_clients if client.shipped_minute is not None]
            wave_completion[wave_id] = max(shipped) if len(shipped) == len(wave_clients) else None
        lost_by_type: dict[str, int] = {}
        count_by_type: dict[str, int] = {}
        for row in self.collision_rows:
            key = row["collision_type"]
            lost_by_type[key] = lost_by_type.get(key, 0) + int(row["lost_minutes"])
            count_by_type[key] = count_by_type.get(key, 0) + 1
        picker_util = [picker.pick_minutes + picker.walk_minutes for picker in self.pickers]
        reach_util = [truck.travel_minutes + truck.completed_ops * 2 for truck in self.reachtrucks]
        return {
            "run_id": self.run_id,
            "mode": self.args.mode,
            "seed": self.args.seed,
            "out_dir": str(self.out_dir),
            "scenario": {
                "clients": self.args.clients,
                "waves": self.args.waves,
                "clients_per_wave": self.args.clients_per_wave,
                "sku": self.args.sku,
                "pick_faces": self.args.pick_faces,
                "pickers": self.args.pickers,
                "reachtrucks": self.args.reachtrucks,
                "shift_minutes": self.shift_minutes,
                "replenishment_lead_minutes": self.replenishment_lead_minutes,
                "case_replenishment_per_hour": self.args.case_replenishment_per_hour,
                "pallet_drop_minutes": self.args.pallet_drop_minutes,
                "pallet_exchange_minutes_min": self.args.pallet_exchange_minutes_min,
                "pallet_exchange_minutes_max": self.args.pallet_exchange_minutes_max,
                "dock_accumulation_minutes": self.args.dock_accumulation_minutes,
                "dock_shipping_minutes": self.args.dock_shipping_minutes,
            },
            "totals": {
                "case_pallets": sum(len(client.case_pallets) for client in self.clients.values()),
                "mono_pallets": sum(len(client.mono_pallets) for client in self.clients.values()),
                "pick_lines": total_lines,
                "done_pick_lines": len(self.completed_lines),
                "replenishment_tasks": len(self.replenishment_queue),
                "done_replenishment_tasks": sum(1 for task in self.replenishment_queue if task.status == "DONE"),
                "shipped_pallets": len(self.shipped_pallets),
                "collisions": len(self.collision_rows),
                "lost_minutes": sum(row["lost_minutes"] for row in self.collision_rows),
                "dynamic_reroutes": reroute_events,
            },
            "wave_completion_minutes": wave_completion,
            "collision_count_by_type": count_by_type,
            "lost_minutes_by_type": lost_by_type,
            "resource_utilization": {
                "picker_busy_minutes_avg": round(statistics.mean(picker_util), 2) if picker_util else 0,
                "picker_busy_minutes_max": max(picker_util) if picker_util else 0,
                "reachtruck_busy_minutes_avg": round(statistics.mean(reach_util), 2) if reach_util else 0,
                "reachtruck_busy_minutes_max": max(reach_util) if reach_util else 0,
            },
            "capacity_analysis": {
                "total_pick_boxes": total_pick_boxes,
                "done_pick_boxes": done_pick_boxes,
                "picker_box_capacity_per_shift": picker_box_capacity,
                "picker_demand_to_capacity_ratio": round(total_pick_boxes / max(1, picker_box_capacity), 2),
                "replenishment_tasks": len(self.replenishment_queue),
                "case_replenishment_tasks": case_replenishment_tasks,
                "pallet_replenishment_tasks": pallet_replenishment_tasks,
                "reachtruck_nominal_capacity_per_shift": reachtruck_nominal_capacity,
                "case_replenishment_capacity_if_all_case": case_replenishment_capacity,
                "replenishment_demand_to_nominal_capacity_ratio": round(len(self.replenishment_queue) / max(1, reachtruck_nominal_capacity), 2),
                "dynamic_pick_faces": len(dynamic_pick_faces),
                "end_of_aisle_dynamic_pick_faces": len(end_of_aisle_dynamic_pick_faces),
                "dynamic_pick_face_share": round(len(dynamic_pick_faces) / max(1, len(layout_pick_faces)), 2),
            },
            "bottleneck_summary": self.build_bottleneck_summary(
                total_pick_boxes=total_pick_boxes,
                picker_box_capacity=picker_box_capacity,
                reachtruck_nominal_capacity=reachtruck_nominal_capacity,
                count_by_type=count_by_type,
                lost_by_type=lost_by_type,
            ),
            "artifacts": {
                "layout": "layout.json",
                "events": "events.jsonl",
                "timeline": "timeline.csv",
                "metrics_by_minute": "metrics-by-minute.csv",
                "collisions": "collision-report.csv",
                "orders": "generated-orders.json",
                "stock": "generated-stock.json",
                "animation_page": "wiki-raw/wms_admin_ui_reference/warehouse-simulation.html",
            },
        }

    def build_bottleneck_summary(
        self,
        total_pick_boxes: int,
        picker_box_capacity: int,
        reachtruck_nominal_capacity: int,
        count_by_type: dict[str, int],
        lost_by_type: dict[str, int],
    ) -> list[dict[str, Any]]:
        summary: list[dict[str, Any]] = []
        if total_pick_boxes > picker_box_capacity:
            summary.append(
                {
                    "code": "PICKER_CAPACITY_SHORTAGE",
                    "severity": "critical",
                    "message": "Коробочный спрос смены превышает расчетную мощность комплектовщиков.",
                    "demand": total_pick_boxes,
                    "capacity": picker_box_capacity,
                    "ratio": round(total_pick_boxes / max(1, picker_box_capacity), 2),
                }
            )
        replenishment_tasks = len(self.replenishment_queue)
        if replenishment_tasks > reachtruck_nominal_capacity:
            summary.append(
                {
                    "code": "REACHTRUCK_CAPACITY_SHORTAGE",
                    "severity": "critical",
                    "message": "Количество задач пополнения превышает номинальную сменную мощность ричтраков.",
                    "demand": replenishment_tasks,
                    "capacity": reachtruck_nominal_capacity,
                    "ratio": round(replenishment_tasks / max(1, reachtruck_nominal_capacity), 2),
                }
            )
        for collision_type, lost_minutes in sorted(lost_by_type.items(), key=lambda item: item[1], reverse=True)[:3]:
            summary.append(
                {
                    "code": collision_type,
                    "severity": "warning",
                    "message": "Операционная коллизия входит в топ потерь смены.",
                    "count": count_by_type.get(collision_type, 0),
                    "lost_minutes": lost_minutes,
                }
            )
        return summary

    def write_events(self) -> None:
        path = self.out_dir / "events.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for event in self.events:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def write_json(self, name: str, payload: Any) -> None:
        (self.out_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_csv(self, name: str, rows: list[dict[str, Any]]) -> None:
        path = self.out_dir / name
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def write_markdown_report(self, report: dict[str, Any]) -> None:
        lines = [
            f"# Warehouse Minute Simulation {self.run_id}",
            "",
            f"- Mode: `{report['mode']}`",
            f"- Seed: `{report['seed']}`",
            f"- Clients: `{report['scenario']['clients']}`",
            f"- Waves: `{report['scenario']['waves']}`",
            f"- Pick lines: `{report['totals']['pick_lines']}` / done `{report['totals']['done_pick_lines']}`",
            f"- Replenishment tasks: `{report['totals']['replenishment_tasks']}` / done `{report['totals']['done_replenishment_tasks']}`",
            f"- Shipped pallets: `{report['totals']['shipped_pallets']}`",
            f"- Collisions: `{report['totals']['collisions']}`",
            f"- Lost minutes: `{report['totals']['lost_minutes']}`",
            "",
            "## Collision Types",
            "",
        ]
        for key, count in sorted(report["collision_count_by_type"].items()):
            lines.append(f"- `{key}`: count `{count}`, lost minutes `{report['lost_minutes_by_type'].get(key, 0)}`")
        lines.extend(
            [
                "",
                "## Capacity Analysis",
                "",
                f"- Pick demand: `{report['capacity_analysis']['total_pick_boxes']}` boxes; picker shift capacity: `{report['capacity_analysis']['picker_box_capacity_per_shift']}` boxes; ratio `{report['capacity_analysis']['picker_demand_to_capacity_ratio']}`.",
                f"- Replenishment demand: `{report['capacity_analysis']['replenishment_tasks']}` tasks; reachtruck nominal capacity: `{report['capacity_analysis']['reachtruck_nominal_capacity_per_shift']}` tasks; ratio `{report['capacity_analysis']['replenishment_demand_to_nominal_capacity_ratio']}`.",
                f"- Replenishment mix: `{report['capacity_analysis']['pallet_replenishment_tasks']}` pallet tasks, `{report['capacity_analysis']['case_replenishment_tasks']}` case tasks.",
                f"- Dynamic pick-face: `{report['capacity_analysis']['dynamic_pick_faces']}` cells (`{report['capacity_analysis']['dynamic_pick_face_share']}` share), end-of-aisle urgent overflow cells `{report['capacity_analysis']['end_of_aisle_dynamic_pick_faces']}`.",
                f"- Dynamic urgent reroutes: `{report['totals']['dynamic_reroutes']}` pick lines.",
                "",
                "## Bottleneck Summary",
                "",
            ]
        )
        for item in report["bottleneck_summary"]:
            lines.append(f"- `{item['code']}` ({item['severity']}): {item['message']}")
        lines.extend(
            [
                "",
                "## Artifacts",
                "",
                "- `layout.json`",
                "- `events.jsonl`",
                "- `timeline.csv`",
                "- `metrics-by-minute.csv`",
                "- `collision-report.csv`",
                "- `generated-orders.json`",
                "- `generated-stock.json`",
            ]
        )
        (self.out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_presentation(self, report: dict[str, Any]) -> None:
        body = json.dumps(report, ensure_ascii=False, indent=2)
        html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Warehouse Simulation Evidence {self.run_id}</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f5f8fc; color: #0b1f3a; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 32px; }}
    section {{ margin: 0 0 16px; padding: 20px; background: #fff; border: 1px solid #dde6f1; border-radius: 8px; }}
    pre {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>Warehouse Simulation Evidence</h1>
      <p>Run: <b>{self.run_id}</b></p>
      <p>Open <code>wiki-raw/wms_admin_ui_reference/warehouse-simulation.html</code> and load <code>layout.json</code>, <code>events.jsonl</code>, and <code>report.json</code> from this folder.</p>
    </section>
    <section><h2>Report JSON</h2><pre>{escape_html(body)}</pre></section>
  </main>
</body>
</html>
"""
        (self.out_dir / "evidence-presentation.html").write_text(html, encoding="utf-8")


def parse_clock(value: str) -> datetime:
    hour, minute = [int(part) for part in value.split(":", 1)]
    return datetime(2026, 5, 19, hour, minute)


def manhattan(x1: float, y1: float, x2: float, y2: float) -> float:
    return abs(x1 - x2) + abs(y1 - y2)


def warehouse_route_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    if abs(y1 - y2) < 0.01:
        return abs(x1 - x2)
    cross_aisles = (0.0, 45.0, 90.0)
    return min(abs(x1 - cross_x) + abs(y1 - y2) + abs(x2 - cross_x) for cross_x in cross_aisles)


def segment_key(x_m: float, y_m: float) -> str:
    return f"A{round(y_m / 4) + 1:02d}-SEG{math.floor(x_m / 10):02d}"


def escape_html(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


if __name__ == "__main__":
    main()
