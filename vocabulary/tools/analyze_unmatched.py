#!/usr/bin/env python3
"""Aggregate quality diagnostics for EIKEN words absent from CEFR lists.
Does not publish upstream row-level word lists.
"""
import collections, csv, json, pathlib, re, urllib.request
from build_eiken_crosswalk import UPSTREAM, load_cefr, norm

RAW=pathlib.Path("vocabulary/raw")
VOWELS="aeiou"
def category(w,known):
    if not re.fullmatch(r"[a-z]+(?:[-'][a-z]+)*",w):
        return "nonstandard_characters"
    if w.endswith("ies") and w[:-3]+"y" in known:return "plural_ies"
    if w.endswith("es") and (w[:-2] in known or w[:-1] in known):return "inflection_es"
    if w.endswith("s") and w[:-1] in known:return "inflection_s"
    if w.endswith("ied") and w[:-3]+"y" in known:return "past_ied"
    if w.endswith("ed") and (w[:-2] in known or w[:-1] in known):return "past_ed"
    if w.endswith("ing") and (w[:-3] in known or w[:-3]+"e" in known):return "progressive_ing"
    if "-" in w:return "hyphenated"
    if "'" in w:return "apostrophe"
    return "not_resolved_by_simple_rules"

def main():
    sources=[RAW/"cefrj-vocabulary-profile-1.5.csv",RAW/"octanove-vocabulary-profile-c1c2-1.0.csv"]
    known=load_cefr(sources)
    counts=collections.Counter()
    examples=collections.defaultdict(list)
    with urllib.request.urlopen(UPSTREAM,timeout=120) as resp:
        for line in resp:
            if not line.strip():continue
            try:r=json.loads(line)
            except ValueError:continue
            w=r.get("word")
            if not isinstance(w,str) or not w.strip() or r.get("isPhrase") or r.get("isTypo"):continue
            w=norm(w)
            if w in known:continue
            group=category(w,known)
            counts[group]+=1
            grade=(r.get("count") or {}).get("1")
            if isinstance(grade,(int,float)) and grade>0:counts[group+"_grade1_observed"]+=1
            # No row-level examples saved: respect third-party source rights
    result={"unmatched_total":sum(v for k,v in counts.items() if not k.endswith("_grade1_observed")),
            "categories":dict(sorted(counts.items())),
            "caveat":"Heuristics only; not lemmatization, typo correction or CEFR sense matching."}
    p=pathlib.Path("vocabulary/analysis/eiken-unmatched-quality-summary.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
