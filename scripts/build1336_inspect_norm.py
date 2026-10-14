from pathlib import Path
s=Path("scripts/browser1334_forecast.mjs").read_text(encoding="utf-8")
a=s.index(" await page.locator('#wfNormLoad').click();")
s=s[:a]+"""
 const response=page.waitForResponse(r=>r.url().includes('/api/resources/workload/warehouses/'));
 await page.locator('#wfNormLoad').click();const r=await response;console.log(JSON.stringify({status:r.status(),body:await r.json()}));
 await page.waitForFunction(()=>!document.querySelector('#wfNormLoad').disabled);
 console.log(JSON.stringify({message:await page.locator('#wfNormMessage').innerText(),options:await page.locator('#wfNormSites').innerHTML(),errors}));
}finally{await browser.close();}
"""
Path("scripts/browser1336_inspect_norm.mjs").write_text(s,encoding="utf-8")
