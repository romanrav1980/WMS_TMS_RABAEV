/* Export the maintained role and process text for reading directly on GitHub. */
const fs=require('node:fs');
const path=require('node:path');
global.window={};
for(const file of ['data.js','content.js','job-profiles.js','job-authority.js'])require('./'+file);
const D=window.GUIDE,site='https://romanrav1980.github.io/WMS_TMS_RABAEV/';
const role=id=>D.roles.find(r=>r.id===id),name=id=>role(id)?.title||D.roots[id]||id;
const roleLink=id=>role(id)?`[${name(id)}](#role-${id})`:name(id);
const bullets=items=>items.map(t=>'- '+t).join('\n');
const screenURL=t=>t.startsWith('raw:')?'http://127.0.0.1:8088/wms-admin/'+t.slice(4):t.startsWith('store:')?'http://127.0.0.1:3010'+t.slice(6):'http://127.0.0.1:3000/?'+(t.startsWith('workspace=')?'page=workspace&':'')+t;
let out=`# Описание работы в системе\n\n[Открыть сайт с иллюстрациями](${site}) · [Выбрать должность](#должностные-инструкции) · [Перейти к процессам](#сквозной-процесс)\n\nВыберите свою должность, прочитайте обязанности и откройте порядок работы или нужный экран. Руководитель согласует инструкции и полномочия перед их вводом в компании.\n\nДля выполнения операций установите систему и войдите под своей учётной записью. Ссылки «Открыть экран» ведут в локально установленное приложение.\n\n## Сквозной процесс\n\n`;
for(const p of D.processes){
 out+=`<a id="process-${p.id}"></a>\n\n### ${p.title}\n\n${p.purpose}\n\n**Ответственный:** ${roleLink(p.owner)}.\n\n**Получить:** ${p.input}\n\n**Порядок работы:**\n\n`;
 out+=p.steps.map((s,i)=>`${i+1}. ${roleLink(s.role)}: ${s.action} [Описание экрана](${site}#screen/${s.screen}). Результат: ${s.result}`).join('\n')+'\n\n';
 out+=`**Проверить перед передачей:**\n\n${bullets(p.gates)}\n\n**При остановке:** ${p.exception}\n\n**Передать:** ${p.handover}\n\n**Результат:** ${p.output}\n\n`;
}
out+='## Должностные инструкции\n\n'+D.roles.map(r=>'- '+roleLink(r.id)).join('\n')+'\n\n';
for(const r of D.roles){
 const j=r.job,a=j.authority,subs=D.roles.filter(x=>x.reports_to===r.id);
 out+=`<a id="role-${r.id}"></a>\n\n### ${r.title}\n\n${j.mission}\n\n[Порядок работы в системе](${site}#role/${r.id}/screens) · [Рабочий день](${site}#role/${r.id}/day) · [Место в структуре](${site}#org/${r.id})\n\n**Подчиняется:** ${roleLink(r.reports_to)}.\n\n**Подчинённые:** ${subs.length?subs.map(s=>roleLink(s.id)).join(', '):'нет'}.\n\n**Должен знать:** ${j.know}\n\n**Результат работы:** ${j.output}\n\n**Обязанности:**\n\n${j.duties.map((t,i)=>(i+1)+'. '+t).join('\n')}\n\n**Полномочия:**\n\n${bullets(a.rights)}\n\n${a.boundary}\n\n**Ответственность:** ${a.responsibility}\n\n**Взаимодействует:** ${j.partners.map(roleLink).join(', ')}.\n\n**Что проверять:**\n\n${bullets(a.checks)}\n\n**Передача работы:** ${a.handover}\n\n**Когда обращаться к руководителю:** ${j.risk}\n\n**Экраны:**\n\n`;
 out+=r.screens.map(id=>{const s=D.screens[id];return `- ${s.title}: [описание работы](${site}#screen/${id}) · [открыть экран](${screenURL(s.target)})`;}).join('\n')+'\n\n';
}
out+=`## Согласованные показатели\n\nКомплектовщику показываются строки и коробки в час сборки, отдельно — строки и коробки в час смены. Строка засчитывается завершившему её сотруднику, коробки — каждому по собственным отборам. Зарегистрированные паузы исключаются из времени сборки и остаются во времени смены.\n\nДоставка считается своевременной, если машина прибыла в исходное окно магазина. Полнота подтверждается завершённой приёмкой магазина без недостачи, отказа и повреждений по назначенному способу проверки.\n\n[Открыть учебный пример от планирования до приёмки](${site}#example/0).\n`;
fs.writeFileSync(path.join(__dirname,'WORK-IN-SYSTEM.md'),out,'utf8');
console.log(`Exported ${D.roles.length} roles and ${D.processes.length} processes`);
