"""Independent ReportLab vector fixture for the Chromium software camera test."""
import argparse
import json
import reportlab
from reportlab.graphics.barcode import createBarcodeDrawing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('format', choices=('CODE128', 'EAN13', 'GS1128'))
    parser.add_argument('code')
    args = parser.parse_args()
    drawing = createBarcodeDrawing('EAN13' if args.format == 'EAN13' else 'Code128',
                                   value=('\xf1' + args.code) if args.format == 'GS1128' else args.code,
                                   humanReadable=False, barWidth=1, barHeight=60)
    group = drawing.contents[0].draw()
    assert group.transform == (1, 0, 0, 1, 0, 0)
    bars = []
    for shape in group.contents:
        assert type(shape).__name__ == 'Rect'
        if shape.fillColor is None:
            continue
        assert (shape.fillColor.red, shape.fillColor.green, shape.fillColor.blue) == (0, 0, 0)
        bars.append([shape.x, shape.y, shape.width, shape.height])
    assert bars
    print(json.dumps({'generator': 'ReportLab', 'version': reportlab.Version,
                      'format': args.format, 'width': drawing.width, 'height': drawing.height, 'bars': bars}))


if __name__ == '__main__':
    main()
