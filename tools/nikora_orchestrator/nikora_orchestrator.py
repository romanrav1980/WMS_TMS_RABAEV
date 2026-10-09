#!/usr/bin/env python3
"""Bounded orchestrator for the NIKORA early cross-dock increments.

It is deliberately a state machine, not an autonomous deployer.  Each
increment has an author run, an independent review, and an explicit human
acceptance gate.  CD00 may run read-only on an unsealed workspace; every
subsequent author run requires an immutable baseline SHA and an isolated
worktree supplied by the operator.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "tmp" / "nikora-orchestrator"
STATE_FILE = RUNTIME / "state.json"

STEPS = [
    ("CD00", "B", "Claude Sonnet 5", "high", "Claude Sonnet 5", "high", True,
     "Паспорт стенда: доступы, test Oracle, два источника, rollback; без продуктовой доработки."),
    ("CD01", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Один XML ingress и отрицательные schema tests."),
    ("CD02", "X", "Codex Astra -> Codex Sol", "high", "Claude Opus 5", "high", False, "Идемпотентность, outbox/retry и инварианты."),
    ("CD03", "C", "Claude Sonnet 5", "medium", "Codex Terra", "medium", False, "Адреса, магазины, артикулы и revision."),
    ("CD04", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "OrderManifest revision/cancel и ожидаемые части."),
    ("CD05", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Стабильный идентификатор части/HU без repack."),
    ("CD06", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "PLAN/ACTUAL_ONLY WMS №1."),
    ("CD07", "C", "Claude Sonnet 5", "medium", "Codex Terra", "medium", False, "Четыре outbound ERP-статуса и мониторинг."),
    ("CD08", "C", "Claude Sonnet 5", "medium", "Codex Terra", "high", False, "Тонкий совместимый адаптер WMS №2."),
    ("CD09", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Leg/custody источник → хаб."),
    ("CD10", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Ручные время, ворота и ёмкость."),
    ("CD11", "H", "Codex Sol", "high", "Claude Sonnet 5 + человек", "high", False, "Quality evidence существующей WMS."),
    ("CD12", "X", "Codex Astra -> Codex Sol", "high", "Claude Opus 5", "high", False, "Атомарные validator/freeze/release."),
    ("CD13", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Ручная волна и обратный расчёт времени."),
    ("CD14", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Ручной маршрут и порядок обработки."),
    ("CD15", "C", "Claude Sonnet 5", "medium", "Codex Terra", "high", False, "Приёмка HU в target WMS, без merge/repack."),
    ("CD16", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Load/departed и ERP transit."),
    ("CD17", "H", "Codex Sol", "high", "Claude Sonnet 5", "high", False, "Минимальные HOLD/missing/mismatch."),
    ("CD18", "C", "Claude Sonnet 5", "medium", "Codex Terra", "high", False, "Приёмка магазина и ERP delivered."),
    ("CD19", "H", "Codex Sol", "high", "Claude Opus 5 + человек", "high", False, "Gate двух источников и evidence."),
    ("CDP", "P", "Человек + local Qwen", "n/a", "Claude Sonnet 5", "high", False, "Десятидневный наблюдаемый пилот."),
]


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        raise SystemExit("Оркестратор не инициализирован: выполните bootstrap.")
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def step_by_id(step_id: str) -> dict[str, Any]:
    for index, data in enumerate(STEPS):
        if data[0] == step_id:
            return dict(zip(("id", "profile", "author", "author_effort", "reviewer", "reviewer_effort", "read_only", "scope"), data, strict=True)) | {"index": index}
    raise SystemExit(f"Неизвестный CD-ID: {step_id}")


def bootstrap(_: argparse.Namespace) -> None:
    if STATE_FILE.exists():
        print(f"Уже инициализирован: {STATE_FILE}")
        return
    save_state({
        "version": 1,
        "created_at": now(),
        "baseline_sha": None,
        "steps": {item[0]: {"status": "PENDING", "events": []} for item in STEPS},
    })
    print(f"Создано состояние: {STATE_FILE}")
    print("Следующее действие: prepare CD00, затем run-author CD00.")


def status(_: argparse.Namespace) -> None:
    state = load_state()
    print(f"baseline_sha: {state['baseline_sha'] or 'НЕ ЗАКРЕПЛЁН'}")
    for data in STEPS:
        step = state["steps"][data[0]]
        print(f"{data[0]:4}  {step['status']:17}  {data[2]}")


def set_baseline(args: argparse.Namespace) -> None:
    state = load_state()
    result = subprocess.run(["git", "rev-parse", "--verify", args.sha + "^{commit}"], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise SystemExit("SHA не является доступным commit. Сначала закрепите согласованную ревизию.")
    state["baseline_sha"] = result.stdout.strip()
    save_state(state)
    print(f"Baseline закреплён: {state['baseline_sha']}")


def prior_accepted(state: dict[str, Any], step: dict[str, Any]) -> bool:
    return step["index"] == 0 or state["steps"][STEPS[step["index"] - 1][0]]["status"] == "ACCEPTED"


def write_task(step: dict[str, Any], state: dict[str, Any]) -> Path:
    directory = RUNTIME / step["id"]
    directory.mkdir(parents=True, exist_ok=True)
    task = directory / "TASK.md"
    mode = "read-only assessment" if step["read_only"] else "implementation in a separate worktree from the baseline SHA"
    task.write_text(
        f"# NIKORA {step['id']}\n\n"
        f"Mode: {mode}\n\n"
        f"## Scope\n\n{step['scope']}\n\n"
        "## Mandatory reading\n\n"
        "- `AGENTS.md`\n- `wiki/index.md`\n- `wiki/roadmap/nikora_crossdock_first.md`\n"
        "- `wiki/requirements/nikora_crossdock_increments.md`\n"
        "- `wiki/roadmap/nikora_crossdock_agent_map.md`\n"
        "- relevant parent cards and `wiki/requirements/nikora_sprint_contract.md`\n\n"
        "## Limits\n\n"
        "One CD-ID only. Do not commit, push, deploy, apply Oracle migrations, contact ERP/WMS, or mark `ACCEPTED_CD`. "
        "Do not broaden XML, replace the WMS core, or touch unrelated staged changes.\n\n"
        "## Required result\n\n"
        "Return: scope confirmation, files/contract affected, negative tests, commands executed, evidence, slow-SQL decision if a business scenario ran, and explicit residual risks.\n\n"
        f"Baseline SHA: {state['baseline_sha'] or 'not required for CD00; REQUIRED for the next implementation step'}\n",
        encoding="utf-8",
    )
    return task


def prepare(args: argparse.Namespace) -> None:
    state = load_state()
    step = step_by_id(args.step)
    record = state["steps"][step["id"]]
    if not prior_accepted(state, step):
        raise SystemExit("Предыдущий CD-ID ещё не принят человеком.")
    if not step["read_only"] and not state["baseline_sha"]:
        raise SystemExit("Для реализации нужен закреплённый baseline SHA. Выполните set-baseline после human-gate CD00.")
    task = write_task(step, state)
    record["status"] = "PREPARED"
    record["task"] = str(task)
    record["events"].append({"at": now(), "event": "prepared"})
    save_state(state)
    print(task)


def command_for(step: dict[str, Any], task: Path) -> list[str]:
    if "Claude" not in step["author"]:
        raise SystemExit(f"{step['id']} назначен {step['author']}; этот runner запускает Claude author runs только для Claude-карточек.")
    executable = shutil.which("claude")
    if not executable:
        package_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        candidates = sorted(package_dir.glob("Anthropic.ClaudeCode_*/*claude.exe"))
        executable = str(candidates[-1]) if candidates else None
    if not executable:
        raise SystemExit("Claude Code CLI не найден. Установите его, войдите в подписку и повторите команду.")
    prompt = (
        f"Ты автор {step['id']}. Прочитай {task} и обязательные документы. "
        "Выполни только указанный bounded ticket. Не делай commit/push/deploy/Oracle mutation. "
        "Сначала проверь scope, затем верни структурированный evidence report."
    )
    return [executable, "-p", "--model", "claude-sonnet-5", "--effort", step["author_effort"], "--max-turns", "25", "--max-budget-usd", "8", "--output-format", "json", prompt]


def run_author(args: argparse.Namespace) -> None:
    state = load_state()
    step = step_by_id(args.step)
    record = state["steps"][step["id"]]
    if record["status"] not in {"PREPARED", "AUTHOR_BLOCKED"}:
        raise SystemExit("Сначала выполните prepare для этого шага; AUTHOR_BLOCKED можно безопасно повторить после устранения причины.")
    task = Path(record["task"])
    command = command_for(step, task)
    output = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout)
    directory = RUNTIME / step["id"]
    (directory / "author.stdout.json").write_text(output.stdout, encoding="utf-8")
    (directory / "author.stderr.txt").write_text(output.stderr, encoding="utf-8")
    record["status"] = "AUTHOR_DONE" if output.returncode == 0 else "AUTHOR_BLOCKED"
    record["events"].append({"at": now(), "event": "author_run", "exit_code": output.returncode})
    save_state(state)
    print(f"exit={output.returncode}; evidence={directory}")
    if output.returncode:
        raise SystemExit(output.returncode)


def accept(args: argparse.Namespace) -> None:
    state = load_state()
    step = step_by_id(args.step)
    record = state["steps"][step["id"]]
    if record["status"] not in {"AUTHOR_DONE", "REVIEW_DONE"}:
        raise SystemExit("Принять можно только результат автора/reviewer с приложенным evidence.")
    if not args.evidence:
        raise SystemExit("Нужна ссылка или путь к evidence human-acceptance.")
    record["status"] = "ACCEPTED"
    record["events"].append({"at": now(), "event": "human_accepted", "evidence": args.evidence})
    save_state(state)
    print(f"{step['id']} принят человеком. Следующий шаг можно подготовить.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)
    sub.add_parser("bootstrap").set_defaults(func=bootstrap)
    sub.add_parser("status").set_defaults(func=status)
    baseline = sub.add_parser("set-baseline")
    baseline.add_argument("sha")
    baseline.set_defaults(func=set_baseline)
    prepared = sub.add_parser("prepare")
    prepared.add_argument("step")
    prepared.set_defaults(func=prepare)
    author = sub.add_parser("run-author")
    author.add_argument("step")
    author.add_argument("--timeout", type=int, default=1800)
    author.set_defaults(func=run_author)
    accepted = sub.add_parser("accept")
    accepted.add_argument("step")
    accepted.add_argument("--evidence", required=True)
    accepted.set_defaults(func=accept)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
