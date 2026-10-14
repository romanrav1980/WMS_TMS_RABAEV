from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/wave-execution-view.js');s=p.read_text(encoding='utf-8');anchor="        const composition=document.createElement('a');composition.className='wave-execution-action';"
s=s.replace(anchor,"""        if(window.wmsAdminAuth?.hasPermission('case_pick_view')){
          const picking=document.createElement('a');picking.className='wave-execution-action';
          picking.href='case-pick-tsd.html?case_task_id='+encodeURIComponent(item.id);
          picking.textContent='Открыть задание сборки';
          picking.title='Прочитать именно это задание, его строки и следующий этап; без автоматического взятия в работу';
          links.append(picking);
        }
"""+anchor);p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/short-recovery-monitor.js');s=p.read_text(encoding='utf-8').replace('let rows = [], loadedAt = 0;','let rows = [], loadedAt = 0, generation = 0;\n  const scope = () => JSON.stringify([window.wmsAdminAuth?.state?.apiBase, window.wmsAdminAuth?.state?.user?.username]);')
s=s.replace('      tr.append(actions); return tr;', '''      if (row.recovery_state === "READY" && /^[1-9]\\d*$/.test(String(row.case_pick_task_id))) {
        const link = document.createElement("a");
        link.href = "case-pick-tsd.html?case_task_id=" + encodeURIComponent(row.case_pick_task_id);
        link.textContent = " Продолжить сборку #" + row.case_pick_task_id;
        link.title = "Открыть исходное задание; допуск и текущий остаток проверяются сервером";
        actions.append(link);
      }
      tr.append(actions); return tr;''')
s=s.replace('  async function load() {\n', '  async function load() {\n    const token=++generation, identity=scope();\n')
s=s.replace('      rows = await response.json(); loadedAt = Date.now(); render();', '      const result = await response.json();\n      if(token!==generation||identity!==scope())return;\n      rows=result; loadedAt = Date.now(); render();')
s=s.replace('    } catch (error) { panel.querySelector("p").textContent = error.message; }','    } catch (error) { if(token===generation&&identity===scope())panel.querySelector("p").textContent = error.message; }')
s=s.replace('window.addEventListener("wms-admin-auth-ready", load);','window.addEventListener("wms-admin-auth-ready", () => { generation++; rows=[]; loadedAt=0; panel.querySelector("tbody").replaceChildren(); panel.querySelector("p").textContent=""; void load(); });')
p.write_text(s,encoding='utf-8')
