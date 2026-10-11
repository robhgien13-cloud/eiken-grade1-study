# Lexical enrichment integrations

These integrations provide access to further resources without copying large upstream corpora into this public repository.

- **wordfreq**: Python dependency, computes Zipf frequency from the installed package; its source corpus is not redistributed here.
- **CMUdict**: Python dependency, provides American English pronunciation entries. Keep upstream copyright notices when redistributing derived content.
- **Open English WordNet**: optional external lexical database via the `wn` Python package; download separately using `python -m wn download oewn:2024`. WordNet data are **not** bundled. Credit Open English WordNet / Princeton WordNet as required by their license.

## Quick start

```bash
pip install -r requirements.txt
python -m wn download oewn:2024
python vocabulary/tools/enrich_vocabulary.py --limit 100 --output vocabulary/analysis/sample-enriched.csv
```

The output includes source, CEFR, Zipf frequency, CMU pronunciation and optional WordNet synset IDs. These are **tools only**; full dataset enrichment has not been executed or validated yet. The `wn` WordNet API should be smoke-tested before relying on it in production.
