"""Code128 B carries the existing task identity and frozen task signature; no new document ledger."""
import re
from .sscc_label import PATTERNS


def task_barcode(task: int, signature: str) -> tuple[str, str]:
    if task < 1 or not re.fullmatch(r"[A-F0-9]{64}", signature):
        raise ValueError("Invalid task paper identity")
    reference = f"WTASK:{task}:{signature}"
    codes = [104, *(ord(char) - 32 for char in reference)]
    codes += [(codes[0] + sum(i * code for i, code in enumerate(codes[1:], 1))) % 103, 106]
    x, bars = 10, []
    for code in codes:
        for i, width in enumerate(PATTERNS[code]):
            if i % 2 == 0:
                bars.append(f'<rect x="{x}" y="0" width="{width}" height="65"/>')
            x += int(width)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x + 10} 84" width="100%" role="img" aria-label="Task {task}">'
           + ''.join(bars) + f'<text x="{(x + 10) / 2}" y="80" text-anchor="middle" font-size="10">{task}</text></svg>')
    return reference, svg
