#!/usr/bin/env python3
"""Official exam corpus: strict reading passage segmentation and listening dialogue segmentation.
Produces aggregate diagnostics, not copyrighted passages. Fail closed on unknown layouts.
"""
import json,re,pathlib,urllib.request,collections
import fitz
from simplemma import lemmatize
from wordfreq import zipf_frequency
BASE="https://www.eiken.or.jp/eiken/exam/kakomon/"
EXAMS={"2025-3":("2025-3-1ji-1kyu.pdf","2025-3-1ji-1kyuscript.pdf"),"2026-1":("2026-1-1ji-1kyu.pdf","2026-1-1ji_1kyuscript.pdf"),"2026-2":("2026-2-1ji_1kyu.pdf","2026-2-1ji_1kyuscript.pdf")}
TOK=re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
QSTART=re.compile(r"^\(?\s*(?:2[6-9]|3[0-5])\s*\)?\s*$")
HEADER=re.compile(r"(?:Grade 1|copyright|無断転載|公益財団|検定一次試験|Continue to the next page|mark your answer)",re.I)
NARRATION=re.compile(r"(?:You have \d+ seconds|Now (?:mark|listen|read)|This is the end|Question No\.|^No\.\s*\d+|^Part\s*[1-4])",re.I)
def pdf(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 with urllib.request.urlopen(req,timeout=120) as r:return fitz.open(stream=r.read(),filetype="pdf")
def lines(page):
 d=page.get_text("dict")
 for block in d["blocks"]:
  if "lines" not in block:continue
  for line in block["lines"]:
   s="".join(x["text"] for x in line["spans"]).strip()
   if s:yield (line["bbox"][0],line["bbox"][1],s)
def reading(doc):
 accepted=[]; diagnostics=[]
 for pno in range(6,12):
  ls=list(lines(doc[pno-1]))
  # A reading passage is followed by comprehension questions. Use first numbered
  # question position per column; never include answer-choice blocks.
  # Page 9 is comprehension-only across observed official layouts.
  if pno==9:
   diagnostics.append({"page":pno,"status":"question-only excluded","accepted_lines":0});continue
  qs=[(x,y) for x,y,s in ls if QSTART.match(s)]\n  # Page 7 contains a full passage followed by question blocks. PDF text order\n  # is more reliable here than comparing y coordinates across columns.\n  if pno==7 and qs:\n   first=next((i for i,(_,_,t) in enumerate(ls) if QSTART.match(t)),len(ls))\n   passage=[t for _,_,t in ls[:first] if not HEADER.search(t) and not re.fullmatch(r"[\\W\\d_]+",t)]\n   accepted.extend(passage)\n   diagnostics.append({"page":pno,"question_markers":len(qs),"accepted_lines":len(passage),"status":"pre-question text-order extraction"})\n   continue
  kept=[]
  for x,y,s in ls:
   if HEADER.search(s) or re.fullmatch(r"[\W\d_]+",s):continue
   # On 2-column layouts, question cutoff is per column.
   column=0 if x<doc[pno-1].rect.width/2 else 1
   col_q=[qy for qx,qy in qs if (0 if qx<doc[pno-1].rect.width/2 else 1)==column]
   if col_q and y>=min(col_q):continue
   if QSTART.match(s) or re.fullmatch(r"[1-4]",s):continue
   kept.append(s)
  accepted.extend(kept)
  diagnostics.append({"page":pno,"question_markers":len(qs),"accepted_lines":len(kept),"status":"auto-segmented"})
 return " ".join(accepted),diagnostics
def listening(doc):
 out=[];dropped=0;in_question=False
 for p in doc:
  for x,y,s in lines(p):
   if HEADER.search(s) or NARRATION.search(s) or not re.search("[A-Za-z]",s):
    dropped+=1;continue
   if re.search(r"\bQuestions?\s*:",s,re.I):
    in_question=True;dropped+=1;continue
   if re.match(r"^[☆★*\s]*(?:No\.\s*\d+|\([A-J]\))",s):
    in_question=False;dropped+=1;continue
   if in_question:
    dropped+=1;continue
   s=re.sub(r"^[☆★*\s]*(?:[A-Z]{1,3})\s*:\s*","",s)
   if s:out.append(s)
 return " ".join(out),{"removed_lines":dropped}
def count(text):
 words=[w.lower().replace("’","'") for w in TOK.findall(text)]
 words=[w for w in words if len(w)>1]
 lemmas=[lemmatize(w,lang="en") for w in words]
 # Proper names cannot be safely inferred from sentence-case text; keep all
 # but explicitly flag that this requires named-entity recognition.
 c=collections.Counter(lemmas)
 bands=collections.Counter()
 for w,n in c.items():
  z=zipf_frequency(w,"en")
  b=">=5" if z>=5 else "4-5" if z>=4 else "3-4" if z>=3 else "<3"
  bands[b]+=n
 return {"tokens":len(words),"surface_types":len(set(words)),"lemma_types":len(c),"lemma_changes":sum(a!=b for a,b in zip(words,lemmas)),"zipf_token_bands":dict(bands)}
def main():
 result={"status":"AUTOMATED_EXTRACTION_NOT_MANUALLY_VALIDATED","notes":["Reading question removal uses position and numbered-question markers; cannot certify all pages without visual/manual verification","Listening narrator removal is heuristic; cannot certify no contamination","simplemma context-free; proper names are not yet separated"],"exams":{}}
 for name,(q,s) in EXAMS.items():
  result["exams"][name]={}
  for section,f in [("reading",q),("listening",s)]:
   try:
    d=pdf(BASE+f)
    text,diag=(reading(d) if section=="reading" else listening(d))
    result["exams"][name][section]={**count(text),"diagnostics":diag}
   except Exception as e:result["exams"][name][section]={"error":str(e)}
 p=pathlib.Path("vocabulary/analysis/official-exam-strict-aggregate.json")
 p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
