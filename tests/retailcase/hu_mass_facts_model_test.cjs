// Source provenance checks only; no Python quality projection, API, native or hardware claim.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'../..'),ts=require(path.join(root,'admin/wms_admin_frontend/node_modules/typescript')),exportsModel={};
vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(root,'admin/wms_admin_frontend/src/features/inventory/huMassFacts.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText,{exports:exportsModel});
const {huMassFacts:f,massText}=exportsModel,base=()=>({root:'GENERIC',nodes:[{uid:'GENERIC',kind:'CONTAINER',tare_weight_kg:'1'}],unknown_weight_leaves:0,unknown_tare_containers:0,gross_weight_kg:'11'});
let count=0;function check(name,run){run();count++;console.log('PASS',name);}
check('exact decimal strings and explicit zero retained',()=>{assert.equal(massText('9007199254740993.000000001'),'9007199254740993.000000001 кг');assert.equal(massText('0'),'0 кг');});
check('negative NaN scientific and missing values remain unknown',()=>{for(const x of [null,undefined,'NaN','Infinity','-1','1e3','',4])assert.equal(massText(x),null);});
check('empty source has reasons, not implicit zero',()=>{const n={uid:'GENERIC',kind:'CONTAINER'};const r=f(n,{...base(),nodes:[n]});assert.equal(r.facts.length,0);assert.equal(r.legacyTotal,null);assert.ok(r.missing.length>=2);});
check('CASE QC stays distinct source, never approved outer measurement',()=>{const r=f({uid:'CASE:1',kind:'CASE',gross_weight_kg:'10',scale_qc:{}},base());assert.equal(r.facts[0].label,'GROSS из контроля CASE');assert.match(r.facts[0].basis,/Не отгрузочное/);assert.equal(r.legacyTotal,null);});
check('bare gross without QC source is not promoted',()=>assert.equal(f({uid:'CASE:1',kind:'CASE',gross_weight_kg:'10'},base()).facts.length,0));
check('stock master weight explicitly remains accounting data',()=>{const r=f({uid:'LOT',kind:'STOCK',weight_kg:'8'},base());assert.match(r.facts[0].basis,/не измерение/);assert.equal(r.facts[0].value,'8 кг');});
check('non-STOCK weight field not invented into stock fact',()=>assert.equal(f({uid:'BOX',kind:'CONTAINER',weight_kg:'8'},base()).facts.length,0));
check('zero own tare is known field but not weight receipt',()=>{const r=f({uid:'BOX',kind:'CONTAINER',tare_weight_kg:'0'},base());assert.equal(r.facts[0].value,'0 кг');assert.match(r.facts[0].basis,/не новая квитанция/);});
check('complete legacy number remains reference-only field',()=>{const s=base();assert.equal(f(s.nodes[0],s).legacyTotal,'11 кг');});
check('missing container tare hides even numeric legacy total',()=>{const s=base();s.nodes.push({uid:'BOX',kind:'CONTAINER'});assert.equal(f(s.nodes[0],s).legacyTotal,null);});
check('all known missing counters or absent coverage hide legacy number',()=>{for(const patch of [{unknown_weight_leaves:1},{unknown_tare_containers:1},{unknown_weight_leaves:undefined},{unknown_tare_containers:undefined}]){const s={...base(),...patch};assert.equal(f(s.nodes[0],s).legacyTotal,null);}});
check('historical composition cannot present current legacy aggregate',()=>{const s={...base(),historical_composition:true};assert.equal(f(s.nodes[0],s).legacyTotal,null);});
check('stale placement retained as explicit historical source',()=>{const s={...base(),placement:{gross_weight_kg:'9',version_matches:false}};const p=f(s.nodes[0],s).facts.find(x=>x.label.includes('размещения'));assert.equal(p.value,'9 кг');assert.match(p.basis,/историческая/);});
check('placement is not copied into unrelated child',()=>{const s={...base(),placement:{gross_weight_kg:'9',version_matches:true}};assert.ok(!f({uid:'CHILD',kind:'CONTAINER'},s).facts.some(x=>x.label.includes('размещения')));});
console.log(count+' HU mass source-model checks PASS');
