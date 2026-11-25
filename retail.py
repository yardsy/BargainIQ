"""Import a local, authorised AUD product feed. No network access."""
import csv,json,re,math,argparse
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
 return dict(row,price=p,condition=c,gtin=gtin(row.get('gtin','')))

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

def profit(buy,sell,fee,other):
 if not all(math.isfinite(x) and x>=0 for x in (buy,sell,fee,other)) or fee>100: raise ValueError('Invalid costs')
 return round(sell-buy-sell*fee/100-other,2)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--authorised',action='store_true');p.add_argument('--output',default='retail.json');a=p.parse_args()
 if not a.authorised:p.error('Confirm feed display and reuse rights first')
 with open(a.csv,encoding='utf-8-sig',newline='') as f: rows=[parse(r) for r in csv.DictReader(f)]
 Path(a.output).write_text(json.dumps({'products':rows,'matches':groups(rows),'coverage':'Authorised imported snapshot; confirm availability'},indent=2))
