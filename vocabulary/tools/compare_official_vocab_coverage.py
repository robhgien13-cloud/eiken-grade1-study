#!/usr/bin/env python3
"""Compare candidate vocab lists against official Reading/Listening; aggregates only."""
import collections,json,pathlib,urllib.request
from simplemma import lemmatize
from analyze_eiken_distribution import norm,UPSTREAM
from finish_official_exam_corpus import EXAMS,BASE,pdf,reading,listening,TOK

def vocab():
    out={}
    with urllib.request.urlopen(UPSTREAM,timeout=120) as r:
        for line in r:
            try:x=json.loads(line)
            except ValueError:continue
            w=x.get("word")
            if not isinstance(w,str) or not w.strip() or x.get("isTypo") or x.get("isPhrase"):continue
            w=norm(w)
            if w in out:continue
            score=(x.get("score") or {}).get("1")
            count=(x.get("count") or {}).get("1")
            out[w]={"score":score if isinstance(score,(int,float)) else None,"count":count if isinstance(count,(int,float)) else 0}
    return out

def ranks(v):
    positive=[(w,x) for w,x in v.items() if x["score"] is not None and x["score"]>0]
    observed=[(w,x) for w,x in v.items() if x["count"]>0]
    eligible=[(w,x) for w,x in observed if x["score"] is not None]
    score=sorted(positive,key=lambda p:(-p[1]["score"],p[0]))
    count=sorted(observed,key=lambda p:(-p[1]["count"],p[0]))
    def percentile(rows,key):
        order=sorted(rows,key=lambda p:(-key(p[1]),p[0]))
        return {w:1-i/max(1,len(order)-1) for i,(w,_) in enumerate(order)}
    sr=percentile(eligible,lambda x:x["score"])
    cr=percentile(eligible,lambda x:x["count"])
    balanced=sorted(eligible,key=lambda p:(-(sr[p[0]]+cr[p[0]])/2,p[0]))
    return {name:[w for w,_ in rows] for name,rows in (("characteristic",score),("occurrence",count),("balanced",balanced))}

def evaluate(text,ranked):
    forms=[w.lower().replace("’","'") for w in TOK.findall(text) if len(w)>1]
    lemmas=[lemmatize(w,lang="en") for w in forms]
    # Coverage is of all passage tokens; common function words inflate absolute coverage.
    out={"tokens":len(lemmas),"types":len(set(lemmas)),"strategies":{}}
    for name,order in ranked.items():
        out["strategies"][name]={}
        for n in (500,1000,2000,3000):
            chosen=set(order[:n])
            matched=sum(w in chosen for w in lemmas)
            types=len(set(lemmas)&chosen)
            out["strategies"][name][str(n)]={"token_matches":matched,"token_coverage_pct":round(100*matched/max(1,len(lemmas)),2),"type_matches":types,"type_coverage_pct":round(100*types/max(1,len(set(lemmas))),2)}
    return out

def main():
    ranked=ranks(vocab())
    result={"status":"PROVISIONAL_AUTOMATED","training_sessions":["2025-3","2026-1"],"holdout":"2026-2 excluded entirely","notes":["These are passage-token/type coverage, not exam score or knowledge gain.","Reading and listening extraction are heuristic and not manually validated.","Vocabulary question choices are excluded; no claim of vocabulary-question coverage.","All source text and word-level inventories stay in runner memory; only aggregates exported.","Source count is transformed and is not verified independent exam frequency."],"sessions":{}}
    for name in ("2025-3","2026-1"):
        q,s=EXAMS[name]
        result["sessions"][name]={}
        for section,file in (("reading",q),("listening",s)):
            try:
                d=pdf(BASE+file)
                passage,_=reading(d) if section=="reading" else listening(d)
                result["sessions"][name][section]=evaluate(passage,ranked)
            except Exception as e:result["sessions"][name][section]={"error":str(e)}
    dest=pathlib.Path("vocabulary/analysis/official-vocab-coverage.json")
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
