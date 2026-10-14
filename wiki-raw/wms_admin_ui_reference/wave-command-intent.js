(() => {
  function create(prefix,valid,options={}) {
    function scope() {
      const auth=window.wmsAdminAuth;
      if(!auth?.state?.user?.username)throw new Error('Войдите в систему.');
      return options.storageKey ? options.storageKey() : prefix+auth.state.apiBase+':'+auth.state.user.username;
    }
    function read() {
      const storageKey=scope(),raw=localStorage.getItem(storageKey);
      if(raw===null)return{storageKey,raw:null,value:null};
      try{const value=JSON.parse(raw);if(!valid(value))throw new Error('INVALID');return{storageKey,raw,value};}
      catch{return{storageKey,raw,value:null,damaged:true};}
    }
    function save(value) {
      if(!valid(value))throw new Error(options.invalid||'Некорректное решение по волне.');
      const previous=read(),raw=JSON.stringify(value);
      if(previous.damaged||(previous.raw!==null&&previous.raw!==raw))
        throw new Error('Сначала восстановите или повторите сохранённое решение.');
      localStorage.setItem(previous.storageKey,raw);
      if(localStorage.getItem(previous.storageKey)!==raw)throw new Error('Решение не сохранено.');
      return{storageKey:previous.storageKey,raw,value};
    }
    function settle(record) {
      if(record.storageKey!==scope()||localStorage.getItem(record.storageKey)!==record.raw)
        throw new Error('Контекст сохранённого решения изменился. Перечитайте состояние.');
      localStorage.removeItem(record.storageKey);
      if(localStorage.getItem(record.storageKey)!==null)throw new Error('Не удалось очистить сохранённое решение. Повторите исходный запрос.');
    }
    function archiveDamaged(record) {
      if(!record.damaged||record.storageKey!==scope()||localStorage.getItem(record.storageKey)!==record.raw)
        throw new Error('Сохранённый запрос изменился. Перечитайте состояние.');
      const archive=record.storageKey+':damaged:'+crypto.randomUUID();
      localStorage.setItem(archive,record.raw);
      if(localStorage.getItem(archive)!==record.raw)throw new Error('Не удалось сохранить архив.');
      localStorage.removeItem(record.storageKey);
      if(localStorage.getItem(record.storageKey)!==null)throw new Error('Не удалось очистить сохранённое решение. Повторите исходный запрос.');
    }
    return{valid,scope,read,save,settle,archiveDamaged};
  }
  function baseValid(value) {
    return Boolean(value&&Number.isSafeInteger(value.wave)&&value.wave>0&&value.body&&
      typeof value.body==='object'&&!Array.isArray(value.body)&&typeof value.body.operation_id==='string'&&
      value.body.operation_id.length<=100&&/^[A-Za-z0-9_.:-]+$/.test(value.body.operation_id));
  }
  window.wmsCommandIntent={create};
  window.wmsWaveCommandIntent={create,baseValid};
})();
