---
name: literature-provenance
description: Verify DOI identity, retrieve registry-generated citations and locate short verbatim evidence in an authorized offline corpus. Use for source-backed engineering research, reference preparation and claim checks; venue labels are local policy, not proof of correctness.
---

Use [doi.py](scripts/doi.py) to fetch CSL metadata and BibTeX through DOI content negotiation. Supply an independently expected title and an explicit venue policy. DOI/title mismatch, missing fields, unsupported redirects or network failure stop processing. Never invent or silently repair bibliographic fields. The script retains returned citation bytes, source URLs and hashes for approved records; unknown/preprint venues remain blocked unless the policy explicitly permits that tier.

Use [locate_quote.py](scripts/locate_quote.py) to locate an exact passage in a permitted local PDF or form-feed-delimited text export. Evidence includes source/page hashes, offsets, page index and nearest detectable heading. Quotes are limited to 40 counting units (words, or individual CJK characters). Return all matches, not a preferred occurrence. Missing text, failed extraction or ambiguous equations require manual review; never fabricate a page/heading or reconstruct a formula by guesswork.

An authorized acquisition node can keep a hashed offline archive for other entitled nodes. Metadata access is not full-text access or permission to redistribute copyrighted material. Record retrieval rights, version and permitted recipients before synchronization. Keep restricted corpora and private network facts out of public repositories.

After authorized acquisition, [archive_corpus.py](scripts/archive_corpus.py) creates an offline index with file hashes and explicit source/version/access/recipient records. Missing rights block indexing. The tool does not grant entitlements, download paywalled documents or automatically redistribute the archive.

See [tool contracts and provenance](references/toolchain.md) for formats, dependencies, venue policy and extraction limitations. Verify a claim against the actual passage and surrounding assumptions; a high-tier venue or a DOI match alone does not validate the claim.
