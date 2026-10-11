#!/usr/bin/env python3
"""Compare Kelly independent CEFR annotations with EIKEN and cefrpy estimates.
Aggregate-only output: do not redistribute Kelly vocabulary entries."""
import collections,json,pathlib,re,urllib.request
from cefrpy import CEFRAnalyzer
from wordfreq import zipf_frequency
from analyze_eiken_distribution import band, BANDS
from build_eiken_crosswalk import UPSTREAM,load_cefr,norm
KELLY="https://raw.githubusercontent.com/kotoshu/frequency-list-kelly/main/data/en.json"
LEVELS=("A1","A2","B1","B2","C1","C2")
IRREGULAR={"became":"become","felt":"feel","went":"go","gone":"go","was":"be","were":"be","had":"have","did":"do","done":"do","got":"get","known":"know","knew":"know","seen":"see","saw":"see","written":"write","wrote":"write"}
def candidate_lemmas(w):
    """Conservative candidates: accept only if present in an actual CEFR source."""
    out=[]
    if w in IRREGULAR:out.append(IRREGULAR[w])
    if w.endswith("ing") and len(w)>5:
        stem=w[:-3]
        out.extend([stem,stem+"e"])
        if len(stem)>2 and stem[-1]==stem[-2]:out.append(stem[:-1])
    if w.endswith("ied") and len(w)>4:out.append(w[:-3]+"y")
    if w.endswith("ed") and len(w)>4:
        stem=w[:-2];out.extend([stem,stem+"e"])
        if len(stem)>2 and stem[-1]==stem[-2]:out.append(stem[:-1])
    if w.endswith("ies") and len(w)>4:out.append(w[:-3]+"y")
    if w.endswith("es") and len(w)>4:out.extend([w[:-2],w[:-1]])
    if w.endswith("s") and len(w)>3:out.append(w[:-1])
    return list(dict.fromkeys(x for x in out if x!=w))

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
    original_spellings=collections.defaultdict(set)
    with urllib.request.urlopen(UPSTREAM,timeout=120) as f:
        for line in f:
            try:entry=json.loads(line)
            except ValueError:continue
            w=entry.get("word")
            if not isinstance(w,str) or not w.strip() or entry.get("isTypo") or entry.get("isPhrase"):continue
            n=(entry.get("count") or {}).get("1")
            if isinstance(n,(int,float)) and n>0:
                grade1.add(norm(w))
                original_spellings[norm(w)].add(w)
    a=CEFRAnalyzer(); counts=collections.Counter(); levels=collections.Counter()
    comparison=collections.Counter(); disagreements=collections.Counter()
    frequency=collections.defaultdict(collections.Counter)
    cleaning=collections.Counter(); cleaning_examples=collections.defaultdict(list)
    unmatched_zipf_5_to_6=[]
    full_cleaning=collections.Counter()
    full_examples=collections.defaultdict(list)
    def classify(w):
        forms=original_spellings[w]
        if len(w)==1 and w.isalpha():return "exclude_single_letter"
        if re.fullmatch(r"[a-z](?:\\.[a-z])+\\.?",w):return "exclude_dotted_initialism"
        if any(form.isupper() and len(form)>1 for form in forms):return "review_acronym"
        if any(form[:1].isupper() for form in forms):return "review_proper_name"
        return "retain_unverified"

    for w in grade1:
        decision=classify(w)
        full_cleaning[decision]+=1
        if decision!="retain_unverified" and len(full_examples[decision])<40:full_examples[decision].append(w)
        old={e["cefr"] for e in baseline.get(w,[]) if e["cefr"] in LEVELS}
        new=kelly.get(w,set())
        counts["total"]+=1
        freq_band=band(zipf_frequency(w,"en"))
        frequency[freq_band]["total"]+=1
        frequency[freq_band]["baseline_matched" if old else "baseline_unmatched"]+=1
        frequency[freq_band]["kelly_added" if (not old and new) else "not_kelly_added"]+=1
        frequency[freq_band]["matched_after_kelly" if (old or new) else "unmatched_after_kelly"]+=1
        if freq_band=="5-6" and not old and not new:
            unmatched_zipf_5_to_6.append({"word":w,"zipf":round(zipf_frequency(w,"en"),2)})
        if not old and not new:
            if len(w)==1 and w.isalpha():
                cleaning["single_letter_quarantine"]+=1
                if len(cleaning_examples["single_letter_quarantine"])<30:cleaning_examples["single_letter_quarantine"].append(w)
            else:
                matches=[(lemma,{e["cefr"] for e in baseline.get(lemma,[]) if e["cefr"] in LEVELS}|kelly.get(lemma,set())) for lemma in candidate_lemmas(w)]
                matches=[(lemma,levels) for lemma,levels in matches if levels]
                if len(matches)==1:
                    cleaning["one_candidate_lemma_match"]+=1
                    if len(cleaning_examples["one_candidate_lemma_match"])<30:cleaning_examples["one_candidate_lemma_match"].append({"surface":w,"lemma":matches[0][0]})
                elif len(matches)>1:
                    cleaning["ambiguous_candidate_lemmas"]+=1
                    if len(cleaning_examples["ambiguous_candidate_lemmas"])<30:cleaning_examples["ambiguous_candidate_lemmas"].append({"surface":w,"candidates":[x[0] for x in matches]})
                else:cleaning["still_unmatched_after_conservative_cleaning"]+=1
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
            "levels":dict(levels),"cleaning_audit":{"counts":dict(cleaning),"examples":dict(cleaning_examples),"full_population_screen":{"counts":dict(full_cleaning),"examples":dict(full_examples),"automatically_excluded":full_cleaning["exclude_single_letter"]+full_cleaning["exclude_dotted_initialism"],"retained_or_review":len(grade1)-full_cleaning["exclude_single_letter"]-full_cleaning["exclude_dotted_initialism"]},"note":"Only previously unmatched words evaluated; no original rows removed. Candidate lemmas require CEFR-source match and ambiguous candidates remain unassigned."},"unmatched_zipf_5_to_6":sorted(unmatched_zipf_5_to_6,key=lambda x:(-x["zipf"],x["word"])),"frequency_by_zipf_band":{k:dict(v) for k,v in frequency.items()},"cefrpy_vs_kelly_on_new_matches":dict(comparison),
            "cefrpy_disagreements_top":disagreements.most_common(12),
            "cautions":["Kelly is independent of CEFR-J but its CEFR methodology may differ.",
            "Exact headword matching, not sense or POS agreement.","Kelly derived data subject to original project terms.",
            "cefrpy is a model estimate, not independently attested CEFR."]}
    p=pathlib.Path("vocabulary/analysis/kelly-cefr-independent-crosscheck.json")
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
