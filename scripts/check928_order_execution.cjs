const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements={},events={};let resolvers=[];
const element=id=>elements[id]??=({textContent:'',children:[],replaceChildren(){this.children=[];},append(x){this.children.push(x);}});
const window={wmsAdminAuth:{state:{user:{username:'a'}}},addEventListener:(t,f)=>events[t]=f};
const context={window,orderState:{selectedId:1},orderApiBase:()=> 'local',loadOrderDelivery:()=>{},
 document:{getElementById:element,createElement:()=>({children:[],append(x){this.children.push(x);}})},
 orderRequest:()=>new Promise(r=>resolvers.push(r))};
vm.createContext(context);vm.runInContext(fs.readFileSync('wiki-raw/wms_admin_ui_reference/order-execution.js','utf8'),context);
const response=label=>({execution_status:label,warehouse_id:1,lines:[{line_no:1,articul:'SKU',requested_quantity:'4',picked_quantity:'3',remaining_quantity:'1',base_uom:'EA',reason:'Pending1'}]});
(async()=>{
 const old=context.loadOrderExecution(1),fresh=context.loadOrderExecution(1);
 resolvers[1](response('PARTIAL'));await fresh;
 const current=element('orderExecutionStatus').textContent;
 resolvers[0](response('PICKED'));await old;
 assert.equal(element('orderExecutionStatus').textContent,current);
 assert.match(current,/склад 1/);assert.equal(element('orderExecutionRows').children.length,1);
 const third=context.loadOrderExecution(1);events['wms-admin-auth-ready']();resolvers[2](response('PICKED'));await third;
 assert.equal(element('orderExecutionRows').children.length,0);
 assert.equal(element('orderExecutionStatus').textContent,'Выберите заказ');
 console.log('928 PASS same-order older response ignored and auth clears old physical rows; no network/stock mutations');
})().catch(e=>{console.error(e);process.exitCode=1;});
