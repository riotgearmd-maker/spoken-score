const $ = s => document.querySelector(s);
const normalize = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’']/g,'');
if ($('#search')) {
  const filter = () => {
    const words = normalize($('#search').value).split(/\s+/).filter(w => w && !['pronunciation','pronounciation','diction','lyrics','text'].includes(w));
    let count = 0;
    document.querySelectorAll('.work').forEach(row => {
      const match = words.every(w => normalize(row.dataset.search).includes(w)) && (!$('#language').value || row.dataset.language === $('#language').value);
      row.hidden = !match; row.style.display = match ? '' : 'none'; if(match) count++;
    });
    $('#count').textContent = `${count} ${count === 1 ? 'work' : 'works'}`;
    $('#empty').hidden = count !== 0;
  };
  $('#search').addEventListener('input', filter); $('#language').addEventListener('change', filter);
}
if (document.body.dataset.work) {
  let voices=[], token=0, current=null;
  $('#speed').replaceChildren(...[['1','1×'],['0.9','0.9×'],['0.8','0.8×'],['0.5','0.5×'],['0.4','0.4×']].map(([value,label])=>new Option(label,value,value==='1',value==='1')));
  const lines=[...document.querySelectorAll('.line')];
  const lang=$('.poem').lang;
  const status=message => $('#status').textContent=message;
  const clear=() => { lines.forEach(l=>l.classList.remove('active')); $('#stop').disabled=true; $('#play').textContent='▶ Preview full text'; };
  const stop=() => { token++; if('speechSynthesis' in window) speechSynthesis.cancel(); current=null; clear(); };
  function loadVoices(){
    const old=$('#voice').value;
    voices=speechSynthesis.getVoices().filter(v=>v.lang.toLowerCase().split(/[-_]/)[0]===lang.split('-')[0]);
    $('#voice').replaceChildren(...(voices.length ? voices.map(v=>new Option(v.name+' · '+v.lang,v.voiceURI)) : [new Option('No matching voice installed','')]));
    if(voices.some(v=>v.voiceURI===old)) $('#voice').value=old;
    $('#play').disabled=!voices.length; lines.forEach(l=>l.disabled=!voices.length);
    status(voices.length ? 'Device voice ready. Not reviewed for diction accuracy.' : 'No matching voice is available. Add a '+lang+' speech voice in your device settings, then reload.');
  }
  function speak(start,whole){
    stop(); if(!voices.length)return;
    const own=token;
    const next=i=>{
      if(own!==token)return;
      if(i>=lines.length){clear();status('Preview finished.');return;}
      lines.forEach(l=>l.classList.remove('active'));lines[i].classList.add('active');
      $('#stop').disabled=false;$('#play').textContent='↻ Restart full text';status(`Reading line ${i+1} of ${lines.length} · Device speech`);
      current=new SpeechSynthesisUtterance(lines[i].textContent);current.lang=lang;current.voice=voices.find(v=>v.voiceURI===$('#voice').value)||voices[0];current.rate=Number($('#speed').value);
      current.onend=()=>{if(own!==token)return;if(whole)next(i+1);else{clear();status('Line preview finished.');}};
      current.onerror=e=>{if(own!==token)return;clear();status('Speech could not play. Try another voice or browser.');};
      speechSynthesis.speak(current);
    };next(start);
  }
  if('speechSynthesis' in window){loadVoices();speechSynthesis.addEventListener('voiceschanged',loadVoices);$('#play').onclick=()=>speak(0,true);$('#stop').onclick=()=>{stop();status('Preview stopped.');};lines.forEach((l,i)=>l.onclick=()=>speak(i,false));$('#voice').onchange=()=>{stop();status('Voice selected. Ready to preview.');};$('#speed').onchange=()=>{stop();status('Speed changed. Restart the preview to listen.');};window.addEventListener('pagehide',stop);}
  else{$('#voice').replaceChildren(new Option('Speech preview not supported',''));status('This browser does not support device speech. The full text is available below.');}
}
