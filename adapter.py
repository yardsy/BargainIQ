"""Pilot collector. Run only for sources you have permission to collect from."""
import re,json,datetime,urllib.request,urllib.robotparser,urllib.parse,time,argparse,hashlib
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).parent
DEALERS=[('Essendon Hyundai','VIC','essendonhyundai'),('Shepparton Hyundai','VIC','sheppartonhyundai'),('Sydney City Hyundai','NSW','sydneycityhyundai'),('Wayville Hyundai','SA','wayvillehyundai'),('John Hughes Hyundai','WA','johnhugheshyundai')]
MODELS='IONIQ 9|IONIQ 6|IONIQ 5|Santa Fe|STARIA LOAD HEV|STARIA LOAD|STARIA|Tucson|Kona|Palisade|Venue|i30|i20|INSTER|ELEXIO|Sonata'
class Links(HTMLParser):
 def __init__(self): super().__init__(); self.links=[]; self.current=None
 def handle_starttag(self,tag,attrs):
  if tag=='a': self.current=[dict(attrs).get('href',''),[]]
 def handle_data(self,data):
  if self.current is not None:self.current[1].append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.current is not None:self.links.append((self.current[0],' '.join(self.current[1])));self.current=None

def parse(text,dealer,state,url):
 text=' '.join(text.split()); m=re.search(r'(20\d\d) Hyundai ('+MODELS+r')\b(.*?)\bnew\s+(SUV|Sedan|Hatch|People Mover|Van|Ute)\b(.*?)Drive Away',text,re.I)
 if not m or 'just sold' in text.lower():return None
 year,model,variant,body,details=m.groups(); p=re.findall(r'\$\s*([\d,]+)',details); km=re.search(r'([\d,]+)\s*km',details,re.I)
 stockmatch=re.search(r'Stock No:\s*([\w-]+)',details,re.I); stock=stockmatch[1] if stockmatch else None
 path=urllib.parse.urlsplit(url).path.rstrip('/')
 if not stock and (not path or path.lower().endswith('/search/new-cars') or path.lower()=='/search'):return None
 identity=stock or 'url:'+urllib.parse.urlunsplit((*urllib.parse.urlsplit(url)[:3],'',''))

 if not p:return None
 return dict(id='real-'+hashlib.sha256((dealer+identity).encode()).hexdigest()[:16],brand='Hyundai',model=model.title() if model.lower() not in ('i30','i20') else model.lower(),variant=variant.strip() or 'Unspecified',year=int(year),body=body,km=int(km[1].replace(',','')) if km else None,price=int(p[-1].replace(',','')),dealer=dealer,state=state,stock=stock,identity=identity,url=url,colour='Not captured',status='Advertised new; confirm availability',drive='AWD' if '4X4 On Demand' in details else 'FWD' if 'Front Wheel Drive' in details else 'Unknown',observed=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='collector')

def collect(approved):
 rows=[]; report=[]
 for dealer,state,domain in DEALERS:
  if domain not in approved:
   report.append({'dealer':dealer,'count':0,'status':'Not enabled: permission not confirmed'});continue
  base='https://www.'+domain+'.com.au'; url=base+'/search/new-cars'
  try:
   rp=urllib.robotparser.RobotFileParser(base+'/robots.txt'); robots=urllib.request.urlopen(urllib.request.Request(base+'/robots.txt',headers={'User-Agent':'CarRadarPilot/0.1'}),timeout=20).read().decode('utf-8','replace');rp.parse(robots.splitlines())
   if not rp.can_fetch('CarRadarPilot',url):raise ValueError('robots.txt does not permit access')
   req=urllib.request.Request(url,headers={'User-Agent':'CarRadarPilot/0.1'}); html=urllib.request.urlopen(req,timeout=20).read().decode('utf-8','replace'); parser=Links();parser.feed(html); found={}
   for href,text in parser.links:
    link=urllib.parse.urljoin(url,href)
    if urllib.parse.urlparse(link).netloc!=urllib.parse.urlparse(base).netloc:continue
    row=parse(text,dealer,state,link)
    if row:found[row['id']]=row
   rows.extend(found.values());report.append({'dealer':dealer,'count':len(found),'status':'partial first page' if found else 'no supported cards; adapter needed'})
  except Exception as e:report.append({'dealer':dealer,'count':0,'status':str(e)})
  time.sleep(2)
 output={'vehicles':rows,'report':report}; (ROOT/'refresh-attempt.json').write_text(json.dumps(output,indent=2));print(json.dumps(report,indent=2))
 return output

