const { chromium } = require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const path = require('path');
const fs = require('fs');
(async () => {
 const target = path.resolve('reports/retailcase/2026-10-14/access-knowledge');
 const browser = await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1365,height:900}});
  const basic=(process.env.VITE_ADMIN_BASIC_AUTH || fs.readFileSync('front.bat','utf8').match(/VITE_ADMIN_BASIC_AUTH=([^"\r\n]+)/)[1]);
  const offset=basic.indexOf(':');
  const login=async()=>{
    await page.getByLabel('Пользователь',{exact:true}).fill(basic.slice(0,offset));
    await page.getByLabel('Пароль',{exact:true}).fill(basic.slice(offset+1));
    await page.getByRole('button',{name:'Войти',exact:true}).click();
    await page.getByRole('button',{name:'? Справка',exact:true}).waitFor();
  };
  const errors=[];page.on('pageerror', e=>errors.push(String(e)));
  await page.goto('http://127.0.0.1:3000/?page=transport');
  await login();
  await page.getByRole('button',{name:'? Справка',exact:true}).click();
  await page.getByRole('heading',{name:'Как пользоваться встроенной справкой',exact:true}).waitFor();
  const dialog=page.getByRole('dialog');
  if(await dialog.locator('button:not([data-help-id])').count())throw Error('Unexplained help button');
  await page.screenshot({path:path.join(target,'desktop.png')});
  await page.getByLabel('Найти инструкцию').fill('потерян');
  await dialog.getByRole('button',{name:'Если ответ на команду потерян',exact:true}).click();
  await dialog.getByRole('heading',{name:'Если ответ на команду потерян',exact:true}).waitFor();
  if(!page.url().includes('help=operation-recovery'))throw Error('Missing local article deep link');
  await page.reload();
  await login();
  await dialog.getByRole('heading',{name:'Если ответ на команду потерян',exact:true}).waitFor();
  await page.setViewportSize({width:375,height:812});
  await page.screenshot({path:path.join(target,'mobile.png')});
  const overflow=await dialog.evaluate(node=>node.scrollWidth>node.clientWidth);
  if(overflow)throw Error('Mobile help overflow');
  await page.keyboard.press('Escape');
  if(await dialog.isVisible())throw Error('Escape did not close help');
  if(!page.url().includes('page=transport')||page.url().includes('help='))throw Error('Workplace not preserved');
  await page.keyboard.press('F1');
  await dialog.getByRole('heading',{name:'Если ответ на команду потерян',exact:true}).waitFor();
  await page.route('**/api/help/**',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'test unavailable'})}));
  await dialog.getByRole('button',{name:'Роли и доступ',exact:true}).click();
  await dialog.getByRole('alert').waitFor();
  await page.unroute('**/api/help/**');
  await dialog.getByRole('button',{name:'Повторить',exact:true}).click();
  await dialog.getByRole('heading',{name:'Роли и области ответственности',exact:true}).waitFor();
  const result={desktop:true,mobile:true,search:true,related:true,deepLinkReload:true,escape:true,f1:true,workplacePreserved:true,retry:true,mobileOverflow:overflow,pageErrors:errors};
  fs.writeFileSync(path.join(target,'ui-report.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
  if(errors.length)throw Error('Unexpected browser error');
 }finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});


