#!/usr/bin/env python3
"""Print compact per-page diagnostics to choose precise official exam sections."""
import fitz,urllib.request,re,json
BASE="https://www.eiken.or.jp/eiken/exam/kakomon/"
FILES={"2026-1":("2026-1-1ji-1kyu.pdf","2026-1-1ji_1kyuscript.pdf"),"2025-3":("2025-3-1ji-1kyu.pdf","2025-3-1ji_1kyuscript.pdf"),"2026-2":("2026-2-1ji_1kyu.pdf","2026-2-1ji_1kyuscript.pdf")}
for exam,files in FILES.items():
 for typ,f in zip(("questions","listening"),files):
  with urllib.request.urlopen(BASE+f,timeout=120) as r:doc=fitz.open(stream=r.read(),filetype="pdf")
  print("\n",exam,typ,len(doc))
  for i,p in enumerate(doc):
   s=p.get_text()
   lines=[re.sub(r"\s+"," ",x).strip() for x in s.splitlines() if x.strip()]
   print(json.dumps({"page":i+1,"chars":len(s),"first":lines[:5],"last":lines[-3:]},ensure_ascii=False))
