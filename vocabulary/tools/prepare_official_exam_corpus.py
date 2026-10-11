#!/usr/bin/env python3
"""Build aggregate-only EIKEN Grade 1 Reading/Listening lexical inventory.
No official copyrighted passage text or per-word source inventory is published.
Reading is limited to known pages; page-level contamination is tracked.
"""
import collections,json,pathlib,re,urllib.request,time
import fitz
from simplemma import lemmatize
from wordfreq import zipf_frequency
BASE="https://www.eiken.or.jp/eiken/exam/kakomon/"
EXAMS={
 "2026-1":("2026-1-1ji-1kyu.pdf","2026-1-1ji_1kyuscript.pdf"),
 "2025-3":("2025-3-1ji-1kyu.pdf","2025-3-1ji-1kyuscript.pdf"),
 "2026-2":("2026-2-1ji_1kyu.pdf","2026-2-1ji_1kyuscript.pdf")}
# 1-indexed PDF pages. Readings are on pages 6-11; vocabulary multiple-choice 3-5,
# writing 12-14, and listening answer choices 16-22 are intentionally excluded.
READING_PAGES=range(6,12)
TOKEN=re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
REMOVE=re.compile(r"(?:Grade 1|copyright|無断転載|公益財団|検定一次試験|mark your answer|now mark your answer|you have \d+ seconds|question no\.|^\s*no\.\s*\d+)",re.I)
def get(url):
 last=None
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
   with urllib.request.urlopen(req,timeout=120) as r:return fitz.open(stream=r.read(),filetype="pdf")
  except Exception as e:
   last=e
   if attempt<3:time.sleep(2*(attempt+1))
 raise last
def cleaned_lines(doc,pages,mode):
 lines=[];removed=0
 for page in pages:
  for line in doc[page-1].get_text().splitlines():
   s=line.strip()
   if not s:continue
   if REMOVE.search(s) or re.fullmatch(r"[\W\d_]+",s):
    removed+=1;continue
   if mode=="listening":
    # Strip narrator/speaker prefixes and question prompts where possible.
    if re.search(r"\bQuestion(?:s)?\s*:",s,re.I):
     removed+=1;continue
    s=re.sub(r"^[\W\d]*(?:[A-Z]{1,3}|\*{1,3})\s*:\s*","",s)
   else:
    # Standalone answer-option numbers and question labels are removed, but
    # passage pages still contain some question and option text.
    if re.match(r"^\(?\d{1,2}\)?\s*$",s):
     removed+=1;continue
   lines.append(s)
 return " ".join(lines),removed
def tokenize(s):
 forms=[w.lower().replace("’","'") for w in TOKEN.findall(s)]
 return [w for w in forms if len(w)>1]
def aggregate(forms):
 lemmas=[lemmatize(w,lang="en") for w in forms]
 c=collections.Counter(lemmas)
 zipft=collections.Counter();zipf_types=collections.Counter()
 for w,n in c.items():
  z=zipf_frequency(w,"en")
  b=">=6" if z>=6 else "5-6" if z>=5 else "4-5" if z>=4 else "3-4" if z>=3 else "2-3" if z>=2 else "<2"
  zipft[b]+=n;zipf_types[b]+=1
 return {"tokens":len(forms),"surface_types":len(set(forms)),"lemma_types":len(c),"zipf_token_bands":dict(zipft),"zipf_lemma_type_bands":dict(zipf_types),"lemma_token_changes":sum(a!=b for a,b in zip(forms,lemmas))}
def main():
 out={"status":"PROVISIONAL","reading_pages":"6-11 (includes some comprehension questions/options)","listening":"official scripts, with heuristic removal of headers/narrator prompts","lemmatization":"simplemma, context-free; verify irregular words manually","holdout":"2026-2: descriptive metrics only; do not tune cutoffs","exams":{}}
 for exam,(q,s) in EXAMS.items():
  out["exams"][exam]={}
  for section,filename in [("reading",q),("listening",s)]:
   try:doc=get(BASE+filename)
   except Exception as e:
    out["exams"][exam][section]={"error":str(e)};continue
   pages=list(READING_PAGES) if section=="reading" else list(range(1,len(doc)+1))
   cleaned,removed=cleaned_lines(doc,pages,section)
   out["exams"][exam][section]={"pages":pages,"removed_lines":removed,**aggregate(tokenize(cleaned))}
 p=pathlib.Path("vocabulary/analysis/official-exam-cleaning-aggregates.json")
 p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
