#!/usr/bin/env python3
"""Automated acceptance gates for six official exam sections.
A pass is NOT a substitute for manual review of PDF layout or lemma errors.
"""
import json,pathlib,sys
p=pathlib.Path("vocabulary/analysis/official-exam-strict-aggregate.json")
data=json.loads(p.read_text(encoding="utf-8"))
checks=[]
for exam in ("2025-3","2026-1","2026-2"):
 for section in ("reading","listening"):
  x=data["exams"].get(exam,{}).get(section,{})
  checks.append({"check":f"{exam}/{section} source obtained","passed":"error" not in x and x.get("tokens",0)>1000})
  checks.append({"check":f"{exam}/{section} lemma counts plausible","passed":x.get("lemma_types",0)>500 and x.get("lemma_types",0)<=x.get("surface_types",0)})
  if section=="reading":
   pages={d["page"]:d for d in x.get("diagnostics",[])}
   checks.append({"check":f"{exam} page 7 short reading retained","passed":pages.get(7,{}).get("accepted_lines",0)>=20})
   checks.append({"check":f"{exam} page 9 comprehension-only excluded","passed":pages.get(9,{}).get("accepted_lines",-1)==0})
report={"automated_checks":checks,"automated_pass":all(c["passed"] for c in checks),"human_visual_review":"NOT PERFORMED","proper_noun_lemma_review":"NOT PERFORMED","production_ready":False}
pathlib.Path("vocabulary/analysis/official-exam-acceptance.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
if not report["automated_pass"]:sys.exit(1)
