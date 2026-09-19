from pathlib import Path
import json,urllib.request,concurrent.futures,xml.etree.ElementTree as ET
r=Path('data/sources');tree=json.loads((r/'libretti-tree.txt').read_text())['tree'];paths=[v['path'] for v in tree if 'TNAH2020' in v['path'] and v['path'].endswith('.xml')];print('French sources',len(paths),flush=True)
def get(p):
 name=p.split('/')[-1];local=r/name
 try:
  if not local.exists():local.write_bytes(urllib.request.urlopen('https://raw.githubusercontent.com/Chartes-TNAH/libretti/master/'+p,timeout=30).read())
  doc=ET.parse(local);ns={'t':'http://www.tei-c.org/ns/1.0'};title=doc.find('.//t:titleStmt/t:title',ns);authors=doc.findall('.//t:titleStmt/t:author',ns);return {'file':name,'path':p,'title':''.join(title.itertext()),'authors':[(a.get('role'),''.join(a.itertext())) for a in authors]}
 except Exception as e:return {'file':name,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:meta=list(pool.map(get,paths))
(r/'french-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(meta,ensure_ascii=False,indent=2),flush=True)
