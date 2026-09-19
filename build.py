import json, pathlib, html
root=pathlib.Path(__file__).parent
works=[dict(slug='che-gelida-manina',title='Che gelida manina',composer='Giacomo Puccini',collection='La bohème · Act I · Rodolfo',kind='Aria',language='Italian',lang='it-IT',author='Luigi Illica & Giuseppe Giacosa',regions=['Northern Italian','Central Italian','Roman'],text='''Che gelida manina,
se la lasci riscaldar.
Cercar che giova?
Al buio non si trova.
Ma per fortuna
è una notte di luna,
e qui la luna
l’abbiamo vicina.

Aspetti, signorina,
le dirò con due parole
chi son, che faccio,
e come vivo. Vuole?

Chi son? Sono un poeta.
Che cosa faccio? Scrivo.
E come vivo? Vivo.
In povertà mia lieta
scialo da gran signore
rime ed inni d’amore.
Per sogni e per chimere
e per castelli in aria,
l’anima ho milionaria.
Talor dal mio forziere
ruban tutti i gioielli
due ladri, gli occhi belli.
V’entrar con voi pur ora,
ed i miei sogni usati
e i bei sogni miei,
tosto si dileguar!
Ma il furto non m’accora,
poiché, poiché v’ha preso stanza
la speranza!

Or che mi conoscete,
parlate voi, deh! parlate. Chi siete?
Vi piaccia dir!'''),dict(slug='an-die-musik',title='An die Musik',composer='Franz Schubert',collection='D. 547 · Op. 88, No. 4',kind='Art song',language='German',lang='de-DE',author='Franz von Schober',regions=['Northern German','Austrian','Swiss German'],text='''Du holde Kunst, in wie viel grauen Stunden,
Wo mich des Lebens wilder Kreis umstrickt,
Hast du mein Herz zu warmer Lieb’ entzunden,
Hast mich in eine beßre Welt entrückt!

Oft hat ein Seufzer, deiner Harf’ entflossen,
Ein süßer, heiliger Akkord von dir,
Den Himmel beßrer Zeiten mir erschlossen,
Du holde Kunst, ich danke dir dafür!'''),dict(slug='apres-un-reve',title='Après un rêve',composer='Gabriel Fauré',collection='Trois mélodies · Op. 7, No. 1',kind='Art song',language='French',lang='fr-FR',author='Romain Bussine',regions=['Parisian French','Southern French','Belgian French'],text='''Dans un sommeil que charmait ton image,
Je rêvais le bonheur, ardent mirage,
Tes yeux étaient plus doux, ta voix pure et sonore,
Tu rayonnais comme un ciel éclairé par l’aurore;

Tu m’appelais et je quittais la terre
Pour m’enfuir avec toi vers la lumière,
Les cieux pour nous entr’ouvraient leurs nues,
Splendeurs inconnues, lueurs divines entrevues,

Hélas! Hélas! triste réveil des songes!
Je t’appelle, ô nuit, rends-moi tes mensonges;
Reviens, reviens radieuse,
Reviens, ô nuit mystérieuse!''')]
(root/'dist/works.json').write_text(json.dumps(works,ensure_ascii=False))
css='''*{box-sizing:border-box}body{margin:0;background:#fafaf7;color:#242521;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5}a{color:inherit}button,input,select{font:inherit}button,a,input,select{touch-action:manipulation}button{cursor:pointer}button:disabled{cursor:default}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #3557dc;outline-offset:4px}header{height:94px;display:flex;align-items:center;justify-content:space-between;max-width:1440px;margin:auto;padding:0 5%;border-bottom:1px solid #d9d9d0}.brand{font-family:Georgia,serif;font-size:29px;text-decoration:none;letter-spacing:-1px}.brand i{color:#3155ce}.edition{font-size:12px;letter-spacing:2px;text-transform:uppercase}main{max-width:1320px;margin:auto;padding:48px 32px 90px}.eyebrow{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#61635b}.intro{display:flex;justify-content:space-between;align-items:end;gap:30px;margin-bottom:34px}.intro h1{font-family:Georgia,serif;font-size:54px;font-weight:400;letter-spacing:-2px;margin:0}.intro p{max-width:380px;color:#65665f}.search{display:flex;gap:16px;align-items:center;margin:26px 0}.search input{background:#fff;border:1px solid #bcbeb2;border-radius:4px;padding:17px 20px;flex:1;min-width:0}.search select{padding:17px 14px;border:1px solid #bcbeb2;background:transparent;border-radius:4px}.catalog-head{display:flex;justify-content:space-between;border-top:1px solid #cccfc2;padding:20px 0;color:#686a60;font-size:14px}.work{display:grid;grid-template-columns:70px 1.5fr 1fr 120px 25px;gap:20px;align-items:center;padding:29px 12px;border-top:1px solid #dadcd3;text-decoration:none}.work:hover{background:#eff1e8}.work strong{display:block;font-family:Georgia,serif;font-size:27px;font-weight:400}.work small{font-size:14px;color:#74766c}.num{font-family:Georgia,serif;font-style:italic;color:#77796f;font-size:23px}.lang{font-size:14px}.arrow{color:#3155ce;font-size:25px}.note{border-left:3px solid #3155ce;padding:2px 20px;max-width:690px;margin-top:48px;color:#66685f;font-size:14px}.crumb{font-size:14px;color:#686b62;text-decoration:none}.title{padding:25px 0 36px;border-bottom:1px solid #cccfc2}.title h1{font:400 clamp(38px,5vw,62px)/1.13 Georgia,serif;letter-spacing:-2px;margin:12px 0 17px}.title p{margin:0;color:#65675e}.title .tags{display:flex;gap:12px;align-items:center}.pill{background:#e9eddb;padding:4px 10px;border-radius:3px;font-size:12px;letter-spacing:1px;text-transform:uppercase}.workspace{display:grid;grid-template-columns:minmax(0,1fr) 390px;gap:70px;align-items:start;padding-top:34px}.section-label{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}.section-label h2{font-size:12px;letter-spacing:2px;text-transform:uppercase;font-weight:400;margin:0}.section-label span{font-size:12px;color:#77796f}.poem{padding:4px 0}.stanza{margin-bottom:28px}.line{display:block;text-align:left;border:0;border-left:2px solid transparent;background:transparent;padding:4px 12px;font-family:Georgia,serif;font-size:23px;line-height:1.48;width:100%;color:#33352e}.line:hover{background:#ecf0df}.line.active{border-color:#3557dc;background:#edf0fa;color:#2546b2}.line:disabled{opacity:1}.credit{font-size:13px;color:#77796f;margin-top:34px}aside{position:sticky;top:25px}.listen{background:#eef0e5;border:1px solid #dde0d2;border-radius:5px;padding:25px}.listen h2{font:400 27px Georgia,serif;margin:0 0 8px}.listen .sub{font-size:14px;color:#676b5e;margin:0 0 23px}.voice-label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:1.5px;margin:20px 0 9px}.listen select{width:100%;padding:12px 8px;border:1px solid #b6bcaa;border-radius:3px;background:#fafbf5;color:#333}.controls{display:flex;gap:8px;margin:18px 0}.primary{flex:1;background:#2e50c5;color:white;border:0;padding:14px;border-radius:3px}.stop{background:transparent;border:1px solid #b6bcaa;padding:10px 14px;border-radius:3px}.primary:disabled{background:#a9afa0;color:#fff}.speed{display:flex;justify-content:space-between;align-items:center;font-size:14px}.speed select{width:94px;padding:6px}.status{font-size:13px;min-height:38px;color:#555e4b;margin:16px 0 0}.regional{margin-top:26px}.regional h3{font-size:14px;font-weight:500;margin:0}.regional>p{font-size:13px;color:#77796f;margin:4px 0 14px}.region{border-top:1px solid #d8dbce;padding:13px 0;display:flex;justify-content:space-between;gap:10px;font-size:14px}.region span{color:#7b7e73;font-size:12px}.aside-note{font-size:13px;color:#707568;padding:0 5px;margin-top:21px}.aside-note strong{color:#41473a;font-weight:500}footer{border-top:1px solid #d9d9d0;max-width:1320px;margin:auto;padding:23px 32px;display:flex;justify-content:space-between;gap:20px;color:#76796e;font-size:12px}.empty{padding:40px 0}.sr-only{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip:rect(0,0,0,0)}@media(max-width:850px){.workspace{grid-template-columns:1fr;gap:35px}.workspace aside{position:static;grid-row:1}.work{grid-template-columns:35px 1fr 80px}.work .composer,.work .arrow{display:none}.intro{display:block}.intro h1{font-size:42px}.intro p{max-width:none}.edition{font-size:10px;letter-spacing:1px}main{padding:30px 20px 60px}.line{font-size:21px}.title h1{letter-spacing:-1px}.search{flex-wrap:wrap}.search input{flex-basis:100%}.search select{padding:10px}.section-label span{display:none}.brand{font-size:25px}.work strong{font-size:23px}.work{gap:12px;padding:22px 0}footer{padding:20px;flex-wrap:wrap}}'''
(root/'dist/style.css').write_text(css)
def wrap(title,body,slug=''):
 return '<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' | Spoken Score</title><meta name="description" content="Explore aria and art song texts and a prototype spoken pronunciation workspace. Regional AI recordings are not yet available."><link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script></head><body data-work="'+slug+'"><header><a class="brand" href="/">Spoken <i>Score</i></a><span class="edition">The diction collection · Prototype</span></header><main>'+body+'</main><footer><span>Spoken Score</span><span>Original words. A closer listen.</span><span>AI recording collection in development</span></footer></body></html>'
rows=''
for i,w in enumerate(works):
 rows+=f'<a class="work" data-search="{html.escape(w["title"]+" "+w["composer"]+" "+w["collection"]+" "+w["language"]+" "+w["text"],quote=True)}" data-language="{w["language"]}" href="/works/{w["slug"]}/"><span class="num">0{i+1}</span><div><strong>{w["title"]}</strong><small>{w["collection"]}</small></div><div class="composer">{w["composer"]}<br><small>{w["kind"]}</small></div><span class="lang">{w["language"]}</span><span class="arrow" aria-hidden="true">↗</span></a>'
body='''<div class="intro"><div><div class="eyebrow">Aria & art song</div><h1>Begin with the words.</h1></div><p>A listening workspace for the texts you sing. Find a work, open the text, and explore its spoken language.</p></div><div class="search"><label class="sr-only" for="search">Search title, composer, or text</label><input id="search" type="search" placeholder="Search a title, composer, or first line…" autocomplete="off"><label class="sr-only" for="language">Language</label><select id="language"><option value="">All languages</option><option>Italian</option><option>French</option><option>German</option></select></div><div class="catalog-head"><span>The collection</span><span id="count" role="status">3 works</span></div><div id="results">'''+rows+'''</div><p class="empty" id="empty" hidden>No works found. Try “Puccini,” “An die Musik,” or another title in this small collection.</p><div class="note"><strong>A first look at Spoken Score.</strong><br>Full original texts are available. Listening currently uses your device’s synthetic voices, where supported. Reviewed regional AI recordings are not yet available.</div>'''
(root/'dist/index.html').write_text(wrap('Aria & art song diction',body))
for w in works:
 lines='';n=0
 for stanza in w['text'].split('\n\n'):
  lines+='<div class="stanza">'
  for line in stanza.split('\n'):
   lines+=f'<button class="line" data-line="{n}" disabled title="Preview this line with a device voice">{html.escape(line)}</button>';n+=1
  lines+='</div>'
 regions=''.join(f'<div class="region">{r}<span>Not recorded yet</span></div>' for r in w['regions'])
 body=f'''<a class="crumb" href="/">← All works</a><div class="title"><div class="tags"><span class="pill">{w['language']}</span><span class="eyebrow">{w['kind']}</span></div><h1>{w['title']}</h1><p>{w['composer']} &nbsp; / &nbsp; {w['collection']}</p></div><div class="workspace"><section aria-label="Original text"><div class="section-label"><h2>Original text</h2><span>Select a line to preview it</span></div><div class="poem" lang="{w['lang']}">{lines}</div><p class="credit">Text: {w['author']}<br>Original-language text; musical repetitions omitted.</p></section><aside><div class="listen"><h2>Hear the words.</h2><p class="sub">Device speech preview · {w['language']}</p><label class="voice-label" for="voice">Available device voice</label><select id="voice"><option>Checking available voices…</option></select><div class="controls"><button id="play" class="primary" disabled>▶ Preview full text</button><button id="stop" class="stop" disabled>Stop</button></div><div class="speed"><label for="speed">Reading speed</label><select id="speed"><option value="0.7">Slow</option><option value="0.85">Relaxed</option><option value="1" selected>Normal</option></select></div><p class="status" id="status" role="status">Looking for a {w['language']} voice on your device.</p><div class="regional"><h3>Regional AI recordings</h3><p>Planned voices for this text</p>{regions}</div></div><p class="aside-note"><strong>Listen in the language of the text.</strong> Regional voices follow the text’s language, regardless of where the opera is set.</p><p class="aside-note">This preview is synthetic speech, not a native-speaker recording or a reviewed diction reference. Device voices do not establish regional accents. Regional speech and standard diction for singing may differ.</p></aside></div>'''
 path=root/'dist/works'/w['slug'];path.mkdir(parents=True,exist_ok=True);(path/'index.html').write_text(wrap(w['title']+' pronunciation',body,w['slug']))
