# Evidence DB (nonfiction & self-help — claims with sources)

> For fiction, use `canon.md` instead. **No fabricated citations.** If a source can't be verified, mark it `unverified` and find a real one or cut the claim. This is non-negotiable.

## Format

| ID | Claim | Source | Source type | Confidence | Used in ch |
|----|-------|--------|-------------|------------|------------|
| E001 | Sleep deprivation impairs decision-making more than alcohol impairment. | Walker, M. (2017). *Why We Sleep.*, ch. 8 | expert-opinion | high | 4 |
| E002 | The 10,000-hour rule has significant exceptions. | Macnamara et al. (2014), meta-analysis | peer-reviewed | high | 3 |
| E003 | <claim> | <unverified — needs real source> | — | — | 7 |

## Source types (with skepticism weighting)
- **peer-reviewed** — highest. Journal articles, meta-analyses.
- **journalistic** — major outlets, investigative reporting.
- **expert-opinion** — credentialed expert in their field (cite the credential).
- **official** — government statistics, court records, institutional reports.
- **anecdotal** — a single case. **Flag as illustrative, not proof.**
- **author's original analysis** — your own reasoning/data. Mark clearly.

## Confidence
- **high** — strong source, multiple supporting, consensus in field.
- **medium** — single solid source, or multiple weaker sources.
- **low** — contested, emerging, or single weak source. State this on the page.

## Rules
- **Every claim the book makes must trace to a row here** before drafting the chapter that uses it.
- **No fabrication.** A made-up source is a hard failure. Better to cut the claim.
- **Anecdotes ≠ evidence.** A story illustrates; it doesn't prove. Frame accordingly.
- **Engage the steelman.** If a strong source disagrees, cite it and engage, don't hide it.
- **Currency.** For fast-moving fields (medicine, tech), sources < 5 years unless foundational.

## Bibliography (auto-built at export)
`scripts/export.py` deduplicates entries by source and builds the back-matter bibliography from this file.
