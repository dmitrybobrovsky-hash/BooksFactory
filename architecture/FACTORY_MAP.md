---
document: FACTORY_MAP
layer: BooksFactory
version: 1.1
created: 2026-04-18
updated: 2026-05-10
status: active
note: >
  Этот файл — индекс, не определения. Все термины определены в shared_vocabulary.md.
  Все контракты — в handoff_contracts.md. Здесь — карта связей и точка входа.
---

# BooksFactory — Карта фабрики (Factory Map)

> Карта актуализирована 2026-04-25 в рамках P2-1 ТЗ-аудита. Производственная цепочка переписана под beat-by-beat модель (writer-loop), список агентов расширен с 6 до **12** (включая `bf-pm` как DEPRECATED stub). Источники истины:
>
> - `archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md` §5 — фазовая ось Ф0–Ф13.
> - `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md` — точечные дыры аудита, sequence PART 1 + PART 2.
> - `archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` §13.2 — приоритетный план P0–P3 (исторический, бо́льшая часть закрыта или перенесена в ТЗ-аудит).

---

## Производственная цепочка (актуальная, 2026-04-25)

```
bf-researcher (Opus)
    ↓ outline + tonal_compass + literature_pool
bf-material-author (Opus)
    ↓ MATERIAL_Glava_NN.md (секции, beat sheets, арены, quote-anchors)
bf-planner (Opus)
    ↓ NN_beat_plan.json (13–17 beats × ~500 слов, sum=1.13×target)
bf-compiler (Sonnet, mechanical)
    ↓ NN_session_compiled.md (Session-файл с маркерами T1..T12 + REFERENCE/VERBOT/CALIBRATION)
bf-coordinator (Sonnet)
    ↓ writer-loop (per-beat, max_iterations=3):
    │   bf-writer (Opus, no tools) ↔ bf-critic (Sonnet, Read) ↔ bf-controller (Sonnet, Read/Grep/Glob) → refiner-revise
    ↓ glava.md (статус: draft)
bf-editor (Opus, Read/Grep/Write — отчёт ≤5 точек, без перезаписи)
    ↓ glava_clean.md (clean)
bf-humanizer (Opus, диспетчер по языку → skills/humanizer/{ru,de,en})
    ↓ glava_humanized.md (humanized)
final
```

| Агент | Модель | Tools | Вход | Выход |
|-------|--------|-------|------|-------|
| `bf-researcher` | opus | Read, Grep, Glob, WebSearch, WebFetch, Write | идея + серийный канон | outline, tonal_compass, verbot_liste, literature_pool |
| `bf-material-author` | opus | Read, Grep, Write | outline + tonal_compass | MATERIAL_Glava_NN.md |
| `bf-planner` | opus | Read, Grep, Glob | MATERIAL + tonal_compass | NN_beat_plan.json |
| `bf-compiler` | sonnet | Read, Write, Bash | beat_plan + MATERIAL + tonal/verbot/reference + Session_TEMPLATE | NN_session_compiled.md |
| `bf-coordinator` | sonnet | Read, Write, Glob, Grep, Task | статус главы + Session-compiled | маршрут к следующему агенту / writer-loop orchestration (после Ф8) |
| `bf-writer` | opus | — (pure LLM) | beat-промпт от coordinator (всё в тексте) | `<beat_text>` + `<word_count>` |
| `bf-critic` | sonnet | Read | beat_text + beat-описание | JSON-вердикт {action, flags, notes} |
| `bf-controller` | sonnet | Read, Grep, Glob | фаза/правка + DoD | JSON-вердикт {action: accept/warn/block} |
| `bf-editor` | opus | Read, Grep, Write | glava.md (draft) | редакторский отчёт + glava_clean.md (статус clean) |
| `bf-humanizer` | opus | Read, Edit, Write | glava_clean.md (clean) | glava_humanized.md (humanized) |

Артефакт, не прошедший контракт, — возвращается назад, не исправляется текущей ролью.

---

## Субагенты (`.claude/agents/`) — 11 агентов

> Список **синхронизирован** с `.claude/memory/architecture.md`. При расхождении — править оба файла.

| # | Агент | Статус | Назначение |
|---|-------|--------|------------|
| 1 | [`bf-coordinator`](../.claude/agents/bf-coordinator.md) | ✅ готов (v3, Ф7+Ф8 закрыты 2026-05-01) | роутинг + writer-loop + `/bf-next`, `/bf-status`, `/bf-route`, `/bf-write-loop` |
| 3 | [`bf-writer`](../.claude/agents/bf-writer.md) | ✅ готов (Ф7 закрыт 2026-05-01) | pure-LLM beat-writer, tagged-output `<beat_text>` + `<word_count>` |
| 4 | [`bf-editor`](../.claude/agents/bf-editor.md) | legacy | редактор главы post-compile, отчёт ≤5 точек, не переписывает |
| 5 | [`bf-humanizer`](../.claude/agents/bf-humanizer.md) | legacy | роутинг по языку → ru/de/en модули в `skills/humanizer/` |
| 7 | [`bf-critic`](../.claude/agents/bf-critic.md) | новый (Ф1, готов 2026-04-23) | per-beat детерминированный gate в writer-loop, JSON-вердикт, Read-only |
| 8 | [`bf-controller`](../.claude/agents/bf-controller.md) | новый (Ф0, готов 2026-04-23; расширен audit_task 2026-04-25) | DoD-валидатор фаз тюнинга и пунктов ТЗ-аудита |
| 9 | [`bf-compiler`](../.claude/agents/bf-compiler.md) | новый (Ф3, готов 2026-04-24) | механическая сборка Session из компонентов |
| 10 | [`bf-researcher`](../.claude/agents/bf-researcher.md) | новый (Ф4, готов 2026-04-24) | research, outline, tonal_compass книги |
| 11 | [`bf-material-author`](../.claude/agents/bf-material-author.md) | новый (Ф4, готов 2026-04-24) | MATERIAL_Glava_NN.md |
| 12 | [`bf-planner`](../.claude/agents/bf-planner.md) | новый (Ф5, готов) | beat-план JSON, self-check sum=1.13×target |

---

## Архитектурный слой (федеральный)

```
BooksFactory/architecture/
├── shared_vocabulary.md      ← ПЕРВЫЙ. Единый источник терминов.
├── handoff_contracts.md      ← ВТОРОЙ. Контракты передачи между ролями.
├── writing_control.md        ← ТРЕТИЙ. Beat sheet, плотность, Правило 6 (объёмы).
└── FACTORY_MAP.md            ← ЭТОТ ФАЙЛ.
```

**Иерархия**: федеральный слой → уровень книги. Правила книги (`<book>/tonal_compass.md`) дополняют, не противоречат.

---

## Правило ветвления `skills/` vs `.claude/skills/`

Это разные слои, у каждого своя роль:

| Слой | Что | Длина | Когда используется |
|------|-----|-------|---------------------|
| `skills/<role>/` | **Полные модули ролей** — длинные инструкции, references, examples, lexicon, patterns | Сотни–тысячи строк | Агент читает по требованию через `Read` (или `Skill`-вызов из диспетчера) |
| `.claude/skills/<dispatcher>/` | **Slash-command-диспетчеры** — короткие точки входа | < 200 строк | Прямой вызов автором (`/bf-something`) или агентом через `Skill`-tool |

**Критерий выбора при создании нового skill**:
- Новый skill — **диспетчер** (короткая точка входа, обращается к агенту/skills/) → `.claude/skills/`.
- Новый skill — **глубокий модуль роли** (lexicon, patterns, examples, длинные инструкции) → `skills/<role>/`.
- Если skill начинается как диспетчер и **разрастается > 200 строк** — split: диспетчер остаётся в `.claude/skills/`, тело уезжает в `skills/<role>/<topic>.md`.

---

## Скиллы ролей (`skills/`)

```
BooksFactory/skills/
├── humanizer/
│   ├── ru/           ← ГОТОВ. SKILL.md + lexicon + patterns + russian_specific.
│   ├── de/           ← ГОТОВ. SKILL.md + lexicon_de + patterns_de + german_specific.
│   └── en/           ← ГОТОВ. SKILL.md + lexicon_en + patterns_en + english_specific.
├── writer/           ← ГОТОВ. SKILL.md + self_checks + writing_principles.
├── editor/           ← ГОТОВ. SKILL.md (7-вопросный чеклист, 6 типов вмешательств).
├── project-manager/  ← ГОТОВ. SKILL.md + material_guide + session_guide. (legacy слой; пайплайн перешёл на bf-researcher/bf-material-author.)
```

## Скиллы-диспетчеры (`.claude/skills/`)

```
.claude/skills/
├── project-manager/SKILL.md
├── writer/SKILL.md
├── editor/SKILL.md
├── humanizer/SKILL.md        ← диспетчер → skills/humanizer/{ru,de,en}
├── outline-book/SKILL.md
├── draft-chapter/SKILL.md
├── edit-chapter/SKILL.md
├── repurpose-to-reels/SKILL.md
├── repurpose-to-lecture/SKILL.md
├── repurpose-to-podcast/SKILL.md
├── generate-handout/SKILL.md
├── synthesize-ideas/SKILL.md
├── check-consistency/SKILL.md
└── connect-to-existing/SKILL.md
```

---

## Книги серии и их связь с BooksFactory

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Серия SpellBooks                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  ОНМ («Она не монстр», RU)         │  MdP («Management durch Panik», DE)    │
│  Путь: <book_A>/                      │  Путь: <book_B>/  │
│  Статус: 30 глав + заключение      │  Статус: 20 глав + заключение          │
├────────────────────────────────────┴─────────────────────────────────────────┤
│  (проекты указываются в production_state.md)        │
│  Книга 4–6 — планируются                                                      │
└──────────────────────────────────────────────────────────────────────────────┘
                            │ наследуют правила
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BooksFactory (федеральный уровень)                        │
│   architecture/  │  skills/  │  .claude/agents/  │  .claude/skills/         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Текущее состояние тюнинга

Активный тюнинг идёт по двум осям одновременно:

- **Фазовая ось** — archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md §5 (Ф0–Ф13). Закрыты: Ф0–Ф8, Ф12. Незакрыты: Ф10 (hooks), Ф11 (continuity-checker), Ф13 (документация).
- **Аудит-ось** — `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md` §0.7 sequence:
  - PART 1 закрыта 2026-04-25: P0-0a, P0-0, P0-1, P0-2, P1-1, P1-2, P2-2.

Приоритетный план (archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md §13.2) — исторический.


---

## Как использовать этот файл при возврате к работе

1. Прочитай этот файл (карта).
2. Прочитай `shared_vocabulary.md` (термины) и `handoff_contracts.md` (контракты).
3. Открой `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md` §4/§4-bis — какой пункт sequence следующий.
4. Проверь fingerprint в `archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md §10.5`.
5. Запускай работу по §0.7 sequence ТЗ-аудита, не выбирая между пунктами.
