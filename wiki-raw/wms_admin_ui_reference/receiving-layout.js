(() => {
  const el = id => document.getElementById(id);
  let order = null, line = null, epoch = 0;
  const message = text => {el('receiptLayoutMessage').textContent = text;};
  window.addEventListener('wms-receipt-selected', event => {
    order = event.detail; line = null; epoch++; el('receiptLayoutPreview').disabled=false;
    el('receiptLayoutRows').replaceChildren(); message('Выберите строку товара.');
  });
  window.addEventListener('wms-receipt-line-selected', event => {
    line = event.detail; epoch++; el('receiptLayoutPreview').disabled=false;
    el('receiptLayoutCount').value = ''; el('receiptLayoutAmounts').value = '';
    el('receiptLayoutStep').value = ''; el('receiptLayoutRows').replaceChildren();
    message(`Строка ${line.line_number}: осталось ${line.remaining_qty} ${line.base_uom}.`);
  });
  window.addEventListener('wms-admin-auth-ready',()=>{order=null;line=null;epoch++;el('receiptLayoutRows').replaceChildren();el('receiptLayoutPreview').disabled=false;message('Выберите заказ и строку.');});
  window.addEventListener('wms-receipt-selection-reset',()=>{order=null;line=null;epoch++;el('receiptLayoutRows').replaceChildren();el('receiptLayoutPreview').disabled=false;message('Выберите заказ и строку.');});
  async function preview() {
    if (!order || !line) {message('Выберите заказ и товар.'); return;}
    const token = ++epoch, currentOrder = order, currentLine = line;
    const body = {line_number: currentLine.line_number};
    const manual = el('receiptLayoutAmounts').value.trim();
    const count = el('receiptLayoutCount').value.trim(), step = el('receiptLayoutStep').value.trim();
    if (manual) body.quantities = manual.split(/[;\r\n]+/).map(x => x.trim()).filter(Boolean);
    else if (count) body.pallet_count = Number(count);
    if (step) body.quantity_step = step;
    el('receiptLayoutPreview').disabled = true;
    try {
      const base = (window.wmsAdminAuth.state.apiBase || 'http://127.0.0.1:8088').replace(/\/$/, '');
      const r = await fetch(base + '/api/integrations/sap/supply-orders/' + encodeURIComponent(currentOrder.order_id) + '/pallet-plan', {
        method: 'POST', headers: window.wmsAdminAuth.headers({'Content-Type': 'application/json'}), body: JSON.stringify(body),
      });
      const result = await r.json();
      if (token !== epoch) return;
      if (!r.ok) throw new Error(typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail));
      el('receiptLayoutRows').replaceChildren(...result.quantities.map((quantity, index) => {
        const row = document.createElement('tr');
        for (const value of [index + 1, quantity, result.base_uom, result.above_norm_pallets.includes(index + 1) ? 'Выше нормы укладки' : '']) {
          const td = document.createElement('td'); td.textContent = String(value); row.appendChild(td);
        }
        const td=document.createElement('td'),button=document.createElement('button');
        button.type='button';button.textContent='Использовать количество';
        button.addEventListener('click',()=>window.dispatchEvent(new CustomEvent('wms-receipt-layout-quantity',{
          detail:{order_id:result.order_id,line_number:result.line_number,quantity,source_signature:result.source_signature},
        })));
        td.appendChild(button);row.appendChild(td);return row;
      }));
      message(`Предложено ${result.pallet_count} паллет, количество ${result.planned_quantity}; не распределено ${result.unplanned_quantity}.
        Это предложение: этикетки, товар и задания ещё не созданы. Фактическая приёмка — отдельно по каждой паллете.`);
    } catch (e) {if (token === epoch) message(e.message);}
    finally {if (token === epoch) el('receiptLayoutPreview').disabled = false;}
  }
  el('receiptLayoutPreview').addEventListener('click', preview);
})();
