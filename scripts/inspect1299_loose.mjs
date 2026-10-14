import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
const browser=await chromium.launch({headless:true});try{const page=await browser.newPage();await page.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1064');await page.locator('#adminLoginForm button[type=submit]').click();await page.waitForFunction(()=>document.querySelector('#cpTsdMethod').textContent.includes('Товар на развес'));
console.log(JSON.stringify(await page.evaluate(()=>({method:cpTsdEl('cpTsdMethod').textContent,disabled:cpTsdEl('cpTsdFactQty').disabled,outer:cpTsdEl('cpTsdFactQty').outerHTML,show:cpWeightedBox.show.toString().slice(0,620)}))));
}finally{await browser.close();}
