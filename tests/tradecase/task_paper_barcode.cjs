// Decode generated vector bars with the independently installed ZXing Code128 reader; no scanner hardware claim.
const assert=require('assert'),cp=require('child_process'),path=require('path');
const {Code128Reader,BitArray}=require('../../terminal/wms_terminal_web/node_modules/@zxing/library');
const root=path.resolve(__dirname,'../..');
const python='import json; from app.modules.inventory.domain.task_paper import task_barcode; print(json.dumps([task_barcode(t,s)for t,s in [(1,"0"*64),(1231,"F"*64),(9007199254740991,"0123ABCD"*8)]]))';
const vectors=JSON.parse(cp.execFileSync('python',['-c',python],{cwd:root,env:{...process.env,PYTHONPATH:path.join(root,'api/wms_api_server')}}).toString());
for(const [reference,svg]of vectors){
 const width=Number(svg.match(/viewBox="0 0 (\d+) /)[1]),row=new BitArray(width);
 for(const rect of svg.matchAll(/<rect x="(\d+)" y="0" width="(\d+)" height="65"\/>/g))
  for(let x=Number(rect[1]);x<Number(rect[1])+Number(rect[2]);x++)row.set(x);
 assert.equal(new Code128Reader().decodeRow(0,row,new Map()).getText(),reference);
}
console.log('Independent ZXing Code128 decode: PASS '+vectors.length);
