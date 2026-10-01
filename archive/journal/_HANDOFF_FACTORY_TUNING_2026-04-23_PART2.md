# HANDOFF — Factory Tuning, Session 2026-04-23 (Part 2)

> Продолжение `_HANDOFF_FACTORY_TUNING_2026-04-23.md`.
> Читать **после** первого handoff-а — этот файл фиксирует прогресс внутри сессии + новые дефекты из research.
> Автор — Dmitry Bobrovsky. Язык общения — русский. Рукописи — немецкий.

---

## 0. Жёсткие рамки работы (обновлено 2026-04-23 вечер)

**Делегированное направление исполняется, не переспрашивается.** План утверждён в ТЗ §5. Фазы Ф2…Ф11 в фиксированном порядке. Формальные «ок начинать?», «продолжить?» — запрещены (см. MEMORY `feedback_decision_style.md`).

### 0.1 Когда ИСПОЛНЯТЬ без вопросов (по умолчанию)

- Фаза по ТЗ с ясным DoD (§9) → Write/Edit сразу.
- Проверка fingerprint-а → если совпадает, идти дальше без доклада.
- Создание нового файла из контракта ТЗ (bf-compiler, bf-researcher и т. д.) → Write, потом показ итога.
- Правка существующего файла по прописанному плану → Edit, потом показ diff.
- Самопроверка через bf-controller → исполнять по его вердикту.

### 0.2 Когда ЭСКАЛИРОВАТЬ автору

- Fingerprint разошёлся с ожидаемым состоянием (§10.5).
- Найден реальный блокер / неоднозначность в ТЗ, не решаемая анализом.
- Работа выходит за одобренный scope (ТЗ §8 «что НЕ меняется»).
- bf-controller вернул `action: "block"` с причиной, требующей решения автора.
- Обнаружена двойная работа (правка в промежуточную форму вместо конечной).

### 0.3 Что остаётся как было

- **Band III отложен.** К третьей книге возвращаемся позже.
- **Не дублировать фабрику** под конкретную книгу. Специализации — в `tonal_compass.md` книги.
- **Cite, don't reconstruct** — перед спецификационным ответом Grep/Read.
- **Ф7 + Ф8 не в одну сессию** (риск сломать пайплайн).
- **Никаких «переходных форм»** без конечного контракта из ТЗ.

### 0.4 Контроль качества — через bf-controller

Валидацию каждой фазы делает агент `bf-controller` (файл: `BooksFactory/.claude/agents/bf-controller.md`). Не автор. Автор получает только эскалации.

Controller проверяет **четыре уровня**:
1. **DoD-checks** — файл существует, YAML валиден, контракт ТЗ выполнен.
2. **Runtime-integrity** — ссылки, tag-контракт, JSON-schema, tool-capability, scope-isolation, contract-drift.
3. **Hang-detection** — infinite loops, loop-bounds, exit-paths, compiler preflight, escalation wiring, fixture completeness.
4. **Dry-run** (для Ф7/Ф8) — симуляция accept/revise/rewrite/compile-paths без реального запуска.

Любой из четырёх уровней может выдать `block`. Автор видит эскалацию только при `block` или `warn`, требующем решения.

---

## 1. Что СДЕЛАНО в этой сессии (2026-04-23)

### 1.1 Правило 6 добавлено в `writing_control.md` ✅

Файл: `BooksFactory/architecture/writing_control.md`
Место: между «Правилом 5: Специализации под книгу» и «Антипаттерны PM».
Вставка: новое **Правило 6: Умолчания по объёму главы**.

Содержание:
- Обычная глава: **до 6000 слов** (максимум после редактуры).
- Введение/Заключение: **3500–3700 слов**.
- Override через `tonal_compass.md` (per-книга) и `target_words` в MATERIAL (per-глава).
- Привязка к Draft Fat (writer +10–20%, editor режет) и Правилу 4 (плотность ≥4/100).

**Проверка готовности:** `grep -n "Правило 6" BooksFactory/architecture/writing_control.md` → должна быть одна строка.

### 1.2 Research-документ изучен ✅

Файл: `_testing/03_Manipulationen/_workdir/_RESEARCH_LLM_WRITING.md` (488 строк, вчерашняя работа).

**Основные выводы research, релевантные фабрике:**
- LLM не умеет считать — умеет планировать. Решение: нумерованные под-бюджеты per-beat.
- Writer ≠ Editor = **pipeline, а не роль**. Разные tool-сеты, разные промпты, отдельные агенты.
- «Draft fat, edit lean» (King 10%, Lamott) — Writer пишет +13–25%, Editor режет.
- Beat-decomposition industry-standard: **~500 слов × 15–17 beats/главу** (Sudowrite, NovelCrafter, AgentWrite).
- Жесткий length-controller — **нумерованный план с sum-check**.

### 1.3 Сопоставление «research vs наша фабрика» сделано ✅

### 1.4 Д9 — создан `bf-critic.md` ✅ (ФАЗА Ф1 по ТЗ)

Файл: `BooksFactory/.claude/agents/bf-critic.md`
- `tools: Read` (только, без Grep/Edit/Write — структурная защита от «редактора, который сам правит»).
- `model: sonnet` (детерминированные проверки, не нужен Opus).
- Book-agnostic: читает `<book>/_workdir/tonal_compass.md` + `verbot_liste.md` + эталон голоса книги.
- Выход: JSON-вердикт `{beat_id, action, actual_words, target_words, flags, notes}`.
- 6 групп флагов: Volume / Lexical / Rhythm / Style / Final / Provocation.
- Решение: 0 флагов → accept; 1+ → revise; 3+ или critical_short или style_drift<50 → rewrite.
- Различие с `bf-editor`: Critic — per-beat, JSON, машинный loop. Editor — вся глава, нарратив, human-in-loop.

**Проверка готовности:** `ls BooksFactory/.claude/agents/bf-critic.md` → файл есть, `model: sonnet`, `tools: Read`.

### 1.5 Создано ТЗ на beat-by-beat переход ✅

Файл: `BooksFactory/_TZ_WRITER_BEAT_BY_BEAT.md` (~600 строк).

**Причина:** попытка минимального фикса `bf-writer.md` обнаружила, что мелкая правка (снять Edit, убрать Step 3) **не решает главное** — writer по-прежнему пишет всю главу целиком в одном вызове. Через 2–3 сессии всё равно переписывать полностью. Автор: «минимальный фикс, а потом переделка. двойная работа!»

**Что в ТЗ:**
- §0 — обоснование, запреты (никаких «переходных форм» без даты отказа).
- §1 — полный пайплайн beat-by-beat + финальная таблица ролей/моделей/tools.
- §2 — контракт нового `bf-writer.md` (pure LLM, БЕЗ tools, tagged output).
- §3 — контракт переписанного `bf-coordinator.md` (loop-машина с scratchpad).
- §4 — адаптация Session-шаблона (MATERIAL внутри, BEGIN_REFERENCE, BEGIN_VERBOT, BEGIN_CALIBRATION).
- §5 — 13 фаз перехода (Ф0–Ф13) с зависимостями.
- §6 — миграция Abuse / Band III / готовых книг.
- §7 — риски и смягчения.
- §8 — что НЕ меняется (явный anti-scope-creep список).
- §9 — критерии готовности per phase.

**Статус:** проект ТЗ, ожидает одобрения автора в следующей сессии. До одобрения — никаких правок `bf-writer.md` / `bf-coordinator.md`.

**Где мы совпадаем** с консенсусом:
- Beat-decomposition (Правило 2 writing_control.md).
- Story Bible = MATERIAL внутри Session (ONM — даже плотнее, чем у других).
- Draft Fat + 10% cut (Правило 6 + ONM).
- Long-context prompt order.
- Per-book tonal_compass.
- Editor-Lite / Workflow B (у других вообще отсутствует).

**Где мы впереди** research:
- MATERIAL внутри Session (меньше фрагментации промпта).
- Compiler как Sonnet-механика (никто не выделяет сборщик файла).
- Workflow B для внешних книг (пропущен во всём research).
- Humanizer как отдельный шаг.

**Где GAP (новые дефекты Д9–Д11):**
- G1 → усиливает Д2: Writer БЕЗ filesystem-tools (структурная защита от Session-2-failure).
- **G2/G3 → Д9 (новый):** нет явного `bf-critic` с детерминированными JSON-флагами.
- **G4 → часть Д3:** Planner должен выдавать beat-лист с `sum_target_words = 1.13 × target` и self-check.
- **G5 → Д10 (новый):** нет writer-critic-refiner loop с max_iterations.
- G6 → Д11 (новый): нет Continuity-Checker между главами.
- G7 — опционально, низкий приоритет (embedding-distance).

---

## 2. Список дефектов (актуальная версия после research)

### Подтверждены в первом handoff-е:
- **Д1** ⚠️ `BooksFactory/CLAUDE.md` стр. 13: «для серии книг» — формулировка слишком узкая. Должна покрывать и создание с нуля, и переделку внешних книг.
- **Д2** 🔒 **BLOCKED на одобрении ТЗ.** `bf-writer.md` — НЕ точечная правка, а полная переделка на beat-by-beat (см. `_TZ_WRITER_BEAT_BY_BEAT.md` §2). Фаза Ф7 по ТЗ. Не трогать до одобрения ТЗ автором.
- **Д3** ⚠️ `bf-pm.md` конфлатит 3 роли (Researcher + MATERIAL-author + Compiler). Расщепить.
- **Д4** ⚠️ нет отдельного Compiler-агента (Sonnet, механический bash `cp`+`sed`).
- **Д5** ❌ **FALSE** (humanizer/translator — оба с model:opus и валидными tools). Удалён.
- **Д6** ⚠️ `bf-coordinator.md`: нет маршрута Workflow B (вход через Editor-Lite для внешних книг).
- **Д7** ⚠️ backup-hook: проверить, покрывает ли Edit (не только Write).
- **Д8** ❌ **FALSE** (skills/editor-lite + .claude/skills/editor-lite — двухслойная архитектура, намеренная). Удалён.

### Новые (из research 2026-04-23):
- **Д9** ✅ **СДЕЛАНО 2026-04-23.** `bf-critic.md` создан. Sonnet, Read-only, JSON-вердикт.
- **Д10** 🔒 **BLOCKED на одобрении ТЗ.** `bf-coordinator.md` — полная переделка в loop-машину. Фаза Ф8 по ТЗ (`_TZ_WRITER_BEAT_BY_BEAT.md` §3). Не трогать до одобрения ТЗ.
- **Д11** ⚠️ **(новый)** Нет Continuity-Checker. Роль между главами: лексические дубли, фактические противоречия, имена собственные, повторы ключевых метафор.

---

## 3. Порядок исполнения (финальный, после ТЗ 2026-04-23)

**ИСТОЧНИК ИСТИНЫ: `_TZ_WRITER_BEAT_BY_BEAT.md` §5.**

13 фаз Ф0–Ф13. Сводка:

| Фаза | Дефект | Что | Статус |
|------|--------|-----|--------|
| Ф0 | — | Правило 6 в writing_control.md | ✅ 2026-04-23 |
| Ф1 | Д9 | bf-critic.md создан | ✅ 2026-04-23 |
| Ф2 | Д1 | CLAUDE.md строка 13 | ✅ 2026-04-24 |
| Ф3 | Д4 | bf-compiler.md (новый) | ✅ 2026-04-24 |
| Ф4 | Д3 | split bf-pm → bf-researcher + bf-material-author | ✅ 2026-04-24 |
| Ф5 | — | bf-planner.md (новый) | ⬜ |
| Ф6 | — | Session-шаблон: T7 + BEGIN_REFERENCE/VERBOT/CALIBRATION | ⬜ |
| Ф7 | Д2 | **bf-writer.md полная переделка** (BLOCKED на ТЗ) | 🔒 |
| Ф8 | Д10 | **bf-coordinator.md переделка в loop-машину** (BLOCKED на ТЗ) | 🔒 |
| Ф9 | Д6 | маршрут Workflow B | ⬜ |
| Ф10 | Д7 | backup-hook покрытие Edit | ⬜ |
| Ф11 | Д11 | bf-continuity-checker.md | ⬜ |
| Ф12 | — | миграция Abuse | ⬜ |
| Ф13 | — | Band III Kapitel 01 | ⬜ отложено |

### Рекомендуемый порядок следующей сессии

**Шаг 1 (обязательно):** автор подтверждает ТЗ (`_TZ_WRITER_BEAT_BY_BEAT.md`) или вносит коррективы. Без одобрения ТЗ — Ф7/Ф8 не трогаем.

**Шаг 2 (если контекста много):**
1. Ф2 (Д1, одна строка в CLAUDE.md).
2. Ф3 (Д4, новый bf-compiler.md).
3. Ф4 (Д3, split bf-pm).
4. Ф5 (bf-planner.md).

**Шаг 3 (если ТЗ одобрен и контекста ещё есть):**
5. Ф6 (Session template).
6. Ф7 (bf-writer переделка).
7. Ф8 (bf-coordinator loop).

**Шаг 4 (если силы остались):**
8. Ф9/Ф10/Ф11.

**Никогда в одну сессию:** Ф7 + Ф8 одновременно (сердце loop-а, риск сломать пайплайн — см. ТЗ §5.3).

---

## 4. Проверка готовности каждого пункта

| Дефект | Команда проверки | Ожидаемый результат |
|---|---|---|
| Правило 6 (done) | `grep -c "Правило 6" BooksFactory/architecture/writing_control.md` | `1` |
| Д1 ✅ | `grep -n "для серии книг" BooksFactory/CLAUDE.md` | пусто (фраза заменена 2026-04-24) |
| Д2 | `grep -E "^tools:" BooksFactory/.claude/agents/bf-writer.md` | `tools:` отсутствует или пустой |
| Д2 | `grep -c "MATERIAL" BooksFactory/.claude/agents/bf-writer.md` | 0 или минимум, нет шага «прочитай MATERIAL» |
| Д3 ✅ | `ls BooksFactory/.claude/agents/bf-researcher.md bf-material-author.md` | оба файла существуют 2026-04-24; bf-pm.md помечен DEPRECATED, tools урезаны до Read |
| Д4 ✅ | `ls BooksFactory/.claude/agents/bf-compiler.md` | файл существует 2026-04-24, model: sonnet, tools: Read Write Bash |
| Д6 | `grep -c "Workflow B\|Editor-Lite" BooksFactory/.claude/agents/bf-coordinator.md` | ≥1 |
| Д7 | `cat ~/.claude/hooks/backup-before-write.sh` + проверка events | покрывает Edit |
| Д9 | `ls BooksFactory/.claude/agents/bf-critic.md` | существует, model: sonnet, tools: Read |
| Д10 | `grep -c "max_iterations\|writer-critic\|loop" BooksFactory/.claude/agents/bf-coordinator.md` | ≥1 |
| Д11 | `ls BooksFactory/.claude/agents/bf-continuity-checker.md` | существует |

---

## 5. Первое действие в следующей сессии

1. Прочитать **этот файл** (`_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md`) целиком.
2. Прочитать **первый handoff** (`_HANDOFF_FACTORY_TUNING_2026-04-23.md`) — ограничения и история провалов.
3. Проверить раздел 4 этого файла — что уже сделано (правило 6 в writing_control.md должно быть).
4. **Спросить автора**, с какого пункта продолжать. **Не начинать работу без подтверждения.**
5. Для каждой правки: Read → показ diff → ждать «ок» → Edit/Write.

---

## 6. Ключевые цитаты автора (якоря)

Сохранять как компас при любом сомнении:

- «фабрика как создает новые книги, так и работает со старыми»
- «агенту два нужны способности опуса. он как маленький писатель»
- «писатель получает сессион и ему уже не надо ничего дополнительного, кроме написанных глав для калибровки»
- «работа компилятора самая простая — сборка файла из имеющихся материалов»
- «что касается глав/книг, которые написаны не на фабрике — там работа начинается с редактора»
- «к третьей книге вернемся позже»

---

## 7. Карта важных файлов фабрики

### Конституция
- `BooksFactory/CLAUDE.md` — констьtutция фабрики (нужна правка Д1)
- `BooksFactory/architecture/writing_control.md` — управление раздуванием (Правило 6 добавлено)
- `BooksFactory/architecture/shared_vocabulary.md` — термины

### Агенты (`BooksFactory/.claude/agents/`)
- `bf-coordinator.md` — Haiku-роутер (нужна правка Д6, Д10)
- `bf-pm.md` — текущий PM (нужно расщепление Д3)
- `bf-writer.md` — писатель (нужна правка Д2)
- `bf-editor.md` — редактор (Read+Write для отчётов)
- `bf-humanizer.md` — гуманизатор (Opus, корректен)
- `bf-translator.md` — переводчик (Opus, корректен)

### Skills
- `BooksFactory/skills/editor-lite/SKILL.md` — полный скил (4 проверки: читабельность, спотыкания, дубли, откровенная херня)
- `BooksFactory/.claude/skills/editor-lite/SKILL.md` — dispatcher-вариант

### Референсные шаблоны (не трогать, только читать как пример)
- `Abuse/Session_TEMPLATE_v2_ONM.md` — рабочий ONM-шаблон (516 строк). MATERIAL внутри Session. Mechanical compile.
- `Abuse/PROMPT_create_MATERIAL_v4.md` — инструкция агенту 2 (Opus, «маленький писатель»).

### Research / аналитика
- `_testing/03_Manipulationen/_workdir/_RESEARCH_LLM_WRITING.md` — вчерашний research (488 строк). Источник Д9/Д10/Д11.
- `_testing/03_Manipulationen/_workdir/_AUDIT_BOOKSFACTORY_2026-04-22.md` — **помечен как FALSE**, удалить при возможности.
- `_testing/03_Manipulationen/_workdir/_ARCHITECTURE_PROPOSAL_DRAFTER.md` — **помечен как FALSE**, удалить при возможности.

### Глобальные дубли (удалить)
- `~/.claude/agents/band3-planner.md` — дубль, удалить
- `~/.claude/agents/band3-writer.md` — дубль, удалить
- `~/.claude/agents/band3-critic.md` — дубль, удалить
- `~/.claude/agents/band3-editor.md` (если есть) — дубль, удалить

---

## 8. Память о провалах (чтобы не повторить)

**Session 1 (2026-04-21):** голос Band III реконструирован по заголовкам протокола → эссеистика. Структурный урок уже зашит в `_testing/03_Manipulationen/CLAUDE.md` §7.

**Session 2 (2026-04-22):** writer-задача отдана агенту с Read/Grep/Edit → агент повёл себя как редактор (знато, точно, экономно) → ×4 недобор объёма. Структурная защита — Д2 (снять Read с writer).

**Session 3 (2026-04-22, начало этой):** в глобальную `~/.claude/agents/` положены дубли `band3-*` агентов под третью книгу → «заточка фабрики под одну книгу, что абсолютно неприемлемо». Не повторять: все правила живут в `BooksFactory/`, специализации — в `tonal_compass.md`.

**Session 4 (2026-04-23, эта):** почти начал править агенты до предъявления плана → остановлен автором. Правило зашито: перед любым Edit → Read файла + diff-ревью + «ок» автора.

---

## 9. Band III — статус

**Отложено явно.** Автор: «к третьей книге вернемся позже». Диагноз провала 2000 слов vs 7500 target не делался. Когда вернёмся — сначала закончить тюнинг фабрики, потом использовать тюнингованную фабрику для Band III Kapitel 01.

Файлы Band III (в покое до возврата):
- `_testing/03_Manipulationen/_workdir/Session_Kapitel01.md` — контракт
- `_testing/03_Manipulationen/_workdir/stil_chunks/` — пять чанков голоса
- `_testing/03_Manipulationen/_workdir/REFERENZ_STIL_Kapitel08_UdK.md` — разбор эталона
- `Serie/06Unschuld_des_Komplizen/chapters_UdK/09_Kapitel08_Die_Erschoepfung_normalisieren.md` — сам эталон голоса
- `_testing/03_Manipulationen/CLAUDE.md` — правила работы с Band III (трогать осторожно)

---

---

## 10. FINGERPRINT: точное состояние файлов на 2026-04-23 конец сессии

> **Критический раздел.** Следующая сессия проверяет каждую строку этой таблицы перед началом работы. Если какой-то маркер НЕ совпадает — значит состояние другое, надо разобраться, не начинать работу наобум.

### 10.1 Файлы, СОЗДАННЫЕ в этой сессии

| Файл | Размер (прибл.) | Ключевой маркер для проверки |
|------|-----------------|-------------------------------|
| `BooksFactory/.claude/agents/bf-critic.md` | ~155 строк | первая строка YAML `name: bf-critic`, `model: sonnet`, `tools: Read` |
| `BooksFactory/_TZ_WRITER_BEAT_BY_BEAT.md` | ~600 строк | заголовок `# ТЗ: Переход Writer на beat-by-beat архитектуру`, секция §5 «Фазы перехода» с 13 фазами |
| `BooksFactory/_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` | этот файл | этот раздел §10 |
| `BooksFactory/.claude/agents/bf-controller.md` | ~140 строк | YAML `name: bf-controller`, `model: sonnet`, `tools: Read, Grep, Glob`. Создан 2026-04-23 вечер по запросу автора (замена переспрашивания DoD). |
| `BooksFactory/.claude/agents/bf-compiler.md` | ~200 строк | YAML `name: bf-compiler`, `model: sonnet`, `tools: Read, Write, Bash`. Механический сборщик Session-файла. Создан 2026-04-24 в рамках Ф3/Д4. Пять префиксов ошибок (`COMPILER_PREFLIGHT_FAILED`, `COMPILER_BEAT_PLAN_INVALID`, `COMPILER_BEAT_PLAN_STRUCTURE_BROKEN`, `COMPILER_MARKER_MISSING`, `COMPILER_WRITE_FAILED`). |
| `BooksFactory/.claude/agents/bf-researcher.md` | ~140 строк | YAML `name: bf-researcher`, `model: opus`, `tools: Read, Grep, Glob, WebSearch, WebFetch, Write`. Создан 2026-04-24 в рамках Ф4/Д3/A3. Выход: `_research/pre_mortem.md`, `literature_pool.md`, `topical_notes.md`, `decision_log.md` + в корне книги `_outline.md`, `tonal_compass.md`, `verbot_liste.md`. Покрывает Workflow A (с нуля) и Workflow B (внешние книги — после Editor-Lite). |
| `BooksFactory/.claude/agents/bf-material-author.md` | ~160 строк | YAML `name: bf-material-author`, `model: opus`, `tools: Read, Grep, Write`. Создан 2026-04-24 в рамках Ф4/Д3/A3. Выход: `<book>/_drafts/MATERIAL_Glava_NN.md` с секциями, beat sheets, аренами, провокациями, quote-anchors, continuity, QUELLEN. Явно нет WebSearch/WebFetch. |
| `BooksFactory/_SESSION_START_PROMPT.md` | ~50 строк | Канонический промпт v2.0 (без Q1/Q2 ритуала). Заголовок «Канонический промпт для старта сессии тюнинга BooksFactory». |

### 10.2 Файлы, ИЗМЕНЁННЫЕ в этой сессии

| Файл | Что изменено | Маркер |
|------|--------------|--------|
| `BooksFactory/architecture/writing_control.md` | Добавлено **Правило 6: Умолчания по объёму главы** между старыми Правилом 5 и «Антипаттернами PM» | `grep "Правило 6" writing_control.md` → 1 совпадение; содержит таблицу «Обычная глава: до 6000 слов», «Введение/Заключение: 3500–3700 слов» |
| `BooksFactory/architecture/FACTORY_MAP.md` | Вставлен STALE-маркер в шапку (2026-04-23), между «# BooksFactory — Карта фабрики» и «## Производственная цепочка». Перечисляет добавления: bf-critic, bf-controller, ТЗ, Правило 6. Указывает фактическое число агентов. | `Select-String … "STALE 2026-04-23"` → 1 |
| `BooksFactory/architecture/handoff_contracts.md` | ✅ 2026-04-24. Добавлены **контракты 6/7/8** перед «Сводной таблицей статусов» (C1/Ф3a). Контракт 6: Writer↔Critic per-beat loop. Контракт 7: Любая фаза → Controller. Контракт 8: Compiler → Coordinator. Статус-preamble указывает, что контракты 1–5 живы до Ф7/Ф8. | `Select-String … "Контракт 6: Writer ↔ Critic"` → 1; `"Контракт 7: Любая фаза"` → 1; `"Контракт 8: Compiler"` → 1 |
| `BooksFactory/CLAUDE.md` | ✅ Ф2 + B2 2026-04-24. Стр. 13 расширена (три режима). Стр. 64 в структуре директории: `promptBF.txt` → `_SESSION_START_PROMPT.md` (битая ссылка → живой файл). |

### 10.3 Файлы, КОТОРЫЕ НЕ ТРОГАЛИСЬ (должны быть как были)

| Файл | Ожидаемое состояние |
|------|---------------------|
| `BooksFactory/.claude/agents/bf-coordinator.md` | БЕЗ изменений. Текущая форма — роутер по статусу. НЕ loop-машина. |
| `BooksFactory/.claude/agents/bf-pm.md` | ✅ Ф4 2026-04-24. Помечен DEPRECATED. YAML description и шапка файла явно сообщают о замене. Tools урезаны до `Read` (структурная защита от вызова в новом производстве). Содержимое архива сохранено ниже deprecation-маркера для rollback/исторической справки. |
| `BooksFactory/.claude/agents/bf-writer.md` | БЕЗ изменений. `tools: Read, Write, Edit`, model: opus. Шаг 3 «Прочитай MATERIAL» ЕЩЁ ТАМ. 38 строк. |
| `BooksFactory/.claude/agents/bf-editor.md` | БЕЗ изменений. `tools: Read, Grep, Write`, model: opus. Корректен. |
| `BooksFactory/.claude/agents/bf-humanizer.md` | БЕЗ изменений. Корректен. |
| `BooksFactory/.claude/agents/bf-translator.md` | БЕЗ изменений. Корректен. |
| `BooksFactory/CLAUDE.md` | ✅ Ф2 выполнена 2026-04-24. Строка 13 расширена: три режима (создание с нуля / развитие серии / Workflow B через Editor-Lite). Обе якорные цитаты автора отражены. Фраза «для серии книг» отсутствует (grep — пусто). |
| `~/.claude/hooks/backup-before-write.sh` | НЕ проверен в этой сессии. Статус неизвестен. Нуждается в Д7/Ф10. |

### 10.4 Файлы, которые СУЩЕСТВУЮТ как FALSE

**Обновлено автором 2026-04-23 конец сессии: 4 файла Band III удалены автором вручную.**

Удалённые автором (ожидается, что их НЕТ на диске):
- `_testing/03_Manipulationen/_drafts/01_draft_v1.md` — провальный черновик 2026-04-22
- `_testing/03_Manipulationen/_workdir/_ARCHITECTURE_PROPOSAL_DRAFTER.md` — FALSE
- `_testing/03_Manipulationen/_workdir/_AUDIT_BOOKSFACTORY_2026-04-22.md` — FALSE
- `_testing/03_Manipulationen/_workdir/_HANDOFF_NEXT_CHAT.md` — устаревший handoff

Всё ещё к удалению следующей сессией (в глобальной `~/.claude/agents/`):

| Файл | Причина |
|------|---------|
| `~/.claude/agents/band3-planner.md` | Дубль фабрики под одну книгу. Автор: «абсолютно неприемлемо». Удалить в следующей сессии. |
| `~/.claude/agents/band3-writer.md` | То же. |
| `~/.claude/agents/band3-critic.md` | То же. Его функция теперь в `bf-critic.md` на уровне фабрики. |
| `~/.claude/agents/band3-editor.md` | (если существует) Удалить. |

Спорное (оставлено, решить в следующей сессии):
- `_testing/03_Manipulationen/_workdir/_POSTMORTEM_Kapitel01_2026-04-21.md` (6 KB) — урок уже зашит в Band III CLAUDE.md §7. Оставить как исторический артефакт или удалить.

**⚠️ ВАЖНО:** перед удалением `band3-*` файлов в `~/.claude/agents/` — проверить, что в них нет уникального content, который НЕ переехал в `bf-*`. `bf-critic.md` в этой сессии писался с полного нуля, не копировался с `band3-critic.md`, но содержательно пересекается.

### 10.5 Проверка fingerprint в первые 60 секунд следующей сессии

Команды для быстрой сверки (PowerShell-совместимо):

```powershell
# Что точно должно существовать:
Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-critic.md"
Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_TZ_WRITER_BEAT_BY_BEAT.md"
Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md"

# Правило 6 в writing_control.md:
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\writing_control.md" -Pattern "Правило 6" -SimpleMatch

# bf-writer.md ЕЩЁ НЕ переделан (проверка что мы не стартовали Ф7 случайно):
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-writer.md" -Pattern "Прочитай MATERIAL" -SimpleMatch
# ДОЛЖНО найти. Если НЕ найдёт — значит кто-то уже тронул, разбираться.

# CLAUDE.md строка 13 ЕЩЁ не исправлена:
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md" -Pattern "для серии книг" -SimpleMatch
# ДОЛЖНО найти. Если НЕ найдёт — значит Ф2 уже сделана.
```

---

## 11. ТОЧНЫЙ первый шаг следующей сессии

```
1. Прочитать:
   - _HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md (этот файл) — целиком.
   - _TZ_WRITER_BEAT_BY_BEAT.md — целиком.
   - _HANDOFF_FACTORY_TUNING_2026-04-23.md (первый handoff) — как минимум §1-3 (ограничения, цитаты).

2. Выполнить PowerShell-проверки из §10.5 этого файла.
   Сверить ожидаемое состояние со входящим. Расхождения — в диалог с автором.

3. Спросить автора двумя вопросами:
   Q1. «Одобрите ТЗ _TZ_WRITER_BEAT_BY_BEAT.md как есть, или нужны коррективы?»
   Q2. «С какой фазы продолжаем — Ф2 (CLAUDE.md, одна строка) или Ф3 (bf-compiler.md)?»

4. НИ ОДНОЙ правки файла до ответов на Q1+Q2. Показ diff → «ок» → Edit.

5. Если Q1 = «есть коррективы» — обсудить и обновить ТЗ. Только после — продолжать.
```

---

## 12. Последняя заметка: что сэкономило эту сессию

- **Read существующего `bf-editor.md` перед дизайном Critic** — увидел что Editor и Critic разного слоя, оба нужны.
- **Пауза перед Write bf-critic.md** — автор одобрил дизайн из таблицы, файл написан с первого раза без rewrite.
- **Предложение «минимального фикса» bf-writer.md** было остановлено автором: «двойная работа!» — это спасло от реальной двойной работы в следующей сессии.
- **ТЗ написано, когда в голове ещё свежий research** — следующая сессия не будет гадать о дизайне, она получит готовый контракт.

---

**Конец handoff Part 2. Обновлено 2026-04-23. Остаток сессии ~25%.**

---

## 13. Аудит целостности фабрики 2026-04-23 (вечер) + очередь P0–P3

> Аудит выполнен в прошлом контексте перед summary-compaction. Дословный перечень 23 проблем не восстанавливается по памяти (cite-don't-reconstruct). Здесь — категории, приоритеты, исполнение.

### 13.1 Категории найденных проблем

- **A. Архитектурные дыры** — агенты, не прошитые в маршрут координатора; отсутствующие роли; карта устарела.
- **B. Технические ошибки** — неверные пути в контрактах, битые ссылки (promptBF.txt), модельные мисматчи, непокрытые hook-события.
- **C. Нарушенные связи** — контракты между парами агентов (writer↔critic, coordinator↔controller, compiler→session) не прописаны в `handoff_contracts.md`.
- **D. Устаревшие артефакты** — FACTORY_MAP phase 4, CLAUDE.md §65, постмортемы, устаревшие handoff-ы.
- **E. Конфликты контрактов** — пересечение зон ответственности (editor vs critic, pm vs researcher+material-author).

### 13.2 Очередь приоритетов

| Приоритет | Метка | Суть | Фаза ТЗ | Статус |
|-----------|-------|------|---------|--------|
| P0 | A1 | `bf-coordinator` не знает о `bf-critic` / `bf-controller` | Ф8 | 🔒 BLOCKED на одобрении ТЗ |
| P0 | A2 | `FACTORY_MAP.md` устарел («6 агентов», факт — 8, нет упоминания critic/controller/ТЗ) | новая Ф1a | ⬜ |
| P0 | B5 | `bf-critic.md` путь `<book>/_workdir/tonal_compass.md` — Band-III-specific | — | ✅ 2026-04-23 (см. §13.4) |
| P0 | C1 | `handoff_contracts.md` не покрывает writer↔critic, coordinator↔controller, compiler→session | новая Ф3a | ✅ 2026-04-24 |
| P1 | A3 | `bf-pm.md` конфлатит 3 роли | Ф4 | ✅ 2026-04-24 (Д3) |
| P1 | B2 | `CLAUDE.md §65` ссылается на несуществующий `promptBF.txt` | новая Ф13a | ✅ 2026-04-24 |
| P1 | B4 | `bf-coordinator` model: haiku → sonnet (loop-машина требует Sonnet) | Ф8 | 🔒 BLOCKED на ТЗ |
| P2 | B3,C2,C3,C4 | Session T7 slot, scratchpad schema, critic↔editor контракт, coordinator↔writer scratchpad | Ф8–Ф10 | ⬜ |
| P3 | D1 | FACTORY_MAP phase 4 section stale | Ф1a | ⚠️ dup-of A2 (STALE-флаг вставлен 2026-04-23; полный рефакторинг в Ф1a) |
| P3 | D2 | CLAUDE.md «для серии книг» | Ф2 | ✅ 2026-04-24 (закрыто в Ф2) |
| P3 | D3 | _POSTMORTEM_Kapitel01 (архив Band III) | — | ⏸️ решение автора (оставить как исторический артефакт или удалить) |
| P3 | D4 | promptBF.txt reference | Ф13a | ✅ 2026-04-24 (закрыто в B2) |
| P3 | E1 | Д2 (writer) vs Д9 (critic) пересечение | Ф7 | ⏸️ невалиден до Ф7 (новый writer ещё не написан; разграничение уже прописано в bf-critic.md §«Отличие от bf-editor») |
| P3 | E2 | bf-editor vs bf-critic overlap | — | ✅ 2026-04-24 — в `bf-editor.md` добавлен раздел «Отличие от bf-critic» с таблицей слоёв + два режима работы (legacy section-by-section vs beat-by-beat после Ф8) |

### 13.2a Модели агентов (model-sync 2026-04-25)

> Сверено с фактом (frontmatter `.claude/agents/bf-*.md`) в рамках P1-3 ТЗ-аудита `_TZ_AUDIT_FIXES_2026-04-25.md`. Совпадает с `_TZ_WRITER_BEAT_BY_BEAT.md` §1.2.

| Агент | Модель (факт) | Tools (факт) | Целевая модель |
|-------|---------------|--------------|----------------|
| bf-researcher | opus | Read, Grep, Glob, WebSearch, WebFetch, Write | opus |
| bf-material-author | opus | Read, Grep, Write | opus |
| bf-planner | opus | Read, Grep, Glob, Write | opus |
| bf-compiler | sonnet | Read, Write, Bash | sonnet |
| bf-coordinator | haiku | Read, Write, Glob, Grep | sonnet (после Ф8 — B4) |
| bf-writer | opus | Read, Write, Edit | opus, **без tools** (после Ф7 — Д2) |
| bf-critic | sonnet | Read | sonnet |
| bf-controller | sonnet | Read, Grep, Glob | sonnet |
| bf-editor | opus | Read, Grep, Write | opus |
| bf-humanizer | opus | Read, Edit, Write | opus |
| bf-translator | opus | Read, Write, Edit | opus |
| bf-pm | opus | Read | DEPRECATED (stub только) |

Расхождения target vs факт:
- **bf-coordinator**: haiku → sonnet — переход внутри Ф8 (B4). Loop-машина требует Sonnet.
- **bf-writer**: Read/Write/Edit → none — переход внутри Ф7 (Д2). Pure-LLM beat-writer без tools, structural protection.
- Остальные 10 агентов — model и tools совпадают с целевыми.

### 13.3 Новые фазы для ТЗ §5 (добавить в следующей сессии)

- **Ф1a** — `FACTORY_MAP.md` актуализация (8 агентов, bf-critic, bf-controller, ТЗ beat-by-beat, 13 фаз).
- **Ф3a** — `handoff_contracts.md`: секции writer↔critic, coordinator↔controller, compiler→session.
- **Ф8a** — coordinator model haiku→sonnet (выполняется внутри Ф8).
- **Ф12** — чистка устаревших артефактов (D1–D4).
- **Ф13a** — CLAUDE.md §65 (promptBF.txt) заменить на актуальную ссылку на Session-шаблон.

### 13.4 Выполнено 2026-04-23 в этой сессии (после compaction)

- ✅ **B5** — `bf-critic.md` init-блок параметризован. `<book>/tonal_compass.md` как базовый путь, `<book>/_workdir/…` оставлен как fallback для Band III / тестовых книг. Координатор передаёт фактический путь в промпте. Книга-агностичность восстановлена.
  - Проверка: `Select-String -Path ".../bf-critic.md" -Pattern "Fallback для тестовых"` → найти одну строку.

### 13.5 Правила работы с очередью

- P0 без зависимости от ТЗ (A2, C1) исполняются в любой следующей сессии сразу после fingerprint-проверки.
- P0 с зависимостью (A1) блокируется на Ф8 — не трогать до одобрения ТЗ.
- Все D/E-правки — после Ф7+Ф8, чтобы не рефакторить дважды.
- Новые фазы Ф1a/Ф3a/Ф8a/Ф12/Ф13a добавить в `_TZ_WRITER_BEAT_BY_BEAT.md §5` при следующем открытии ТЗ (вместе с обновлением зависимостей).

---

## 10.6 Delta к §10 после §13 (2026-04-23 вечер)

Дополнение к fingerprint после compaction:

| Файл | Было | Стало | Маркер |
|------|------|-------|--------|
| `BooksFactory/.claude/agents/bf-critic.md` | путь `<book>/_workdir/tonal_compass.md` в шаге 1 инициализации | `<book>/tonal_compass.md` + fallback-строка | `Select-String … "Fallback для тестовых"` → 1 |

**Конец §13. Следующая сессия: читать §13.2 вместе с §3 — это совмещённый план.**

### 13.6 Финальная отметка 2026-04-23 вечер (контекст ~7%)

Сессия закрыта автором на контексте ~7% сразу после §13.5. Состояние:

- ✅ Закрыто в этой итерации: **B5** (bf-critic путь), **§13** аудит зафиксирован.
- ✅ **A2** (FACTORY_MAP.md) — STALE-маркер вставлен в шапку (между `# BooksFactory — Карта фабрики` и «## Производственная цепочка»). Перечисляет добавления с 2026-04-18 (bf-critic, bf-controller, ТЗ, Правило 6) и указывает фактическое число агентов (8 сейчас, 9 после Ф4, +3 после Ф3/Ф5/Ф11). Полный рефакторинг карты — в рамках Ф1a.
  - Проверка: `Select-String -Path ".../architecture/FACTORY_MAP.md" -Pattern "STALE 2026-04-23"` → 1.
- ⬜ **C1** (handoff_contracts.md) — не начат.
- 🔒 Остальные фазы — по зависимостям (A1/B4 — на Ф8, и т.д.).

**Fingerprint актуален как в §10 + §10.6.** `bf-writer.md`, `bf-coordinator.md`, `bf-pm.md`, `CLAUDE.md`, `architecture/FACTORY_MAP.md`, Session-шаблон — НЕ тронуты.

Следующая сессия: запустить `_SESSION_START_PROMPT.md` как есть. Первая полезная правка — A2 (Read `architecture/FACTORY_MAP.md`, отметить устаревание, либо актуализировать в пределах Ф1a).
