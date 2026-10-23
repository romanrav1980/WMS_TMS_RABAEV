// Real read of the accepted factory receipt; no receipt or stock write.
const fs=require('fs'),assert=require('assert');const {chromium}=require('../../admin/wms_admin_frontend/node_modules/playwright');
const out='runtime/test-evidence/tradecase/2026-10-23/T03',s=JSON.parse(fs.readFileSync(out+'/factory-hierarchy-225687965.json'));
const pass=fs.readFileSync('AGENTS.md','utf8').match(/PASS=(\S+?)[`,)\s]/)[1],report={status:'FAIL',checks:[],writes:[],errors:[]};
(async()=>{const b=await chromium.launch();try{for(const width of [1440,390]){
 const c=await b.newContext({viewport:{width,height:900}});await c.addInitScript(basic=>sessionStorage.setItem('wmsAdminAuth',JSON.stringify({apiBase:'http://127.0.0.1:8088',basic})),'Basic '+Buffer.from('admin:'+pass).toString('base64'));
 const p=await c.newPage();p.on('pageerror',e=>report.errors.push(String(e)));await p.route('**/api/**',r=>{const m=r.request().method();if(m!=='GET'&&m!=='OPTIONS'){report.writes.push(m+' '+r.request().url());return r.abort()}return r.continue()});
 await p.goto(`http://127.0.0.1:8088/wms-admin/receiving.html?warehouse_id=${s.warehouse_id}&supply_order_id=${s.supply_order}`);
 await p.waitForFunction(()=>document.querySelector('#receiptLines')?.innerText.includes('10'),null,{timeout:30000});
 await p.locator('#receiptContext[data-ready=true]').waitFor({timeout:30000});
 const text=await p.locator('#receiptLines').innerText();assert(text.includes(s.fixture.article),text);
 assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.screenshot({path:out+`/factory-received-${width}.png`,fullPage:false});report.checks.push({width,acceptedLine:text,pageFits:true});await c.close();
}assert.deepStrictEqual(report.writes,[]);assert.deepStrictEqual(report.errors,[]);report.status='PASS'}finally{fs.writeFileSync(out+'/factory-received-ui.json',JSON.stringify(report,null,2));await b.close()}console.log(report.status)})().catch(e=>{console.error(e);process.exit(1)});
