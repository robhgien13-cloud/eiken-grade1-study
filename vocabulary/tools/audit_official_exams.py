#!/usr/bin/env python3
"""Official EIKEN Grade 1 PDF vocabulary audit. Aggregate statistics only.
2026-2 is held out; 2026-1 and 2025-3 are development sets.
Extraction is provisional until page boundaries and PDF text are reviewed.
"""
import collections,io,json,re,urllib.request,pathlib
import fitz
from wordfreq import zipf_frequency
from build_eiken_crosswalk import load_cefr,norm
BASE="https://www.eiken.or.jp/eiken/exam/kakomon/"
EXAMS={
"2026-1":("2026-1-1ji-1kyu.pdf","2026-1-1ji_1kyuscript.pdf"),
"2025-3":("2025-3-1ji-1kyu.pdf","2025-3-1ji-1kyuscript.pdf"),
"2026-2":("2026-2-1ji_1kyu.pdf","2026-2-1ji_1kyuscript.pdf")}
LEVELS=["A1","A2","B1","B2","C1","C2"]
def stats(text,cefr):
    words=[norm(w) for w in re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*",text)]
    words=[w for w in words if len(w)>1]
    c=collections.Counter(words)
    result={"tokens":len(words),"types":len(c),"cefr_token_counts":{},"cefr_type_counts":{},"zipf_token_counts":{},"zipf_type_counts":{}}
    for word,n in c.items():
        entries=cefr.get(word,[])
        levels={e["cefr"] for e in entries if e["cefr"] in LEVELS}
        lv=max(levels,key=LEVELS.index) if levels else "unmatched"
        z=zipf_frequency(word,"en")
        band=">=6" if z>=6 else "5-6" if z>=5 else "4-5" if z>=4 else "3-4" if z>=3 else "2-3" if z>=2 else "<2"
        for key,value in [("cefr_token_counts",lv),("cefr_type_counts",lv),("zipf_token_counts",band),("zipf_type_counts",band)]:
            result[key][value]=result[key].get(value,0)+(n if "token" in key else 1)
    return result
def main():
    root=pathlib.Path("vocabulary/raw")
    cefr=load_cefr([root/"cefrj-vocabulary-profile-1.5.csv",root/"octanove-vocabulary-profile-c1c2-1.0.csv"])
    result={"method":"Text extraction from official PDFs; reading excludes vocabulary options? NO, pages 3-12 include prompts/options and are a preliminary proxy; not a clean reading-passage corpus. Listening uses all script pages, including directions. 2026-2 held out.","exams":{}}
    for name,(q,s) in EXAMS.items():
        result["exams"][name]={}
        for kind,filename in [("reading_provisional",q),("listening_provisional",s)]:
            url=BASE+filename
            with urllib.request.urlopen(url,timeout=90) as f:pdf=fitz.open(stream=f.read(),filetype="pdf")
            # Question PDF pages 3-12 (zero-based 2-11) include vocab and reading.
            pages=list(pdf)[2:12] if kind.startswith("reading") else list(pdf)
            txt="\n".join(p.get_text() for p in pages)
            result["exams"][name][kind]={"pdf_pages":len(pdf),"pages_sampled":len(pages),"chars_extracted":len(txt),**stats(txt,cefr)}
    p=pathlib.Path("vocabulary/analysis/official-exam-preliminary-aggregate.json")
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
