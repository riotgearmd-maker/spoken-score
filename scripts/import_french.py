from import_corpus import *
metadata=json.loads((CACHE/'french-metadata.json').read_text());fix={'Bizet':'Georges Bizet','Adam, Adolphe':'Adolphe Adam','Christoph Willibald von Gluck':'Christoph Willibald Gluck'}
for meta in metadata:
 if any(x in meta['title'] for x in ['Porgy','Carmélites','Vaisseau','sortilèges']):continue
 r=ET.parse(CACHE/meta['file']).getroot();title=clean(meta['title']);composer=clean(next(a[1] for a in meta['authors'] if a[0]=='songWriter'));composer=fix.get(composer,composer)
 if 'LES DEUX AVEUGLES' in title:title='Les deux aveugles';composer='Jacques Offenbach'
 if title.isupper():title=title.capitalize()
 parents={c:p for p in r.iter() for c in p};segments=[];characters={}
 for sp in r.findall('.//t:body//t:sp',N):
  label=txt(sp.find('t:speaker',N)).strip(' .,;:');label=re.split(r'\s*\(',label)[0].strip(' ,.:')
  label=clean(label);parts=[]
  for e in sp.iter():
   if e.tag.split('}')[-1] not in ['l','p']:continue
   a=parents.get(e);excluded=False
   while a is not None and a is not sp:
    if a.tag.split('}')[-1] in ['stage','note','l','p']:excluded=True;break
    a=parents.get(a)
   if not excluded and clean(spoken(e)):parts.append(clean(spoken(e)))
  if not parts:continue
  labels=[n.strip(' .,;:') for n in re.split(r',|\s+ET\s+|\s+et\s+',label) if n.strip(' .,;:')];who=[]
  for name in labels:
   # Collective labels are not silently expanded into individual roles.
   cid=slug(name)
   if not cid:continue
   who.append(cid);characters[cid]={'id':cid,'name':name.title(),'aliases':[name],'group':bool(re.search(r'CH[ŒO]EUR|TOUS|TOUTES|ENSEMBLE|REPRISE|LES |LA FOULE|VOIX',name.upper()))}
  if not who:who=['unattributed'];characters['unattributed']={'id':'unattributed','name':'Unattributed','aliases':[],'group':True}
  loc=[];a=parents.get(sp)
  while a is not None:
   if a.tag.endswith('}div'):
    h=a.find('t:head',N)
    if h is not None:loc.insert(0,txt(h))
   a=parents.get(a)
  segments.append({'id':f's{len(segments)+1:04}','order':len(segments)+1,'speakers':who,'speakerLabel':label,'location':' · '.join(loc),'form':'Verse' if sp.findall('.//t:l',N) else 'Prose / dialogue','text':'\n'.join(parts)})
 if not segments:print('Skipped empty',title);continue
 save({'id':slug(title+' '+composer.split()[-1]),'title':title,'composer':composer,'language':'French','lang':'fr-FR','characters':list(characters.values()),'segments':segments,'source':{'name':'École nationale des chartes · Libretti','url':'https://github.com/Chartes-TNAH/libretti/blob/master/'+meta['path'],'edition':txt(r.find('.//t:sourceDesc',N)),'license':'Libretti corpus CC0; historical text transcription adapted into passage playlists.','licenseUrl':'https://creativecommons.org/publicdomain/zero/1.0/'},'coverage':'Imported; role review pending','coverageNote':'All speech blocks in this French source have been imported. Speaker names were parsed automatically; collective labels remain separate. Variant names and shared lines need review against your score.','review':'Speaker and ensemble review pending'})
 print(title,len(segments),len(characters))
