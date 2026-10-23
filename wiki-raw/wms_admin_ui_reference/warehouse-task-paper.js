/* Frozen paper version uses the existing task command and recovery. */
(() => {
  let binding = null, checkedIdentity = '', epoch = 0;
  const panel = document.createElement('section');
  panel.className = 'warehouse-task-paper'; panel.setAttribute('aria-label', 'Факт по бумажному заданию');
  panel.innerHTML = '<h3>Факт по бумажному заданию</h3><form><label>Штрихкод с бланка<input autocomplete="off" spellcheck="false" aria-label="Штрихкод с бланка" title="Считайте полный штрихкод задания; Enter проверяет версию"></label><button type="submit" title="Проверить версию бланка перед вводом факта" data-help-id="warehouse-task.paper.check">Проверить бланк</button></form><p role="status"></p><a href="/help/warehouse-task-paper.html" target="_blank" rel="noopener" title="Открыть порядок подтверждения работы по бумаге">Инструкция</a>';
  document.getElementById('warehouseTaskDetail').prepend(panel);
  const input = panel.querySelector('input'), message = panel.querySelector('p');
  const identity = () => JSON.stringify([warehouseTaskApiBase(), window.wmsAdminAuth?.state?.user?.username]);
  function parse(value) {
    const m = /^WTASK:([1-9]\d*):([A-F0-9]{64})$/i.exec(value.trim());
    if (!m || !Number.isSafeInteger(Number(m[1]))) throw Error('Считайте полный штрихкод бланка складского задания.');
    return { task: Number(m[1]), signature: m[2].toUpperCase() };
  }
  function render(task) {
    if (!input.value.trim()) return;
    for (const id of ['warehouseTaskAssign', 'warehouseTaskStart', 'warehouseTaskCancel']) {
      const button = warehouseTaskEl(id); button.disabled = true;
      button.title = 'При подтверждении бумажного факта состояние не меняется отдельной командой';
    }
    const button = warehouseTaskEl('warehouseTaskComplete');
    if (!binding || task?.task_id !== binding.task || checkedIdentity !== identity()) {
      button.disabled = true; button.title = 'Проверьте бланк выбранного задания';
    }
    warehouseTaskEl('warehouseTaskEditAssignee').disabled = true;
  }
  async function check() {
    const mine = ++epoch, session = identity(); checkedIdentity = ''; binding = null;
    try {
      const original = parse(input.value), task = warehouseTaskState.selectedTask;
      if (task?.task_id !== original.task) throw Error('Откройте задание №' + original.task + ', указанное на бланке.');
      message.textContent = 'Проверка бланка…'; render(task);
      const value = await warehouseTaskFetch('/api/warehouse-tasks/' + original.task + '/paper?expected_signature=' + original.signature);
      if (mine !== epoch || session !== identity() || warehouseTaskState.selectedTask?.task_id !== original.task) return;
      if (value.task?.task_id !== original.task || value.task?.task_signature !== original.signature)
        throw Error('Сервер не подтвердил версию исходного бланка.');
      binding = original; checkedIdentity = session;
      message.textContent = 'Бланк проверен. Введите фактическое количество и физические сканы в карточке ниже.';
    } catch (error) {
      if (mine !== epoch || session !== identity()) return;
      message.textContent = error.status === 409 ? 'Бланк устарел. Сверьте выполненную работу с текущим заданием; не переносите факт на новый бланк без проверки.' :
        [401, 403, 404].includes(error.status) ? 'Задание недоступно. Проверьте вход и доступ к складу.' : error.message;
    } finally {
      if (mine === epoch && session === identity()) window.warehouseTaskActions.render(warehouseTaskState.selectedTask);
    }
  }
  input.addEventListener('input', () => {
    epoch++; binding = null; checkedIdentity = ''; message.textContent = '';
    window.warehouseTaskActions.render(warehouseTaskState.selectedTask);
  });
  panel.querySelector('form').addEventListener('submit', event => { event.preventDefault(); void check(); });
  window.addEventListener('warehouse-task-selected', () => {
    epoch++; binding = null; checkedIdentity = '';
    message.textContent = input.value ? 'Проверьте бланк перед подтверждением факта.' : '';
    render(warehouseTaskState.selectedTask);
  });
  window.addEventListener('wms-admin-auth-ready', () => {
    epoch++; binding = null; checkedIdentity = ''; render(warehouseTaskState.selectedTask);
  });
  input.value = new URLSearchParams(location.search).get('paper_reference') || '';
  const linked = new URLSearchParams(location.search).get('task_id');
  let direct = null;
  try { const parsed = parse(input.value); if (String(parsed.task) === linked) direct = parsed.task; } catch {}
  if (direct) {
    document.body.classList.add('warehouse-paper-focus');
    const queueLink = document.createElement('a'); queueLink.href = 'warehouse-tasks.html';
    queueLink.textContent = 'Открыть общую очередь'; queueLink.title = 'Открыть полный список заданий в отдельной вкладке';
    queueLink.target = '_blank'; queueLink.rel = 'noopener'; panel.append(queueLink);
  }
  window.warehouseTaskPaper = {
    directTaskId: () => direct,
    render,
    guard(task, action, payload) {
      if (!input.value.trim()) return;
      if (action !== 'complete') throw Error('Для бумажного факта используйте подтверждение выполнения.');
      const original = parse(input.value);
      if (!binding || original.task !== task.task_id || binding.task !== original.task ||
          binding.signature !== original.signature || checkedIdentity !== identity())
        throw Error('Проверьте бланк выбранного задания перед подтверждением факта.');
      payload.expected_task_signature = original.signature;
    }
  };
})();