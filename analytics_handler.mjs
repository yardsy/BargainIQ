import {validateEngagement} from "./analytics_request.mjs";
// Not deployed as a public route until quota controls and storage are verified.
export async function handleEngagement(request,{enabled=false,allow,increment}={}){
 const reply=status=>new Response(null,{status,headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff","X-Robots-Tag":"noindex, nofollow"}});
 if(!enabled||typeof allow!=="function"||typeof increment!=="function")return reply(503);
 const result=await validateEngagement(request);
 if(result.status!==200)return reply(result.status);
 try{
 if(!await allow(request))return reply(429);
 await increment(result.event);
 return reply(204);
 }catch{return reply(503)}
}
