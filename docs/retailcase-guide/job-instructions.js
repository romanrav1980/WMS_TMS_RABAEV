/* The same job document is used on the role page and in the print collection. */
(() => {
'use strict';
const D=window.GUIDE;
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const role=id=>D.roles.find(r=>r.id===id);
const label=id=>role(id)?.title||D.roots[id]||id;
const link=id=>role(id)?`<a href="#role/${esc(id)}">${esc(label(id))}</a>`:esc(label(id));
const list=items=>`<ul>${items.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`;
const sections=[['general','Подчинение и необходимые знания'],['purpose','Результат работы'],['duties','Должностные обязанности'],['rights','Полномочия'],['responsibility','Ответственность'],['interaction','Работа в системе и взаимодействие'],['control','Что проверять'],['handover','Передача работы']];
function tabs(r,active){return `<nav class="role-tabs" aria-label="Документы должности">${[['instruction','Должностная инструкция'],['screens','Работа в системе'],['day','Рабочий день']].map(([id,t])=>`<a href="#role/${r.id}/${id}" ${active===id?'aria-current="page"':''}>${t}</a>`).join('')}</nav>`;}
function workLinks(r){return `<p class="job-work-links"><a href="#role/${r.id}/screens">Порядок работы в системе</a><a href="#role/${r.id}/day">Рабочий день</a><a href="#org/${r.id}">Место в структуре</a></p>`;}
function screenRows(r){return `<ul class="job-screen-links">${r.screens.map(id=>{const s=D.screens[id];return `<li><strong>${esc(s.title)}</strong><span><a href="#screen/${id}" title="Прочитать порядок работы: ${esc(s.title)}">Описание работы</a><a href="${esc(window.GuideScreenLinks.url(s.target))}" target="_blank" rel="noopener" title="Открыть ${esc(s.title)} в локальной системе; требуется вход">Открыть экран ↗</a></span></li>`;}).join('')}</ul><p class="job-meta">Экраны открываются в запущенной локальной системе. Для работы нужен вход и доступ к соответствующему складу, рейсу или магазину.</p>`;}
function render(r,full=false){
 const j=r.job,a=j.authority,subs=D.roles.filter(x=>x.reports_to===r.id);
 const heading=(n,body)=>`<section class="job-section" id="job-${r.id}-${sections[n][0]}"><h2>${n+1}. ${sections[n][1]}</h2>${body}</section>`;
 const kpi=r.id==='picker'?'<p><strong>Выработка:</strong> строки и коробки в час сборки; отдельно — строки и коробки в час смены. Строка засчитывается завершившему её сотруднику, коробки — каждому по собственным отборам. Зарегистрированные паузы исключаются из времени сборки и остаются во времени смены. Штучный отбор пересчитывается в коробки только при известном количестве штук в упаковке.</p>':(['driver','dispatcher','route_planner','store_receiver','store_director','logistics_director','transport_director'].includes(r.id)?'<p><strong>Доставка вовремя:</strong> машина прибыла в исходное плановое окно магазина. <strong>Доставлено полностью:</strong> магазин завершил приёмку без недостачи, отказа и повреждения. Способ проверки задаётся для поставки.</p>':'');
 return `${full?'':tabs(r,'instruction')}<article class="job-document" data-job="${r.id}"><div class="eyebrow">Должностная инструкция · ${esc(D.families[r.family]||r.family)}</div>${full?`<h2 class="job-title">${esc(r.title)}</h2>`:`<h1>${esc(r.title)}</h1>`}<p class="job-meta">RETAILCASE · 19.10.2026 · Проект для согласования</p><p class="lede">${esc(j.mission)}</p>${workLinks(r)}${full?'':`<nav class="job-toc" aria-label="Содержание инструкции">${sections.map(([id,t],n)=>`<a href="#role/${r.id}/instruction/${id}">${n+1}. ${t}</a>`).join('')}</nav>`}
 ${heading(0,`<p><strong>Подчиняется:</strong> ${link(r.reports_to)}.</p><p><strong>Подчинённые:</strong> ${subs.length?subs.map(s=>link(s.id)).join(' · '):'Нет.'}</p><p><strong>Должен знать:</strong> ${esc(j.know)}</p>`)}
 ${heading(1,`<p>${esc(j.output)}</p>`)}
 ${heading(2,`<ol class="job-duties">${j.duties.map(t=>`<li>${esc(t)}</li>`).join('')}</ol><p><a href="#role/${r.id}/screens">Как выполнять эти обязанности в системе →</a></p>`)}
 ${heading(3,`${list(a.rights)}<p>${esc(a.boundary)}</p>`)}
 ${heading(4,`<p>${esc(a.responsibility)}</p>`)}
 ${heading(5,`<p><strong>Взаимодействует:</strong> ${j.partners.map(link).join(' · ')}.</p><p><strong>Процессы:</strong> ${r.processes.map(id=>`<a href="#process/${id}">${esc(D.processes.find(p=>p.id===id).title)}</a>`).join(' · ')}.</p><p><a href="#role/${r.id}/screens">Порядок действий по процессам</a> · <a href="#role/${r.id}/day">Последовательность рабочего дня</a></p>${screenRows(r)}`)}
 ${heading(6,`${list(a.checks)}${kpi}`)}
 ${heading(7,`<p>${esc(a.handover)}</p><p><strong>Когда обращаться к руководителю:</strong> ${esc(j.risk)}</p>`)}
 <p class="source-ref">Основания: <a href="#sources/catalog">каталог должностей</a> · <a href="#sources/workplaces">рабочие места и процессы</a> · <a href="#sources/access">права доступа</a> · <a href="#rules">правила и KPI</a>.</p>${full?'':`<div class="actions"><a class="button secondary" href="#manual/roles">Все должностные инструкции</a></div>`}</article>`;
}
window.GuideJobs={render,tabs};
})();
