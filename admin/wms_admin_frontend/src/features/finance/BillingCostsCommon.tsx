import type {ReactNode} from "react";
import {ApiRequestError} from "../../api";
import "./BillingCosts.css";

// Общие элементы расшифровки счёта (NI07.1): точная десятичная сумма в пределах одной валюты,
// понятные ошибки чтения, состояния блока. Разные валюты никогда не складываются.

// Сумма десятичных строк без float: масштабируем до общего числа знаков и складываем BigInt.
export function addDecimals(values: string[]): string {
 const parsed=values.map(v=>String(v).trim()).filter(v=>/^-?\d+(\.\d+)?$/.test(v));
 if(!parsed.length)return "0";
 const scale=Math.max(...parsed.map(v=>(v.split(".")[1]||"").length));
 const total=parsed.reduce((sum,v)=>{
  const negative=v.startsWith("-"),[i,f=""]=v.replace("-","").split(".");
  const n=BigInt(i+f.padEnd(scale,"0"));
  return sum+(negative?-n:n);
 },0n);
 const negative=total<0n,digits=(negative?-total:total).toString().padStart(scale+1,"0");
 const text=scale?digits.slice(0,-scale)+"."+digits.slice(-scale):digits;
 return (negative?"-":"")+text;
}

// Группировка по валюте с точной суммой.
export function totalsByCurrency<T>(rows: T[],currency:(r:T)=>string,amount:(r:T)=>string): {currency:string;amount:string;count:number}[] {
 const map=new Map<string,string[]>();
 for(const r of rows){const c=currency(r)||"—";map.set(c,[...(map.get(c)||[]),amount(r)]);}
 return [...map.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([c,values])=>({currency:c,amount:addDecimals(values),count:values.length}));
}

export function readError(e: unknown, what: string): string {
 if(e instanceof ApiRequestError){
  if(e.status===401)return "Требуется вход: сессия истекла.";
  if(e.status===403)return "Нет прав на чтение "+what+" по складам этого счёта.";
  if(e.status===404)return "Счёт или источник "+what+" не найден.";
  const detail=e.detail as {message?:string;code?:string}|string|undefined;
  const text=typeof detail==="string"?detail:detail?.message;
  return (text||"Сервер отклонил чтение "+what)+(typeof detail==="object"&&detail?.code?" ("+detail.code+")":"")+".";
 }
 if(e instanceof TypeError)return "Сервер WMS недоступен — "+what+" не прочитаны. Повторите позже.";
 return e instanceof Error?e.message:"Не удалось прочитать "+what+".";
}

export type BlockState="loading"|"error"|"empty"|"ready";

export function BlockStatus({state,error,empty,onRetry}:{state:BlockState;error?:string;empty:string;onRetry?:()=>void}){
 if(state==="loading")return <p className="bc-state bc-loading" aria-live="polite">Загрузка…</p>;
 if(state==="error")return <div className="bc-state bc-error" role="alert"><span>{error}</span>{onRetry&&<button type="button" onClick={onRetry}>Прочитать ещё раз</button>}</div>;
 if(state==="empty")return <p className="bc-state bc-empty">{empty}</p>;
 return null;
}

export function Money({amount,currency}:{amount:string|null|undefined;currency:string}){
 return amount===null||amount===undefined?<span className="bc-muted">—</span>:<span className="bc-money">{amount}<small> {currency}</small></span>;
}

export function Chip({tone,children,title}:{tone:"ok"|"warn"|"bad"|"info"|"idle";children:ReactNode;title?:string}){
 return <span className={"bc-chip bc-"+tone} title={title}>{children}</span>;
}

export function TableWrap({label,children}:{label:string;children:ReactNode}){
 return <div className="bc-table-wrap" role="region" aria-label={label} tabIndex={0}>{children}</div>;
}
