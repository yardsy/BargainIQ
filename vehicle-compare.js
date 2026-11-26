const el=id=>document.getElementById(id);
const label=v=>[v.year,v.brand,v.model,v.variant,v.powertrain].join(' · ');
const display=v=>v===true?'Standard':v===false?'Not included':v==null?'Not verified':String(v);
const node=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n};
async function init(){
 const res=await fetch('vehicle-specs.json');if(!res.ok)throw Error('Could not load specifications');const data=await res.json();
 const vehicles=data.vehicles;const ids=['a','b','c'];const params=new URLSearchParams(location.search);
 ids.forEach((id,i)=>{const select=el(id);if(i===2)select.add(new Option('None',''));vehicles.forEach(v=>select.add(new Option(label(v),v.id)));const requested=params.get(id);select.value=vehicles.some(v=>v.id===requested)?requested:(i===2?'':vehicles[i].id);select.addEventListener('change',render)});
 el('coverage').textContent=data.brands.map(b=>b+' — '+(vehicles.some(v=>v.brand===b)?'partial data available':'planned')).join(' • ');
 el('diff').checked=params.get('diff')!=='0';el('diff').addEventListener('change',render);
 function render(){
 const selected=ids.map(id=>vehicles.find(v=>v.id===el(id).value)).filter(Boolean);
 const unique=new Set(selected.map(v=>v.id));const table=el('table');table.replaceChildren(node('caption','Equipment comparison'));
 el('summary').replaceChildren();el('sources').replaceChildren();el('status').textContent='Australian specifications · checked '+data.checked+' · selected equipment only';
 if(unique.size!==selected.length){el('status').textContent='Please select different vehicles.';return}
 const head=table.createTHead().insertRow();head.append(node('th','Feature'));selected.forEach(v=>head.append(node('th',label(v))));
 const body=table.createTBody();let group='',count=0;
 const differences=[];
 data.features.forEach((f,i)=>{const values=selected.map(v=>v.specs[i]);const known=values.every(v=>v!=null);const changed=known&&new Set(values).size>1;if(changed)differences.push(f.label);if(el('diff').checked&&!changed&&known)return;
 if(group!==f.group){const row=body.insertRow();row.className='group';const cell=node('th',f.group);cell.colSpan=selected.length+1;row.append(cell);group=f.group}
 const row=body.insertRow();if(changed)row.className='different';const h=node('th',f.label);h.scope='row';row.append(h);values.forEach(v=>row.append(node('td',display(v))));count++});
 if(!count){const cell=body.insertRow().insertCell();cell.colSpan=selected.length+1;cell.textContent='No verified differences in the recorded features.'}
 el('summary').append(node('h2',differences.length+' verified equipment differences'),node('p',differences.length?differences.join(' · '):'No known differences in this partial dataset.'),node('p','Pricing is not yet verified. Confirm vehicle build revision and equipment with the dealer.'));
 [...new Set(selected.map(v=>v.source))].forEach(url=>{const link=node('a','Manufacturer specification sheet');link.href=url;link.target='_blank';link.rel='noopener noreferrer';el('sources').append(link,document.createTextNode(' '))});
 }
 el('share').addEventListener('click',async()=>{const url=new URL(location.href);ids.forEach(id=>url.searchParams.set(id,el(id).value));url.searchParams.set('diff',el('diff').checked?'1':'0');try{await navigator.clipboard.writeText(url.href);el('shareStatus').textContent='Link copied.'}catch{el('shareStatus').textContent=url.href}});
 render();
}
init().catch(()=>{el('status').textContent='Specifications could not load. Please refresh and try again.';el('share').disabled=true});
