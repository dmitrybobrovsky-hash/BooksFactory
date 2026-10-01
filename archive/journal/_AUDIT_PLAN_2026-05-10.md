# План полного аудита фабрики BooksFactory

**Дата создания:** 2026-05-09
**Исполнение:** следующая сессия Claude.ai
**Принцип:** Karpathy — что работает, не ломаем. Аудит = поиск + фиксация. **Никаких правок** без явного решения автора.

---

## 0. Контекст

После Test3 фабрика прошла серию правок (Ф14, Ф15, INCIDENT-04..08). Накопилась критическая масса возможных латентных дефектов класса:
- Декларация в каноне без реализации (INCIDENT-06, INCIDENT-08)
- Self-check форма vs факт (INCIDENT-05)
- Масштабируемость артефактов (INCIDENT-07)

Цель — систематически найти всё подобное, не дожидаясь следующего INCIDENT-XX в производстве.

---

## 1. Объём

### Файлы для проверки

**Корень:** `CLAUDE.md`, `BOOKSFACTORY.md`, `BOOKSFACTORY_AI.md`, `CHANGELOG.md`, `_HANDOFF_AUDIT_*.md`, `_SESSION_START_PROMPT.md`

**`.claude/`:** `settings.json`, `settings.local.json`, все `agents/*.md`, `memory/architecture.md`, `memory/production_state.md`, `hooks/*.sh`, `skills/*.md`

**`architecture/`:** `FACTORY_MAP.md`, `handoff_contracts.md`, `shared_vocabulary.md`, `provocation_principles.md`, `series-bible.md`, `brand-voice.md`, `ABGRENZUNG.md`

**`skills/`:** все `SKILL.md` (editor, editor-lite, humanizer, project-manager, translator, writer)

**`templates/`:** `tpl-session-template.md`, `tpl-verbot-liste-proposals-pending.md`, `tpl-session-state.md`

**`method/`:** `METHOD.md`, `LESSONS_LEARNED.md`, `PATTERNS_OF_FAILURE.md`

**`tools/`:** `init_book.py`, `backup.py`, `rollback.py`

**Глобальный:** `~/.claude/CLAUDE.md` (Karpathy) — применяется ли проектными.

### НЕ проверять

`_testing/Test1*`, `_testing/Test2*`, `_testing/Test3_*/_archive_2026-05-08/`, `archive/journal/*`, `.claude/backups/*`.

---

## 2. Метод — 7 классов проверок

### Класс A: Декларация vs реализация (главный)

Класс INCIDENT-06 и INCIDENT-08. Для каждого правила в каноне — есть ли инфраструктура для исполнения.

**Конкретные проверки:**
- Каждый агент с упоминанием `Task(...)` или `subagent` — есть ли `Task` в `tools` frontmatter?
- Каждая ссылка на скилл (`@skills/X/SKILL.md`) — существует ли скилл?
- Каждая ссылка на шаблон (`templates/tpl-*.md`) — существует ли шаблон?
- Каждая ссылка на файл артефакта (`<book>/file_XX.md`) — описан ли формат создания?
- Каждое JSON-правило (например `pattern_budget`) — описана ли схема полностью?
- bf-editor «meta-critic функция» — описано ли **как именно** он считает cross-section повторы?
- bf-humanizer, bf-translator — латентные декларации (цепочка не тестировалась).

### Класс B: Self-check форма vs факт

Класс INCIDENT-05. Для каждой self-check секции в агентах:

**Маркеры формальной проверки** (плохо):
- «Continuity-блок заполнен» — наличие, не содержимое
- «Frontmatter присутствует» — без проверки полей

**Маркеры фактической проверки** (хорошо):
- «Открой файл X, убедись, что строки добавлены»
- «Сумма N по beat-ам = M»

### Класс C: Cross-references

- Все ссылки на файлы — существование пути
- Все ссылки на разделы (`§N`) — наличие раздела
- Все упоминания версий — единый актуальный
- Имена агентов в тексте — соответствуют ли реальным `bf-*.md`
- Журнальные пути (`archive/journal/...`) — без `rchive/` или двойных префиксов

### Класс D: Версионирование и даты

- BOOKSFACTORY_AI.md `version: 1.9` — другие архитектурные файлы синхронизированы по дате?
- Frontmatter `updated:` — актуален (последний — 2026-05-09)?
- CHANGELOG.md — отражает Ф14 INCIDENT-06+08, Ф15?

### Класс E: Масштабируемость артефактов

Класс INCIDENT-07. Для каждого растущего артефакта — рост за время Test3, прогноз к Главе 16/Книге 5, есть ли защита:
- `_skvoznye_formuly_XX.md`
- `verbot_liste_XX.md`
- `_critic_log_Glava_NN.json`
- `production_state.md`
- `_SESSION_STATE.md` (per-book)
- Session-файл (Ф15 закрыта частично)

### Класс F: Дублирование правил

Одно правило в нескольких местах — риск расхождения. Проверить согласованность:
- «Сигнатурная фигура ≤8 на главу, ≤50 на книгу» — `shared_vocabulary`, `tpl-session-template` T9, `bf-material-author`, `bf-critic`
- «§IX-staging» — `bf-material-author`, `bf-coordinator`, `tpl-session-template` T14, `skills/project-manager/SKILL.md`, `handoff_contracts`
- «Изоляция critic как subagent» — `bf-coordinator`, `bf-critic`, `BOOKSFACTORY_AI`

### Класс G: Глобальный Karpathy CLAUDE.md

- `~/.claude/CLAUDE.md` существует и содержит 4 принципа?
- Проектный `CLAUDE.md` BooksFactory — наследует или конфликтует с глобальным?
- Есть ли в проектном правила, противоречащие Karpathy?

---

## 3. Формат отчёта

**Файл:** `_FACTORY_AUDIT_2026-05-10.md` в корне `BooksFactory/`.

```markdown
# Полный аудит фабрики BooksFactory — 2026-05-10

## Сводка
| Класс | Critical | High | Medium | Low | Total |

## Находки
### A1. [Заголовок]
**Класс:** A | **Приоритет:** Critical/High/Medium/Low | **Статус:** confirmed/latent
**Файл:** path
**Описание:** что не так
**Доказательство:** конкретный фрагмент
**Предлагаемая починка:** план без реализации
**Зависимости:** другие находки

## Рекомендуемый порядок починки
## Backup (подтверждение)
```

**Приоритеты:**
- **Critical** — фабрика остановится на следующем production run.
- **High** — фабрика будет давать ложные результаты.
- **Medium** — рассогласование документации.
- **Low** — косметика.

---

## 4. Подготовка перед стартом

1. `python tools/backup.py` — обязательно. Без бэкапа не начинать.
2. Прочитать `_testing/Test3_05.05.2026/_SESSION_STATE.md` записи (41)–(20).
3. Прочитать `_test3_report.md` — все находки + addendum 2026-05-09.

---

## 5. Триггеры остановки

- Critical latent-дефект, угрожающий целостности фабрики → остановиться, отчитаться.
- Ресурс сессии < 20% → partial audit, описать что не проверено.
- Backup падает → не начинать аудит.

---

## 6. Что НЕ делать

- Не править канон.
- Не закрывать находки.
- Не менять версии.
- Не удалять файлы.
- Не делать `git commit`.

---

## 7. После завершения

- Запись в `_SESSION_STATE.md` Test3: результат аудита, путь к отчёту, число находок по приоритетам.
- Упоминание в `BOOKSFACTORY_AI.md` как событие 2026-05-10 (без закрытия фаз).

---

## 8. Время

~50–60% сессии Claude.ai. При нехватке — в две сессии (первая: A, B; вторая: C, D, E, F, G).
