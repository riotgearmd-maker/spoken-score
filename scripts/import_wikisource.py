"""Import verified public-domain opera libretti from Wikisource.

The source pages use three recurring structures: speaker + indented verse
(French/Czech), explicit speaker divs (Russian), and inline labels (English and
Russian).  Stage directions are intentionally not turned into spoken passages.
"""
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
import hashlib, json, re, unicodedata
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/operas"
CACHE = ROOT / "data/sources/wikisource"
CACHE.mkdir(parents=True, exist_ok=True)

def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()

def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()).strip("-")

def page_html(lang, page):
    # Non-Latin titles can collapse to the same ASCII slug, so retain a digest.
    key = f"{lang}-{slug(page) or 'page'}-{hashlib.sha1(page.encode()).hexdigest()[:10]}.json"
    path = CACHE / key
    if not path.exists():
        url = f"https://{lang}.wikisource.org/w/api.php?" + urlencode({"action":"parse", "page":page, "prop":"text", "format":"json"})
        path.write_bytes(urlopen(Request(url, headers={"User-Agent":"SpokenScore/0.2 (public-domain libretto research)"}), timeout=60).read())
    return html.fromstring(json.loads(path.read_text())["parse"]["text"]["*"])

def visible(node):
    for bad in node.xpath('.//style|.//script|.//*[contains(concat(" ",normalize-space(@class)," ")," ws-noexport ")]'):
        if bad.getparent() is not None: bad.getparent().remove(bad)
    return clean(" ".join(node.itertext()))

def nearest_label(dl):
    node = dl.getprevious()
    while node is not None and node.tag == "dl": node = node.getprevious()
    return visible(node) if node is not None else ""

def parse_indented(root, acts=False):
    segments=[]; location=""
    for node in root.xpath('.//*[self::h2 or self::h3 or self::h4 or self::dl]'):
        if node.tag in ("h2","h3","h4"):
            heading=visible(node)
            if heading: location=heading
            continue
        if node.xpath('ancestor::dl'): continue
        label=nearest_label(node)
        label=re.sub(r"^.*?\}\s*", "", label).strip(" .:")
        # Parenthetical cues are stage directions, not additional characters.
        label=clean(label.split("(",1)[0]).strip(" .:")
        if (not label or len(label)>90 or label.startswith("(") or
            label[0].islower() or re.fullmatch(r"[IVX]+",label) or
            re.search(r"^(reprise|cavatine|ensemble)$",label,re.I)): continue
        text=visible(node)
        if not text: continue
        segments.append((label, text, location))
    return segments

def parse_poem(root):
    out=[]; location=""
    for node in root.xpath('.//*[self::h2 or self::h3 or self::h4 or (self::div and contains(concat(" ",normalize-space(@class)," ")," poem "))]'):
        if node.tag in ("h2","h3","h4"):
            location=visible(node); continue
        speaker=""
        for child in node:
            cls=child.get("class","").split()
            if child.tag=="div" and "re" in cls:
                speaker=visible(child).strip(" .:")
            elif child.tag=="p" and speaker:
                text=visible(child)
                if text: out.append((speaker,text,location))
    return out

def parse_inline(roots, labels, start_marker=None):
    pattern=re.compile(r"(?<!\w)("+"|".join(sorted(map(re.escape,labels),key=len,reverse=True))+r")\s*(?:\([^)]*\))?\s*[.,:]",re.I)
    out=[]; location=""; started=not start_marker
    for root in roots:
        for node in root.xpath('.//*[self::h2 or self::h3 or self::h4 or self::p]'):
            text=visible(node)
            if node.tag in ("h2","h3","h4"):
                location=text
                if start_marker and start_marker.lower() in text.lower(): started=True
                continue
            if start_marker and start_marker.lower() in text.lower(): started=True
            if not started: continue
            hits=list(pattern.finditer(text))
            for i,m in enumerate(hits):
                body=clean(text[m.end():hits[i+1].start() if i+1<len(hits) else len(text)])
                if body: out.append((m.group(1),body,location))
    return out

def make(spec, raw):
    aliases=spec.get("role_aliases",{})
    def canonical(label):
        bare=clean(re.sub(r"\([^)]*\)","",label)).strip(" .:")
        return aliases.get(bare.casefold(), bare)
    chars=[]; ids={}
    def cid_for(label):
        name=canonical(label); key=name.casefold()
        if key not in ids:
            base=slug(name) or "ensemble"; cid=base; n=2
            while cid in ids.values(): cid=f"{base}-{n}";n+=1
            ids[key]=cid; chars.append({"id":cid,"name":name,"aliases":[label] if label!=name else [],"group":bool(re.search(r"chor|choeur|sbor|народ|гости|девуш|ратник|рыбак|women|nymph|sailor",name,re.I))})
        return ids[key]
    segments=[]
    for label,text,loc in raw:
        speakers=[]
        label=re.sub(r"\([^)]*$","",label)
        for part in re.split(r"\s*(?:,|;|\.(?=\s*[A-ZÁ-Ž])|\bet\b|\ba\b|\band\b|\s+и\s+)\s*",label,flags=re.I):
            if canonical(part): speakers.append(cid_for(part.strip()))
        if not speakers: continue
        segments.append({"id":f"s{len(segments)+1:04}","order":len(segments)+1,"speakers":speakers,"speakerLabel":label,"location":loc,"form":"Libretto text","text":text})
    assert len(segments)>10, (spec["title"],len(segments))
    url=f'https://{spec["wiki"]}.wikisource.org/wiki/{quote(spec["pages"][0].replace(" ","_"))}'
    obj={"id":spec["id"],"title":spec["title"],"composer":spec["composer"],"language":spec["language"],"lang":spec["lang"],"characters":chars,"segments":segments,"source":{"name":spec["source"],"url":url,"edition":spec["edition"],"license":"Public-domain historical libretto; Wikisource transcription","licenseUrl":url},"coverage":"Full source libretto imported","coverageNote":"All explicitly attributed speech in this public-domain source edition is imported in source order. Stage directions are excluded. Check against your score for cuts, revisions, spelling variants, and musical repetitions.","review":"Source-structured; score comparison pending"}
    obj["segmentCount"]=len(segments);obj["characterCount"]=len(chars);obj["textHash"]=hashlib.sha256(json.dumps(segments,ensure_ascii=False).encode()).hexdigest()
    (OUT/f'{obj["id"]}.json').write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":")))
    print(obj["title"],len(chars),len(segments))

SPECS=[
 {"id":"les-pecheurs-de-perles-bizet","title":"Les pêcheurs de perles","composer":"Georges Bizet","language":"French","lang":"fr-FR","wiki":"fr","pages":["Les Pêcheurs de perles"],"parser":"indent","source":"French Wikisource","edition":"1863 libretto by Eugène Cormon and Michel Carré","allowed":["Chœur","Le chœur des pêcheurs","Reprise du chœur","Les pêcheurs","Le chœur des femmes","Zurga","Nadir","Nourabad","Leila","Leïla","Tous les pêcheurs","Les fakirs"],"role_aliases":{"le chœur":"Chœur","chœur":"Chœur","le chœur des pêcheurs":"Chœur des pêcheurs","reprise du chœur":"Chœur","les pêcheurs":"Chœur des pêcheurs","le chœur des femmes":"Chœur des femmes","leila":"Leïla","tous les pêcheurs":"Chœur des pêcheurs","les fakirs":"Fakirs"}},
 {"id":"dido-and-aeneas-purcell","title":"Dido and Aeneas","composer":"Henry Purcell","language":"English","lang":"en-GB","wiki":"en","pages":["Dido and Aeneas (1689)"],"parser":"inline","source":"English Wikisource","edition":"1689 libretto by Nahum Tate","start":"ACT the Firſt","role_aliases":{"bel":"Belinda","cho":"Chorus","æn":"Aeneas","sorc":"Sorceress","incha":"Enchantresses","spir":"Spirit","2 d. wom":"Second Woman","2 women":"Second Woman"},"labels":["Bel.","Bel","Dido","2 Women","Cho.","Cho","Æn.","Æn","Sorc.","Sorc","Incha.","Incha","2 d. Wom.","Spir.","Spir"]},
 {"id":"eugene-onegin-tchaikovsky","title":"Eugene Onegin","composer":"Pyotr Ilyich Tchaikovsky","language":"Russian","lang":"ru-RU","wiki":"ru","pages":["Евгений Онегин (опера)/Действие первое","Евгений Онегин (опера)/Действие второе","Евгений Онегин (опера)/Действие третье"],"parser":"inline","source":"Russian Wikisource","edition":"Libretto by Tchaikovsky and Konstantin Shilovsky","labels":["ТАТЬЯНА, ОЛЬГА","ЛАРИНА, ФИЛИППЬЕВНА","ТАТЬЯНА","ОЛЬГА","ЛАРИНА","ФИЛИППЬЕВНА","ЛЕНСКИЙ","ОНЕГИН","ГРЕМИН","ЗАРЕЦКИЙ","ТРИКЕ","РОТНЫЙ","ГОСТИ","ДЕВУШКИ","КРЕСТЬЯНЕ","МУЖЧИНЫ","ЖЕНЩИНЫ"]},
 {"id":"rusalka-dvorak","title":"Rusalka","composer":"Antonín Dvořák","language":"Czech","lang":"cs-CZ","wiki":"cs","pages":["Rusalka"],"parser":"indent","source":"Czech Wikisource","edition":"1901 libretto by Jaroslav Kvapil","role_aliases":{"ježiaba":"Ježibaba"}},
 {"id":"the-bartered-bride-smetana","title":"The Bartered Bride (Prodaná nevěsta)","composer":"Bedřich Smetana","language":"Czech","lang":"cs-CZ","wiki":"cs","pages":["Prodaná nevěsta"],"parser":"indent","source":"Czech Wikisource","edition":"1872 Czech libretto by Karel Sabina"},
 {"id":"prince-igor-borodin","title":"Prince Igor","composer":"Alexander Borodin","language":"Russian","lang":"ru-RU","wiki":"ru","pages":["Князь Игорь (Бородин)/Либретто"],"parser":"poem","source":"Russian Wikisource","edition":"Opera libretto by Alexander Borodin"},
]

def main():
    for spec in SPECS:
        roots=[page_html(spec["wiki"],p) for p in spec["pages"]]
        if spec["parser"]=="indent": raw=parse_indented(roots[0])
        elif spec["parser"]=="poem": raw=parse_poem(roots[0])
        else: raw=parse_inline(roots,spec["labels"],spec.get("start"))
        if spec.get("allowed"):
            allowed={x.casefold() for x in spec["allowed"]}
            raw=[x for x in raw if x[0].strip(" .:").casefold() in allowed]
        make(spec,raw)

if __name__=="__main__": main()
