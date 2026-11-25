"""Build a retail snapshot from explicitly approved, local CSV feeds.
No network fetching; never publish credentials or arbitrary source columns.
"""
import argparse,csv,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import urlsplit
from retail import parse,groups,record_history,price_context,observation_time,write_json_atomic

PUBLIC_FIELDS=('retailer','name','url','price','observed_at','condition','currency','brand','mpn','gtin','pack','variant','category','image_url','shipping','width_cm','depth_cm','height_cm','clearance')

def build(manifest,root,previous,now=None):
    now=now or datetime.now(timezone.utc)
    if not isinstance(manifest,list) or not manifest:
        raise ValueError('At least one approved feed is required')
    root=Path(root).resolve()
    products=[]
    report=[]
    retailers=set()
    for source in manifest:
        if source.get('authorised') is not True:
            raise ValueError('Feed display and reuse permission required')
        retailer=source['retailer'].strip()
        key=retailer.casefold()
        if not key or key in retailers:
            raise ValueError('Missing or duplicate retailer')
        retailers.add(key)
        path=(root/source['file']).resolve()
        if not path.is_relative_to(root) or path.suffix.lower()!='.csv':
            raise ValueError('Feed must be a CSV inside the approved input directory')
        hosts=source.get('allowed_hosts')
        if not isinstance(hosts,list) or not hosts or not all(isinstance(h,str) and h and h==h.lower() for h in hosts):
            raise ValueError('Explicit listing host allowlist required')
        count=0
        stale=0
        identities=set()
        with path.open(encoding='utf-8-sig',newline='') as f:
            for raw in csv.DictReader(f):
                if raw.get('retailer','').strip().casefold()!=key:
                    raise ValueError('Retailer mismatch')
                row=parse({k:v for k,v in raw.items() if k in PUBLIC_FIELDS})
                row['retailer']=retailer
                if urlsplit(row['url']).hostname not in hosts:
                    raise ValueError('Unapproved listing host')
                at=observation_time(row['observed_at'])
                if at>now+timedelta(minutes=5):
                    raise ValueError('Future observation')
                if at<now-timedelta(days=7):
                    stale+=1
                    continue
                if row['url'] in identities:
                    raise ValueError('Duplicate listing URL in snapshot')
                identities.add(row['url'])
                products.append(row)
                count+=1
        if not count:
            raise ValueError('No fresh listings for an approved retailer; publication stopped')
        report.append({'retailer':retailer,'accepted':count,'stale_excluded':stale})
    history=record_history(products,previous)
    for row in products:
        row['price_history']=price_context(row,history)
    export={'products':products,'matches':groups(products),'coverage':'Approved retailer snapshots; verify stock and final price','generated_at':now.isoformat()}
    return export,history,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('manifest',type=Path)
    p.add_argument('--input-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('retail.json'))
    p.add_argument('--history',type=Path,default=Path('retail-history.json'))
    p.add_argument('--publish',action='store_true',help='Write validated snapshot; otherwise preview only')
    a=p.parse_args()
    if a.output.resolve()==a.history.resolve():
        p.error('Output and history must be separate files')
    previous=json.loads(a.history.read_text()) if a.history.exists() else {}
    export,history,report=build(json.loads(a.manifest.read_text()),a.input_dir,previous)
    json.dumps(export,allow_nan=False)
    json.dumps(history,allow_nan=False)
    if a.publish:
        write_json_atomic(a.history,history)
        write_json_atomic(a.output,export)
    print(json.dumps({'published':a.publish,'retailers':report,'listings':len(export['products'])},indent=2))

if __name__=='__main__':
    main()
