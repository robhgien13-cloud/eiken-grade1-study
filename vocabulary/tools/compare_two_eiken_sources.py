#!/usr/bin/env python3
"""Compare two user-selected EIKEN-related word lists against CEFR and wordfreq.
Public GitHub source 2 is a curated study list, NOT verified past-exam occurrences.
Outputs aggregate summaries only, not third-party words.
"""
import collections,csv,io,json,pathlib,urllib.request
from wordfreq import zipf_frequency
from build_eiken_crosswalk import UPSTREAM,load_cefr,norm

SECOND="https://raw.githubusercontent.com/ryujiinoue1031-ai/Eiken_Tango_Practice/main/Eiken_1st_Grade_Vocabulary_1000_Full.csv"
LEVELS=("A1","A2","B1","B2","C1","C2")
BANDS=[(">=6",6,99),("5-6",5,6),("4-5",4,5),("3-4",3,4),("2-3",2,3),("<2",-99,2)]
def bucket(z):
    return next((name for name,lo,hi in BANDS if lo<=z<hi),"unknown")
def summarize(words,cefr):
    counts=collections.Counter()
    for word in words:
        entries=cefr.get(word,[])
        levels={e["cefr"] for e in entries if e["cefr"] in LEVELS}
        counts["total"]+=1
        counts["cefr:matched" if levels else "cefr:unmatched"]+=1
        for lv in levels:counts["cefr:"+lv]+=1
        counts["zipf:"+bucket(zipf_frequency(word,"en"))]+=1
    return dict(counts)
def main():
    root=pathlib.Path("vocabulary/raw")
    cefr=load_cefr([root/"cefrj-vocabulary-profile-1.5.csv",root/"octanove-vocabulary-profile-c1c2-1.0.csv"])
    with urllib.request.urlopen(SECOND,timeout=120) as r:
        rows=list(csv.DictReader(io.StringIO(r.read().decode("utf-8-sig"))))
    second={norm(row.get("Word","")) for row in rows if row.get("Word","").strip()}
    first=set();observed=set();positive=set()
    with urllib.request.urlopen(UPSTREAM,timeout=120) as r:
        for line in r:
            try:row=json.loads(line)
            except ValueError:continue
            w=row.get("word")
            if not isinstance(w,str) or not w.strip() or row.get("isTypo") or row.get("isPhrase"):continue
            w=norm(w);first.add(w)
            count=(row.get("count") or {}).get("1")
            if isinstance(count,(int,float)) and count>0:observed.add(w)
            score=(row.get("score") or {}).get("1")
            if isinstance(score,(int,float)) and score>0:positive.add(w)
    result={
        "source_a":UPSTREAM,"source_b":SECOND,
        "source_b_csv_rows":len(rows),
        "source_b_unique":len(second),
        "source_b_overlap_with_a":len(second&first),
        "source_b_overlap_with_a_grade1_observed":len(second&observed),
        "source_b_overlap_with_a_grade1_positive_score":len(second&positive),
        "source_b_only":len(second-first),
        "source_a_grade1_observed_only":len(observed-second),
        "distribution":{
            "a_grade1_observed":summarize(observed,cefr),
            "a_grade1_positive_score":summarize(positive,cefr),
            "b_curated_study_list":summarize(second,cefr),
            "intersection_b_a_grade1_observed":summarize(second&observed,cefr)
        },
        "cautions":[
            "Source B is an EIKEN Grade 1 study-list label, not verified historical past-exam evidence.",
            "Source A grade 1 occurrence is derived from upstream PDF processing; exam coverage unverified.",
            "CEFR levels may overlap; Zipf frequency bands are not rank positions.",
            "No raw third-party word list or translated example is written to the repository."
        ]
    }
    path=pathlib.Path("vocabulary/analysis/two-eiken-sources-comparison.json")
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
