"""Add and validate romanization for non-Latin libretto text."""
from pathlib import Path
import json, re

CYRILLIC = re.compile(r"[\u0400-\u04ff]")
NON_LATIN = re.compile(r"[\u0370-\u052f\u0590-\u08ff\u0900-\u109f\u1780-\u18af\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
RU = {"а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo","ж":"zh","з":"z","и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya"}

def russian(text):
    out=[]
    for ch in text:
        value=RU.get(ch.lower())
        if value is None: out.append(ch); continue
        out.append(value.upper() if ch.isupper() else value)
    return "".join(out)

def transliterate(text):
    if not NON_LATIN.search(text or ""): return ""
    if CYRILLIC.search(text or ""): return russian(text)
    return ""

def enrich_opera(opera):
    for field in ("title","composer"):
        if NON_LATIN.search(opera.get(field,"")):
            key="romanized"+field.title()
            opera[key]=opera.get(key) or transliterate(opera[field])
            if not opera[key]: raise ValueError(f'{opera["id"]}: romanization required for {field}')
    for character in opera["characters"]:
        if NON_LATIN.search(character["name"]):
            character["romanizedName"] = transliterate(character["name"])
            if not character["romanizedName"]: raise ValueError(f'{opera["id"]}: romanization required for character {character["name"]}')
    for segment in opera["segments"]:
        if NON_LATIN.search(segment.get("location","")):
            segment["romanizedLocation"] = segment.get("romanizedLocation") or transliterate(segment["location"])
            if not segment["romanizedLocation"]: raise ValueError(f'{opera["id"]}: romanization required for passage location')
        if NON_LATIN.search(segment["speakerLabel"]):
            segment["romanizedSpeakerLabel"] = transliterate(segment["speakerLabel"])
            if not segment["romanizedSpeakerLabel"]: raise ValueError(f'{opera["id"]}: romanization required for speaker label')
        if NON_LATIN.search(segment["text"]):
            segment["romanizedText"] = transliterate(segment["text"])
            if not segment["romanizedText"]: raise ValueError(f'{opera["id"]}: romanization required for passage {segment["id"]}')
    return opera

if __name__ == "__main__":
    root=Path(__file__).resolve().parents[1]
    for path in (root/"data/operas").glob("*.json"):
        opera=json.loads(path.read_text())
        before=json.dumps(opera,ensure_ascii=False,sort_keys=True)
        enrich_opera(opera)
        if json.dumps(opera,ensure_ascii=False,sort_keys=True)!=before:
            path.write_text(json.dumps(opera,ensure_ascii=False,separators=(",",":")))
            print(path.name)
