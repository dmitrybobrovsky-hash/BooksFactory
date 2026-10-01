# Задание: ремонт фабрики по аудиту 2026-05-10

**Модель:** Sonnet
**Контекст:** аудит `_FACTORY_AUDIT_2026-05-10.md`, трассировка всех находок через производственную цепочку
**Принцип:** хирургические правки. Не перестраивать. Каждая изменённая строка прослеживается до находки аудита.

---

## Шаг 0. Бэкап

```bash
python tools/backup.py
```

Если бэкап упал — СТОП.

---

## Шаг 1. Битые пути в документации (C1 + C2 + C3)

Не влияют на цепочку — ссылки на журналы, ни один агент не переходит по ним в production.

### `architecture/FACTORY_MAP.md`
Заменить ВСЕ `aarchive/` на `archive/` и ВСЕ `rchive/` (без «a») на `archive/`. Ожидается 4 замены.

### `.claude/memory/architecture.md`
Заменить ВСЕ `rchive/journal/` на `archive/journal/`. Ожидается 3 замены.

### `BOOKSFACTORY_AI.md`
В секции §5 «Журнальные файлы» найти два пути с двойным префиксом `archive/journal/archive/journal/` — удалить дублирование (оставить одинарный `archive/journal/`). Ожидается 2 замены. Остальные пути в блоке корректны — НЕ ТРОГАТЬ.

### Проверка после шага 1:
```bash
grep -rn "aarchive" architecture/ .claude/memory/
grep -rn "rchive/" architecture/ .claude/memory/ | grep -v "archive/"
grep -c "archive/journal/archive/journal/" BOOKSFACTORY_AI.md
```
Все три команды должны вернуть 0 строк.

---

## Шаг 2. Синхронизация документации (D2 + D3 + C4)

Не влияют на цепочку — это документация для ориентации, не оперативные входы агентов.

### `.claude/memory/architecture.md`
- Frontmatter: `updated: 2026-05-06` → `updated: 2026-05-10`
- Найти строку с «Закрытые фазы» — дописать в конец списка: `, Ф14, Ф15⚠`

### `architecture/FACTORY_MAP.md`
- Frontmatter: `updated: 2026-05-06` → `updated: 2026-05-10`
- В таблице агентов (может быть в двух местах — проверить обе) найти bf-coordinator, столбец Tools. Если `Task` отсутствует — добавить: `Read, Write, Glob, Grep, Task`

### Проверка после шага 2:
```bash
grep "updated:" architecture/FACTORY_MAP.md .claude/memory/architecture.md
```
Обе строки: `2026-05-10`.
```bash
grep "Task" architecture/FACTORY_MAP.md
```
Должна быть строка с bf-coordinator и Task.

---

## Шаг 3. Передача пути draft-файла editor-у (A2)

ВЛИЯЕТ НА ЦЕПОЧКУ. Без этого fix-а editor не найдёт draft при маршрутизации через coordinator.

Проблема: coordinator compile_draft записывает файл (знает путь), потом при `/bf-route editor NN` вызывает editor, но НЕ передаёт путь. Editor ищет по хардкоду `NN_draft_v1.md` — не совпадает с реальным именем.

### `.claude/agents/bf-coordinator.md`

Найти раздел `/bf-route <agent> NN`, шаг 4:
```
4. Если выполнен — вызвать агента через Agent tool.
```
Заменить на:
```
4. Если выполнен — вызвать агента через Agent tool. При вызове bf-editor — передать в промпте Agent-вызова путь к draft-файлу главы, найденному Glob-ом в шаге 2.
```

### `.claude/agents/bf-editor.md`

Найти фрагмент в разделе «Beat-by-beat (после Ф8 ТЗ)»:
```
(`<book>/_drafts/NN_draft_v1.md`)
```
Заменить на:
```
(путь к draft-файлу передаётся coordinator в промпте вызова при `/bf-route editor NN`)
```

### Проверка после шага 3:
```bash
grep "NN_draft_v1" .claude/agents/bf-editor.md
```
0 строк.
```bash
grep "draft-файл" .claude/agents/bf-coordinator.md
```
Должна быть строка в /bf-route шаг 4.

---

## Шаг 4. pattern_budget обязательный + self-check (F1)

ВЛИЯЕТ НА ЦЕПОЧКУ. Без этого fix-а planner может пропустить pattern_budget → critic даёт ложные revise на сигнатурную фигуру при 6–8 вхождениях (канон допускает ≤8).

### `.claude/agents/bf-planner.md`

**4a.** Найти (в секции «pattern_budget», ближе к концу файла):
```
bf-planner добавляет в beat_plan.json опциональную секцию:
```
Заменить на:
```
bf-planner добавляет в beat_plan.json обязательную секцию:
```

**4b.** Найти self-check §4 (раздел «4. Self-check (обязательный перед Write)»). После пункта 8 (`is_last_beat`) добавить:

```
9. `pattern_budget` присутствует. Если книга имеет сигнатурную фигуру (из `stil_und_ton_XX.md` или `shared_vocabulary.md §4`) — массив содержит запись с `planned_count` ≤8. Если сигнатурных фигур нет — пустой массив `[]`. Отсутствие секции — ошибка.
```

**4c.** Сразу после закрывающего ` ``` ` примера JSON (блок с `"pattern": "сигнатурная_фигура"`) добавить:

```markdown
**Минимум:** если книга имеет сигнатурную фигуру (из `stil_und_ton_XX.md` или `shared_vocabulary.md §4`) — запись с `planned_count` по канону (≤8). Если сигнатурных фигур нет — `[]` с `"justification": "книга без заявленных сигнатурных фигур"`.
```

### Проверка после шага 4:
```bash
grep "опциональную" .claude/agents/bf-planner.md
```
0 строк.
```bash
grep "pattern_budget" .claude/agents/bf-planner.md
```
Должно быть ≥3 вхождений (описание + self-check + минимум).

---

## Шаг 5. Meta-critic guidance (A1 + B1)

Не меняет контракт editor-а — добавляет guidance для существующих проверок.

### `.claude/agents/bf-editor.md`

**5a.** В разделе «meta-critic функция», пункт 2 (структурные паттерны), после «Если ≥6 на главу — точка отчёта.» добавить:
```
Grep-паттерны (аналогично bf-critic §C): `Не .+\. .+\.`, `Это не .+\. Это .+`, иные повторяющиеся синтаксические каркасы ≥6 раз.
```

**5b.** В пункте 3 (атрибуция), найти:
```
если нет соответствующей записи в quellen_pool с привязкой к этой главе
```
Заменить на:
```
Метод: Grep имён учёных из текста по quellen_pool главы. Имя в тексте без записи в quellen_pool → точка отчёта. Эвристика: quellen_pool не содержит per-утверждение привязки
```

---

## Шаг 6. CHANGELOG v1.1 (D1)

Документация для человека. Не влияет на цепочку.

### `CHANGELOG.md`

Вставить ПЕРЕД строкой `## v1.0 (2026-05-03)` (CHANGELOG идёт reverse chronological — новое сверху):

```markdown
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
```

---

## Шаг 7. Пометки масштабируемости и наследования (E1 + E2 + G1)

Три одностроковых добавления. Не влияют на цепочку.

### `BOOKSFACTORY_AI.md`

**7a.** После блока §11 «Оперативный журнал сессии» (после описания «Создание файла»), перед разделителем `---` следующей секции, добавить:

```markdown

### Ротация _SESSION_STATE.md 🚧

При >100 записей или >100 КБ — архивировать старые записи в `_SESSION_STATE_archive_YYYY-MM-DD.md`, оставить последние 30. Coordinator при старте читает только первую запись — архивированные не нужны для навигации. Аудит 2026-05-10 (E1): 57 КБ / 42 записи за Test3 KS.
```

**7b.** В §2 «Документы уровня книги», найти строку с `_skvoznye_formuly_XX.md`. Сразу после её описания добавить:
```markdown
> ⚠ Масштабируемость: 44 КБ / 5 MATERIAL (аудит 2026-05-10). Мониторить при >100 КБ.
```

### `CLAUDE.md`

**7c.** Перед строкой `# BooksFactory — Конституция` добавить:
```markdown
> Наследует `~/.claude/CLAUDE.md` (4 принципа Karpathy). Проектные правила дополняют, не отменяют глобальные.
```

---

## Шаг 8. Запись в _SESSION_STATE.md

### `_testing/Test3_05.05.2026/_SESSION_STATE.md`

Добавить в начало (после заголовка, перед записью 42):

```markdown
## 2026-05-10 (43)
status: completed
step: Ремонт фабрики по аудиту `_FACTORY_AUDIT_2026-05-10.md` (v2). 16 находок, 0 Critical, 2 High, 11 Medium, 3 Low. Выполнено 7 шагов: (1) битые пути C1/C2/C3 — 9 замен в 3 файлах; (2) синхронизация D2/D3/C4 — даты + Task; (3) A2 — передача пути draft-файла editor-у через coordinator /bf-route; (4) F1 — pattern_budget обязательный + self-check п.9 в planner; (5) A1/B1 — meta-critic regex и метод атрибуции; (6) D1 — CHANGELOG v1.1; (7) E1/E2/G1 — пометки. Не починено: F2 (перенумерация правил — создаёт рассинхрон с BOOKSFACTORY_AI §8, отложена). Отложено: A3 (smoke-test humanizer→translator при первом clean).
agent: Claude Code (Sonnet)
artifacts_updated: architecture/FACTORY_MAP.md, .claude/memory/architecture.md, BOOKSFACTORY_AI.md, .claude/agents/bf-coordinator.md, .claude/agents/bf-editor.md, .claude/agents/bf-planner.md, CHANGELOG.md, CLAUDE.md
next: возврат к производству КС или иной план автора.
```

---

## Шаг 9. Финальная проверка

```bash
# Битые пути — должны быть 0
grep -rn "aarchive\|[^a]rchive/" architecture/ .claude/memory/ | grep -v "archive/"
grep -c "archive/journal/archive/journal/" BOOKSFACTORY_AI.md

# Даты — должны быть 2026-05-10
grep "updated:" architecture/FACTORY_MAP.md .claude/memory/architecture.md

# Task — должен быть в строке coordinator
grep -i "coordinator.*Task\|Task.*coordinator" architecture/FACTORY_MAP.md

# A2 — хардкод убран
grep "NN_draft_v1" .claude/agents/bf-editor.md

# F1 — опциональную убрана, self-check 9 добавлен
grep "опциональную" .claude/agents/bf-planner.md
grep "pattern_budget" .claude/agents/bf-planner.md | wc -l

# CHANGELOG — v1.1 присутствует
grep "v1.1" CHANGELOG.md
```

Ожидаемые результаты: битые пути = 0, даты = 2026-05-10, Task найден, NN_draft_v1 = 0 строк, опциональную = 0 строк, pattern_budget ≥ 3 вхождений, v1.1 найден.

---

## Что НЕ делать

- Не менять нумерацию правил в CLAUDE.md (F2 отложена — создаёт рассинхрон с BOOKSFACTORY_AI §8)
- Не менять логику compile_draft, writer-loop, critic
- Не трогать Test3 артефакты (кроме _SESSION_STATE запись 43)
- Не менять содержание правил, контрактов, скиллов
- Не делать git commit
