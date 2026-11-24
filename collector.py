import argparse, datetime as dt, json, time
from pathlib import Path
from adapter import collect, DEALERS
ROOT=Path(__file__).parent

def save(name,obj):
 p=ROOT/name; tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2),encoding='utf-8');tmp.replace(p)
def load(name,default):
 p=ROOT/name;return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default

def key_for(r):
 return (r['dealer'],r.get('stock') or r.get('identity')) if r.get('stock') or r.get('identity') else None

def merge(old,attempt,history,now):
 rows={ key_for(r):dict(r) for r in old['vehicles'] if key_for(r) }
 unkeyed=[dict(r) for r in old['vehicles'] if not key_for(r)]
 for r in list(rows.values())+unkeyed:
  r['status']='Previously observed; not confirmed in latest refresh'
 for r in attempt['vehicles']:
  if not key_for(r):continue
  key=key_for(r); prev=rows.get(key);r=dict(r)
  r['first_seen']=prev.get('first_seen',now) if prev else now
  r['last_seen']=now
  r['status']='Observed on latest listing page; confirm availability'
  r['price_change']=r['price']-prev['price'] if prev and prev.get('last_seen') else 0
  if not prev or not prev.get('last_seen') or r['price_change']:
   history.append({'dealer':r['dealer'],'stock':r.get('stock'),'id':r['id'],'price':r['price'],'at':now,'change':r['price_change']})
  rows[key]=r
 return {'vehicles':list(rows.values())+unkeyed,'report':attempt['report'],'refreshed_at':now,'coverage':'Partial first pages only; missing listings are not confirmed sold'},history

def refresh(approved):
 now=dt.datetime.now(dt.timezone.utc).isoformat();attempt=collect(approved);old=load('stock.json',{'vehicles':[]});history=load('history.json',[])
 result,history=merge(old,attempt,history,now);save('stock.json',result);save('history.json',history);print('Saved',len(result['vehicles']),'records;',len(attempt['vehicles']),'observed this run',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--approved',nargs='+',required=True,choices=[d[2] for d in DEALERS]);p.add_argument('--loop',action='store_true');a=p.parse_args()
 if not a.approved:p.error('Check source terms and obtain permission before using --approved.')
 while True:
  refresh(set(a.approved))
  if not a.loop:break
  time.sleep(4*3600)
