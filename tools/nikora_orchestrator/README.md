# NIKORA bounded orchestrator

`nikora_orchestrator.py` runs the early cross-dock plan one CD-ID at a time. It is intentionally incapable of silently accepting, deploying, applying Oracle migrations or proceeding past a human gate.

```powershell
python tools/nikora_orchestrator/nikora_orchestrator.py bootstrap
python tools/nikora_orchestrator/nikora_orchestrator.py prepare CD00
python tools/nikora_orchestrator/nikora_orchestrator.py run-author CD00
python tools/nikora_orchestrator/nikora_orchestrator.py status
```

The local, ignored state and evidence live in `tmp/nikora-orchestrator/`. CD00 is a read-only readiness/pilot-passport assessment. After a human accepts it, first create a reviewed baseline commit, then bind it:

```powershell
python tools/nikora_orchestrator/nikora_orchestrator.py set-baseline <commit-sha>
python tools/nikora_orchestrator/nikora_orchestrator.py accept CD00 --evidence <path-or-link>
python tools/nikora_orchestrator/nikora_orchestrator.py prepare CD01
```

Only Claude-author cards can currently be run by `run-author`; Codex-author cards are deliberately prepared for the existing Codex runner until a separately reviewed worktree launcher is added. This prevents an accidental run in the shared dirty tree.
