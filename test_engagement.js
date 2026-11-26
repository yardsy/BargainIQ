const assert=require("node:assert/strict"),vm=require("node:vm"),fs=require("node:fs");
const source=fs.readFileSync("engagement.js","utf8");
function run({endpoint,privacy=false,dnt="0"}={}){
 const sent=[],listeners={},searchListeners={},timers=[];
 const ctx={URLSearchParams,location:{search:"?view=same&secret=private",pathname:"/"},navigator:{globalPrivacyControl:privacy,doNotTrack:dnt},window:{},document:{querySelector:()=>endpoint?{content:endpoint}:null,getElementById:()=>({addEventListener:(k,f)=>searchListeners[k]=f}),addEventListener:(k,f)=>listeners[k]=f},fetch:(url,opts)=>{sent.push({url,opts});return Promise.resolve()},clearTimeout:()=>{},setTimeout:f=>{timers.push(f);return timers.length}};
 vm.runInNewContext(source,ctx);
 return {sent,ctx,listeners,searchListeners,timers};
}
const endpoint="/.netlify/functions/engagement";
for(const opts of [{},{endpoint:"https://example.com"},{endpoint,privacy:true},{endpoint,dnt:"1"}]) assert.equal(run(opts).sent.length,0);
const t=run({endpoint});
assert.equal(t.sent.length,1);
assert.deepEqual(JSON.parse(t.sent[0].opts.body),{event:"page_view",view:"same",category:"unknown"});
assert.equal(t.sent[0].opts.credentials,"omit");
t.ctx.window.bargainIQEngagement("invalid");
t.ctx.window.bargainIQEngagement("retailer_click","private");
assert.equal(t.sent.length,1);
t.listeners.click({isTrusted:true,target:{closest:()=>({dataset:{engagementCategory:"retail"}})}});
assert.equal(t.sent.length,2);
t.searchListeners.input({isTrusted:true,target:{value:"private search words"}});
t.timers[0]();
assert.equal(t.sent.length,3);
assert.ok(t.sent.every(e=>!e.opts.body.includes("private")));
console.log("Engagement client tests passed");
