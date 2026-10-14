import { receiptBase } from "./api";
import { humanReceiptMessage } from "./messages";
import type { ReceiptCredentials } from "./contracts";
export interface ReceiptPhoto {photo_id:string;sha256:string;view:string;recorded_at:string;recorded_by:string;mime_type:string}
const auth=(credentials:ReceiptCredentials)=>({Authorization:"Basic "+btoa(credentials.username+":"+credentials.password)});
const photoBase=()=>receiptBase()+"/api/delivery/store-photos";
async function checked(response:Response):Promise<Response> {
 if(!response.ok){
  const data=await response.json();
  throw new Error(humanReceiptMessage(typeof data.detail==="string"?data.detail:data.detail?.message||JSON.stringify(data.detail)));
 }
 return response;
}
export async function listPhotos(load:string,address:string,credentials:ReceiptCredentials):Promise<ReceiptPhoto[]> {
 const query=new URLSearchParams({load_operation_id:load,store_address:address});
 return (await checked(await fetch(photoBase()+"/list?"+query,{headers:auth(credentials)}))).json() as Promise<ReceiptPhoto[]>;
}
export async function uploadPhoto(load:string,address:string,view:string,file:File,credentials:ReceiptCredentials):Promise<void> {
 const query=new URLSearchParams({load_operation_id:load,store_address:address,view});
 await checked(await fetch(photoBase()+"/upload?"+query,{method:"POST",headers:{...auth(credentials),"Content-Type":file.type},body:file}));
}
export async function photoContent(photo:ReceiptPhoto,credentials:ReceiptCredentials):Promise<Blob> {
 return (await checked(await fetch(photoBase()+"/"+photo.photo_id+"/content",{headers:auth(credentials)}))).blob();
}
