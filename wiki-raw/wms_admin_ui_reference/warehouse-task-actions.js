/* Presentation of existing task transitions. Oracle remains the command authority. */
(() => {
  let busy = false;
  const identity = () => JSON.stringify([
    warehouseTaskApiBase(), window.wmsAdminAuth?.state?.user?.username
  ]);
  function render(task) {
    const status = task?.status;
    const assignable = ['PLANNED', 'ASSIGNED'].includes(status);
    const terminal = !task || ['DONE', 'CANCELLED'].includes(status);
    const execute = warehouseTaskCan('warehouse_task_execute');
    const states = {
      warehouseTaskAssign: [assignable && execute, 'Назначить указанному исполнителю; начатое задание переназначить нельзя'],
      warehouseTaskStart: [assignable && execute, 'Начать исполнение под текущим пользователем после серверной проверки допуска'],
      warehouseTaskComplete: [!terminal && execute, 'Подтвердить физические сканы и фактическое количество серверу'],
      warehouseTaskCancel: [!terminal && warehouseTaskCan('warehouse_task_edit'), 'Отменить задание с указанной причиной после серверной проверки']
    };
    for (const [id, [allowed, title]] of Object.entries(states)) {
      const button = warehouseTaskEl(id);
      button.disabled = busy || !allowed;
      button.title = busy ? 'Дождитесь ответа и перечитывания задания' : title;
    }
    warehouseTaskEl('warehouseTaskEditAssignee').disabled = busy || !assignable || !execute;
    warehouseTaskEl('warehouseTaskAssign').textContent = status === 'ASSIGNED' ? 'Переназначить' : 'Назначить';
    const hint = !task ? 'Выберите задание.' : busy ? 'Команда выполняется. Ожидаем текущее состояние сервера.' :
      status === 'DONE' ? 'Факт подтверждён. Продолжение частичного задания — в цепочке ниже.' :
      status === 'CANCELLED' ? 'Задание отменено. Отмена не является подтверждением перемещения.' :
      status === 'IN_PROGRESS' ? 'Исполнение начато: ' + (task.assigned_to || 'исполнитель не указан') +
        '. Переназначение начатого задания недоступно. Подтвердите фактически выполненный объём.' :
      assignable ? 'Исполнитель: ' + (task.assigned_to || 'не назначен') +
        '. Можно назначить сотрудника до начала. «Начать» действует от имени вошедшего пользователя.' :
      'Проверьте причину в поле «Ошибка». Доступность проведения проверит сервер.';
    warehouseTaskEl('warehouseTaskActionHint').textContent = hint;
  }
  async function send(task, action, payload) {
    if (busy) throw new Error('Дождитесь результата предыдущего действия.');
    const session = identity();
    busy = true; render(task);
    try {
      await warehouseTaskFetch(`/api/warehouse-tasks/${task.task_id}/${action}`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
      });
      if (session !== identity()) return;
      // Preserve a directly opened task even when assignment changes its queue filter.
      if (warehouseTaskState.selectedTask?.task_id === task.task_id)
        warehouseTaskState.initialTaskId = task.task_id;
      await loadWarehouseTasks();
    } catch (error) {
      if (session !== identity()) return;
      throw new Error(error.message + ' Перечитайте карточку перед повторным действием.');
    } finally {
      busy = false; render(warehouseTaskState.selectedTask);
    }
  }
  window.warehouseTaskActions = {render, send};
})();
