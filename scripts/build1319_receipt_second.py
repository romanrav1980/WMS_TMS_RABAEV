from pathlib import Path
s=Path("scripts/browser1313_receipt.mjs").read_text(encoding="utf-8").replace("const facts=[];","const facts=JSON.parse(fs.readFileSync('tmp/result1313.json','utf8')).facts;").replace("for (const suffix of [':1',':2'])","for (const suffix of [':2'])").replace("await receipt.getByText('Это место уже принято.',{exact:true}).waitFor();","await receipt.getByText(/Приёмка подтверждена/).waitFor();")
s=s.replace(" await receipt.screenshot("," await receipt.getByRole('button',{name:/B01.1238.*:2 /}).click();\n await receipt.getByText('Это место уже принято.',{exact:true}).waitFor();\n await receipt.screenshot(")
Path("scripts/browser1319_receipt_second.mjs").write_text(s,encoding="utf-8")
s=Path("scripts/run1313_receipt.py").read_text(encoding="utf-8").replace("browser1313_receipt.mjs","browser1319_receipt_second.mjs")
Path("scripts/run1319_receipt_second.py").write_text(s,encoding="utf-8")
