"""Keep maintained command owners reachable from the canonical stock root."""
from pathlib import Path
import re

def assert_runtime_dispatch(manifest: dict, directory: Path) -> list[str]:
    sources = [(name, (directory / name).read_text(encoding="utf-8")) for name in manifest["components"]]
    roots = [text for _, text in sources if re.search(r"create\s+or\s+replace\s+package\s+RRL_STOCK_POSTING_API\s", text, re.I)]
    if len(roots) != 1:
        raise ValueError("Exactly one canonical RRL_STOCK_POSTING_API source is required")
    root = roots[0]
    owners: list[str] = []
    for filename, text in sources:
        package = re.search(r"create\s+or\s+replace\s+package\s+(\w+)", text, re.I)
        if not package:
            continue
        name = package[1].upper()
        if name == "RRL_STOCK_POSTING_API":
            continue
        if not all(re.search(r"procedure\s+" + method + r"\s*\(", text, re.I) for method in ("compile_command", "execute_command")):
            continue
        for method in ("compile_command", "execute_command"):
            if not re.search(r"\b" + name + r"\s*[.]\s*" + method + r"\s*\(", root, re.I):
                raise ValueError(f"Installed command owner {name}.{method} is missing from current stock root ({filename})")
        owners.append(name)
    if len(owners) != len(set(owners)):
        raise ValueError("Duplicate canonical command owner sources")
    return sorted(owners)
