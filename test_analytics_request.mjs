import assert from "node:assert/strict";
import {validateEngagement} from "./analytics_request.mjs";
const origin="https://bargainiq.pages.dev",url=origin+"/api/engagement";
const valid={event:"page_view",view:"home",category:"unknown"};
function req(body=valid,headers={},method="POST"){return new Request(url,{method,headers:{Origin:origin,"Content-Type":"application/json",...headers},...(method==="POST"?{body:JSON.stringify(body)}:{})})}
assert.deepEqual(await validateEngagement(req()),{status:200,event:valid});
for(const [request,status] of [[req(valid,{},"GET"),405],[req(valid,{Origin:"https://example.invalid"}),403],[req(valid,{"Sec-GPC":"1"}),204],[req(valid,{DNT:"1"}),204],[req(valid,{"Content-Type":"text/plain"}),415],[req({...valid,email:"test@example.invalid"}),400],[req({...valid,event:"unknown"}),400],[req({...valid,view:"private"}),400],[req({...valid,category:"x".repeat(600)}),413],[req(null),400],[req([valid]),400]])assert.equal((await validateEngagement(request)).status,status);
console.log("Analytics request validation tests passed");
