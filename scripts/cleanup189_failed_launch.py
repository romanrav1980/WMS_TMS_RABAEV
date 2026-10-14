from pathlib import Path
import json
t=Path("scripts/cleanup182_first_cases.py").read_text(encoding="utf-8").replace("for wave in [412,413,414]:","for wave in [423]:")
exec(compile(t,"cleanup189-native","exec"))
