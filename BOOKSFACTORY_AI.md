---
document: BOOKSFACTORY_AI
layer: BooksFactory
version: 2.5
created: 2026-05-01
updated: 2026-05-15
purpose: >
  Техническая инструкция BooksFactory для Claude Code.
  Параллельный документ к BOOKSFACTORY.md (для человека).
  Та же структура — но вместо концепции: файлы, агенты, форматы, контракты.
  КРИТИЧЕСКОЕ ПРАВИЛО: каждый элемент имеет статус (✅ ГОТОВ / 🚧 ДОРОЖНАЯ КАРТА / ⛔ DEPRECATED).
  Элементы со статусом ✅ — НЕ ПЕРЕДЕЛЫВАТЬ. Они работают. Дублирование запрещено.
  При расхождении между этим документом и специализированными файлами
  (handoff_contracts.md, FACTORY_MAP.md, agent .md) — специализированный файл побеждает.
reads_first:
  - BOOKSFACTORY.md (параллельный документ для человека)
  - architecture/shared_vocabulary.md (термины)
  - architecture/handoff_contracts.md (контракты)
  - architecture/FACTORY_MAP.md (карта агентов)
---

# BooksFactory — Техническая инструкция для Claude Code

> Этот документ — зеркало `BOOKSFACTORY.md`. Каждый раздел здесь соответствует разделу в человеческом документе. Человек видит «что и зачем», ты видишь «как и чем».
>
> **Статусы элементов:**
> - ✅ **ГОТОВ** — реализовано, работает, протестировано. Не переделывать, не дублировать, не «улучшать» без явного запроса автора.
> - 🚧 **ДОРОЖНАЯ КАРТА** — спроектировано, но не реализовано. Реализовывать по запросу автора.
> - ⛔ **DEPRECATED** — существует на диске, но не используется. Не вызывать, не ссылаться.
>
> **Аудит 2026-05-01:** пункты A1–A5, A7, A9 закрыты. Подробности: _HANDOFF_AUDIT_2026-05-01.md.

---

## Оглавление

1. [Системные требования и точка входа](#1-системные-требования-и-точка-входа)
2. [Источники истины](#2-источники-истины)
3. [Два режима работы — техническая реализация](#3-два-режима-работы--техническая-реализация)
4. [Точки вмешательства автора — реализация остановок](#4-точки-вмешательства-автора--реализация-остановок)
5. [Компоненты системы — файловая структура](#5-компоненты-системы--файловая-структура)
6. [Агенты — спецификации и статусы](#6-агенты--спецификации-и-статусы)
7. [Производственная цепочка — техническая последовательность](#7-производственная-цепочка--техническая-последовательность)
8. [Принцип изоляции — правила для агентов](#8-принцип-изоляции--правила-для-агентов)
9. [Иерархия правил — приоритет файлов](#9-иерархия-правил--приоритет-файлов)
10. [Языки и перевод — маршрутизация](#10-языки-и-перевод--маршрутизация)
11. [Команды эксплуатации](#11-команды-эксплуатации)
12. [Глоссарий — ссылки на определения](#12-глоссарий--ссылки-на-определения)
13. [Карта документации — полная](#13-карта-документации--полная)

---

## 1. Системные требования и точка входа

> Параллель: BOOKSFACTORY.md §1 «Что такое BooksFactory»

### Среда исполнения ✅

- **Платформа:** Claude Code (CLI)
- **Рабочая директория:** `BooksFactory/`
- **Первый файл при старте:** `CLAUDE.md` (конституция фабрики)
- **Второй файл:** `architecture/FACTORY_MAP.md` (карта агентов и связей)
- **Кодировка:** UTF-8 везде. Кириллические файлы читать через Python: `python -c "print(open(r'path', encoding='utf-8').read())"`. PowerShell `Get-Content` для кириллицы запрещён — MCP-транспорт необратимо ломает кириллицу в PowerShell-выводе.

### Порядок чтения при старте сессии ✅

1. `CLAUDE.md` — конституция, производственная цепочка, ключевые файлы, запреты
2. `architecture/FACTORY_MAP.md` — карта агентов, их модели, tools, входы/выходы
3. `.claude/memory/production_state.md` — текущее состояние всех книг и глав
4. `<book>/book_config.json` — манифест текущего проекта (пути к файлам, параметры голоса, структура)
5. `.claude/memory/architecture.md` — быстрая карта архитектуры и статус тюнинга

---

## 2. Источники истины

> Параллель: BOOKSFACTORY.md §2 «Зачем она нужна»

### Федеральные документы (уровень фабрики) ✅

| Документ | Назначение | Статус |
|----------|-----------|--------|
| `architecture/shared_vocabulary.md` | Единственный источник определений терминов. Нельзя переопределять термин в другом файле. | ✅ ГОТОВ |
| `architecture/handoff_contracts.md` | Контракты передачи между ролями. 9 контрактов (1–5 section-by-section, 6–9 beat-by-beat). | ✅ ГОТОВ |
| `architecture/writing_control.md` | Beat sheet, контроль раздувания, word budgets, Правило 6 (объёмы). | ✅ ГОТОВ |
| `architecture/FACTORY_MAP.md` | Карта агентов, модели, tools, входы/выходы, индекс всей архитектуры. | ✅ ГОТОВ |

### Серийные документы (уровень серии) ✅

| Документ | Назначение | Статус |
|----------|-----------|--------|

### Документы уровня книги

Создаются `bf-researcher` для каждой книги. Формат и содержание — `skills/project-manager/SKILL.md` §«РЕЖИМ A: RESEARCH».

| Документ | Назначение |
|----------|-----------|
| `<book>/anweisungen_XX.md` | Операционная инструкция книги |
| `<book>/stil_und_ton_XX.md` | Тональная карта книги (заменяет legacy `tonal_compass.md`) |
| `<book>/arbeitsplan_XX.md` | Полный план книги: части × главы |
| `<book>/quellen_pool_XX.md` | Источники. Формат определяется полем bibliography_mode в anweisungen |
| `<book>/arenen_pool_XX.md` | Репозиторий арен + per-chapter блоки + контроль |

### bibliography_mode (поле в anweisungen_XX.md)

Формат оформления источников. Задаётся АВТОРОМ в брифе, researcher фиксирует без изменений.

| Значение | Автор пишет в брифе | Поведение фабрики |
|----------|--------------------|--------------------|
| per-chapter | «источники в каждой главе» | Раздел «Для дополнительного изучения» в конце каждой главы. researcher формирует per-chapter блоки в quellen_pool. compiler включает блок в session. coordinator включает блок при сборке главы. editor проверяет наличие и качество. |
| unified | «источники в конце книги» | Один раздел «Для дополнительного изучения» в конце книги. researcher формирует один общий список. compiler НЕ включает блок в session главы. coordinator НЕ вставляет блок при сборке. editor НЕ требует блок в главе. Ссылки внутри глав на источники не делаются. |

Выдумывать источники запрещено. Вставлять нерелевантные ради количества запрещено.
| `<book>/<technique>_XX.md` | Ведущая техника книги |
| `<book>/session_template_XX.md` | Технический протокол T2–T14 |
| `<book>/_skvoznye_formuly_XX.md` | Реестр сквозных операциональных формул (T13). Обновляется bf-material-author. |
> ⚠ Масштабируемость: 44 КБ / 5 MATERIAL (аудит 2026-05-10). Мониторить при >100 КБ.
| `<book>/_verbot_liste_proposals_pending.md` | Staging для §IX-предложений запретов (T14). Создаётся bf-researcher, обновляется bf-material-author. Введён 2026-05-07 после INCIDENT-04. |
| `<book>/abgrenzung_XX.md` | Отграничения (только для книг в серии) |

### Состояние производства ✅

| Файл | Назначение | Статус |
|------|-----------|--------|
| `.claude/memory/production_state.md` | Статусы всех глав всех книг. Обновлять после каждой смены статуса. | ✅ ГОТОВ |
| `.claude/memory/architecture.md` | Быстрая карта архитектуры. Синхронизирована с FACTORY_MAP. | ✅ ГОТОВ |

---

## 3. Два режима работы — техническая реализация

> Параллель: BOOKSFACTORY.md §3 «Что фабрика умеет»

### Режим A: новая книга с нуля ✅

Полная цепочка:
```
bf-researcher → bf-material-author → bf-planner → bf-compiler → bf-coordinator(writer-loop) → bf-editor → bf-humanizer
```

Точка входа: автор задаёт тему, аудиторию, язык, тон. `bf-researcher` создаёт слой A книги (§2 «Документы уровня книги»). Автор одобряет. Далее — per-chapter производство.

### Режим B: продолжение начатой книги ✅

Точка входа: `bf-coordinator /bf-status NN` — определить, на каком этапе глава. `bf-coordinator /bf-next NN` — определить следующего агента. Слой A уже существует.

## 4. Точки вмешательства автора — реализация остановок

> Параллель: BOOKSFACTORY.md §4 «Принцип работы и роль автора»

### Обязательные остановки (агент НЕ продолжает без одобрения автора) ✅

| Точка | Агент | Что ждёт одобрения | Формат одобрения |
|-------|-------|---------------------|------------------|
| После исследования | `bf-researcher` | Outline + tonal_compass + literature_pool + arenen_pool | Автор пишет «принимаю» или указывает правки |
| После сборки материала | `bf-material-author` | MATERIAL_Glava_NN.md | Автор просматривает и одобряет |
| После редактуры | `bf-editor` | Редакторский отчёт (≤5 точек) | Автор применяет правки или отклоняет |

### Автоматические этапы (не требуют одобрения) ✅

Планирование (`bf-planner`), сборка задания (`bf-compiler`), координация (`bf-coordinator`), гуманизация (`bf-humanizer`).

### Эскалации (система сама уведомляет автора при проблемах) ✅

| Ситуация | Агент | Действие |
|----------|-------|---------|
| 3 неудачные итерации на одном beat | `bf-coordinator` (writer-loop) | STOP, уведомление автору |
| action: "rewrite" от критика | `bf-critic` | Возврат к `bf-planner`, уведомление |
| action: "block" от контролёра | `bf-controller` | STOP конвейера, эскалация |
| 3 цикла editor↔writer без закрытия | `bf-coordinator` | Эскалация автору |

---

## 5. Компоненты системы — файловая структура

> Параллель: BOOKSFACTORY.md §5 «Из чего фабрика состоит»

### Структура директории ✅

```
BooksFactory/
├── CLAUDE.md                         ✅ конституция
├── BOOKSFACTORY.md                   ✅ документ для человека
├── BOOKSFACTORY_AI.md                ✅ этот документ (для Claude Code)
├── Session_TEMPLATE.md               ✅ шаблон session (общий)
├── │
├── architecture/                     ✅ федеральные документы
│   ├── FACTORY_MAP.md                ✅ карта фабрики
│   ├── shared_vocabulary.md          ✅ единый словарь терминов
│   ├── handoff_contracts.md          ✅ контракты передачи (9 шт.)
│   ├── writing_control.md            ✅ контроль объёма и плотности
│
├── method/                           ✅ метод и уроки
│   ├── METHOD.md                     ✅ цикл от идеи до переведённой главы
│   ├── LESSONS_LEARNED.md            ✅ уроки из прогонов
│   └── PATTERNS_OF_FAILURE.md        ✅ паттерны провала с grep-маркерами
│
├── skills/                           ✅ полные модули ролей
│   ├── writer/                       ✅ SKILL.md + self_checks + writing_principles
│   ├── editor/                       ✅ SKILL.md (7-вопросный чеклист, 6 типов вмешательств)
│   ├── humanizer/ru/                 ✅ SKILL.md + lexicon + patterns + russian_specific
│   ├── humanizer/de/                 ✅ SKILL.md + lexicon_de + patterns_de + german_specific
│   ├── humanizer/en/                 ✅ SKILL.md + lexicon_en + patterns_en + english_specific
│   └── project-manager/              ✅ SKILL.md + material_guide + session_guide (legacy, используется как reference)
│
├── .claude/
│   ├── agents/                       агенты (статусы в §6)
│   ├── skills/                       диспетчеры (статусы в §6)
│   ├── hooks/                        🚧 частично реализованы (см. §8)
│   ├── memory/                       ✅ production_state + architecture
│   └── settings.json                 ✅ конфигурация хуков
│
├── templates/
│   ├── tpl-session-template.md       ✅ шаблон session_template книги
│   ├── tpl-book-config.json          ✅ JSON-шаблон манифеста проекта
│   └── tpl-book-config.md            ✅ аннотированная схема с описанием полей
│
├── tools/                            ✅ init_book.py, backup.py, rollback.py, validate_factory.py, starter_form.html
│
├── archive/                          ✅ завершённые проекты
└── _outbound/                         тестовые проекты (игнорировать при работе с фабрикой)
```

### Журнальные файлы (операционная история, перенесены в archive/journal/)

```
archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md            ✅ ТЗ writer-loop (фазовый план Ф0–Ф13)
archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md         ✅ аудит целостности
archive/journal/_TZ_POST_PRE_F8_AUDIT_2026-04-26.md   ✅ пост-аудит
archive/journal/_TZ_PRE_F8_FIXES_2026-04-26.md        ✅ пре-Ф8 правки
archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23.md  ✅ история тюнинга
archive/journal/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md  ✅ продолжение (§13.2 — приоритетный план)
archive/journal/_CONTINUATION_2026-04-18.md            ✅ история
archive/journal/_first_run_2026-04-27.md               ✅ результат первого прогона
archive/journal/_smoke_test_2026-04-25.md              ✅ smoke test
archive/journal/_pre_f8_validation_2026-04-26.md       ✅ пре-Ф8 валидация
```

Эти файлы — операционная история. Не удалять, не переименовывать. Читать при необходимости для контекста.

---

## 6. Агенты — спецификации и статусы

> Параллель: BOOKSFACTORY.md §6 «Команда специалистов»

### Сводная таблица агентов

| # | Агент | Файл | Модель | Tools | Статус |
|---|-------|------|--------|-------|--------|
| 1 | Исследователь | `.claude/agents/bf-researcher.md` | opus | Read, Grep, Glob, WebSearch, WebFetch, Write | ✅ ГОТОВ |
| 2 | Сборщик материала | `.claude/agents/bf-material-author.md` | opus | Read, Grep, Write | ✅ ГОТОВ |
| 3 | Планировщик | `.claude/agents/bf-planner.md` | opus | Read, Grep, Glob | ✅ ГОТОВ |
| 4 | Сборщик задания | `.claude/agents/bf-compiler.md` | sonnet | Read, Write, Bash | ✅ ГОТОВ |
| 5 | Координатор | `.claude/agents/bf-coordinator.md` | sonnet | Read, Write, Glob, Grep | ✅ ГОТОВ (routing + writer-loop) |
| 6 | Писатель | `.claude/agents/bf-writer.md` | opus | — (pure LLM) | ✅ ГОТОВ (beat-by-beat) |
| 7 | Критик | `.claude/agents/bf-critic.md` | sonnet | Read | ✅ ГОТОВ |
| 8 | Контролёр | `.claude/agents/bf-controller.md` | sonnet | Read, Grep, Glob | ✅ ГОТОВ |
| 9 | Редактор | `.claude/agents/bf-editor.md` | opus | Read, Grep, Write | ✅ ГОТОВ |
| 10 | Гуманизатор | `.claude/agents/bf-humanizer.md` | opus | Read, Edit, Write | ✅ ГОТОВ |
| — | PM (legacy) | `.claude/agents/bf-pm.md` | opus | Read | ⛔ Удалён 2026-05-06 (заменён bf-researcher + bf-material-author + bf-compiler). |

### Диспетчеры (`.claude/skills/`)

| Диспетчер | Файл | Статус |
|-----------|------|--------|
| project-manager | `.claude/skills/project-manager/SKILL.md` | ✅ ГОТОВ |
| writer | `.claude/skills/writer/SKILL.md` | ✅ ГОТОВ |
| editor | `.claude/skills/editor/SKILL.md` | ✅ ГОТОВ |
| humanizer | `.claude/skills/humanizer/SKILL.md` | ✅ ГОТОВ |
| outline-book | `.claude/skills/outline-book/SKILL.md` | ✅ ГОТОВ |
| draft-chapter | `.claude/skills/draft-chapter/SKILL.md` | ✅ ГОТОВ |
| edit-chapter | `.claude/skills/edit-chapter/SKILL.md` | ✅ ГОТОВ |
| check-consistency | `.claude/skills/check-consistency/SKILL.md` | ✅ ГОТОВ |
| connect-to-existing | `.claude/skills/connect-to-existing/SKILL.md` | ✅ ГОТОВ |
| synthesize-ideas | `.claude/skills/synthesize-ideas/SKILL.md` | ✅ ГОТОВ |
| generate-handout | `.claude/skills/generate-handout/SKILL.md` | ✅ ГОТОВ |
| repurpose-to-reels | `.claude/skills/repurpose-to-reels/SKILL.md` | ✅ ГОТОВ |
| repurpose-to-lecture | `.claude/skills/repurpose-to-lecture/SKILL.md` | ✅ ГОТОВ |
| repurpose-to-podcast | `.claude/skills/repurpose-to-podcast/SKILL.md` | ✅ ГОТОВ |

### Полные модули ролей (`skills/`)

| Модуль | Путь | Статус |
|--------|------|--------|
| Writer | `skills/writer/` (SKILL.md + self_checks.md + writing_principles.md) | ✅ ГОТОВ |
| Editor | `skills/editor/` (SKILL.md) | ✅ ГОТОВ |
| Humanizer RU | `skills/humanizer/ru/` (SKILL.md + lexicon + patterns + russian_specific) | ✅ ГОТОВ |
| Humanizer DE | `skills/humanizer/de/` (SKILL.md + lexicon_de + patterns_de + german_specific) | ✅ ГОТОВ |
| Humanizer EN | `skills/humanizer/en/` (SKILL.md + lexicon_en + patterns_en + english_specific) | ✅ ГОТОВ |
| Project Manager | `skills/project-manager/` (SKILL.md + material_guide + session_guide) | ✅ ГОТОВ (legacy, используется как reference для bf-researcher / bf-material-author) |

---

## 7. Производственная цепочка — техническая последовательность

> Параллель: BOOKSFACTORY.md §7 «Как идёт работа над одной главой»

### Полная цепочка ✅

```
bf-researcher (Opus)
    ↓ outline + tonal_compass + literature_pool + arenen_pool
    ↓ [ОСТАНОВКА: одобрение автора]
bf-material-author (Opus)
    ↓ MATERIAL_Glava_NN.md
    ↓ [ОСТАНОВКА: одобрение автора]
bf-planner (Opus)
    ↓ NN_beat_plan.json
bf-compiler (Sonnet)
    ↓ NN_session_compiled.md
bf-coordinator (writer-loop)                          ✅
    ↓ writer ↔ critic ↔ controller ↔ refiner
    ↓ glava_NN.md (статус: draft)
bf-editor (Opus)
    ↓ редакторский отчёт → [ОСТАНОВКА: автор вносит правки]
    ↓ glava_NN_clean.md (статус: clean)
bf-humanizer (Opus)
    ↓ glava_NN_humanized.md (статус: humanized)
    ↓ [ОСТАНОВКА: финальная вычитка автора]
final
```

### Статусы этапов

| Этап | Агент | Контракт | Статус этапа |
|------|-------|----------|-------------|
| 1. Исследование | `bf-researcher` | — (первый в цепочке) | ✅ ГОТОВ |
| 2. Сборка материала | `bf-material-author` | Контракт 1 (расщеплённый) | ✅ ГОТОВ |
| 3. Планирование | `bf-planner` | — | ✅ ГОТОВ |
| 4. Сборка задания | `bf-compiler` | Контракт 8 (compiler→coordinator) | ✅ ГОТОВ |
| 5. Письмо (writer-loop) | `bf-coordinator` + `bf-writer` + `bf-critic` + `bf-controller` | Контракт 6 (writer↔critic), Контракт 7 (→controller) | ✅ ГОТОВ |
| 6. Редактура | `bf-editor` | Контракт 9 (editor→humanizer) | ✅ ГОТОВ |
| 7. Гуманизация | `bf-humanizer` | Контракт 5 (humanizer→final) | ✅ ГОТОВ |
| 8. Финал | автор | — | ✅ ГОТОВ |

### Модель статусов главы ✅

```
(нет файла) → outline-ready → material-draft → draft → review → clean → humanized → final
```

Подстатусы writer-loop внутри `draft`: `compiled` → `beat-N-draft` → `beat-N-accepted` → `draft`.

Полная спецификация: `.claude/memory/production_state.md`.

### Контракты передачи ✅

Все 9 контрактов определены в `architecture/handoff_contracts.md`:

| Контракт | Маршрут | Статус |
|----------|---------|--------|
| 1 | PM → Писатель (legacy section-by-section) | ✅ ГОТОВ |
| 2 | Писатель → Редактор | ✅ ГОТОВ |
| 3 | Редактор → Писатель (отчёт) | ✅ ГОТОВ |
| 4 | Писатель → Гуманизатор | ⛔ DEPRECATED (заменён Контрактом 9) |
| 6 | Writer ↔ Critic (per-beat loop) | ✅ ГОТОВ (контракт описан; loop-машина реализована, Ф8 закрыт 2026-05-03) |
| 7 | Любая фаза → Controller | ✅ ГОТОВ |
| 8 | Compiler → Coordinator | ✅ ГОТОВ |
| 9 | Editor → Humanizer (beat-by-beat pipeline) | ✅ ГОТОВ |

---

## 8. Принцип изоляции — правила для агентов

> Параллель: BOOKSFACTORY.md §8 «Принцип изоляции»

### Правила изоляции ✅

1. Артефакт, не прошедший контракт, возвращается на предыдущую роль. Текущая роль не исправляет нарушение чужого контракта.
2. Нарушение формулируется конкретно: не «MATERIAL неполный», а «отсутствует beat sheet в секции 3 — возврат к bf-material-author».
3. Гуманизатор модифицирует текст — это его домен. Но содержательные ошибки (логика, аргументация) — домен редактора. Гуманизатор не латает логические дыры, а возвращает главу.
4. Редактору запрещён Edit-инструмент. Только Read, Grep, Write (отчёт).

### Правила, которые нельзя нарушать (из CLAUDE.md) ✅

1. Читатель — «ты» (RU) / «du» (DE) / «you» (EN). Никогда «вы» / «Sie».
2. Субъект провокации — система/механизм, не читатель.
4. Редактор не переписывает — только указывает. Edit-инструмент запрещён.
5. Тональная карта книги побеждает дефолты фабрики. Иерархия: книга > серия > фабрика.
6. «Паттерн» — максимум 2 раза на главу. Сигнатурная фигура — максимум 8 на главу, ≤50 на книгу (cross-chapter счётчик в continuity-блоке MATERIAL).

### Хуки контроля статуса

| Хук | Файл | Назначение | Статус |
|-----|------|-----------|--------|
| PreToolUse | `.claude/hooks/check_chapter_status.sh` | Блокировка Write/Edit если статус главы = `final` | 🚧 ЧАСТИЧНО (блокирует только `final`; полная проверка переходов не реализована) |
| PostToolUse | `.claude/hooks/update_production_state.sh` | Логирование изменений в production_state.md | 🚧 ЧАСТИЧНО (дописывает HTML-комментарии; без структуры, без ротации) |

Конфигурация хуков: `.claude/settings.json` ✅

---

## 9. Иерархия правил — приоритет файлов

> Параллель: BOOKSFACTORY.md §9 «Три уровня правил»

### Три уровня — приоритет при конфликте ✅

```
Книга > Серия > Фабрика
```

| Уровень | Источник | Что фиксирует |
|---------|----------|---------------|
| 1. Фабрика (дефолт) | `architecture/shared_vocabulary.md` | Голос, обращение, запреты — общие для всех книг |
| 2. Серия | *(серийные файлы создаются per-project)* | Терминология, инварианты обращения, кросс-книжные правила |
| 3. Книга | `<book>/stil_und_ton_XX.md` (или legacy `<book>/tonal_compass.md`) | Голос конкретной книги, override-правила |

**Правило конфликта:** книжный `stil_und_ton` > серийный уровень > фабричный дефолт.

**Исключение:** обращение «ты»/«du»/«you» фиксируется на уровне серии и не может быть overridden на уровне книги.

**Где проверяется:** Редактор при работе с главой читает все три уровня. Писатель полагается на Session — туда уже впечён актуальный голос (T1–T4 собирает Compiler).

---

## 10. Языки и перевод — маршрутизация

> Параллель: BOOKSFACTORY.md §10 «Языки и перевод»

Перевод книг выполняется в TranslationFactory. BooksFactory пишет на исходном языке книги.

### Маршрутизация гуманизатора ✅

bf-humanizer читает поле language в frontmatter главы и загружает соответствующий языковой модуль:
- language: ru → skills/humanizer/ru/SKILL.md
- language: de → skills/humanizer/de/SKILL.md
- language: en → skills/humanizer/en/SKILL.md

---

## 11. Команды эксплуатации

> Параллель: BOOKSFACTORY.md §11 «Как пользоваться»

### Slash-команды координатора ✅

| Команда | Назначение |
|---------|-----------|
| `/bf-status NN` | Текущий статус главы NN с обоснованием по артефактам |
| `/bf-next NN` | Определить следующего агента для главы NN |
| `/bf-route <agent> NN` | Вызвать агента на главе NN с проверкой вход-контракта |

### Начать новую книгу ✅

1. Автор заполняет `tools/starter_form.html` → скачивает `book_config.json`.
2. Claude получает файл, запускает `python tools/init_book.py book_config.json`.
3. `init_book.py` создаёт `<CODE>/` с `book_config.json` и заготовками файлов.
4. Claude вызывает `bf-researcher` — тот читает `book_config.json` и создаёт слой A (§2).
5. Автор одобряет слой A.
6. Для каждой главы: `bf-material-author` → `bf-planner` → `bf-compiler` → далее по цепочке.

### Продолжить начатую книгу ✅

1. `/bf-status NN` — узнать статус.
2. `/bf-next NN` — узнать следующего агента.
3. `/bf-route <agent> NN` — запустить.

### Автоматический поиск повторов 🚧

Скрипт в `tools/` для поиска:
- Дублированных фраз между главами одной книги
- Дублированных аннотаций в блоках «Для углублённого изучения»
- Дословных повторов между томами серии

Скрипт ищет дублированные фразы, аннотации и примеры между главами одной книги и между томами серии. Результат — отчёт с конкретными совпадениями.

### Проверка кросс-книжной консистентности 🚧

Автоматический поиск фактических противоречий между книгами серии. Результат — отчёт с конкретными расхождениями.

### Инфраструктура обслуживания (паттерны Крола) 🚧

Источник: сравнение с Claude Code Starter v6.1.0 (alexeykrol). Ни один паттерн не меняет агентов, контракты или скиллы.

| Паттерн | Что даёт | Статус |
|---------|---------|--------|
| Быстрый старт | Автор заполняет `tools/starter_form.html` в браузере, скачивает `book_config.json`. Claude запускает `python tools/init_book.py <path/to/book_config.json>`. Создаёт директорию книги с заготовками. | ✅ |
| Validate factory | `python tools/validate_factory.py`. Проверяет, что файлы фабрики не содержат хардкодов конкретных проектов. | ✅ |
| Backup + rollback | `python tools/backup.py` / `python tools/rollback.py`. Бэкапы в `.claude/backups/TIMESTAMP/`. Pre-rollback бэкап создаётся автоматически. | ✅ |
| Аддитивный merge CLAUDE.md | Обновление фабрики в книжных проектах без затирания кастомизаций | 🚧 |
| Формализация changelog | `CHANGELOG.md` с версиями вместо журнальных `_TZ_*` файлов | ✅ |

---

### Оперативный журнал сессии (`_SESSION_STATE.md`) ✅

> Параллель: BOOKSFACTORY.md §11 «Если сессия прервалась»

**Правило:** перед началом каждого значимого шага (создание артефакта, смена статуса главы, запуск агента) — обновить `_SESSION_STATE.md` в рабочей директории книги. После завершения шага — обновить снова.

**Формат записи:**

```
## [timestamp]
status: in_progress | completed
step: <что делается / что сделано>
agent: <какой агент работает>
next: <что следующее>
artifacts_created: <список созданных файлов, если есть>
```

**Порядок записей:** новые — сверху, старые — внизу (reverse chronological). Код при старте читает первую запись после заголовка — это текущее состояние.

**Две записи на шаг:**

1. **ДО начала:** `status: in_progress`, `step: создание session_template_<CODE>.md`, `next: —`
2. **ПОСЛЕ завершения:** `status: completed`, `step: session_template_<CODE>.md создан`, `next: verbot_liste_<CODE>.md`

**При старте новой сессии:** если `_SESSION_STATE.md` существует — прочитать. Последняя запись определяет точку продолжения:
- `status: completed` → начать `next`
- `status: in_progress` → шаг не завершён, перепроверить артефакт и завершить или переделать

**Создание файла:** при инициализации новой книги (`tools/init_book.py`) или вручную из шаблона `templates/tpl-session-state.md`.

### Ротация _SESSION_STATE.md 🚧

При >100 записей или >100 КБ — архивировать старые записи в `_SESSION_STATE_archive_YYYY-MM-DD.md`, оставить последние 30. Coordinator при старте читает только первую запись — архивированные не нужны для навигации. Аудит 2026-05-10 (E1): 57 КБ / 42 записи за Test3 KS.

---

## 11b. События 2026-05-10 (v2.0)

**Аудит фабрики ✅** (`archive/journal/_FACTORY_AUDIT_2026-05-10.md`): 16 находок (0 Critical, 2 High, 11 Medium, 3 Low). Все починены. Найдена и устранена скрытая BEL-контаминация (\x07) в 3 файлах (BOOKSFACTORY_AI.md, FACTORY_MAP.md).

**Smoke-test хвоста цепочки ✅** (записи _SESSION_STATE Test3 (45)–(47)): editor → humanizer пройден end-to-end на Главе 0 KS «Карты на стол». Editor cycle 2 → clean. Humanizer RU 4 правки. **A3 закрыта** — хвост цепочки имеет production-доказательство.


**Канон формата заголовков ✅** (`architecture/shared_vocabulary.md §2`): в контенте книги `## N. Название` (не `## §N`). § только в служебной нотации фабрики. Касается: bf-material-author/writer/compiler (генерация), bf-editor (проверка в clean-pass как точка отчёта).

**Архивация мета-документации**: 6 audit/repair/handoff файлов из корня → `archive/journal/`. В корне только `_SESSION_START_PROMPT.md`.

---

## 11d. События 2026-05-13 (v2.2) — трёхзонная модель голоса, жанровые рубрики книги

**Контекст:** длинная сессия по Band III «Manipulationen» — две главы (Kap 01 Einführung + Kap 02 Ontologie und Epistemologie) доведены до `clean-final`. Сессия вскрыла три ограничения канона фабрики, которые исправлены тут же.

### Трёхзонная модель голоса ✅
**Файл:** `.claude/agents/bf-editor.md`.

Раньше канон знал два состояния — «разрешено» и «BLOCK». Хулиганство, точечный сленг, провокативные анекдоты, рискованные аналогии попадали в дыру и часто получали BLOCK по инерции. Введены три зоны:
- **Зелёная** — канонические метафоры разрешённой территории, Street-Calibration сцены, диагностические рефрены. Не трогать.
- **Жёлтая** — «хулиганство в рамках» (острота, сарказм, рискованная аналогия). **НЕ блокировать категорически.** Per case через контрольный вопрос: «если переписать как нейтральное утверждение — пропадёт ли диагностическая работа?» Да → оставить, INFO/WARN. Нет → декорация, флагать.
- **Красная** — поп-shortcut, терапия, оптимизм, цифры без источника. BLOCK с штатным весом.

**Кейс-валидация:** на Kap 02 первый проход флагнул Tiger/Hai/Balz как BLOCK (зоопоэзия) — ошибка, биология разрешена T6 канона книги, зелёная зона. Matrix/rote Pille красная — резать; театральные образы жёлтая — per case; анекдот jüdischer Weiser жёлтая → WARN → удалён как декорация без диагностической функции.

### Жанровые рубрики книги — отдельный слой ✅
**Файлы:** `.claude/agents/bf-editor.md` (расширенная инициализация), книжный канон `anweisungen_XX.md` + `verbot_liste_XX.md`.

Каждая книга может иметь жанровые блоки, которые редактор не должен флагать как нарушения. Эти блоки фиксируются в `<book>/anweisungen_XX.md` и оформляются как явные исключения в `<book>/verbot_liste_XX.md` (формат §X-N). Editor читает `anweisungen_XX.md` **до** вынесения вердикта; в `_architecture_debt_XX.md` ведётся открытый реестр структурных отклонений тома, чтобы не флагать их повторно.

**Кейс-валидация:** Band III имеет рубрику `## PRAKTISCHE ANWENDUNG` в 21 из 22 контентных глав — жанровый блок тома. Первый проход editor-а на Kap 02 трактовал её как §E структурное BLOCK (терапия/протоколы) и предлагал удалить → ошибка, разрушает архитектуру всего тома. После канон-правки: рубрика разрешена в форме 3–5 жёстких диагностических вопросов по 4 критериям (конкретный адресат / отвечаемость / без рецепта / без защитного контракта), `verbot_liste_MAN.md §E-1` явное исключение. Editor пересмотрел: переформат, не удаление.


## 12. Глоссарий — ссылки на определения

> Параллель: BOOKSFACTORY.md §12 «Глоссарий ключевых понятий»

Все термины определены в одном месте: `architecture/shared_vocabulary.md` ✅

Не переопределять термины в других файлах. Если нужен новый термин — добавить в shared_vocabulary.md.

Диагностический вопрос для нового термина: «Применимо ли это ко всем книгам?» — если да, в shared_vocabulary.md; если нет — в словарь конкретной книги.

---

## 13. Карта документации — полная

> Параллель: BOOKSFACTORY.md §13 «Карта документации»

### Архитектура и правила

| Задача | Файл | Статус |
|--------|------|--------|
| Конституция фабрики | `CLAUDE.md` | ✅ |
| Концепция для человека | `BOOKSFACTORY.md` | ✅ |
| Техническая инструкция для AI | `BOOKSFACTORY_AI.md` (этот файл) | ✅ |
| Журнал версий фабрики | `CHANGELOG.md` | ✅ |
| Карта агентов и связей | `architecture/FACTORY_MAP.md` | ✅ |
| Определения терминов | `architecture/shared_vocabulary.md` | ✅ |
| Контракты передачи | `architecture/handoff_contracts.md` | ✅ |
| Контроль объёма и плотности | `architecture/writing_control.md` | ✅ |

### Серия

| Задача | Файл | Статус |
|--------|------|--------|

### Метод и уроки

| Задача | Файл | Статус |
|--------|------|--------|
| Метод от идеи до главы | `method/METHOD.md` | ✅ |
| Уроки из прогонов | `method/LESSONS_LEARNED.md` | ✅ |
| Паттерны провала | `method/PATTERNS_OF_FAILURE.md` | ✅ |

### Агенты

| Задача | Файл | Статус |
|--------|------|--------|
| Исследователь | `.claude/agents/bf-researcher.md` | ✅ |
| Сборщик материала | `.claude/agents/bf-material-author.md` | ✅ |
| Планировщик | `.claude/agents/bf-planner.md` | ✅ |
| Сборщик задания | `.claude/agents/bf-compiler.md` | ✅ |
| Координатор | `.claude/agents/bf-coordinator.md` | ✅ |
| Писатель | `.claude/agents/bf-writer.md` | ✅ (beat-by-beat, pure LLM) |
| Критик | `.claude/agents/bf-critic.md` | ✅ |
| Контролёр | `.claude/agents/bf-controller.md` | ✅ |
| Редактор | `.claude/agents/bf-editor.md` | ✅ |
| Гуманизатор | `.claude/agents/bf-humanizer.md` | ✅ |
| PM (legacy) | `.claude/agents/bf-pm.md` | ⛔ Удалён 2026-05-06 |

### Состояние производства

| Задача | Файл | Статус |
|--------|------|--------|
| Статусы глав | `.claude/memory/production_state.md` | ✅ |
| Быстрая карта архитектуры | `.claude/memory/architecture.md` | ✅ |

### Фазовый план тюнинга

| Задача | Файл | Статус |
|--------|------|--------|
| ТЗ writer-loop (Ф0–Ф13) | `archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md` | ✅ (документ); Ф7–Ф8 реализованы 2026-05-01; 🚧 Ф9–Ф13 |
| Аудит целостности | `archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md` | ✅ |

### Незакрытые фазы тюнинга (дорожная карта)

> Источник: `archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md` §5 (исторический).
> Закрытые фазы (Ф0–Ф8, Ф12) зафиксированы в CHANGELOG.md. Ниже — только открытые.

#### Ф10 — Hooks: полная проверка переходов статусов | 🚧

**Scope:** `check_chapter_status.sh` использует `VALID_TRANSITIONS` (подготовлена, не активирована) для блокировки невалидных переходов (не только `final`). `update_production_state.sh` получает структурированное логирование с ротацией.

**DoD:** Хук блокирует переход `draft → humanized` (минуя `clean`) и пропускает `draft → review`. Логирование содержит timestamp, агент, статус до/после. Ротация — 45 дней.

**Зависимости:** нет.

#### Ф11 — Continuity-checker: кросс-книжная проверка | 🚧

**Scope:** Скрипт(ы) в `tools/` для поиска дублей и противоречий: (а) дублированные фразы между главами одной книги, (б) дублированные аннотации в блоках «Для дополнительного изучения», (в) дословные повторы между томами серии. Опционально: агент `bf-continuity-checker` (sonnet, Read/Grep) для вызова из coordinator.

**DoD:** Скрипт находит известные проблемы MdP: 19 дублированных аннотаций, повтор «Und jetzt dein Büro» в гл. 6/7, превышение лимита конструкции в гл. 3. Результат — отчёт с конкретными совпадениями.

**Зависимости:** нет (можно реализовать независимо).



#### Ф15 — Масштабируемость bf-compiler (открыто 2026-05-09, частично закрыто) | ✅⚠

**Scope:** bf-compiler собирает Session-файл, объединяя MATERIAL главы + session_template + brief-артефакты + reference. Текущая реализация передаёт всё inline, что приводит к обрыву compiler на главах с MATERIAL > 70 КБ. Рецидив зафиксирован 2026-05-08 (запись 23) и 2026-05-09 (запись 30) — на Главе 1 KS (MATERIAL 76 КБ). Главы 3–5 имеют MATERIAL 92–123 КБ, compiler там тоже не пройдёт.

**Симптом:** обрыв сессии Code на стадии compiler без явной ошибки.

**Гипотеза (по убыванию вероятности):**
1. Превышение бюджета токенов входа compiler (250+ КБ inline — сумма MATERIAL + template + verbot + skvoznye + arenen + arbeitsplan + остальное).
2. Time-out на Write большого Session-файла.
3. Загрязнение родительской сессии (отвергнуто — рецидив в чистой сессии тоже).

**Варианты починки:**
- (а) **Фильтрация входа.** Compiler копирует в Session только релевантное: только три арены текущей главы (не весь arenen_pool); только §IX, релевантные главе (не весь verbot_liste); только формулы из _skvoznye_formuly, упомянутые в beat_plan (не весь реестр).
- (б) **Split-compile.** Session собирается за 2–3 прохода по T-блокам.
- (в) **Reference-mode для writer.** Writer читает Session + по ссылкам читает дополнительное. Меняет contract.

**Закрыто 2026-05-09 как вариант (а) — фильтрация входа.**

Проверка на Главе 1 KS (MATERIAL 74.6 КБ): Session собран без обрыва, размер 175.8 КБ — мягкий лимит 150 превышен, жёсткий 200 OK. Экономия фильтрации ~42% (без неё ~318 КБ). Рецидивный обрыв снят.

**Открытый риск (отложено):** `reference_chapter` (предыдущая глава как контекст) не фильтруется по канону, занимает 23% Session. Для глав с reference > 50 КБ Session перевалит за жёсткий лимит. На текущей KS (главы 3500–5800 слов) маловероятно, но возможно.

**Если блокировка повторится** — переход к варианту (б) split-compile или (в) reference-on-demand. Сейчас не делать (Karpathy: не делай заранее).

**DoD изначально:** compiler собирает Session для глав MATERIAL до 130 КБ ≤ 200 КБ. **Не достигнуто полностью** (мягкий лимит 150 превышен на 25.8 КБ), но рабочее состояние.

**Зависимости:** —

#### Ф13 — Документация и стабилизация | 🚧

**Scope:** Финальная синхронизация всех документов, закрытие TODO, чистка. Включает: аддитивный merge CLAUDE.md (паттерн Крола), обновление _SESSION_START_PROMPT.md до актуального состояния, верификация всех cross-references.

**DoD:** Новая сессия Claude Code, начавшая с `_SESSION_START_PROMPT.md`, корректно ориентируется без чтения архивных журналов. Все ссылки между файлами валидны.

**Зависимости:** желательно после Ф9–Ф11 (чтобы документировать финальное состояние), но частично выполняется по ходу (как сегодняшний аудит).

#### Ф14 — Изоляция bf-critic + meta-critic (введено 2026-05-08) | ✅

**Scope:** После эксперимента 2026-05-08 (sonnet vs opus как critic) обнаружено: (а) inline-режим writer+critic = ложные accept; (б) у bf-critic отсутствуют флаги для тонких дефектов.

**Сделано (2026-05-08):**
- bf-critic.md: добавлены флаги `cross_chapter_phrase_repeat`, `structural_pattern_repeat`, `attribution_missing`.
- bf-coordinator.md: правило изоляции — bf-critic вызывается как subagent, не inline.
- bf-editor.md: расширение до meta-critic (cross-section проверки повторов, паттернов, атрибуции).

**Дополнено 2026-05-09 (INCIDENT-06):** при первой попытке запуска после Ф14 обнаружено: у bf-coordinator отсутствовал `Task` в `tools` — правило изоляции было декларировано в документации, но физически невозможно к исполнению. Добавлено: `Task` в frontmatter coordinator, технический подраздел «Реализация: Task-вызов» в bf-coordinator.md. Урок для протокола: документационное закрытие фазы ≠ исполнительное закрытие. Будущие фазы — проверять реализуемость до пометки ✅.

**Дополнено 2026-05-09 (INCIDENT-08):** проверка Ф14 на реальном writer-loop (Глава 1 KS, draft v2) показала: флаг `structural_pattern_repeat` без знания о плановых паттернах в beat_plan даёт ложные срабатывания на каждую плановую сигнатуру с beat 4. Code обошёл через инструкцию в промпте — это workaround, не системное решение. Починено: (а) `bf-coordinator.md` Task-контракт расширен полем `planned_pattern_exceptions`; (б) `bf-critic.md` использует это поле для эффективного порога; (в) `bf-planner.md` дополнен описанием опциональной секции `pattern_budget` в beat_plan.json. Урок: новый флаг критика требует проверки на реальном loop перед закрытием — статические тесты недостаточны.

**DoD:** повторный эксперимент с правильной архитектурой даёт измеримую разницу между моделями critic. До этого — модель critic не менять.

**Зависимости:** —
