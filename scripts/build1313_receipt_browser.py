from pathlib import Path
s=Path("scripts/browser1311_driver.mjs").read_text(encoding="utf-8")
s=s.replace("import {chromium}", "import fs from 'node:fs';\nimport {chromium}",1)
a=s.index(" await page.screenshot(");s=s[:a]+"""
 const facts=[];
 for (const suffix of [':1',':2']) {
  const place=receipt.getByRole('button',{name:new RegExp('B01.1238.*'+suffix+' ')});
  await place.click();
  await receipt.getByLabel('Идентификатор грузового места',{exact:true}).waitFor();
  const root='B01.1238:c0c2a00c0b'+suffix;
  await receipt.getByLabel('Идентификатор грузового места',{exact:true}).fill(root);
  await receipt.getByLabel('Грузовое место установлено перед камерами').check();
  if(await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).count()){
   const response=page.waitForResponse(r=>r.url().endsWith('/unloading/start')&&r.request().method()==='POST');
   await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).click();
   const r=await response;facts.push({kind:'start',status:r.status(),body:await r.json()});
   if(!r.ok())throw Error('Start failed: '+JSON.stringify(facts.at(-1)));
  }
  await receipt.getByLabel('Способ выгрузки',{exact:true}).selectOption('PALLET');
  await receipt.getByLabel('Основание подтверждения',{exact:true}).fill('OWN.DEV.B03.1313'+suffix);
  const response=page.waitForResponse(r=>r.url().endsWith('/store-receipts/confirm')&&r.request().method()==='POST');
  await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();
  const r=await response;facts.push({kind:'receipt',status:r.status(),body:await r.json(),request:r.request().postDataJSON()});
  fs.writeFileSync('tmp/result1313.json',JSON.stringify({facts,errors},null,2));
  if(!r.ok())throw Error('Receipt failed: '+JSON.stringify(facts.at(-1)));
  await receipt.getByText('Это место уже принято.',{exact:true}).waitFor();
 }
 await receipt.screenshot({path:'reports/retailcase/2026-10-13/screenshots/86-b03-store-received.png'});
 console.log(JSON.stringify({facts,errors}));
}finally{await browser.close();}
"""
Path("scripts/browser1313_receipt.mjs").write_text(s,encoding="utf-8")
s=Path("scripts/run1311_driver.py").read_text(encoding="utf-8").replace("browser1311_driver.mjs","browser1313_receipt.mjs").replace("timeout=75","timeout=100")
Path("scripts/run1313_receipt.py").write_text(s,encoding="utf-8")
