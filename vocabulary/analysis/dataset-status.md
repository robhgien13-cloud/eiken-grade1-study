# Dataset ingestion status

| Dataset | State | Notes |
|---|---|---|
| CEFR-J v1.5 | Raw CSV imported | A1-B2 |
| Octanove C1/C2 v1.0 | Raw CSV imported | C1-C2 |
| wordfreq | Dependency/integration added | Corpus not copied; enrichment not run |
| CMUdict | Dependency/integration added | Dictionary not copied; enrichment not run |
| Open English WordNet | Optional integration added | External download required; not bundled or tested |
| Official EIKEN exams | Reference only | Copyrighted questions/audio not redistributed |
| pnsk-lab/eiken-vocab | Under review | Repository pipeline is not equivalent to a licensed ready-to-publish dataset |
| Kelly, EFLLex, academic lists | Under review | Verify dataset-specific reuse terms and overlap |

Important: adding integration code does not mean the third-party data were imported or that enrichment ran. Run and validate locally/CI before reporting coverage or match rates.
