---
document: humanizer/en/references/english_specific.md
layer: BooksFactory
version: 1.0
created: 2026-04-18
description: English-specific rules for humanizer. Register, contractions, rhythm, series rules.
---

# English-Specific Rules

## E-01 — Contractions: Human Signal

AI-generated English often avoids contractions in an attempt to sound «professional».

| AI default | Human version |
|-----------|--------------|
| it is | it's (in non-academic prose) |
| you are | you're |
| do not | don't |
| will not | won't |
| cannot | can't |
| they are | they're |
| there is | there's |

**Rule**: In the series (non-academic register), use contractions where natural. Absence of contractions in all cases = AI marker.

**Exception**: In a passage written for deliberate cold/clinical register (per tonal_compass.md) — no contractions may be correct. Check the map.

---

## E-02 — «you» as the only reader address

Series invariant. Every language module enforces this.

| Forbidden | Fix |
|-----------|-----|
| one (as impersonal reader) | you |
| the reader | you |
| we (false solidarity) | you — or name the specific group |
| people in this situation | you |

**Example:**  
❌ «When one encounters this pattern in their workplace...»  
✅ «When you encounter this pattern in your workplace...»

---

## E-03 — Register Calibration

The series voice in English = expert + sharp. Not:

| Register | Why forbidden |
|----------|--------------|
| Academic | Dry, impersonal, authority through complexity |
| Corporate | Hollow, hedged, meaningless |
| Coaching | Soft suggestions instead of positions |
| Journalistic (neutral) | False balance, no authorial position |

**Correct register markers**:
- Direct claims without hedging
- Contractions where natural
- Specific examples over abstract principles
- Irony allowed, sarcasm rationed
- Short punchy sentences after long analytical ones

---

## E-04 — Signature Figure in English

«not because X — but because Y»

Same rules as RU and DE:
- Count only, never remove
- Limit ≤ 8 per chapter
- Do not add softening words around it
- Preserve the parallel structure of X and Y

---

## E-05 — Verb Choice: Action Over State

AI defaults to weak state verbs.

| AI state verb | Human action alternative |
|--------------|-------------------------|
| is a testament to | demonstrates / proves / shows |
| serves as | is / works as (or restructure) |
| stands as | is (often just delete the phrase) |
| represents | is / means |
| boasts | has (or show it concretely) |
| features | has / includes |
| highlights that | X shows / the data shows / this means |
| underscores | confirms / proves / makes clear |

**Rule**: Inanimate objects do not «highlight», «underscore», «demonstrate». People do. Data does.

---

## E-06 — Syntactic Variety

AI text defaults to Subject-Verb-Object in every sentence. Human prose varies.

Allowed variations:
- Start with a time/place/condition clause: «When the meeting ended, ...»
- Start with a short fragment: «Three years. That's how long it took.»
- Invert for emphasis: «What he didn't expect was the silence.»
- Use questions: «Why does this matter?» — then answer.
- One-word or two-word sentences for punch: «It didn't.» «Wrong.»

---

## E-07 — Promotional Language (forbidden in the series)

| Marker | Why problematic |
|--------|----------------|
| breathtaking | Promotional, non-analytical |
| stunning | Same |
| renowned | Vague authority claim |
| nestled | Geographic cliché |
| groundbreaking | Inflation, usually unearned |
| revolutionary | Same |
| in the heart of | Decorative geography |
| world-class | Meaningless intensifier |

---

## E-08 — After Translation from RU/DE: New EN AI Fingerprints

When a chapter has been translated into English, new AI markers may appear that weren't in the source.

**High-risk new markers after RU→EN translation:**
- «It is important to note» (from «важно отметить»)
- «One can observe» (from «можно наблюдать»)
- «In this regard» (from «в этой связи»)
- Passive voice inflation (from RU passive constructions)
- Over-formalization (RU formal → EN stiff)

**High-risk after DE→EN translation:**
- «Against this backdrop» (from «vor diesem Hintergrund»)
- «In this context» (from «in diesem Zusammenhang»)
- Nominalstil translated literally → English noun-heavy constructions

**Rule**: After translation, run a full Pass 1 specifically checking for translation-induced markers — these are different from native AI markers.
