"""Import a local, authorised AUD product feed. No network access."""
import csv,json,re,math,argparse,hashlib
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from collections import defaultdict

def norm(s): return re.sub(r'[^a-z0-9]','',str(s).lower())
def gtin(s):
 s=str(s).strip()
 if len(s) not in (8,12,13,14) or not s.isascii() or not s.isdigit(): return None
 return s.zfill(14) if sum(int(x)*(3 if i%2==0 else 1) for i,x in enumerate(reversed(s[:-1])))%10 == (10-int(s[-1]))%10 else None

def parse(row):
 required=['retailer','name','url','price','observed_at','condition']
 if any(not row.get(k) for k in required): raise ValueError('Missing required field')
 u=urlsplit(row['url'])
 if u.scheme!='https' or not u.hostname or u.username or u.password: raise ValueError('Invalid URL')
 if row.get('currency')!='AUD': raise ValueError('AUD required')
 p=float(row['price'])
 if not math.isfinite(p) or p<=0: raise ValueError('Invalid price')
 c=norm(row['condition'])
 if c not in ('new','used','refurbished','exdisplay'): raise ValueError('Unknown condition')
 image=(row.get('image_url') or '').strip()
 if image:
  i=urlsplit(image)
  if i.scheme!='https' or not i.hostname or i.username or i.password: raise ValueError('Invalid image URL')
 shipping=(row.get('shipping') or '').strip()
 if shipping:
  shipping=float(shipping)
  if not math.isfinite(shipping) or shipping<0: raise ValueError('Invalid shipping')
 else: shipping=None
 return dict(row,price=p,condition=c,gtin=gtin(row.get('gtin','')),image_url=image,shipping=shipping)

def match_key(r):
 # Never match different conditions, packs or configurations.
 pack=norm(r.get('pack',''))
 variant=norm(r.get('variant',''))
 if not pack or not variant: return None
 if r['gtin']: return ('gtin',r['gtin'],r['condition'],pack,variant)
 b,m=norm(r.get('brand','')),norm(r.get('mpn',''))
 return ('mpn',b,m,r['condition'],pack,variant) if b and m else None

def groups(rows):
 g=defaultdict(list)
 for r in rows:
  k=match_key(r)
  if k: g[k].append(r)
 return [sorted(v,key=lambda r:r['price']) for v in g.values() if len({norm(r['retailer']) for r in v})>1]

def observation_time(value):
 d=datetime.fromisoformat(str(value).replace('Z','+00:00'))
 if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
 return d.astimezone(timezone.utc)

def offer_key(r):
 # Require a known configuration before linking observations across imports.
 k=match_key(r)
 if not k:return None
 identity=[str(r['retailer']).strip().casefold(),r['url'],list(k)]
 return hashlib.sha256(json.dumps(identity,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def record_history(rows,previous):
 """Keep actual observations only; reject conflicting prices at the same instant."""
 if not isinstance(previous,dict): raise ValueError('Invalid history')
 result={k:list(v) for k,v in previous.items()}
 for r in rows:
  k=offer_key(r)
  if not k:continue
  at=observation_time(r['observed_at']).isoformat()
  p=r['price']
  points=result.setdefault(k,[])
  existing=next((x for x in points if x['at']==at),None)
  if existing:
   if existing['price']!=p:raise ValueError('Conflicting prices at the same observation time')
  else:points.append(dict(at=at,price=p))
  points.sort(key=lambda x:observation_time(x['at']))
  result[k]=points[-365:]
 return result

def price_context(row,history):
 k=offer_key(row)
 if not k:return None
 at=observation_time(row['observed_at'])
 points=[p for p in history.get(k,[]) if observation_time(p['at'])<=at]
 points.sort(key=lambda p:observation_time(p['at']))
 prior=[p for p in points if observation_time(p['at'])<at]
 return dict(observations=points,previous_price=prior[-1]['price'] if prior else None,
             previous_at=prior[-1]['at'] if prior else None,
             lowest_observed=min([p['price'] for p in points],default=row['price']))

def profit(buy,sell,fee,other):
 if not all(math.isfinite(x) and x>=0 for x in (buy,sell,fee,other)) or fee>100: raise ValueError('Invalid costs')
 return round(sell-buy-sell*fee/100-other,2)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--authorised',action='store_true');p.add_argument('--output',default='retail.json');p.add_argument('--history',default='retail-history.json');a=p.parse_args()
 if not a.authorised:p.error('Confirm feed display and reuse rights first')
 with open(a.csv,encoding='utf-8-sig',newline='') as f: rows=[parse(r) for r in csv.DictReader(f)]
 history_path=Path(a.history)
 history=record_history(rows,json.loads(history_path.read_text()) if history_path.exists() else {})
 for row in rows:row['price_history']=price_context(row,history)
 # History contains prices, dates and opaque identities only; no credentials.
 history_path.write_text(json.dumps(history,indent=2))
 Path(a.output).write_text(json.dumps({'products':rows,'matches':groups(rows),'coverage':'Authorised imported snapshot; confirm availability'},indent=2))
