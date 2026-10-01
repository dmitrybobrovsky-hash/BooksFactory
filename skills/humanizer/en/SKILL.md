---
name: deai-writing-en
description: >
  Audit and rewriting of English-language texts to remove AI-generation patterns.
  Language module for the Humanizer role in BooksFactory. Covers future EN translations
  of the series «Die Psychologie der korporativen Psychopathen» and any EN content.
  Two modes: audit (detect only) and rewrite (detect + fix).
layer: BooksFactory
role: humanizer
language: en
version: 1.0
created: 2026-04-18
sources:
  - blader/humanizer (29 English AI patterns)
  - skills/humanizer/ru/SKILL.md (structural template)
  - skills/humanizer/de/SKILL.md (structural template)
---

# DeAI Writing EN — Removing AI Patterns from English Text

## Purpose

Return authorial voice to English text — remove machine-generation markers without rewriting content. Not sanitization for its own sake: restoring the "Intelligent Bastard" voice in English.

---

## Position in BooksFactory Production Chain

```
PM → Writer → Editor → Humanizer → Translator
                           ▲
                           └── you are here (EN module)
```

---

## Preconditions (check BEFORE running)

1. Chapter status: `clean` (passed Editor, corrections applied)
2. Semantic structure is locked — Humanizer does not restructure arguments
3. `tonal_compass.md` of the book has been read — book map overrides all defaults in this skill
4. For EN translations: the source language version (RU or DE) has already been humanized

If precondition not met — **return artifact to previous role**.

---

## Priority Rule

Rules in this skill = defaults for English prose in general.  
**Book's tonal_compass.md → overrides all defaults.**

| Conflict | Resolution |
|----------|-----------|
| lexicon_en.md bans «tapestry». But in this chapter it's used as an intentional ironic marker. | Keep it. Map wins. |
| patterns_en.md requires breaking Rule of Three. But this chapter uses tricolon as rhythmic signature. | Keep it. Context wins. |

---

## Series Invariants (never change under any circumstances)

| Rule | Formulation |
|------|-------------|
| Reader address | Only «you». Never «one», «the reader», «we» (false solidarity) |
| Signature figure | «not because X — but because Y» — count only, never remove |
| Series voice | Expert + sharp. Not academic, not neutral, not coaching |
| Provocation subject | System/mechanism, not the reader |

---

## Module Architecture

```
BooksFactory/skills/humanizer/en/
├── SKILL.md                          ← YOU ARE HERE
└── references/
    ├── lexicon_en.md                 ← English AI markers: 3 tiers, 29+ entries
    ├── patterns_en.md                ← Structural anti-patterns of English AI text
    └── english_specific.md          ← English specifics: contractions, rhythm, register
```

### When to read sub-documents

- **Always**: `references/lexicon_en.md` — marker table
- **Always**: `references/patterns_en.md` — structural anti-patterns
- **As needed**: `references/english_specific.md` — for register and rhythm edge cases

---

## Modes

### Mode 1: AUDIT (detect)

Triggers: «check», «find markers», «audit», «flag only», «show me the problems».

Output format:

```
## AI Pattern Audit: [Chapter]

### Found Markers

| # | Type | Quote | Problem | Level |
|---|------|-------|---------|-------|
| 1 | Lexic T1 | «It's worth noting that...» | Standard AI filler | 🔴 |
| 2 | Structure | Three consecutive same-length paragraphs | Monotone rhythm | 🟡 |

### Assessment
- Total markers: N
- Critical (🔴): N
- Warning (🟡): N
- Optional (🟢): N

### Recommendations
[Specific steps]
```

### Mode 2: REWRITE (default)

Triggers: «rewrite», «clean», «humanize», «remove AI», «make it human» — or any request without explicit mode.

**Procedure (strict order):**

**Pass 1 — Diagnosis.**  
Read the full text. Build internal list of all markers found (do not show user). Cross-reference with `lexicon_en.md` and `patterns_en.md`.

**Pass 2 — Rewriting.**  
Eliminate all found markers. Rules:
- Preserve factual content without loss
- Do not add information not present in original
- Change sentence structure, not just words
- Vary length: short (3–7 words), medium, long
- Allow sentence fragments where stylistically appropriate
- Do not normalize paragraph lengths
- «you» always, «one» / «the reader» never
- Contractions where natural — «it's», «you're», «don't»

**Pass 3 — Self-check.**  
Re-read rewritten text. Check:
- Did new AI markers appear?
- Is the «you» invariant intact?
- Is the section's micro-mode preserved?
- Were any Editor failure modes reintroduced?
- Did «one», «we» (false solidarity), or «the reader» slip in?

If found — fix independently, do not return to Editor.

**Output to user:**

```
## Rewritten Text

[text]

## What Changed

| Was | Became | Reason |
|-----|--------|--------|
| «It's worth noting that X» | [restructured] | Tier-1 filler marker |
| «delve into» | [replaced] | High-frequency AI vocabulary |

## Self-check
N markers found after rewriting → fixed / none found.
```

---

## Marker Tier System

- **Tier 1 (🔴)** — Always flag. Unambiguous AI marker. Replace without discussion.
- **Tier 2 (🟡)** — Flag when clustered. One occurrence acceptable; two or more within 500 words = marker.
- **Tier 3 (🟢)** — Flag at high density. Normal in small doses; flag above 3 per 1000 words.

---

## Rewriting Principles (English)

1. **Concrete over abstract.** «Plays a vital role» → name what it actually does.
2. **Action over state.** «Serves as the foundation» → restructure as action.
3. **Human as subject.** Inanimate objects don't «highlight», «underscore», «demonstrate» — people and data do.
4. **Rhythmic variety.** Alternate short and long. Allow jagged rhythm. Monotone prose is the primary structural AI marker.
5. **Don't sterilize.** Allow conversational touches where context permits.
6. **Don't replace one cliché with another.** Removed «it's worth noting» — don't put «it should be noted» in its place. Restructure the whole sentence.
7. **Contractions are human.** In non-academic English: «it's», «you're», «won't» > «it is», «you are», «will not».

---

## Self-check for Reintroduction

Minimum checklist after Pass 3:

- [ ] No demonizing language introduced?
- [ ] «you» invariant intact — no «one», «the reader», «we» (false solidarity)?
- [ ] Section micro-mode preserved?
- [ ] No absolute statements added («never», «always», «all»)?
- [ ] No coaching tone introduced («you might want to consider», «it would be helpful to»)?
- [ ] No chatbot artifacts («I hope this helps», «let me know», «certainly»)?
