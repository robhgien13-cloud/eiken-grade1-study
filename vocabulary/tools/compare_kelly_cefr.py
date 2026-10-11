#!/usr/bin/env python3
"""Compare Kelly independent CEFR annotations with EIKEN and cefrpy estimates.
Aggregate-only output: do not redistribute Kelly vocabulary entries."""
import collections,json,pathlib,urllib.request
from cefrpy import CEFRAnalyzer
from wordfreq import zipf_frequency
from analyze_eiken_distribution import band, BANDS
from build_eiken_crosswalk import UPSTREAM,load_cefr,norm
KELLY="https://raw.githubusercontent.com/kotoshu/frequency-list-kelly/main/data/en.json"
LEVELS=("A1","A2","B1","B2","C1","C2")
def main():
    raw=pathlib.Path("vocabulary/raw")
    baseline=load_cefr([raw/"cefrj-vocabulary-profile-1.5.csv",raw/"octanove-vocabulary-profile-c1c2-1.0.csv"])
    with urllib.request.urlopen(KELLY,timeout=120) as f:
        data=json.load(f)
    kelly=collections.defaultdict(set)
    for entry in data["full_list"]:
        w=norm(entry.get("word","")); lv=str(entry.get("cefr","")).upper()
        if w and lv in LEVELS:kelly[w].add(lv)
    grade1=set()
    with urllib.request.urlopen(UPSTREAM,timeout=120) as f:
        for line in f:
            try:entry=json.loads(line)
            except ValueError:continue
            w=entry.get("word")
            if not isinstance(w,str) or not w.strip() or entry.get("isTypo") or entry.get("isPhrase"):continue
            n=(entry.get("count") or {}).get("1")
            if isinstance(n,(int,float)) and n>0:grade1.add(norm(w))
    a=CEFRAnalyzer(); counts=collections.Counter(); levels=collections.Counter()
    comparison=collections.Counter(); disagreements=collections.Counter()
    frequency=collections.defaultdict(collections.Counter)
    for w in grade1:
        old={e["cefr"] for e in baseline.get(w,[]) if e["cefr"] in LEVELS}
        new=kelly.get(w,set())
        counts["total"]+=1
        freq_band=band(zipf_frequency(w,"en"))
        frequency[freq_band]["total"]+=1
        frequency[freq_band]["baseline_matched" if old else "baseline_unmatched"]+=1
        frequency[freq_band]["kelly_added" if (not old and new) else "not_kelly_added"]+=1
        frequency[freq_band]["matched_after_kelly" if (old or new) else "unmatched_after_kelly"]+=1
        if old:counts["baseline_matched"]+=1
        if new:
            counts["kelly_matched"]+=1
            for lv in new:levels["kelly_"+lv]+=1
        if old and new:
            counts["both_matched"]+=1
            if old & new:counts["both_any_level_agreement"]+=1
            else:counts["both_disjoint_levels"]+=1
        if not old:
            counts["baseline_unmatched"]+=1
            if new:
                counts["new_independent_match"]+=1
                for lv in new:levels["new_"+lv]+=1
                estimated=a.get_average_word_level_CEFR(w)
                if estimated is not None:
                    estimated=str(estimated).upper()
                    if estimated in LEVELS:
                        comparison["estimate_comparable"]+=1
                        if estimated in new:comparison["estimate_agrees"]+=1
                        else:
                            comparison["estimate_disagrees"]+=1
                            disagreements[estimated+" -> "+"/".join(sorted(new))]+=1
            else:counts["still_unmatched_after_kelly"]+=1
    result={"source":KELLY,"kelly_total_headwords":len(kelly),"counts":dict(counts),
            "levels":dict(levels),"frequency_by_zipf_band":{k:dict(v) for k,v in frequency.items()},"cefrpy_vs_kelly_on_new_matches":dict(comparison),
            "cefrpy_disagreements_top":disagreements.most_common(12),
            "cautions":["Kelly is independent of CEFR-J but its CEFR methodology may differ.",
            "Exact headword matching, not sense or POS agreement.","Kelly derived data subject to original project terms.",
            "cefrpy is a model estimate, not independently attested CEFR."]}
    p=pathlib.Path("vocabulary/analysis/kelly-cefr-independent-crosscheck.json")
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
