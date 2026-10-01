# Доделка по пост-ремонтному аудиту 2026-05-10

**Контекст:** Аудит после ремонта `_POST_REPAIR_AUDIT_2026-05-10.md` нашёл 4 находки (1 High, 2 Medium, 1 Low), которые Code допустил при основном ремонте.

**Модель:** Sonnet
**Бэкап:** уже сделан перед основным ремонтом (`2026-05-10_1234`). Дополнительный не нужен.

---

## Шаг 1. POST-1 [High] — BOOKSFACTORY_AI двойные пути

### `BOOKSFACTORY_AI.md`

В строках 253 и 254 (секция §5 «Журнальные файлы») найти и заменить:

Строка 253:
```
archive/journal/archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md
```
→
```
archive/journal/_TZ_WRITER_BEAT_BY_BEAT.md
```

Строка 254:
```
archive/journal/archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md
```
→
```
archive/journal/_TZ_AUDIT_FIXES_2026-04-25.md
```

**Проверка:**
```bash
grep -c "archive/journal/archive/journal/" BOOKSFACTORY_AI.md
```
Ожидается: `0`

---

## Шаг 2. POST-2 [Medium] — bf-planner заголовок «8 проверок»

### `.claude/agents/bf-planner.md`

Найти строку (около строки 109):
```
Перед записью JSON-файла пройти **8 проверок**:
```
Заменить на:
```
Перед записью JSON-файла пройти **9 проверок**:
```

**Проверка:**
```bash
grep "8 проверок\|9 проверок" .claude/agents/bf-planner.md
```
Ожидается: одна строка с `9 проверок`, ноль строк с `8 проверок`.

---

## Шаг 3. POST-3 [Medium] — bf-planner таблица префиксов

### `.claude/agents/bf-planner.md`

Найти строку (около строки 127):
```
| `PLANNER_SELFCHECK_FAILED` | Self-check §4 пункты 1–8 — детали после двоеточия |
```
Заменить `пункты 1–8` на `пункты 1–9`. Результат:
```
| `PLANNER_SELFCHECK_FAILED` | Self-check §4 пункты 1–9 — детали после двоеточия |
```

**Проверка:**
```bash
grep "пункты 1–" .claude/agents/bf-planner.md
```
Ожидается: одна строка с `1–9`.

---

## Шаг 4. POST-4 [Low] — bf-editor пунктуация

### `.claude/agents/bf-editor.md`

Найти строку 74 (пункт 3 meta-critic):
```
имена учёных без сноски — точка отчёта, Метод: Grep имён учёных
```
Заменить на:
```
имена учёных без сноски — точка отчёта. Метод: Grep имён учёных
```

(Запятую перед «Метод» заменить на точку.)

---

## Шаг 5. Запись в _SESSION_STATE.md

### `_testing/Test3_05.05.2026/_SESSION_STATE.md`

Добавить в начало (после заголовка, перед записью 43) запись 44:

```markdown
## 2026-05-10 (44)
status: completed
step: Доделка по пост-ремонтному аудиту `_POST_REPAIR_AUDIT_2026-05-10.md`. 4 находки от Code-ремонта: POST-1 (High, BOOKSFACTORY_AI двойные пути 253-254 — Code пропустил), POST-2 (Medium, bf-planner заголовок «8 проверок» при 9 пунктах), POST-3 (Medium, bf-planner таблица префиксов «1–8» вместо «1–9»), POST-4 (Low, bf-editor пунктуация). Все 4 починены.
agent: Claude Code (Sonnet)
artifacts_updated: BOOKSFACTORY_AI.md, .claude/agents/bf-planner.md, .claude/agents/bf-editor.md
next: фабрика готова к производству.
```

---

## Шаг 6. Финальная верификация

```bash
# POST-1
grep -c "archive/journal/archive/journal/" BOOKSFACTORY_AI.md
# Ожидается: 0

# POST-2
grep "8 проверок" .claude/agents/bf-planner.md
# Ожидается: пусто
grep "9 проверок" .claude/agents/bf-planner.md
# Ожидается: 1 строка

# POST-3
grep "пункты 1–" .claude/agents/bf-planner.md
# Ожидается: 1 строка с "1–9"

# POST-4
grep "точка отчёта, Метод" .claude/agents/bf-editor.md
# Ожидается: пусто
grep "точка отчёта. Метод" .claude/agents/bf-editor.md
# Ожидается: 1 строка
```

Все 6 проверок должны пройти. Если хотя бы одна не прошла — СТОП, отчитаться автору.
