#!/usr/bin/env python3
"""Fail closed unless official exam corpus meets minimal source and cleaning gates."""
import json,pathlib,sys
p=pathlib.Path("vocabulary/analysis/official-exam-cleaning-aggregates.json")
d=json.loads(p.read_text())
checks=[]
for exam in ("2025-3","2026-1","2026-2"):
 for section in ("reading","listening"):
  x=d["exams"][exam].get(section,{})
  checks.append((f"{exam}/{section} acquired",x.get("tokens",0)>1000))
  checks.append((f"{exam}/{section} normalized",x.get("lemma_types",0)>100))
# These are currently NOT met; do not certify stage 1/2 on merely numeric aggregates.
checks.append(("Reading passage text fully separated from comprehension questions and options",False))
checks.append(("Listening narrator prompts fully separated from spoken content",False))
checks.append(("Proper nouns and lemmatization errors audited",False))
report={"checks":[{"name":n,"passed":ok} for n,ok in checks],"stage_1_2_complete":all(ok for _,ok in checks)}
out=pathlib.Path("vocabulary/analysis/official-exam-quality-gates.json")
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
if not report["stage_1_2_complete"]:sys.exit(2)
