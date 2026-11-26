// Pure request validation; no storage, network calls or active route.
const events=new Set(["page_view","retailer_click","search_run","request_saved"]);
const views=new Set(["home","all","same","clearance","flip","car","watch","account"]);
const categories=new Set(["retail","vehicle","unknown"]);
export async function validateEngagement(request){
 if(request.method!=="POST")return {status:405};
 if(request.headers.get("Origin")!==new URL(request.url).origin)return {status:403};
 if(request.headers.get("Sec-GPC")==="1"||request.headers.get("DNT")==="1")return {status:204};
 if(request.headers.get("Content-Type")?.split(";")[0].trim().toLowerCase()!=="application/json")return {status:415};
 const reader=request.body?.getReader();if(!reader)return {status:400};
 let length=0;const chunks=[];
 try{while(true){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;if(length>512){await reader.cancel();return {status:413}}chunks.push(value)}}catch{return {status:400}}
 let payload;try{const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength}payload=JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(bytes))}catch{return {status:400}}
 if(!payload||typeof payload!=="object"||Array.isArray(payload)||Object.keys(payload).sort().join(",")!=="category,event,view")return {status:400};
 if(!events.has(payload.event)||!views.has(payload.view)||!categories.has(payload.category))return {status:400};
 return {status:200,event:{event:payload.event,view:payload.view,category:payload.category}};
}
