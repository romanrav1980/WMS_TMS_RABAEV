from pathlib import Path
p=Path("scripts/build1269_layout_panel.py");s=p.read_text(encoding="utf-8")
a=s.index("point='<article");b=s.index('panel="""',a)
s=s[:a]+"""point='<section class="panel order-picking-panel" id="orderWavePlanning"'
assert point in s
"""+s[b:];p.write_text(s,encoding="utf-8")
