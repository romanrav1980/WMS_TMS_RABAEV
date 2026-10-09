"""GS1-128 subset C with FNC1/AI00, standalone SVG and printer ZPL."""
from html import escape

FIELD_LABELS = {"article": "Артикул", "quantity": "Количество", "unit": "Единица", "batch": "Партия", "expiry": "Годен до"}

PATTERNS = "212222 222122 222221 121223 121322 131222 122213 122312 132212 221213 221312 231212 112232 122132 122231 113222 123122 123221 223211 221132 221231 213212 223112 312131 311222 321122 321221 312212 322112 322211 212123 212321 232121 111323 131123 131321 112313 132113 132311 211313 231113 231311 112133 112331 132131 113123 113321 133121 313121 211331 231131 213113 213311 213131 311123 311321 331121 312113 312311 332111 314111 221411 431111 111224 111422 121124 121421 141122 141221 112214 112412 122114 122411 142112 142211 241211 221114 413111 241112 134111 111242 121142 121241 114212 124112 124211 411212 421112 421211 212141 214121 412121 111143 111341 131141 114113 114311 411113 411311 113141 114131 311141 411131 211412 211214 211232 2331112".split()


def check_digit(body: str) -> str:
    return str((10 - sum(int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(body))) % 10) % 10)


def barcode_svg(sscc: str) -> str:
    if len(sscc) != 18 or not sscc.isdigit() or sscc[-1] != check_digit(sscc[:-1]):
        raise ValueError('Invalid SSCC')
    numbers = [105, 102] + [int(('00' + sscc)[i:i+2]) for i in range(0,20,2)]
    numbers += [(numbers[0] + sum(i * n for i, n in enumerate(numbers[1:], 1))) % 103, 106]
    x, bars = 10, []
    for number in numbers:
        for i, width in enumerate(PATTERNS[number]):
            w = int(width)
            if i % 2 == 0:
                bars.append(f'<rect x="{x}" y="0" width="{w}" height="65"/>')
            x += w
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x+10} 82" width="100%" role="img" aria-label="SSCC {sscc}">' + ''.join(bars) + f'<text x="{(x+10)/2}" y="78" text-anchor="middle" font-size="8">(00){sscc}</text></svg>'


def label_html(data: dict) -> str:
    fields = ''.join('<p><b>' + escape(FIELD_LABELS.get(k, str(k))) + ':</b> ' + escape(str(v)) + '</p>' for k, v in data.items() if k != 'sscc')
    return '<!doctype html><html><meta charset="utf-8"><title>SSCC ' + escape(data['sscc']) + '</title><style>@page{size:105mm 148mm;margin:5mm}body{font:14px sans-serif;width:95mm}p{margin:5px}svg{margin-top:12px}@media print{button{display:none}}</style><body>' + fields + barcode_svg(data['sscc']) + '<button onclick="window.print()">Печать</button></body></html>'


def label_zpl(data: dict, dpi: int = 203) -> str:
    px = lambda mm: round(mm * dpi / 25.4)
    commands = [f'^XA^CI28^PW{px(105)}^LL{px(148)}']
    for i, (key, value) in enumerate((pair for pair in data.items() if pair[0] != 'sscc')):
        text = f'{FIELD_LABELS.get(key, key)}: {value}'
        encoded = ''.join(f'_{b:02X}' for b in text.encode('utf-8'))
        commands.append(f'^FO{px(5)},{px(5+i*6)}^A0N,{px(4)},{px(4)}^FH_^FD{encoded}^FS')
    commands.append(f"^FO{px(5)},{px(95)}^BY{px(.5)}^BCN,{px(35)},Y,N,N^FD>;>800{data['sscc']}^FS^XZ")
    return '\n'.join(commands)
