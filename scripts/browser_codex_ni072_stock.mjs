import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const out='reports/retailcase/2026-10-13/codex/NI072/',fixture=JSON.parse(fs.readFileSync(out+'synthetic_stock_keys.json','utf8'));
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),writes=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.method()!=='GET'&&r.url().includes('/api/'))writes.push(r.url());});
 await page.goto('http://127.0.0.1:8088/wms-admin/day-reconciliation.html?warehouse_id=9807&day=2026-10-14');await page.locator('#adminLoginForm button[type=submit]').click();await page.locator('#drResult').waitFor({state:'visible'});
 await page.evaluate(f=>{const host=document.createElement('section');host.id='stockFixture';host.style='background:white;color:#111;padding:24px';const title=document.createElement('h2');title.textContent='Проверка отображения: синтетический Oracle CTE, запас не изменён';host.append(title);for(const[key,docs]of Object.entries(f.documents)){const card=document.createElement('article');card.dataset.search='';const label=document.createElement('h3');label.textContent=key;card.append(label);window.dayReconDocuments.append(card,docs,f.counts[key],9807);card.querySelector('details').open=true;host.append(card);}document.body.prepend(host);},fixture);
 const fixturePanel=page.locator('#stockFixture');if(await fixturePanel.locator('li').count()!==40)throw Error('Missing rows');if(await fixturePanel.locator('a').count())throw Error('Invented link');await fixturePanel.screenshot({path:out+'stock-keys-synthetic.png'});
 if(writes.length||errors.length)throw Error(JSON.stringify({writes,errors}));fs.writeFileSync(out+'browser_stock_keys.json',JSON.stringify({synthetic:true,rows:40,writes,errors},null,2));console.log(JSON.stringify({rows:40,writes,errors}));
}finally{await browser.close();}