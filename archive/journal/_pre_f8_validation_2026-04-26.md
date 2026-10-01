# Pre-Ф8 Validation Report — 2026-04-26

> **Версия 1.0** (создан 2026-04-26).
> Закрывающий артефакт ТЗ `_TZ_PRE_F8_FIXES_2026-04-26.md` — пункт **P-FINAL-PRE-F8**.
> Автор: Dmitry Bobrovsky.

---

## §1. Что изменилось

ТЗ Pre-Ф8 cleanup закрывает 12 пунктов (4 critical + 4 middle + 4 minor) на основе независимого аудита фабрики 2026-04-26.

### §1.1. Критические (C-1..C-4)

- **C-1 — Compiler self-check substring bug.** В `bf-compiler.md` шаг 5 «Self-check» переписан: bash-ветка использует `grep -qE "## TN\b"` (extended regex + word boundary); PowerShell-ветка разделена на `$regex_markers` (T1..T12 с `^...\b` БЕЗ `-SimpleMatch`) и `$literal_markers` (`---BEGIN_*---` с `-SimpleMatch`). В §«Абсолютно запрещено» добавлен запрет голого `## T1` (false positive из-за подстроки `## T10`/`## T11`/`## T12`).
- **C-2 — Контракт 4 vs Контракт 9.** В `handoff_contracts.md` начало Контракта 4 помечено DEPRECATED-блоком после P3-2 + P2-4, со ссылкой на Контракт 9 как активный маршрут. Контракт 4 сохранён архивно.
- **C-3 — Системное правило команд идемпотентности.** В `bf-controller.md` добавлен раздел «Правила команд идемпотентности»: `-SimpleMatch` запрещён для regex-паттернов (альтернатива, якоря, квантификаторы, word boundary), допустим только для строго-литеральных строк. Перечислены 5 прецедентов из ТЗ-аудита 2026-04-25 (P0-2, P3-1, P3-4, P2-3, P0-3). `_SESSION_START_PROMPT.md` повышен до v2.4 с памяткой.
- **C-4 — Архивация smoke-теста.** `_testing/smoke_2026-04-25/` перемещена в `archive/smoke_2026-04-25/` (11 файлов сохранены).

### §1.2. Средние (M-5..M-8)

- **M-5 — Статус `outline-ready`.** Введён промежуточный статус между `bf-researcher` и `bf-material-author`. Цепочка теперь: `(нет файла) → outline-ready → material-draft → draft → review → clean → humanized → translated → final`. Обновлены 4 файла (`production_state.md`, `bf-coordinator.md`, `handoff_contracts.md`, `CLAUDE.md`).
- **M-6 — Контракт 9.7 reopen_beat.** Добавлен шаг сохранения `glava_NN.md` в `_drafts/_history/glava_NN_v<timestamp>.md` перед откатом статуса; JSON-формат `reopen_beat` расширен полем `preserve_old_glava_path`.
- **M-7 — Способы вызова controller.** В `bf-controller.md` добавлена секция «Способы вызова»: Путь 1 (прямой subagent) и Путь 2 (general-purpose proxy fallback). Зафиксировано: «Путь 2 — штатный fallback, не аварийный».
- **M-8 — Compiler уточнение «не интерпретировать».** В `bf-compiler.md` §«Абсолютные ограничения» уточнено: «НЕ интерпретировать СОДЕРЖИМОЕ артефактов» + явное разрешение на substitution в placeholder'ах Session_TEMPLATE как механической операции.

### §1.3. Минорные (m-9..m-12)

- **m-9 — Stale ref §13.2.** В `production_state.md` строка про Band III — ссылка на `§13.2` (закрытая priority-таблица) удалена; имя файла `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` сохранено.
- **m-10 — PowerShell encoding.** В `bf-compiler.md` §«Абсолютные ограничения» добавлена памятка про PS 5.x vs PS 7+ encoding кириллицы; единственный `Get-Content` (Шаг 2 валидация beat-плана) дополнен `-Encoding UTF8`.
- **m-11 — Coordinator правило 5.** Переформулировано: review-итерации author↔editor явно отделены от Контракта 6.5 writer-loop Ф8 (max_iterations=3) — это разные счётные машины.
- **m-12 — Иерархия голоса.** В `shared_vocabulary.md` добавлена §4.1 «Иерархия голоса (приоритет при конфликте)»: три уровня (фабрика `brand-voice` → серия `series-bible` → книга `tonal_compass`/`stil_und_ton_XX`) с правилом «книга > серия > фабрика». CLAUDE.md правило 5 расширено ссылкой на §4.1.

---

## §2. Smoke-проверки

### §2.1. C-1 fix smoke-test

**Сценарий**: создан `_testing/_pre_f8_smoke/session_t10_only.md` — файл, содержащий ТОЛЬКО секцию `## T10` (без T1..T9, T11, T12, BEGIN-маркеров). Прогнан обновлённый PowerShell self-check.

**Результат**:
```
MISSING: ^## T1\b
MISSING: ^## T2\b
MISSING: ^## T3\b
MISSING: ^## T4\b
MISSING: ^## T5\b
MISSING: ^## T6\b
MISSING: ^## T7\b
MISSING: ^## T8\b
MISSING: ^## T9\b
MISSING: ^## T11\b
MISSING: ^## T12\b
MISSING: ---BEGIN_REFERENCE_CHAPTER---
MISSING: ---BEGIN_VERBOT_LISTE---
MISSING: ---BEGIN_CALIBRATION---
MISSING: ---BEGIN_PROTOCOL---
Total MISSING: 15 (expected: 15)
```

**Ключевое**: T10 НЕ помечен как MISSING (word boundary `\b` корректно различает `## T1` vs `## T10`). До C-1 fix старая команда `grep -q "## T1"` вернула бы false positive «T1 присутствует» из-за подстроки в `## T10` — баг устранён.

### §2.2. Health-check 12 команд идемпотентности

Все 12 команд идемпотентности из ТЗ прогнаны единым PowerShell-блоком:

| Пункт | Поле | Ожидание | Факт |
|-------|------|----------|------|
| C-1 | `bash_uses_word_boundary_or_dot` | true | ✅ true |
| C-1 | `ps_array_still_naive` | false | ✅ false |
| C-2 | `contract4_deprecated_marked` | true | ✅ true (через `Get-Content -Raw` + `(?s)` multiline regex — после C-3 фикса метода) |
| C-3 | `idempotency_rule_present` | true | ✅ true |
| C-4 | `active_dir_removed` | true | ✅ true |
| C-4 | `archived` | true | ✅ true |
| M-5 | `researched_status_documented` | true | ✅ true |
| M-6 | `history_backup_documented` | true | ✅ true |
| M-7 | `fallback_documented` | true | ✅ true |
| M-8 | `wording_clarified` | true | ✅ true |
| m-9 | `stale_ref_present` | false | ✅ false |
| m-10 | `needs_explicit_utf8` | false (на PS 7+) | ✅ false |
| m-11 | `disambiguation_present` | true | ✅ true |
| m-12 | `relationship_documented` | true | ✅ true |

**12/12 pass.**

### §2.3. Controller full на 8 артефактах

Один прогон bf-controller (depth=full) через Путь 2 (general-purpose proxy) на финальном состоянии 8 файлов:
1. `bf-compiler.md` (правлено в C-1, M-8, m-10)
2. `bf-controller.md` (правлено в C-3, M-7)
3. `bf-coordinator.md` (правлено в M-5, m-11)
4. `handoff_contracts.md` (правлено в C-2, M-5, M-6)
5. `production_state.md` (правлено в M-5, m-9)
6. `shared_vocabulary.md` (правлено в m-12)
7. `CLAUDE.md` (правлено в M-5, m-12)
8. `_SESSION_START_PROMPT.md` (правлено в C-3, v2.4)

**Verdict**: `accept`. 15 прицельных проверок прошли, 2 косметических warning без блока:
- Косметическое: `handoff_contracts.md` frontmatter `depends_on` указывает только `shared_vocabulary.md`, но Контракт 9 (P2-4) ссылается также на `CLAUDE.md` и `production_state.md`. Не блокер.
- Косметическое: `bf-coordinator.md` disclaimer ссылается на `_TZ_WRITER_BEAT_BY_BEAT.md §5` — общий раздел, точная ссылка была бы полезнее. Не блокер.

Статусная модель `outline-ready` консистентна во всех 4 файлах. Контракт 4 DEPRECATED, Контракт 9 активен. Compiler self-check корректно различает regex/literal ветки. Controller содержит и правила идемпотентности (5 прецедентов), и способы вызова (Путь 1/2). Coordinator правило 5 явно отделяет review-итерации от writer-loop. Иерархия голоса (3 уровня) в shared_vocabulary.md §4.1 с явной ссылкой из CLAUDE.md.

---

## §3. Открытые регрессии

Нет.

§6 ТЗ `_TZ_PRE_F8_FIXES_2026-04-26.md` остаётся пустым — за всю серию из 13 пунктов ни одного `block` от controller не было.

---

## §4. Готовность к Ф8

**Pre-Ф8 cleanup закрыт. Готовность к Ф8 = 100% на оси целостности контрактов.**

Что это значит:
- Все 3 критических дефекта, блокировавших Ф8 (C-1 compiler false positive; C-2 двусмысленность Контракта 4 vs 9; C-3 системный дефект команд идемпотентности), устранены.
- Статусная модель готова принять статусы writer-loop Ф8 (Контракт 6.5 ссылается корректно из bf-coordinator.md правило 5; статус `outline-ready` встроен в существующую цепочку без конфликтов).
- bf-controller подготовлен к валидации Ф8-артефактов: задокументированы оба пути вызова и системное правило команд идемпотентности.
- bf-compiler читает кириллические артефакты безопасно (PS 5.x/7+ совместимость).
- Иерархия голоса формализована — Ф8 writer-loop сможет однозначно разрешать конфликты «brand-voice vs series-bible vs tonal_compass».

**Возможно открытие ТЗ Ф8 (writer-loop machine) без блокирующих дефектов.**

---

## §5. Оси, не покрытые этим cleanup

Этот ТЗ закрывал **целостность контрактов и hygiene infra**. За пределами scope:
- Производительность writer-loop (latency, токен-бюджет на iteration) — задача Ф8.
- Семантика критик-правок Ф8 (что считать «критическим нарушением» внутри beat-а) — задача Ф8.
- Эмпирическая калибровка max_iterations=3 — данных пока нет, задача после первых прогонов Ф8.
- Конфликт `tonal_compass.md` (старая модель) vs `stil_und_ton_XX.md` (новая модель слоя A) — двойная номенклатура зафиксирована в shared_vocabulary.md §3.1 и §4.1, но миграция не выполнена; задача отдельной чистки слоя A.

Эти оси НЕ блокируют открытие Ф8 — они становятся видны только после первых прогонов writer-loop.

---

**Конец отчёта. Pre-Ф8 cleanup закрыт 2026-04-26.**
