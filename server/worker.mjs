// Corpus and public files are injected by scripts/build.py. No browser credentials.
export const normalize = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/ß/g,'ss').replace(/[’']/g,'');
const json=(value,status=200)=>Response.json(value,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
const publicError=(message,status=400)=>json({error:message},status);
const inflight=new Map();
const model=()=> 'Kokoro-82M';
const voiceCatalog=[{id:'im_nicola',name:'Nicola',labels:{language:'Italian',accent:'Standard Italian',review:'Geminate consonant test passed'},languages:['it'],description:'Selected after comparative testing for reliable Italian doubled consonants.'}];
const voices=env=>env.KOKORO_API_URL?voiceCatalog:null;
const summarize=o=>({id:o.id,title:o.title,romanizedTitle:o.romanizedTitle||'',composer:o.composer,romanizedComposer:o.romanizedComposer||'',language:o.language,kind:o.kind||'Opera',characterCount:o.characters.length,segmentCount:o.segments.length,coverage:o.coverage,characters:o.characters.map(c=>({id:c.id,name:c.name,romanizedName:c.romanizedName||'',aliases:c.aliases||[],group:!!c.group}))});
export function selectRole(opera,role,includeProse=true){return opera.segments.filter(s=>s.speakers.includes(role)&&(includeProse||s.form!=='Prose / dialogue'));}
export function searchCorpus(corpus,params){
 const q=normalize(params.get('q')||'').trim().split(/\s+/).filter(w=>w&&!['pronunciation','pronounciation','lyrics','diction'].includes(w));
 const language=params.get('language'),composer=params.get('composer'),mode=params.get('mode')||'operas';
 const base=corpus.filter(o=>(!language||o.language===language)&&(!composer||o.composer===composer)&&(mode==='texts'?o.kind==='Aria'||o.kind==='Art song':!o.kind));
 let rows=[];
 for(const o of base){
  const common=normalize(o.title+' '+(o.romanizedTitle||'')+' '+o.composer+' '+(o.romanizedComposer||'')+' '+o.language+' '+(o.aliases||[]).join(' '));
  if(mode==='characters'){
   for(const c of o.characters){if(c.group)continue;const hay=common+' '+normalize(c.name+' '+(c.romanizedName||'')+' '+(c.aliases||[]).join(' '));if(q.every(w=>hay.includes(w)))rows.push({...summarize(o),role:c,passages:selectRole(o,c.id).length});}
  }else{
   const roles=normalize(o.characters.map(c=>c.name+' '+(c.romanizedName||'')+' '+(c.aliases||[]).join(' ')).join(' '));const metadata=common+' '+roles;
   let match=q.every(w=>metadata.includes(w)),snippet='';
   if(!match&&q.length){const full=normalize(o.segments.map(s=>s.text+' '+(s.romanizedText||'')).join(' '));match=q.every(w=>(metadata+' '+full).includes(w));if(match){const s=o.segments.find(s=>q.some(w=>normalize(s.text+' '+(s.romanizedText||'')).includes(w)));snippet=s?.text.slice(0,180)||'';}}
   if(match)rows.push({...summarize(o),snippet});
  }
 }
 rows.sort((a,b)=>a.title.localeCompare(b.title)||String(a.role?.name).localeCompare(String(b.role?.name)));
 const offset=Math.max(0,Number(params.get('offset'))||0),limit=40;
 return {total:rows.length,offset,limit,rows:rows.slice(offset,offset+limit)};
}
async function speech(request,env,corpus){
 if(!env.KOKORO_API_URL)return publicError('Kokoro is selected but its speech service is not connected yet.',503);
 if(!env.BUCKET)return publicError('Audio storage is unavailable. No speech was generated.',503);
 const origin=request.headers.get('Origin');if(origin&&origin!==new URL(request.url).origin)return publicError('Cross-site request rejected.',403);
 if(Number(request.headers.get('Content-Length')||0)>4000)return publicError('Request too large.',413);
 const raw=await request.text();if(raw.length>4000)return publicError('Request too large.',413);
 let data;try{data=JSON.parse(raw)}catch{return publicError('Invalid request.');}
 const o=corpus.find(o=>o.id===data.opera),s=o?.segments.find(s=>s.id===data.segment);
 if(!s)return publicError('This libretto passage was not found.',404);
 const chunks=splitText(s.text),part=Number(data.part||0);if(!Number.isInteger(part)||part<0||part>=chunks.length)return publicError('Invalid passage part.');
 const available=voices(env);if(!available.some(v=>v.id===data.voice))return publicError('Select an available Kokoro voice.');
 if(o.lang.split('-')[0]!=='it')return publicError('The selected Kokoro voice is currently approved for Italian texts only.',400);
 const text=chunks[part];const key=await hash([model(),data.voice,o.lang,text].join('\n'));
 const path='speech/'+key+'.mp3';const stored=await env.BUCKET.get(path);
 if(stored)return new Response(stored.body,{headers:{'Content-Type':'audio/mpeg','Cache-Control':'private, max-age=31536000','X-Audio-Source':'cached'}});
 if(inflight.has(key)){await inflight.get(key);const saved=await env.BUCKET.get(path);if(saved)return new Response(saved.body,{headers:{'Content-Type':'audio/mpeg'}});}
 const work=(async()=>{
  const headers={'Content-Type':'application/json'};if(env.KOKORO_API_KEY)headers.Authorization='Bearer '+env.KOKORO_API_KEY;
  const r=await fetch(env.KOKORO_API_URL,{method:'POST',headers,body:JSON.stringify({text,voice:data.voice,language:'it',speed:1,format:'mp3'}),signal:AbortSignal.timeout(60000)});
  if(!r.ok)throw new Error(r.status===401?'The Kokoro service rejected its API key.':r.status===429?'The Kokoro service is busy.':'Kokoro could not generate this passage.');
  const audio=await r.arrayBuffer();if(!audio.byteLength)throw new Error('Kokoro returned empty audio.');
  await env.BUCKET.put(path,audio,{httpMetadata:{contentType:'audio/mpeg'},customMetadata:{opera:o.id,segment:s.id,voice:data.voice,model:model()}});return audio;
 })();inflight.set(key,work);
 try{return new Response(await work,{headers:{'Content-Type':'audio/mpeg','Cache-Control':'private, max-age=31536000','X-Audio-Source':'generated'}});}finally{inflight.delete(key);}
}
export function splitText(text,max=1800){
 const chunks=[];let current='';
 for(const line of text.split(/\n/)){
  if((current+' '+line).length>max&&current){chunks.push(current.trim());current='';}
  if(line.length>max){const words=line.split(/\s+/);for(const word of words){if((current+' '+word).length>max){chunks.push(current.trim());current='';}current+=(current?' ':'')+word;}}
  else current+=(current?'\n':'')+line;
 }
 if(current.trim())chunks.push(current.trim());return chunks;
}
async function hash(s){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export function createApp(corpus,assets){
 return {async fetch(request,env){
  const u=new URL(request.url),p=u.pathname;
  try{
   if(p==='/api/search'&&request.method==='GET')return json(searchCorpus(corpus,u.searchParams));
   if(p==='/api/catalog'&&request.method==='GET')return json({operas:corpus.filter(o=>!o.kind).length,characters:corpus.reduce((n,o)=>n+o.characters.filter(c=>!c.group).length,0),passages:corpus.reduce((n,o)=>n+o.segments.length,0),composers:[...new Set(corpus.map(o=>o.composer))].sort(),languages:[...new Set(corpus.map(o=>o.language))].sort()});
   if(p.startsWith('/api/opera/')&&request.method==='GET'){const o=corpus.find(o=>o.id===decodeURIComponent(p.slice(11)));return o?json(o):publicError('Opera not found.',404);}
   if(p==='/api/voices'&&request.method==='GET'){const v=voices(env);return json({provider:'Kokoro',connected:v!==null,model:model(),voices:v||voiceCatalog,message:v===null?'Kokoro is selected. A compatible speech endpoint is still required.':''});}
   if(p==='/api/speech'&&request.method==='POST')return await speech(request,env,corpus);
   if(p.startsWith('/api/'))return publicError('Endpoint not found.',404);
   if(!['GET','HEAD'].includes(request.method))return publicError('Method not allowed.',405);
   let asset=assets[p]||assets[p.replace(/\/$/,'')+'/index.html'];
   if(p.startsWith('/operas/')||p.startsWith('/characters/')||p.startsWith('/works/')){
    const id=p.split('/')[2];if(!corpus.some(o=>o.id===id))return new Response('Opera not found',{status:404});asset=assets['/opera.html'];
   }
   if(!asset)return new Response('Page not found',{status:404});
   return new Response(request.method==='HEAD'?null:asset.body,{headers:{'Content-Type':asset.type,'X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'}});
  }catch(e){console.error('Request failed:',e.message);return publicError(e.message==='The operation was aborted due to timeout'?'The voice service timed out. Please try again.':e.message||'Service unavailable. Please try again.',502);}
 }};
}
