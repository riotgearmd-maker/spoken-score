from pathlib import Path
import json,shutil,mimetypes,gzip
from romanization import enrich_opera
root=Path(__file__).resolve().parents[1]
operas=[enrich_opera(json.loads(p.read_text())) for p in sorted((root/'data/operas').glob('*.json'))]
art_songs=json.loads((root/'data/art-songs.json').read_text())
# Retain the three original work URLs and supply the same voice integration.
for w in json.loads((root/'public/works.json').read_text())+art_songs:
 chars=[{'id':'rodolfo','name':'Rodolfo','aliases':[]}] if w['kind']=='Aria' else []
 source_url='https://www.composerdiversity.com/art-song-database' if w.get('research') else 'https://imslp.org/'
 source_name=w['author']+(' · repertoire research via Institute for Composer Diversity' if w.get('research') else '')
 operas.append({'id':w['slug'],'title':w['title'],'composer':w['composer'],'language':w['language'],'lang':w['lang'],'kind':w['kind'],'characters':chars,'segments':[{'id':'s0001','order':1,'speakers':[c['id'] for c in chars],'speakerLabel':chars[0]['name'] if chars else w['author'],'location':w['collection'],'form':w['kind'],'text':w['text']}],'source':{'name':source_name,'url':source_url,'edition':w['collection'],'license':'Historical original-language text.'},'coverage':'Individual work','coverageNote':'This is the individual aria or song text, not a full opera role. Musical repetitions are omitted.','review':'Diction review pending'})
# Common translated titles aid discovery without changing the language spoken.
aliases={'die-zauberflote-mozart':['The Magic Flute','Magic Flute','Zauberfloete'],'le-nozze-di-figaro-mozart':['The Marriage of Figaro'],'cosi-fan-tutte-mozart':['Cosi fan tutte'],'der-fliegende-hollander-wagner':['The Flying Dutchman'],'die-walkure-wagner':['The Valkyrie'],'gotterdammerung-wagner':['Twilight of the Gods'],'il-barbiere-di-siviglia-rossini':['The Barber of Seville'],'la-boheme-puccini':['La Boheme'],'le-villi-puccini':['The Willis']}
for o in operas:
 o['aliases']=aliases.get(o['id'],[])
 assert o['segments'],o['id']
 ids={c['id'] for c in o['characters']};assert len(ids)==len(o['characters']),o['id']
 assert all(set(s['speakers'])<=ids for s in o['segments']),o['id']
ids=[o['id'] for o in operas];assert len(ids)==len(set(ids)),'Duplicate opera id'
assets={}
for p in (root/'public').rglob('*'):
 if p.is_file() and p.suffix in ['.html','.css','.js','.json']:
  typ={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json'}[p.suffix]
  assets['/'+str(p.relative_to(root/'public'))]={'type':typ,'body':p.read_text()}
out=root/'dist'
if out.exists():shutil.rmtree(out)
(out/'server').mkdir(parents=True);(out/'.openai').mkdir();shutil.copy(root/'.openai/hosting.json',out/'.openai/hosting.json')
code=(root/'server/worker.mjs').read_text()+'\nconst corpus='+json.dumps(operas,ensure_ascii=False,separators=(',',':'))+';\nconst assets='+json.dumps(assets,ensure_ascii=False,separators=(',',':'))+';\nexport default createApp(corpus,assets);\n'
(out/'server/index.js').write_text(code)
opera_count=sum(1 for o in operas if not o.get('kind'))
text_count=sum(1 for o in operas if o.get('kind'))
print(f'Built {opera_count} opera editions, {text_count} individual texts, {sum(len(o["segments"]) for o in operas)} passages. Worker {len(code.encode())/1e6:.1f} MB, gzip {len(gzip.compress(code.encode()))/1e6:.1f} MB.')
report={'operaEditions':opera_count,'individualTexts':text_count,'composers':sorted({o['composer'] for o in operas if not o.get('kind')}),'passages':sum(len(o['segments']) for o in operas),'exhaustive':False,'omittedImports':json.loads((root/'data/import-errors.json').read_text()),'note':'This release imports available historical libretti and selected public-domain art-song texts. It is not an exhaustive catalogue.'}
(root/'data/coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
