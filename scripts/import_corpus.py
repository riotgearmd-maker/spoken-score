"""Reproducible source imports. Keeps speaker assignments and edition provenance.
No editorial synopses, translations, or modern copyrighted libretti are imported.
"""
from pathlib import Path
from html.parser import HTMLParser
import urllib.request,urllib.parse,json,re,unicodedata,concurrent.futures,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'data/sources';OUT=ROOT/'data/operas';OUT.mkdir(exist_ok=True)
class Node:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.a=dict(attrs);self.children=[]
 def text(self):return ''.join(c.text() if isinstance(c,Node) else c for c in self.children)
 def find(self,tag=None,cls=None):
  for c in self.children:
   if isinstance(c,Node):
    if (not tag or c.tag==tag) and (not cls or cls in c.a.get('class','').split()):yield c
    yield from c.find(tag,cls)
class HTML(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(s)
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in ['br','img','meta','link','input','hr','source','wbr']:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)
def clean(s):return re.sub(r'\s+',' ',s).strip()
def slug(s):return re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-')
def fetch(url,key):
 p=CACHE/key
 if not p.exists():
  b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SpokenScore/0.1 (libretto research)'}),timeout=35).read();p.write_bytes(b)
 return p.read_text(encoding='utf-8-sig')
def save(o):
 o['segmentCount']=len(o['segments']);o['characterCount']=len(o['characters']);o['textHash']=hashlib.sha256(json.dumps(o['segments'],ensure_ascii=False).encode()).hexdigest()
 (OUT/(o['id']+'.json')).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':')))
 return o['id'],len(o['segments'])
N={'t':'http://www.tei-c.org/ns/1.0'};X='{http://www.w3.org/XML/1998/namespace}'
def txt(e):return clean(''.join(e.itertext())) if e is not None else ''
def spoken(e):
 # Strip stage directions and editorial notes but preserve text following them.
 if e.tag.split('}')[-1] in ['stage','speaker','note','pb','fw','head']:return ''
 return (e.text or '')+''.join(spoken(c)+(c.tail or '') for c in e)
def import_tei(spec):
 filename,composer,language,title=spec;repo='itadracor' if language=='Italian' else 'gerdracor'
 url=f'https://raw.githubusercontent.com/dracor-org/{repo}/main/tei/{filename}.xml';raw=fetch(url,filename+'.xml');r=ET.fromstring(raw)
 source=r.find('.//t:bibl[@type="originalSource"]',N)
 chars=[]
 for e in r.findall('.//t:listPerson/t:person',N)+r.findall('.//t:listPerson/t:personGrp',N):
  names=[txt(n) for n in list(e) if n.tag.split('}')[-1] in ['persName','name']]
  if names:chars.append({'id':e.get(X+'id'),'name':names[0],'aliases':names[1:]})
 body=r.find('.//t:body',N);parents={c:p for p in r.iter() for c in p};segments=[]
 for i,sp in enumerate(body.findall('.//t:sp',N)):
  who=[v.lstrip('#') for v in sp.get('who','').split()]
  parts=[]
  for el in sp.iter():
   if el.tag.split('}')[-1] in ['l','p']:
    ancestor=parents.get(el);inside=False
    while ancestor is not None and ancestor is not sp:
     if ancestor.tag.split('}')[-1] in ['stage','note','l','p']:inside=True;break
     ancestor=parents.get(ancestor)
    if not inside:
     s=clean(spoken(el))
     if s:parts.append(s)
  if not parts:continue
  path=[];anc=parents.get(sp)
  while anc is not None:
   if anc.tag.endswith('}div'):
    h=anc.find('t:head',N)
    if h is not None:path.insert(0,txt(h))
   anc=parents.get(anc)
  # Verse/prose is retained explicitly; it is not asserted to be musicological tagging.
  form='Verse' if sp.findall('.//t:l',N) and not sp.findall('t:p',N) else 'Prose / dialogue'
  segments.append({'id':f's{i+1:04}','order':i+1,'speakers':who,'speakerLabel':txt(sp.find('t:speaker',N)).rstrip('.'),'location':' · '.join(path),'form':form,'text':'\n'.join(parts)})
 known={c['id'] for c in chars};unknown=sorted({w for s in segments for w in s['speakers'] if w not in known});assert not unknown,(filename,unknown)
 if filename=='schikaneder-die-zauberfloete':
  for c in chars:
   if c['id']=='koeniginn':c['aliases']+=['Queen of the Night','Königin der Nacht'];c['name']='Königin der Nacht'
   if c['id']=='weib':c['aliases']+=['Papagena'];c['name']='Papagena / altes Weib'
 o={'id':slug(title+' '+composer.split()[-1]),'title':title,'composer':composer,'language':language,'lang':'it-IT' if language=='Italian' else 'de-DE','characters':chars,'segments':segments,'source':{'name':'DraCor / TextGrid' if repo=='gerdracor' else 'DraCor / Biblioteca Italiana','url':f'https://github.com/dracor-org/{repo}/blob/main/tei/{filename}.xml','edition':txt(source),'license':'DraCor CC0; underlying source attribution retained','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'coverage':'Source text imported','coverageNote':'All attributed speech blocks in this source edition are imported, including shared speaker assignments. Historical spelling is retained. Check against your score for cuts, variants, musical repetitions, and group passages.','review':'Source-structured; score comparison pending'}
 return save(o)
TEI=[('schikaneder-die-zauberfloete','Wolfgang Amadeus Mozart','German','Die Zauberflöte'),('da-ponte-cosi-fan-tutte','Wolfgang Amadeus Mozart','Italian','Così fan tutte'),('da-ponte-don-giovanni','Wolfgang Amadeus Mozart','Italian','Don Giovanni'),('da-ponte-le-nozze-di-figaro','Wolfgang Amadeus Mozart','Italian','Le nozze di Figaro'),('kind-der-freischuetz','Carl Maria von Weber','German','Der Freischütz'),('sonnleithner-fidelio','Ludwig van Beethoven','German','Fidelio')]
for f,title in [('das-rheingold','Das Rheingold'),('der-fliegende-hollaender','Der fliegende Holländer'),('die-meistersinger-von-nuernberg','Die Meistersinger von Nürnberg'),('die-walkuere','Die Walküre'),('goetterdaemmerung','Götterdämmerung'),('lohengrin','Lohengrin'),('parsifal','Parsifal'),('siegfried','Siegfried'),('tannhaeuser','Tannhäuser'),('tristan-und-isolde','Tristan und Isolde')]:TEI.append(('wagner-'+f,'Richard Wagner','German',title))
MAJOR={'VERDI':'Giuseppe Verdi','PUCCINI':'Giacomo Puccini','MOZART':'Wolfgang Amadeus Mozart','ROSSINI':'Gioachino Rossini','DONIZETTI':'Gaetano Donizetti','BELLINI':'Vincenzo Bellini','HÄNDEL':'George Frideric Handel','MONTEVERDI':'Claudio Monteverdi','GLUCK':'Christoph Willibald Gluck','VIVALDI':'Antonio Vivaldi','HAYDN':'Joseph Haydn','CAVALLI':'Francesco Cavalli','PERGOLESI':'Giovanni Battista Pergolesi','LEONCAVALLO':'Ruggero Leoncavallo','MASCAGNI':'Pietro Mascagni','BOITO':'Arrigo Boito','PONCHIELLI':'Amilcare Ponchielli','CILEA':'Francesco Cilea','GIORDANO':'Umberto Giordano'}
def italian_specs():
 tree=HTML((CACHE/'italian-index.html').read_text()).root;result={}
 for row in tree.find('div','alfa'):
  composer=next(row.find('span','pm'),None);title=next(row.find('span','pt'),None);date=next(row.find('span','pe'),None)
  if not composer or not title:continue
  name=clean(composer.text());comp=next((v for k,v in MAJOR.items() if re.search(r'(?<!\w)'+re.escape(k)+r'$',name)),None)
  a=next(title.find('a'),None)
  if not comp or not a:continue
  url='https://www.librettidopera.it/'+a.a['href'];years=re.findall(r'\b(1[6789]\d\d)\b',date.text() if date else '')
  if years and int(years[-1])>1930:continue
  if '➥' in title.text():continue
  titletext=clean(a.text()).capitalize();key=a.a['href'].split('/')[0]
  result[key]={'id':slug(titletext+' '+comp.split()[-1]),'title':titletext,'composer':comp,'language':'Italian','lang':'it-IT','url':url,'key':key,'date':clean(date.text()) if date else ''}
 specs=list(result.values())
 counts={}
 for s in specs:counts[s['id']]=counts.get(s['id'],0)+1
 for s in specs:
  if counts[s['id']]>1:s['id']+='-'+s['key']
 return specs
def import_italian(spec):
 url=urllib.parse.urljoin(spec['url'],'rid.html');raw=fetch(url,'it-'+spec['key']+'.html');r=HTML(raw).root
 chars=[]
 for td in r.find('td','vdes'):
  b=next(td.find('b'),None)
  if b:
   name=clean(b.text());chars.append({'id':slug(name),'name':name.title(),'aliases':[name,clean(td.text())]})
 segments=[];loc=[];speaker='';unresolved=set();order=0
 for div in r.find('div'):
  classes=div.a.get('class','').split()
  if 'rid_a' in classes:loc=[clean(div.text())]
  elif 'rid_s' in classes:loc=loc[:1]+[clean(div.text())]
  elif 'rid_voce' in classes:speaker=clean(div.text())
  elif any(c.startswith('rid_testo') for c in classes):
   lines=[]
   for p in div.find('p'):
    if 'rid_indt' not in p.a.get('class',''):
     s=clean(p.text())
     if s:lines.append(s)
   if not lines:continue
   who=[]
   for c in chars:
    original=c['aliases'][0]
    if re.search(r'(?<!\w)'+re.escape(original)+r'(?!\w)',speaker,re.I):who.append(c['id'])
   # Keep unassigned ensemble labels visible; never guess that "Tutti" means every role.
   if not who:
    ident=slug(speaker) or 'unattributed';who=[ident];unresolved.add(speaker)
   order+=1;segments.append({'id':f's{order:04}','order':order,'speakers':who,'speakerLabel':speaker,'location':' · '.join(loc),'form':'Libretto text','text':'\n'.join(lines)})
 known={c['id'] for c in chars}
 for s in segments:
  for cid in s['speakers']:
   if cid not in known:chars.append({'id':cid,'name':s['speakerLabel'].title(),'aliases':[],'group':True});known.add(cid)
 assert len(segments)>10,(spec['title'],'no structured text')
 o={k:v for k,v in spec.items() if k not in ['key','url']};o.update(characters=chars,segments=segments,source={'name':'Libretti d’opera italiani','url':url,'edition':spec['date']+' · Italian libretto transcription','license':'Historical libretto text; transcription credited to Libretti d’opera italiani','licenseUrl':spec['url']},coverage='Imported; role review pending',coverageNote='Historical Italian libretto text imported automatically. Explicitly named shared lines are included. Collective labels such as “Tutti” remain separate and may need assignment to individual roles. Compare with your score before relying on a complete role playlist.',review='Speaker and ensemble review pending')
 return save(o)
def main():
 specs=italian_specs();(ROOT/'data/import-targets.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2));print('Import targets:',len(specs),'Italian and',len(TEI),'structured TEI',flush=True)
 jobs=[('tei',s) for s in TEI]+[('italian',s) for s in specs if s['id'] not in {slug(t[3]+' '+t[1].split()[-1]) for t in TEI}]
 errors=[]
 def run(job):
  kind,spec=job
  try:return (import_tei(spec) if kind=='tei' else import_italian(spec)),None
  except Exception as e:return None,{'source':spec,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for i,(ok,error) in enumerate(pool.map(run,jobs)):
   if error:errors.append(error);print('FAILED',error,flush=True)
   elif i%15==0:print('Imported',i+1,ok,flush=True)
 (ROOT/'data/import-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2));print('Done:',len(list(OUT.glob('*.json'))),'operas;',len(errors),'failures',flush=True)
if __name__=='__main__':main()
