#!/usr/bin/env python3
"""Measure where EIKEN-derived words sit in CEFR and general English frequency bands.
Aggregates only; no upstream row-level vocabulary is redistributed.
"""
import collections,csv,json,pathlib,urllib.request
from wordfreq import zipf_frequency
from build_eiken_crosswalk import UPSTREAM,load_cefr,norm

LEVELS=["A1","A2","B1","B2","C1","C2"]
# wordfreq Zipf is log10 occurrences per billion, NOT an exact vocabulary rank.
BANDS=[(">=6",6,99),("5-6",5,6),("4-5",4,5),("3-4",3,4),("2-3",2,3),("<2",float("-inf"),2)]
def band(x):
    for label,lo,hi in BANDS:
        if lo<=x<hi:return label
    return "unknown"
def main():
    root=pathlib.Path("vocabulary/raw")
    cefr=load_cefr([root/"cefrj-vocabulary-profile-1.5.csv",root/"octanove-vocabulary-profile-c1c2-1.0.csv"])
    groups=collections.defaultdict(collections.Counter)
    unique=set()
    candidates=[]
    with urllib.request.urlopen(UPSTREAM,timeout=120) as resp:
        for line in resp:
            if not line.strip():continue
            try:r=json.loads(line)
            except ValueError:continue
            w=r.get("word")
            if not isinstance(w,str) or not w.strip() or r.get("isTypo") or r.get("isPhrase"):continue
            w=norm(w)
            if w in unique:
                groups["all"]["duplicate"]+=1
                continue
            unique.add(w)
            n=(r.get("count") or {}).get("1")
            observed=isinstance(n,(int,float)) and n>0
            s=(r.get("score") or {}).get("1")
            distinctive=isinstance(s,(int,float)) and s>0
            cohorts=["all"]
            if observed:cohorts.append("grade1_observed")
            if distinctive:cohorts.append("grade1_positive_score")
            if observed and distinctive:cohorts.append("grade1_observed_positive_score")
            entries=cefr.get(w,[])
            levels={e["cefr"] for e in entries if e["cefr"] in LEVELS}
            z=zipf_frequency(w,"en")
            if distinctive:
                candidates.append({"word":w,"score":s,"observed":observed,"levels":levels,"zipf":z})
            for c in cohorts:
                d=groups[c]
                d["total"]+=1
                d["zipf:"+band(z)]+=1
                d["cefr:unmatched" if not levels else "cefr:matched"]+=1
                for lv in levels:d["cefr:"+lv]+=1
                if levels:
                    d["cefr:multiple_levels" if len(levels)>1 else "cefr:single_level"]+=1
    tiers={}
    for label,rows in [("score_positive",candidates),("score_positive_and_observed",[x for x in candidates if x["observed"]])]:
        ordered=sorted(rows,key=lambda x:(-x["score"],x["word"]))
        tiers[label]={}
        for n in (500,1000,2000,3000):
            sample=ordered[:n]
            c=collections.Counter()
            for x in sample:
                c["total"]+=1
                c["cefr:matched" if x["levels"] else "cefr:unmatched"]+=1
                for lv in x["levels"]:c["cefr:"+lv]+=1
                c["zipf:"+band(x["zipf"])]+=1
            tiers[label][str(n)]=dict(c)
    summary={"top_score_tiers":tiers,"source":UPSTREAM,"method":"unique casefolded unigram headwords; excludes isTypo; grade1 evidence based on upstream count; wordfreq Zipf frequency, not rank","frequency_bands":"Zipf 6=1 per 1000 words, 5=1 per 10000, 4=1 per 100000, 3=1 per million, 2=1 per 10 million (approx).","groups":{k:dict(v) for k,v in groups.items()},"cautions":["CEFR counts may overlap across levels; not mutually exclusive.","Grade1 count not verified against held-out original exam papers.","One EIKEN-derived dataset is used here; independent second dataset must be added and compared.","Zipf bands are not top-N rank bins."]}
    path=pathlib.Path("vocabulary/analysis/eiken-distribution-summary.json")
    path.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
