---
document: handoff
created: 2026-05-01
source: Сессия аудита BooksFactory в Claude.ai (Opus)
purpose: >
  Передача результатов аудита и новых документов в Claude Code.
  Читать ПЕРЕД любой другой работой в следующей сессии.
---

# Handoff: результаты аудита 2026-05-01

## Что сделано в этой сессии

### 1. Созданы два новых документа в корне фабрики

- **`BOOKSFACTORY.md`** — концепция, устройство, процессы и инструкция эксплуатации. Документ для человека. 13 разделов, публичный тон. Фичи в разработке помечены *(дорожная карта)* — при готовности пометка снимается, текст не переписывается.

- **`BOOKSFACTORY_AI.md`** — параллельный документ для Claude Code. Та же структура, технические детали. Каждый элемент имеет статус: ✅ ГОТОВ (не трогать), 🚧 ДОРОЖНАЯ КАРТА (реализовать по запросу), ⛔ DEPRECATED (не использовать). **Читать при каждом старте сессии.**

**TODO:** добавить `BOOKSFACTORY_AI.md` в `CLAUDE.md` (таблица «Ключевые файлы») и в `_SESSION_START_PROMPT.md` (ШАГ 1).

### 2. Аудит фабрики — 12 находок

#### Критичные (починить ПЕРЕД продолжением любой работы)

**A1. Фазы агентов разъехались между двумя картами.**
`architecture/FACTORY_MAP.md` и `.claude/memory/architecture.md` заявлены как синхронизированные. По факту:
- bf-critic: Ф1 в FACTORY_MAP, Ф4 в memory/architecture
- bf-compiler: Ф3 в FACTORY_MAP, Ф6 в memory/architecture
- bf-researcher: Ф4 в FACTORY_MAP, Ф3 в memory/architecture
- bf-material-author: Ф4 в FACTORY_MAP, Ф3 в memory/architecture
**Действие:** выбрать один файл как источник истины, привести второй в соответствие.

**A2. shared_vocabulary.md §1 — устаревшая цепочка.**
Заявлен как `single_source_of_truth`, но §1 описывает старую цепочку `PM → Писатель → Редактор → Гуманизатор → Переводчик`. Актуальная цепочка — 8 звеньев (researcher → material-author → planner → compiler → coordinator → editor → humanizer → translator).
**Действие:** обновить §1 shared_vocabulary.md до актуальной цепочки.

**A3. Кто ставит статус `clean` — противоречие.**
- handoff_contracts.md Контракт 9.4 + сводная таблица: `clean` ставит Editor.
- production_state.md: `clean` ставит автор/refiner.
**Действие:** зафиксировать одну версию в обоих файлах.

#### Битые ссылки

**A4. bf-humanizer.md ссылается на несуществующий файл.**
Шаг 1 инициализации: `skills/humanizer/SKILL.md`. Этот файл не существует в `skills/humanizer/` — только подпапки ru/de/en. Диспетчер существует в `.claude/skills/humanizer/SKILL.md`.
**Действие:** исправить путь в bf-humanizer.md.

**A5. glossary.md — orphan в архитектурном слое.**
Лежит в `architecture/`, но не упомянут ни в FACTORY_MAP, ни в memory/architecture, ни в CLAUDE.md.
**Действие:** добавить в FACTORY_MAP §«Архитектурный слой» и в CLAUDE.md §«Ключевые файлы».

#### Хуки

**A6. check_chapter_status.sh — мёртвый код.**
Переменная `VALID_TRANSITIONS` объявлена и не используется. Поле `role_required` упомянуто в комментарии, но не проверяется в коде. Реально блокирует только статус `final`.
**Действие:** либо реализовать полную проверку переходов, либо упростить комментарии до фактического поведения. Полная реализация — Ф10 дорожной карты.

**A7. Хуки не знают про `outline-ready`.**
`PRODUCTION_STATUSES` в обоих скриптах не включает `outline-ready`. Файл главы с этим статусом хук пропустит молча.
**Действие:** добавить `outline-ready` в список `PRODUCTION_STATUSES` в обоих скриптах.

**A8. update_production_state.sh — дописывание без структуры.**
Дописывает HTML-комментарии в конец production_state.md без ротации и без timestamp с минутами.
**Действие:** отложить до Ф10; пока — не критично.

#### Конвенции

**A9. Двойное именование `project_manager` / `project-manager`.**
`skills/project_manager/` (snake_case) vs `.claude/skills/project-manager/` (kebab-case).
**Действие:** выбрать одну конвенцию, привести к единообразию.

**A10. Диспетчеры в `.claude/skills/` превышают лимит 100 строк.**
FACTORY_MAP требует `< 100 строк` для диспетчеров. 5 из 6 ключевых превышают (writer: 173, translator: 155, editor: 146, project-manager: 110, humanizer: 108).
**Действие:** либо split по правилу FACTORY_MAP, либо обновить правило до реалистичного лимита.

#### Незавершённости (известны, для полноты)

**A11. bf-writer.md описывает section-by-section, FACTORY_MAP ожидает beat-by-beat.**
Это Ф7 дорожной карты — не аудит-баг, а плановая незавершённость. tools в bf-writer.md: Read/Write/Edit. FACTORY_MAP ожидает: нет tools после Ф7.
**Действие:** закрывается в Ф7.

**A12. `tools/` пуст.**
CLAUDE.md: «tools/ ← скрипты анализа рукописей (TODO)».
**Действие:** реализовать dedup-скрипт и continuity-checker (Ф11 дорожной карты).

### 3. Сравнение с Claude Code Starter v6.1.0 (Крол)

Что у фабрики сильнее — 8 пунктов (контракты, мульти-язык, иерархия голоса, статусная модель, workflow B, lessons learned, beat-цикл, декомпозиция PM).

**4 паттерна для заимствования:**
1. Глобальный слой `~/.claude/` + `/setup-project` — стартовать новую книгу одной командой.
2. Backup + rollback одной командой — страховка при правках федеральных документов.
3. Аддитивный merge CLAUDE.md — обновление фабрики не затирает кастомизации книги.
4. Формализация changelog — `CHANGELOG.md` с версиями вместо журнальных файлов `_TZ_*`.

**Не брать:** 28-point reviewer (у нас ≤5 точек), auto-detection типа проекта, 3-агентная схема.

### 4. Решение по bf-pm

`bf-pm` — не сломан, а намеренно расщеплён на bf-researcher + bf-material-author + bf-compiler. Все функции покрыты. Файл сохранён для rollback safety. **Удалить после закрытия Ф7/Ф8.**

## Приоритет работ — разделение ответственности

### Делает Claude.ai (Opus) — НЕ Claude Code

Пункты A1–A4 и A7 чинит Claude.ai в отдельной сессии с автором. Контекст аудита — в этом чате, передавать его в Claude Code нецелесообразно (смена вектора работы).

1. **A1 + A2 + A3** — рассинхроны источников истины. ✅
2. **A4** — битая ссылка в bf-humanizer.md. ✅
3. **A5** — glossary.md orphan (добавлен в FACTORY_MAP и CLAUDE.md). ✅
4. **A7** — `outline-ready` в хуках. ✅
5. **A9** — snake_case → kebab-case (`project_manager` → `project-manager`). ✅
6. **BOOKSFACTORY_AI.md** добавлен в CLAUDE.md и _SESSION_START_PROMPT.md. ✅

**Claude Code: НЕ ТРОГАТЬ пункты A1–A4, A7. Они будут починены отдельно.**

### Делает Claude Code

Продолжать текущую работу (тестовый прогон IU или Ф7/Ф8 — по решению автора). Перед началом прочитать `BOOKSFACTORY_AI.md` для понимания статусов элементов.
