from pathlib import Path
s=Path("scripts/browser1311_driver.mjs").read_text(encoding="utf-8")
s=s.replace(" await page.goto(",''' let started=false,submitted=null;const responses=[];
 await page.route('**/api/delivery/store-receipts/**',async route=>{
  const request=route.request(),url=new URL(request.url());
  if(request.method()==='POST'){
   if(url.pathname.endsWith('/unloading/start')){started=true;await route.fulfill({status:200,json:{operation_id:request.postDataJSON().operation_id,status:'STARTED'}});return;}
   if(url.pathname.endsWith('/confirm')){submitted=request.postDataJSON();await route.fulfill({status:200,json:{operation_id:submitted.operation_id,status:'ACCEPTED'}});return;}
   await route.abort();return;
  }
  const response=await route.fetch(),data=await response.json();
  if(url.pathname.endsWith('/preview')){data.already_received=false;data.unloading=started?{...data.unloading,status:'STARTED',receipt_operation_id:null}:null;}
  if(url.pathname.endsWith('/places')&&Array.isArray(data))for(const row of data){row.receipt_state=null;row.receipt_operation_id=null;}
  await route.fulfill({response,json:data});
 });
 await page.goto(''',1)
a=s.index(" await page.screenshot(")
s=s[:a]+"""
 await receipt.getByRole('button',{name:/B01.1238/}).first().click();
 await receipt.getByLabel('Идентификатор грузового места',{exact:true}).fill('B01.1238:c0c2a00c0b:1');
 await receipt.getByLabel('Грузовое место установлено перед камерами').check();
 await receipt.getByRole('button',{name:'Начать выгрузку',exact:true}).click();
 await receipt.getByLabel('Способ выгрузки').selectOption('PALLET');
 await receipt.getByLabel('Основание подтверждения',{exact:true}).fill('UI_ONLY_NO_DB_WRITE');
 await receipt.getByRole('button',{name:'Подтвердить полную приёмку',exact:true}).click();
 try{await receipt.getByText(/Приёмка подтверждена/).waitFor({timeout:4000});}catch{}
 console.log(JSON.stringify({kind:'synthetic API lifecycle; no writes',started,submitted,text:await receipt.innerText(),errors}));
 if(!submitted?.unloading)throw Error('Continuous UI did not send unloading receipt');
}finally{await browser.close();}
"""
Path("scripts/browser1327_handoff.mjs").write_text(s,encoding="utf-8")
s=Path("scripts/run1311_driver.py").read_text(encoding="utf-8").replace("browser1311_driver.mjs","browser1327_handoff.mjs")
Path("scripts/run1327_handoff.py").write_text(s,encoding="utf-8")
