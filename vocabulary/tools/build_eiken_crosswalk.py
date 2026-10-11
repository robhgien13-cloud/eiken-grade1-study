#!/usr/bin/env python3
"""Build a license-cautious EIKEN x CEFR crosswalk locally. No external vocabulary rows committed."""
import argparse, collections, csv, io, json, pathlib, urllib.request

UPSTREAM="https://raw.githubusercontent.com/pnsk-lab/eiken-vocab/main/viewer/src/assets/metadata.jsonl"
GRADE="1"
POS={"noun":"noun","verb":"verb","adjective":"adjective","adverb":"adverb",
     "preposition":"preposition","conjunction":"conjunction","pronoun":"pronoun",
     "interjection":"interjection","article":"determiner","auxiliary-verb":"verb"}

def norm(w):
    return " ".join(w.casefold().strip().split())

def load_cefr(paths):
    byword=collections.defaultdict(list)
    for p in paths:
        with open(p,encoding="utf-8-sig",newline="") as f:
            for row in csv.DictReader(f):
                w=norm(row.get("headword",""))
                if w:
                    byword[w].append({"source":p.name,"pos":norm(row.get("pos","")),"cefr":row.get("CEFR","")})
    return byword

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default="vocabulary/raw")
    ap.add_argument("--output",default="vocabulary/analysis/eiken-crosswalk-summary.json")
    ap.add_argument("--local-jsonl",default=None,help="Optional licensed local copy of upstream metadata")
    ap.add_argument("--emit-rows",default=None,help="Optional LOCAL-ONLY CSV, do not publish without rights clearance")
    a=ap.parse_args()
    raw=pathlib.Path(a.root)
    sources=[raw/"cefrj-vocabulary-profile-1.5.csv",raw/"octanove-vocabulary-profile-c1c2-1.0.csv"]
    vocab=load_cefr(sources)
    stats=collections.Counter()
    levels=collections.Counter()
    if a.local_jsonl:
        source=open(a.local_jsonl,"rb")
    else:
        source=urllib.request.urlopen(UPSTREAM,timeout=120)
    fields=["word","is_phrase","observed_grade1","grade1_count","grade1_score","grade1_rank","cefr_levels","match_sources","match_type"]
    out=None
    try:
        if a.emit_rows:
            pathlib.Path(a.emit_rows).parent.mkdir(parents=True,exist_ok=True)
            out=open(a.emit_rows,"w",encoding="utf-8",newline="")
            writer=csv.DictWriter(out,fieldnames=fields)
            writer.writeheader()
        with source:
            for line in source:
                if not line.strip():
                    continue
                stats["lines"]+=1
                try:
                    row=json.loads(line)
                except ValueError:
                    stats["invalid_json"]+=1
                    continue
                word=row.get("word")
                if not isinstance(word,str) or not word.strip():
                    stats["missing_word"]+=1
                    continue
                if row.get("isTypo"):
                    stats["quarantined_typo"]+=1
                    continue
                is_phrase=bool(row.get("isPhrase"))
                if is_phrase:
                    stats["phrase"]+=1
                    continue  # unigram headword matching only; phrases need a separate matcher
                stats["eligible_unigrams"]+=1
                entries=vocab.get(norm(word),[])
                if entries:
                    stats["matched_headword"]+=1
                else:
                    stats["unmatched_headword"]+=1
                meanings=row.get("meanings",[])
                pos_set={POS.get(norm(m.get("class","")),"") for m in meanings if isinstance(m,dict)}
                pos_set.discard("")
                exact=[e for e in entries if e["pos"] in pos_set] if pos_set else []
                match_type="pos_confirmed" if exact else ("headword_only" if entries else "none")
                stats["match_"+match_type]+=1
                chosen=exact if exact else entries
                cefr=sorted(set(e["cefr"] for e in chosen if e["cefr"]))
                for lv in cefr:
                    levels[lv]+=1
                grade_count=(row.get("count") or {}).get(GRADE)
                observed=isinstance(grade_count,(int,float)) and grade_count>0
                if observed:
                    stats["grade1_observed"]+=1
                    if entries:
                        stats["grade1_observed_matched_headword"]+=1
                if any(lv in ("C1","C2") for lv in cefr):
                    stats["matched_C1_C2"]+=1
                    if observed:stats["grade1_observed_C1_C2"]+=1
                if out:
                    writer.writerow({"word":word,"is_phrase":False,"observed_grade1":observed,
                       "grade1_count":grade_count,"grade1_score":(row.get("score") or {}).get(GRADE),
                       "grade1_rank":(row.get("rank") or {}).get(GRADE),"cefr_levels":"|".join(cefr),
                       "match_sources":"|".join(sorted(set(e["source"] for e in chosen))),"match_type":match_type})
    finally:
        if out:out.close()
    result={"upstream":UPSTREAM,"sources":[str(x) for x in sources],"counts":dict(stats),
            "matched_cefr_level_counts":dict(levels),
            "method":"casefolded exact headword, optional POS agreement; phrase and isTypo records excluded; missing exam coverage unresolved",
            "caution":"Headword matches do not validate meaning; no source text redistributed"}
    pathlib.Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    pathlib.Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
