from pathlib import Path
p=Path("scripts/browser1313_receipt.mjs");s=p.read_text(encoding="utf-8").replace("getByLabel('Способ выгрузки',{exact:true})","getByLabel('Способ выгрузки')");p.write_text(s,encoding="utf-8")
