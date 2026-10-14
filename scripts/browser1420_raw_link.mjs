import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';
const b=await chromium.launch({headless:true});try{
 const p=await b.newPage();await p.goto('http://127.0.0.1:3000');
 const href=await p.evaluate(async()=>{const {lossRegistryUrl}=await import('/src/features/inventory/TareLossCase.tsx');return lossRegistryUrl({operation_id:'TARE:4530d7c2-19ea-4281-9ed2-9a7fe499b965',owner_ware_id:9807});});
 if(!href.includes(':8088/wms-admin/tare-loss.html?'))throw Error(href);
 const response=await p.goto(href);if(response.status()!==200)throw Error('Raw link unavailable');
 console.log(JSON.stringify({href,status:response.status(),rawTitle:await p.title(),mutations:0}));
}finally{await b.close();}
