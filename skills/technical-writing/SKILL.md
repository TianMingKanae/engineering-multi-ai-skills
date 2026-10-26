---
name: technical-writing
description: Plan, draft and revise evidence-backed technical English, including paper sections, abstracts, captions, theses, reports and reviewer responses. Use for manuscript structure, clarity or a style pass; not for generating unverified results or changing publication criteria.
---

# Technical writing

Write for the actual reader and purpose. Plan the argument, draft it, then revise evidence, structure and language in separate passes. Preserve technical meaning while making the prose easier to follow. Prefer honest, accurate, complete, accessible, concise and diplomatic writing over impressive wording.

These notes adapt the planning and revision approach of Mike Markel, *Writing in the Technical Fields: A Step-by-Step Guide for Engineers, Scientists, and Technicians*, IEEE Press / Wiley, 1994. The guides are condensed, rewritten guidance with synthetic examples, not book excerpts or a substitute for the book. No book PDF or private project context is bundled or required. Manuscript-specific practices below are toolkit adaptations; the target publication's current author instructions and the user's authorized scope take precedence.

## Workflow

1. Identify the audience, document type, requested action and publication/house style. State the purpose in one sentence. Use an existing approved outline when available; do not introduce an approval pause for routine assigned drafting. Resolve a genuinely consequential scope ambiguity before investing in a long draft.
2. Map each proposed claim to its evidence and conditions. Use the project's accepted evidence register when available, or explicit source/results references. Keep missing evidence as an unresolved item in working notes; do not invent a citation, number, significance test or completed experiment.
3. Outline in the order of the reader's questions. Separate the problem, method, observations, interpretation and limitations. Draft without optimizing every sentence. For planning details, read [process.md](references/process.md).
4. Revise factual accuracy and scope before organization, paragraphs, sentences, words, graphics and mechanics. Use [checklists.md](references/checklists.md). A shorter sentence that changes a condition or a technical term is not an improvement.
5. Reopen the revised artifact, verify references/values/notation and the requested change. Follow the project's existing section ownership and review/publication workflow. A style pass never constitutes independent technical verification or permission to submit or send a document.

## Load only the needed reference

- Paper outline, abstract, introduction, results or conclusion: [structure.md](references/structure.md).
- Paragraph flow, voice, emphasis and word choice: [paragraphs-sentences-words.md](references/paragraphs-sentences-words.md).
- Captions, plots, tables or publication layout: [graphics-design.md](references/graphics-design.md).
- Punctuation, units, notation and confused words: [handbook.md](references/handbook.md).
- Articles, tense, agreement or writing for multilingual readers: [esl.md](references/esl.md).
- Reviewer response, cover letter, technical email, proposal or progress report: [other-documents.md](references/other-documents.md).

## Optional read-only style scan

```shell
python scripts/style_check.py draft.tex
python scripts/style_check.py draft.md --only wordy,passive,acronym
```

Paths above are relative to this skill directory. The checker flags phrases with line numbers; it never edits a file and exits zero when a scan succeeds, including when it finds suggestions. Invalid arguments or unreadable input return a nonzero exit. Use `--help` for categories. Flags are prompts to reread, not errors or publication acceptance criteria. Passive voice, specialist vocabulary and long sentences can be appropriate. Read the complete sentence before changing it.

This is a lexical heuristic, not a grammar checker, citation validator, statistical test or full Markdown/LaTeX parser. It skips common displayed math and bibliography blocks in TeX; complex macros, inline definitions and formatting can still produce false positives or omissions. Verify captions in the rendered manuscript as well. Meaning, evidence and house style decide whether a suggestion is useful.

## Evidence and collaboration boundaries

Keep result, inference and recommendation distinct. Report the comparison, sample/workload, uncertainty and limitations actually supported; do not generalize from a narrow test. State practical magnitude when known and distinguish it from statistical significance. Missing journals or failed cases cannot be hidden by fluent prose.

Keep internal task routing, private paths and audit bookkeeping out of reader-facing prose. Retain limitations, unfavorable findings and reproducibility information needed to judge the work; put supplementary detail in appropriately referenced appendices or supporting material. Do not move a material qualification out of view merely to improve style. Preserve coauthor ownership and make proposed edits through the existing authorized workflow. When reviewer responses promise a revision or experiment, verify it exists before claiming completion.
