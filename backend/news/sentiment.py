import re

POSITIVE={"beat","growth","upgrade","profit","record","strong","positive","surge","outperform","buyback"}
NEGATIVE={"miss","loss","downgrade","lawsuit","weak","negative","decline","fraud","cut","warning"}

def score_headline(text:str)->dict:
    words=set(re.findall(r"[a-z]+",text.lower()))
    pos=len(words&POSITIVE); neg=len(words&NEGATIVE); total=pos+neg
    score=0 if total==0 else (pos-neg)/total
    return {"score":score,"label":"positive" if score>.2 else "negative" if score<-.2 else "neutral","positive_hits":pos,"negative_hits":neg}
