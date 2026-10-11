#!/usr/bin/env python3
"""Audit independent CEFR headword matches vs cefrpy *estimated* levels.
Aggregates only; never exports third-party word rows."""
import collections,json,pathlib,urllib.request
from cefrpy import CEFRAnalyzer
from build_eiken_crosswalk import UPSTREAM,load_cefr,norm
LEVELS=("A1","A2","B1","B2","C1","C2")
def main():
    root=pathlib.Path("vocabulary/raw")
    cefr=load_cefr([root/"cefrj-vocabulary-profile-1.5.csv",root/"octanove-vocabulary-profile-c1c2-1.0.csv"])
    analyzer=CEFRAnalyzer()
    words={}
    with urllib.request.urlopen(UPSTREAM,timeout=120) as response:
        for line in response:
            try: row=json.loads(line)
            except ValueError:continue
            word=row.get("word")
            if not isinstance(word,str) or not word.strip() or row.get("isTypo") or row.get("isPhrase"):continue
            count=(row.get("count") or {}).get("1")
            if isinstance(count,(int,float)) and count>0:
                words[norm(word)]=True
    counts=collections.Counter(); bands=collections.Counter()
    for word in words:
        counts["total"]+=1
        if cefr.get(word):
            counts["original_matched"]+=1
            continue
        counts["original_unmatched"]+=1
        level=analyzer.get_average_word_level_CEFR(word)
        if level is None:
            counts["still_unmatched"]+=1
        else:
            level=str(level).upper().strip()
            if level in LEVELS:
                counts["estimated_matched"]+=1
                bands[level]+=1
            else:
                counts["still_unmatched"]+=1
                counts["unexpected_level"]+=1
    result={"source":"cefrpy (model-estimated; partly CEFR-J-derived, NOT independent evidence)",
            "baseline":"CEFR-J v1.5 + Octanove v1.0 exact headword",
            "counts":dict(counts),"estimated_levels_for_baseline_unmatched":dict(bands),
            "cautions":["Estimated CEFR labels must not be merged with source-attested CEFR labels.",
            "Word-level average ignores sense and POS; diagnostic coverage only.",
            "No raw external word list stored."]}
    path=pathlib.Path("vocabulary/analysis/cefrpy-unmatched-coverage.json")
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
