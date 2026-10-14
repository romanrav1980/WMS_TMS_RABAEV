from pathlib import Path
s=Path("scripts/browser1311_driver.mjs").read_text(encoding="utf-8");a=s.index(" await page.screenshot(")
s=s[:a]+"""
 await receipt.getByRole('button',{name:/B01.1238/}).first().click();
 await receipt.getByLabel('Идентификатор грузового места',{exact:true}).waitFor();
 await receipt.screenshot({path:'reports/retailcase/2026-10-13/screenshots/86-b03-store-progress.png'});
 console.log(JSON.stringify({text:await receipt.innerText(),selects:await receipt.locator('select').evaluateAll(xs=>xs.map(x=>({html:x.outerHTML,label:x.labels?.[0]?.textContent}))),errors}));
}finally{await browser.close();}
"""
Path("scripts/browser1314_inspect.mjs").write_text(s,encoding="utf-8")
s=Path("scripts/run1311_driver.py").read_text(encoding="utf-8").replace("browser1311_driver.mjs","browser1314_inspect.mjs")
Path("scripts/run1314_inspect.py").write_text(s,encoding="utf-8")
