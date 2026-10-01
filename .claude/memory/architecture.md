---
document: memory/architecture
layer: BooksFactory
updated: 2026-05-10
purpose: >
  Быстрая карта архитектуры. Загружать вместо полного чтения всех файлов
  когда нужна ориентация без деталей.
---

# BooksFactory — Архитектурная память

## Статус фабрики

Фабрика **в активной фазе тюнинга**. Базовая инфраструктура (architecture/method/skills/.claude/agents/) была собрана к 2026-04-18, но с 2026-04-23 идёт пересборка пайплайна по новой модели (writer-loop, beat-уровень, MATERIAL → planner → compiler → coordinator). См. источники истины:

- `archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md` §5 — фазовый план Ф0–Ф13 (основная ось).
- `archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` §13.2 — приоритетный план P0–P3 (аудит целостности).
- `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md` — точечные дыры аудита 2026-04-25.

**Закрытые фазы**: Ф0, Ф1, Ф2, Ф3, Ф4, Ф5, Ф6, Ф7 (writer beat-level, 2026-05-01), Ф8 (loop-машина, 2026-05-01), Ф12 (smoke test, 2026-05-03), Ф14, Ф15⚠.
**Незакрытые**: Ф10 (hooks), Ф11 (continuity-checker), Ф13 (документация).

## Где что лежит

### Архитектурный слой
- `architecture/shared_vocabulary.md` — определения всех терминов (секция, beat, арена, MATERIAL, Session...)
- `architecture/handoff_contracts.md` — что передаётся между ролями, условия возврата
- `architecture/writing_control.md` — beat sheet, контроль раздувания, word budgets, Правило 6 (объёмы по типу книги)
- `architecture/FACTORY_MAP.md` — индекс всего выше

### Метод
- `method/METHOD.md` — цикл от идеи до переведённой главы
- `method/LESSONS_LEARNED.md` — уроки из ОНМ и MdP
- `method/PATTERNS_OF_FAILURE.md` — паттерны провала с grep-маркерами

### Скиллы ролей
- `skills/project-manager/` — SKILL.md + material_guide.md + session_guide.md
- `skills/writer/` — SKILL.md + self_checks.md + writing_principles.md
- `skills/editor/` — SKILL.md
- `skills/humanizer/ru/` — SKILL.md + lexicon + patterns + russian_specific
- `skills/humanizer/de/` — SKILL.md + lexicon_de + patterns_de + german_specific
- `skills/humanizer/en/` — SKILL.md + lexicon_en + patterns_en + english_specific

### Субагенты (.claude/agents/) — 11 агентов

| # | Агент | Статус | Назначение / фаза |
|---|-------|--------|---------------------|
| 1 | `bf-coordinator` | обновлён v3 (Ф8 закрыт, 2026-05-01) | роутинг + writer-loop, модель sonnet |
| 3 | `bf-writer` | обновлён (Ф7 закрыт, 2026-05-01) | pure-LLM beat-writer, без tools, tagged-output |
| 4 | `bf-editor` | legacy | редактор главы (post-compile), отчёт ≤5 точек, не переписывает |
| 5 | `bf-humanizer` | legacy | роутинг по языку → ru/de/en модули в `skills/humanizer/` |
| 7 | `bf-critic` | новый (Ф1, готов) | per-beat детерминированный gate в writer-loop, JSON-вердикт, Read-only |
| 8 | `bf-controller` | новый (Ф0, готов) | DoD-валидатор фаз тюнинга. Расширен контрактом `audit_task` 2026-04-25 (P0-0a). |
| 9 | `bf-compiler` | новый (Ф3, готов) | механическая сборка Session из MATERIAL + beat_plan + tonal_compass + verbot_liste + reference_chapter |
| 10 | `bf-researcher` | новый (Ф4, готов) | research, outline, tonal_compass книги |
| 11 | `bf-material-author` | новый (Ф4, готов) | MATERIAL_Glava_NN.md (секции, beat sheets, арены, quote-anchors) |
| 12 | `bf-planner` | новый (Ф5, готов) | beat-план JSON: 13–17 beats × ~500 слов, sum_target_words = 1.13 × chapter_target |

Source-of-truth по фазам: `archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md` §5. Точечные правки агентов: `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md`.

### Серийные документы (корень)
