/* No cookies, identifiers, query contents, destination URLs or account details. */
(()=>{"use strict";
const allowedViews=new Set(["home","all","same","clearance","flip","car","watch","account"]);
const allowedEvents=new Set(["page_view","retailer_click","search_run","request_saved"]);
const allowedCategories=new Set(["retail","vehicle","unknown"]);
const endpoint=document.querySelector('meta[name="bargainiq-analytics-endpoint"]')?.content;
if(!endpoint||endpoint!=="/.netlify/functions/engagement")return;
if(navigator.globalPrivacyControl||navigator.doNotTrack==="1")return;
function view(){const v=new URLSearchParams(location.search).get("view");return allowedViews.has(v)?v:location.pathname.endsWith("/account.html")?"account":"home"}
function record(event,category="unknown"){if(!allowedEvents.has(event)||!allowedCategories.has(category))return;const payload=JSON.stringify({event,view:view(),category});fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json"},body:payload,credentials:"omit",referrerPolicy:"no-referrer",keepalive:true}).catch(()=>{});}
window.bargainIQEngagement=record;
record("page_view");
let searchTimer;document.getElementById("search")?.addEventListener("input",e=>{if(!e.isTrusted)return;clearTimeout(searchTimer);if(e.target.value.trim())searchTimer=setTimeout(()=>record("search_run","retail"),1000);});
document.addEventListener("click",e=>{if(!e.isTrusted)return;const link=e.target.closest?.('a[data-engagement-category]');if(link)record("retailer_click",link.dataset.engagementCategory);},true);
})();