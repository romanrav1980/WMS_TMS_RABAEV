const {chromium}=require('../../../../admin/wms_admin_frontend/node_modules/playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{const browser=await chromium.launch({headless:true});try{
 const root=path.resolve(__dirname,'../../../..'),secret=JSON.parse(fs.readFileSync(path.join(root,'runtime/assembly-qa-secrets.json'),'utf8'));
 const checks=[],shots=[];
 for(const width of [360,390,1440]){
  const context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage(),errors=[],posts=[];
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(r.method()!=='GET'&&r.url().includes('/api/'))posts.push(r.method()+' '+new URL(r.url()).pathname);});
  const response=await page.goto('http://127.0.0.1:8088/assembly/?task_id=1032');assert.equal(response.status(),200);
  await page.locator('input[autocomplete="username"]').fill('ASM15.OP1032');await page.locator('input[type="password"]').fill(secret['ASM15.OP1032']);
  await page.getByRole('button',{name:'Войти',exact:true}).click();await page.getByText('Задание 1032',{exact:true}).waitFor();
  await page.locator('.asm-step').waitFor();
  assert.equal(await page.getByRole('button',{name:'Начать укладку',exact:true}).count(),0);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  const shot=path.join(__dirname,'native-assembly-'+width+'.png');await page.screenshot({path:shot,fullPage:true});shots.push(path.basename(shot));
  await page.getByRole('button',{name:'Справка',exact:true}).click();const help=page.getByRole('dialog',{name:'Справка'});
  await help.getByRole('heading',{name:'Сборка на весах: порядок работы'}).waitFor();
  await help.getByRole('button',{name:'Весы и шлюз: склад и магазин',exact:true}).click();await help.getByRole('heading',{name:'Весы и шлюз: склад и магазин'}).waitFor();
  await help.getByRole('button',{name:'Закрыть справку',exact:true}).click();await page.getByText('Задание 1032',{exact:true}).waitFor();
  assert.deepEqual(posts,[]);assert.deepEqual(errors,[]);checks.push('live_context_help_local_links_'+width);
  await context.close();
 }
 const report={status:'PASS',checks,shots,apiWrites:0,nativeContext:true,physicalDevice:false};fs.writeFileSync(path.join(__dirname,'production-native-ui.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
