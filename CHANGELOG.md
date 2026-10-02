---
document: CHANGELOG
layer: BooksFactory
purpose: >
  Журнал версий фабрики. Каждое значимое изменение фиксируется с номером версии.
  При расхождении с текущим состоянием файлов — верить файлам, не журналу.
---

# BooksFactory — Журнал версий

## v2.10.1 — 2026-10-02: правки с проверкой

- **Режим правки с проверкой:** после каждой правки — `lint_beat` (объём против target_words, нарушения), при провале — одна повторная попытка с замечаниями; затем проверка главы и, если превышения остались, добор до 4 точечных правок. Писатель видит соседние beat-ы, чтобы не рвать стыки; вставка компенсируется сокращением. В сессии 5 правки без проверки дали новые антитезы и швы, а вставки съели сокращения (−45 слов при нужных −135).
- **Детектор антитез без ложных срабатываний** на условиях («Не держится — закрыть…») и пояснениях через двоеточие: на главе 02 скрипт = редактор (11 = 11).

---

## v2.10 — 2026-10-02: Сессия 5 — скрипты видят то, что видел только редактор

По итогам главы 02 на v2.9 (17 итераций вместо 31, редактор: «Таро», слипание сцен и пропущенная методичка ушли).
- **Антитезы:** детектор дополнен формами «не X, это Y», «X, не Y,», парой «…не список… Это…»; цитата внутри фразы не ломает счёт. Бюджет 8 теперь **включает** сигнатурную фигуру — так считает редактор. На главе 02: скрипт 14, редактор 12 + 2 скрытых (раньше скрипт 4).
- **Лимиты имён — на всю главу:** ограничения «„Имя“ — один раз» из любого beat-а плана действуют для всей главы и во всех падежах (Роршах/Роршаха). «Решение автора …» главнее остальных. Раньше лимит «Роршах» стоял у одного beat-а — в главе вышло 5.
- **Связки-мостики:** `lint_chapter` считает «Отсюда / Поэтому / Значит…» в начале предложений (лимит 2 на связку).
- **Реплики персонажей** (абзац с тире) не считаются обращением к читателю на «вы» — ложный revise в beat 5 ушёл.
- **Workflow:** запуск с середины главы восстанавливает журнал реквизита и тезисов; журнал критика не перезаписывается (`_from_N`); критик главы сверяет утверждения об исследованиях со списком литературы; **режим правки** `fixes_file` — правки по отчёту редактора только в указанных beat-ах + сборка, без смены статуса.
- **bf-planner:** бюджет антитез считается уже в плане (quote_before + сигнатура ≤ 8); лимиты имён — в форме, которую читают скрипты.
- Потолок объёма в workflow — потолок книги (anweisungen), а не коридор Draft Fat.
- Сравнение писателей (beat-ы 1–4): Sonnet не дешевле Opus (больше итераций, недобор объёма) — писатель остаётся Opus.

---

## v2.9 — 2026-10-01: Сессия 4 — уроки пилота (KS, глава 02)

**Найдено в пилоте и исправлено:**
- **Писатель не получал MATERIAL.** `slice_context.py` искал секцию по «§N», а план после правки заголовков пишет «N. …» — во всех 16 beat-ах вместо секции стояла заглушка, глава написана по одному плану. Отсюда выдуманный реквизит сцен и потерянный слой методической литературы (точки 4, 5 редактора). Теперь секция находится по любому формату, а при её отсутствии скрипт останавливается. В контекст добавлены арены главы, якоря секции и запреты буквальных повторов из MATERIAL.
- **Антитезы «не X, а Y»:** детектор видел 8 из ~20 (не ловил «Это не X — это Y», «X, а не Y», «Не X — Y»). Новый счётчик по предложениям; бюджет на главу (по умолчанию 8); писатель видит остаток бюджета ДО написания (§9 контекста); перебор — обязательное нарушение. Сигнатурная фигура считается отдельно и точнее (4 из 4 в пилоте, раньше 2).
- **Проблемы уровня главы** (повтор тезиса, слияние сцен, объём): новый `lint_chapter.py` и шаг «Глава» в workflow — критик главы назначает до 8 точечных правок, писатель правит только указанные beat-ы. Журнал главы (реквизит сцен и тезисы принятых beat-ов) передаётся писателю и критику каждого следующего beat-а.

**Расход:**
- Критик сам запускает `lint_beat.py` — минус один агент на итерацию (в пилоте 31).
- Критик в workflow читает только beat и его контекст (раньше — по роли: эталонная глава, verbot целиком, план).
- Политика вердикта: revise только за обязательные нарушения, невыполненное задание, сломанный голос, противоречие принятым beat-ам; мелочи — в `minor` для критика главы. Цель — ≈1,2 итерации на beat вместо 1,9.
- Параметры `writer_model`, `critic_model`, `beats_tag`, `end_beat` — для сравнительного прогона писателей без смешения с основной главой.

**Книга KS:** решение автора по «Таро» в гл. 2 (заголовок + ≤3) внесено в реестр формул, MATERIAL и beat-план.

---

## v2.8 — 2026-10-01: Сессия 2 — writer-loop в коде

- **Workflow `write-chapter`** (`.claude/workflows/write-chapter.js`): цикл beat-ов, итерации, решения «принять / переписать» — в программе, не в инструкции модели. На каждый beat: контекст скриптом → `bf-writer` (Opus) → `lint_beat.py` → `bf-critic` (Sonnet) → до 3 итераций. Нарушение, найденное скриптом, отправляет beat на доработку даже при «accept» критика. Сборка главы и статус — скриптами. Детерминированные шаги выполняет дешёвая модель-исполнитель (Haiku), которая только запускает `python tools/*.py`.
- `bf-critic` получает факты скрипта, сам не считает слова; судит о голосе, аудитории, переходах, провокации.
- `bf-writer`: Read — только свой контекст, Write — только свой beat.
- `bf-coordinator`: writer-loop через workflow; ручной цикл через Task — резерв.
- Цепочка: `bf-compiler` выведен из основного пути (резерв).
- Права: `Workflow(write-chapter)` разрешён без подтверждения.

---

## v2.7 — 2026-10-01: Сессия 1 — детерминированный слой

**Новые инструменты (`tools/`, описание — `tools/README.md`):**
- `manifest.py` — машиночитаемые статусы глав (`book_manifest.json`), single writer, запрет перескока этапов, `final` только автором
- `lint_beat.py` — детерминированные флаги критика: объём, запрещённые фразы, ограничения beat-плана, повторы, сквозные формулы, синтаксические фигуры, обращение «вы/Sie»
- `slice_context.py` — контекст одного beat-а: 36 КБ вместо Session 175 КБ (KS гл. 1)
- `assemble_chapter.py` — сборка главы с фактическим подсчётом слов
- `verify_sources.py` — сверка литературы по каталогам; `zotero_pool.py` — подборка автора из Zotero
- `bf_common.py` — общие функции

**Находка при проверке на KS гл. 1:** модель завышала длину beat-ов на 30–45 % (заявлено 6 145 слов, фактически 4 603 — 84 % от цели 5 500). Подсчёт слов больше не доверяется модели.

**bf-researcher:** подборка автора из Zotero (если есть) — единственный источник книг; обязательная сверка по каталогам перед GATE-2; Bash только для `python tools/*.py`.

---

## v2.6 — 2026-10-01: Сессия 0 после аудита AUDIT_2026-10-01

**Критические починки:**
- `bf-researcher.md` — добавлено обязательное поле `description` (без него Claude Code молча пропускал агента; сломано правками 2026-05-14)
- `bf-writer.md` — задано `tools: Read` (без поля агент наследовал ВСЕ инструменты, включая Write/Bash/WebSearch); текст роли приведён в соответствие
- `bf-coordinator.md` — убран хардкод `_KS` в контракте вызова критика → `<CODE>` из book_config.json (запись v2.5 «_KS naming → generic» не была выполнена)
- `tools/validate_factory.py` — шаблоны кодов книг ловят суффикс в имени файла (`anweisungen_KS.md`); добавлена проверка фронтматтера агентов (name/description/tools) и скиллов (неизвестные поля)

**Инфраструктура:**
- Хуки портированы на PowerShell (`.ps1`, exec-форма `powershell -File ${CLAUDE_PROJECT_DIR}/...`) — работают на любом Windows без установки bash/python3/Node; статус `translated` убран. (Первый вариант на Node отменён: Node на рабочих компьютерах не установлен.)
- `.claude/settings.json` — `permissions.defaultMode: acceptEdits` (правки внутри проекта без вопросов, вне — с подтверждением); `.vscode` yoloMode выключен
- `architecture/_TZ_WRITER_BEAT_BY_BEAT.md` — канон writer-loop возвращён из архива

**Когерентность:**
- `CLAUDE.md` v1.1 — по `BOOKSFACTORY.md`: два режима (B помечен нереализованным), цикл writer↔critic без controller/refiner, статусы без `translated`, нумерация правил 0–8, дерево директорий
- `production_state.md` — реликты `f-*`/controller убраны
- Скиллы `humanizer`, `check-consistency` — валидный фронтматтер, вызов только явно
- `CHANGELOG.md` — утёкшие escape-символы, ссылка на TranslationFactory

**В архив (`archive/2026-10-01_session0/`):** `bf-controller` (читал архивные файлы, роль — тюнинг фабрики), 12 устаревших скиллов эпохи PM/Obsidian, 21 снапшот `.claude/backups/`

---

## v2.5 — 2026-05-15: Параметризация фабрики (абстрактная фабрика без привязки к проекту)

**Архитектурное решение:** фабрика не содержит хардкодов конкретных проектов. Проектный контекст — через book_config.json.

**Создано:**
- templates/tpl-book-config.md — аннотированная схема манифеста проекта
- templates/tpl-book-config.json — JSON-шаблон
- tools/validate_factory.py — валидация чистоты фабрики (0 нарушений)

**Обновлено:**
- tools/init_book.py — генерирует book_config.json при инициализации книги
- tools/backup.py — удалены несуществующие файлы, добавлены templates/, tools/, skills/, method/
- CLAUDE.md — правило №8 (изоляция фабрики от проекта)

**Параметризировано (45 хардкодов в 15 файлах → 0):**
- .claude/agents/bf-researcher.md — serie/brand-voice пути → book_config.json
- .claude/agents/bf-critic.md — Band III fallback/examples → generic
- .claude/agents/bf-controller.md — scope isolation rule → validate_factory.py
- .claude/agents/bf-coordinator.md — _KS naming → generic (предыдущая сессия)
- .claude/agents/bf-material-author.md — Band III example → generic
- skills/project-manager/SKILL.md — 12 хардкодов Serie/arenen_pool → book_config.json
- architecture/FACTORY_MAP.md, writing_control.md, shared_vocabulary.md — generic paths
- skills/humanizer/de/SKILL.md — Serie/ path → generic
- method/ (3 файла) — Serie/ paths → generic
- CLAUDE.md — _testing path → book_config.json

---

## v2.4 — 2026-05-14: Вычистка переводчика из BooksFactory

**Архитектурное решение:** bf-translator и все связанные ресурсы перенесены в TranslationFactory. BooksFactory пишет только на исходном языке книги.

**Перенесено в TranslationFactory/_reference/:**
- .claude/agents/bf-translator.md
- skills/translator/ → skills_translator/
- .claude/skills/translator/ → claude_skills_translator/
- rchitecture/glossary.md

**Удалено из architecture/:**
- provocation_principles.md (специфика серии)
- oice_principles.md (специфика серии)

**Вычищены секции и строки из:**
- BOOKSFACTORY.md — §3 (перевод из Режима A), §6 (Переводчик), §7 (Этап 8 Перевод → удалён, Этап 9→8 Финал), §10 (полная замена), §11 (статус translated)
- BOOKSFACTORY_AI.md — §3 (цепочка), §6 (таблица агентов + диспетчеры), §7 (chain + table + status model), §10 (полная замена), §13 (glossary + translator refs)
- handoff_contracts.md — Контракт 5 (humanizer→translator → заменён на humanizer→final), статус translated
- FACTORY_MAP.md — bf-translator из дерева, таблицы агентов, файловых деревьев
- CLAUDE.md — цепочка, glossary, правило переводчика
- shared_vocabulary.md — «6 книгам серии» → «книгам проекта»

---

## v2.3 — 2026-05-14: Разделение фабрик — вычистка Режима C

**Архитектурное решение:** BooksFactory = forge (написание книг с нуля, Режим A/B). Режим C (редактирование готовых книг) выделен в отдельную EditorFactory. Перевод — в TranslationFactory.

**Удалено:**
- _testing/03_Manipulationen/ (76 файлов, тест-прогон Band III)
- _SMOKE_TEST_PROMPT_2026-05-10.md
- skills/editor-lite/ и .claude/skills/editor-lite/ (Mode C skill)

**Вычищены секции из:**
- BOOKSFACTORY.md — §3 Режим C, Workflow B
- BOOKSFACTORY_AI.md — Режим C (§3), Toleranzgrenze, Path 2 compiler, над-канон правила, §11c, §11d частично, Ф9 Workflow B, editor-lite refs
- bf-editor.md — Scope-estimate, Voice-continuity, PRAKTISCHE ANWENDUNG
- bf-material-author.md — Reverse-mode целиком
- bf-researcher.md — Workflow B секция и ссылки
- handoff_contracts.md — §9.3 Toleranzgrenze, §9.5b author_review, Calibration anchor, Mode C status model
- bf-controller.md, CLAUDE.md, FACTORY_MAP.md, memory/architecture.md — точечные ссылки
- skills/editor/SKILL.md, skills/project-manager/SKILL.md — editor-lite refs

**Оставлено:**
- Трёхзонная модель голоса (bf-editor.md) — полезна и для forge
- Жанровые рубрики книги (bf-editor.md) — domain-agnostic

**Перенесено:**
- Над-канонические правила (wow + юр.безопасность) — в series-bible.md

**Бэкап:** _backups/BooksFactory_pre_cleanup_2026-05-14/ (768 файлов)

## v1.1 (2026-05-09) — Test3 «Карты на стол», INCIDENT-04..08, Ф14/Ф15

**Test3 KS (МАК в организационной психологии), Главы 0–1:**
- Полный цикл researcher → material-author → planner → compiler → writer-loop
- Глава 1: 16 beats, 75% accept с первой итерации, 0 rewrite, 6145 слов

**INCIDENTs:**
- 04: continuity-блок MATERIAL >25K токенов → verbot_liste_proposals_pending.md
- 05: self-check compiler формальный → bf-material-author self-check п.11 переписан
- 06: coordinator без Task в tools → Task добавлен + реализация Task-вызова
- 07: Session >150 КБ при MATERIAL >70 КБ → Ф15
- 08: structural_pattern_repeat ложные срабатывания → pattern_budget в beat_plan

**Ф14 ✅ — Изоляция bf-critic + meta-critic (2026-05-08):**
- bf-critic: +3 флага (cross_chapter_phrase_repeat, structural_pattern_repeat, attribution_missing)
- bf-coordinator: critic через Task-вызов, planned_pattern_exceptions
- bf-editor: meta-critic (cross-section проверки)

**Ф15 ✅⚠ — Масштабируемость compiler (2026-05-09):**
- Фильтрация входа compiler: только релевантные арены/§IX/формулы. Экономия ~42%
- Открытый риск: reference_chapter не фильтруется (23% Session)

**Файлы изменены:** bf-coordinator.md, bf-critic.md, bf-editor.md, bf-compiler.md, bf-planner.md, bf-material-author.md, handoff_contracts.md, BOOKSFACTORY_AI.md (v1.7→v1.9), +templates/tpl-verbot-liste-proposals-pending.md, +templates/tpl-session-state.md

**Аудит 2026-05-10 (v2):** 16 находок (0 Critical, 2 High, 11 Medium, 3 Low). Отчёт: `_FACTORY_AUDIT_2026-05-10.md`. Починено: C1–C4, D1–D3, A1, A2, B1, F1, E1/E2 (пометки), G1.

**Источники:** _SESSION_STATE.md Test3 записи (20)–(42), _test3_report.md addendum 2026-05-09

## v1.0 (2026-05-03) — Smoke test пройден, 14 дефектов починены

**Smoke test writer-loop:**
- Книга IU, Глава 01: 13 beats, все accepted, глава собрана
- Полная цепочка material-author → planner → compiler → writer-loop → compile_draft — работает

**14 дефектов найдены и починены:**
- D1: critic file paths в промпте координатора
- D2: revise-промпт — пересканирование всего текста после fix
- D3: persistence beats на диск (починен в прогоне)
- D4: writer target_words = обязательный минимум + critic threshold 0.85
- D5: compiler включает «Для углублённого изучения» из quellen_pool
- D6: compile_draft — `---` между beats запрещены
- D7: compile_draft — заголовок `# Глава NN` после frontmatter
- D8: writer continuity — проверка дублей с предыдущим beat
- D9: переходы между beats — writer + critic (transition_break) + coordinator промпт
- C1: writer голос — «рассказ очевидца» для всех beats + critic (lecture_mode)
- C2: writer аудитория — термины через образ + critic (audience_mismatch)
- I1: permissions auto-allow
- I2: editor Q8–Q10 (голос, аудитория, швы)
- I3: compile_draft — заголовки секций при смене section

**Файлы изменены:**
- `.claude/agents/bf-writer.md` — D4, C1, C2, D8, D9
- `.claude/agents/bf-critic.md` — D4, C1, C2, D9 (3 новых флага: lecture_mode, audience_mismatch, transition_break)
- `.claude/agents/bf-coordinator.md` — D1, D2, D3, D5, D6, D7, D9, I3
- `.claude/agents/bf-compiler.md` — D5
- `skills/editor/SKILL.md` — I2 (Q8, Q9, Q10)
- `.claude/agents/bf-editor.md` — I2

## v0.9 (2026-05-01) — Writer-loop (Ф7 + Ф8)

**Ф7: bf-writer.md — полная переделка:**
- Pure LLM: tools убраны полностью (структурная защита)
- Beat-by-beat: один вызов = один beat (~500 слов)
- Tagged output: `<beat_text>` + `<word_count>` + `<notes>`
- 7 самопроверок, revise-режим, типовые отказы

**Ф8: bf-coordinator.md — writer-loop:**
- v3: routing + writer-loop orchestrator
- Модель: haiku → sonnet
- Loop: writer → critic → accept/revise/rewrite (max 3 итерации/beat)
- Scratchpad для accepted beats
- compile_draft: сборка beats в главу + build-лог
- Exit conditions: эскалация при rewrite или 3 неудачных итерациях
- Новая slash-команда: `/bf-write-loop NN`

**Обновлены:**
- `architecture/FACTORY_MAP.md` — writer tools, coordinator model
- `.claude/memory/architecture.md` — Ф7/Ф8 отмечены закрытыми
- `BOOKSFACTORY.md` — сняты пометки *(дорожная карта)* с Этап 5, Критик, Контролёр
- `BOOKSFACTORY_AI.md` — статусы Ф7/Ф8 → ✅, coordinator sonnet

## v0.8 (2026-05-01) — Аудит, документация, консистентность

**Новые документы:**
- `BOOKSFACTORY.md` — концепция, процессы и инструкция для человека (13 разделов)
- `BOOKSFACTORY_AI.md` — техническая инструкция для Claude Code со статусами элементов
- `_HANDOFF_AUDIT_2026-05-01.md` — результаты аудита
- `CHANGELOG.md` — этот файл

**Починка аудита (12 пунктов, все закрыты):**
- A1: фазы агентов синхронизированы между FACTORY_MAP и memory/architecture
- A2: shared_vocabulary §1 обновлён до 8-звенной цепочки
- A3: статус `clean` — зафиксировано: ставит `bf-editor`
- A4: bf-humanizer — путь к диспетчеру исправлен
- A5: glossary.md подключён к FACTORY_MAP и CLAUDE.md
- A6: check_chapter_status.sh — комментарии приведены в соответствие с кодом
- A7: `outline-ready` добавлен в оба хука
- A8: update_production_state.sh — timestamp с минутами + ротация 45 дней
- A9: `project_manager` → `project-manager` (kebab-case, 9 файлов)
- A10: лимит строк диспетчеров 100 → 200

**Обновлены:**
- CLAUDE.md — добавлены новые документы и glossary.md
- _SESSION_START_PROMPT.md → v2.6

**Инфраструктура (паттерны Крола):**
- `CHANGELOG.md` — формализованный журнал версий
- `tools/backup.py` + `tools/rollback.py` — бэкап федеральных документов + откат одной командой
- `tools/init_book.py` — быстрый старт новой книги одной командой

**Порядок в корне:**
- 10 журнальных файлов перенесены в `archive/journal/`
- Ссылки в `_SESSION_START_PROMPT.md` обновлены

**Источник:** сравнение с Claude Code Starter v6.1.0 (Крол) — 4 паттерна для заимствования, 8 преимуществ фабрики зафиксированы

## v0.7 (2026-04-27) — Первый прогон, smoke test

- Первый реальный тест-прогон на книге IU (Immuner Geist)
- Smoke test фабрики на полном цикле
- Валидация bf-researcher, bf-material-author, bf-compiler
- Выявлены дефекты GATE-1 (универсальность) и arenen_pool

**Источники:** `_first_run_2026-04-27.md`, `_smoke_test_2026-04-25.md`

## v0.6 (2026-04-26) — Pre-Ф8 подготовка

- Аудит целостности: fingerprint-проверка всех агентов
- Pre-Ф8 фиксы: bf-controller, bf-critic, bf-coordinator
- Post-pre-Ф8 аудит: проверка всех контрактов
- Валидация writing_control.md (Правило 6)

**Источники:** `_pre_f8_validation_2026-04-26.md`, `_TZ_PRE_F8_FIXES_2026-04-26.md`, `_TZ_POST_PRE_F8_AUDIT_2026-04-26.md`

## v0.5 (2026-04-25) — Аудит и тюнинг

- Полный аудит целостности фабрики (95 KB документации)
- Smoke test конвейера
- Фиксы по результатам аудита

**Источники:** `_TZ_AUDIT_FIXES_2026-04-25.md`, `_smoke_test_2026-04-25.md`

## v0.4 (2026-04-23) — Тюнинг фабрики, часть 2

- Расщепление bf-pm на bf-researcher + bf-material-author + bf-compiler
- Handoff contracts 6–9 (beat-by-beat pipeline)
- bf-critic, bf-controller, bf-coordinator — новые агенты
- Фазовый план Ф0–Ф13

**Источники:** `_HANDOFF_FACTORY_TUNING_2026-04-23.md`, `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md`

## v0.3 (2026-04-18) — Продолжение архитектуры

- voice_principles.md, provocation_principles.md, writing_control.md
- shared_vocabulary.md как single source of truth
- Система микрорежимов секций

**Источник:** `_CONTINUATION_2026-04-18.md`

## v0.2 — Базовая архитектура

- FACTORY_MAP, handoff_contracts (1–5), brand-voice
- bf-writer, bf-editor, bf-humanizer, bf-translator — первые агенты
- skills/ с полными модулями ролей
- Хуки check_chapter_status и update_production_state

## v0.1 — Инициализация

- CLAUDE.md, series-bible, Session_TEMPLATE
- Базовая структура директорий
- Концепция производственной цепочки
