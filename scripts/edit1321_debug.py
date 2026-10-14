from pathlib import Path
p=Path("scripts/browser1319_receipt_second.mjs");s=p.read_text(encoding="utf-8")
s=s.replace("await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();","await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();\n  console.log(JSON.stringify({afterClick:await receipt.innerText(),errors}));")
s=s.replace("}finally{await browser.close();}","}finally{await browser.close();}")
p.write_text(s,encoding="utf-8")
