"""Code128 B for one CASE pick line on paper (C-0156): existing task and line identity plus the native line signature, no new ledger."""
import re
from .sscc_label import PATTERNS

REFERENCE = re.compile(r"CPICK:([1-9]\d{0,17}):([1-9]\d{0,17}):([A-F0-9]{64})")


def case_line_barcode(task: int, line: int, signature: str) -> tuple[str, str]:
    if task < 1 or line < 1 or not re.fullmatch(r"[A-F0-9]{64}", signature):
        raise ValueError("Invalid CASE paper identity")
    reference = f"CPICK:{task}:{line}:{signature}"
    codes = [104, *(ord(char) - 32 for char in reference)]
    codes += [(codes[0] + sum(i * code for i, code in enumerate(codes[1:], 1))) % 103, 106]
    x, bars = 10, []
    for code in codes:
        for i, width in enumerate(PATTERNS[code]):
            if i % 2 == 0:
                bars.append(f'<rect x="{x}" y="0" width="{width}" height="65"/>')
            x += int(width)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x + 10} 84" width="100%" role="img" aria-label="CASE {task} line {line}">'
           + ''.join(bars) + f'<text x="{(x + 10) / 2}" y="80" text-anchor="middle" font-size="10">{task} / {line}</text></svg>')
    return reference, svg
