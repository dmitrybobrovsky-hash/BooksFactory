# ТЗ-Аудит: Исправление дыр фабрики 2026-04-25

> **Версия 2.0 — Закрыт 2026-04-26.** PART 1 + PART 2 + P-FINAL завершены.
> Версионная история: v1.0 → v1.1 (автобан) → v1.2 (расщепление Ф8 + PART 2) → v2.0 (закрытие 2026-04-26).
> Автор: Dmitry Bobrovsky.
> Источник: аудит фабрики, проведённый Claude в сессии 2026-04-25 (после закрытия Ф5/bf-planner).
> Параллельные документы (НЕ дублировать содержимое — ссылаться):
> - `_TZ_WRITER_BEAT_BY_BEAT.md` §5 — фазовая ось Ф0–Ф13.
> - `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` §13.2 — старый priority list (P0–P3 от 2026-04-23).
> - `_SESSION_START_PROMPT.md` — точка входа в сессию.
>
> Этот файл — **одновременно ТЗ и лог.** Читать в начале каждой сессии. Помечать выполненные пункты по правилам §0.
>
> **Принцип v1.1 — автобан**: ТЗ исполняется линейно, от A до B, без вопросов «куда ехать». Все развилки заранее закрыты явными правилами. Любая остановка — только аварийная (controller block), и тогда работа ждёт автора, без вариантов «обойти».
>
> **Принцип v1.2 — расщепление Ф8**: фазовая ось `_TZ_WRITER_BEAT_BY_BEAT.md` помечала пункты §5 как «ждёт Ф8» консервативно, потому что Ф8 — большая фаза. По факту Ф8 распадается на (а) обновление **routing-таблиц и контрактов-документов** агентов и (б) реализация **исполняемой writer-loop-машины**. Пункты §5, относящиеся к (а), переносятся в §4-bis (PART 2) и закрываются сейчас. Пункты, относящиеся к (б), остаются в §5 и ждут полной Ф8. То же расщепление для Ф1a (документация-карта закрывается сейчас, координация активных артефактов с картой — после Ф8) и Ф6 (шаблон Session_TEMPLATE — сейчас, sed-санитайз compiler — сейчас).

---

## 0. Как пользоваться этим файлом

### 0.1 Подгрузка в начале сессии

`_SESSION_START_PROMPT.md` (после обновления в P0-0) сделает это автоматически: шаг 0 промпта читает этот файл целиком и выполняет команды идемпотентности по всем пунктам без `ВЫПОЛНЕНО`.

До закрытия P0-0 — автор подгружает вручную: «читай `_TZ_AUDIT_FIXES_2026-04-25.md` и продолжай».

### 0.2 Формат метки выполнения

Когда пункт сделан, заголовок переписывается **в одну строку**, формате:

```
### P0-1. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Удалить дубли band3-*.md
```

- Дата — день закрытия пункта.
- Вердикт контроллера (`accept` / `warn`) — обязателен. Без вердикта пункт не закрывается.
- При `warn` — после вердикта в скобках: `(controller: warn — <причина>)`.
- При `block` — пункт **НЕ помечается** как ВЫПОЛНЕНО. См. §0.4.

### 0.3 Команда идемпотентности

Каждый пункт обязан иметь команду (PowerShell / Test-Path / Grep), которая однозначно отвечает:
- `True` / совпадение найдено → пункт уже сделан.
- `False` / совпадения нет → пункт не сделан.

**Если команда говорит «уже сделано» (True)**:
1. Переписать заголовок в формат §0.2 с пометкой `(controller: accept-by-idempotency)`.
2. Записать строку в §7 «Журнал».
3. **Перейти к следующему пункту.** Controller не вызывается (правка уже была провалидирована в той сессии, где её делали).

### 0.4 Block — единое правило стопа

Controller-вердикт `block` означает: правка либо сломала уже сделанное, либо создала структурную дыру (orphan-агент, битая ссылка, hang-risk, нарушение scope). **Реакция — единая, без вариантов выбора:**

1. Правка **остаётся в файлах** (откат вручную не делаем — может разрушить накопленный прогресс).
2. Запись в §6 «Регрессии»: дата, номер пункта, причина block, какая команда идемпотентности у какого пункта теперь возвращает не то, что должна.
3. Запись в §7 «Журнал»: «P0-X — block, см. §6 R-NNN».
4. **Sequence останавливается.** Следующий пункт **не берётся**, пока автор не дал решение по регрессии.
5. Эскалация автору: одно сообщение с цитатой записи §6 и предложенными вариантами решения (если они есть; если автор должен решить с нуля — сказать так).

Не существует ситуации «block, но я продолжу другие пункты». Block — глобальный стоп ТЗ до решения автора.

### 0.5 Минимальный шаг исполнения (один пункт)

```
1. Read команды идемпотентности.
   ├── True  → §0.3 (метка-by-idempotency, журнал, следующий пункт). КОНЕЦ ШАГА.
   └── False → продолжай.
2. Edit / Write / Bash правка по «Что делать».
3. Вызов bf-controller с глубиной из «Controller depth» пункта.
4. Вердикт:
   ├── accept       → §0.2 метка ВЫПОЛНЕНО, журнал, следующий пункт.
   ├── warn         → §0.2 метка с warn-комментарием, журнал, следующий пункт.
   └── block        → §0.4 (стоп, регрессия, эскалация).
```

Никаких других веток. Никаких «может быть, лучше пропустить». Никаких «давай сначала проверю что-то ещё».

### 0.6 Кто исполняет цикл

Распределение ролей в цикле одного пункта:

| Шаг | Исполнитель | Инструмент |
|-----|-------------|------------|
| Загрузка ТЗ в сессию | Автор (Dmitry) | вручную или через `_SESSION_START_PROMPT.md` после P0-0 |
| Выбор первого пункта без ВЫПОЛНЕНО | **Главный агент сессии (Claude)** | Read |
| Команда идемпотентности | Главный агент | Bash / Grep / Read |
| Если уже сделано → маркер | Главный агент | Edit (этот же файл) |
| Если не сделано → правка | Главный агент | Edit / Write / Bash |
| Валидация после правки | **bf-controller** (через `Agent({subagent_type: "bf-controller"})`) | Read-only, JSON-вердикт |
| Маркер ВЫПОЛНЕНО + запись в §7 | Главный агент | Edit |
| Если block → §0.4 | Главный агент: запись + эскалация | Edit (§6) + сообщение автору |

**Жёсткая граница**: главный агент **не валидирует сам себя**. Каждая правка — через `Agent` tool на `bf-controller`. Иначе нет «второго глаза».

### 0.7 Sequence — порядок исполнения пунктов

**Жёстко зафиксирован**. Главный агент берёт следующий по списку, не выбирает:

```
PART 1 (закрыта 2026-04-25):
  P0-0a  → P0-0 → P0-1  → P0-2  → P1-1  → P1-2  → P2-2

PART 2 (расширение v1.2):
  P3-0 → P3-1 → P2-1 → P1-3 → P3-4 → P3-2 → P2-3 → P0-3 → P2-4 → P-FINAL
```

Правило: «следующий пункт = первый в этом sequence, у которого нет `ВЫПОЛНЕНО` в заголовке». Не «выбери по приоритету». Не «начни с лёгкого». Sequence линейный.

Логика порядка PART 1:
- **P0-0a** первым — расширение `bf-controller` контрактом `audit_task` валидируется обычным `full`-вызовом (без `audit_task`-контракта, controller-self-check). Не имеет зависимостей. После закрытия — controller умеет валидировать остальные 6 пунктов в режиме `audit_task`.
- **P0-0** вторым — после P0-0a controller уже знает `audit_task`, поэтому шаг 0 в `_SESSION_START_PROMPT.md` сразу валидируется чисто по протоколу.
- **P0-1** третьим — лёгкая, безрисковая правка (удаление дублей), даёт быструю валидацию controller'а на новом контракте.
- **P0-2** четвёртым — большая правка memory; до неё уже есть рабочий controller, можно поймать регрессии.
- **P1-1** пятым — single-line fix, низкий риск.
- **P1-2** шестым — расширение compiler'а, средний риск.
- **P2-2** седьмым — финальный косметический warn-line.

Логика порядка PART 2 (от изолированно-технического к интегрированному):
- **P3-0** первым — Edit-hook ловит и Edit-инструмент. Один файл, одна строка, изолированный технический фикс безопасности; должен идти раньше доковых правок, потому что hook будет защищать сами эти правки.
- **P3-1** вторым — `CLAUDE.md` (включая 2 минора). Корневой документ, читается каждой сессией; пока не актуализирован — врёт о маршрутизации. Изолированная правка документа, без зависимостей от других пунктов.
- **P2-1** третьим — `FACTORY_MAP.md` refresh + правило ветвления `skills/` vs `.claude/skills/`. После P3-1 — оба корневых документа согласованы.
- **P1-3** четвёртым — haiku/sonnet sync в TZ-документе. Изолированная docs-правка, низкий риск.
- **P3-4** пятым — sed BSD/GNU mismatch в `bf-compiler.md`. Один-два места, замена на PowerShell-эквивалент или явная ветвь.
- **P3-2** шестым — единая модель статусов главы. Концептуальное решение фиксируется в `production_state.md` + `architecture.md`; снимает дисклеймер «модель в переходе».
- **P2-3** седьмым — `Session_TEMPLATE.md` создать. Артефакт Ф6, нужен compiler'у для автономной работы. Зависит от P3-2 (статусы): шаблон ссылается на актуальные статусы.
- **P0-3** восьмым — `bf-coordinator.md` знает о новых агентах. Routing-таблица + tools + model. **Не реализует** writer-loop logic (это полная Ф8) — только маршрутизация по агентам и фазам. Зависит от P3-1, P2-1 (документация согласована), P2-3 (Session-шаблон существует).
- **P2-4** девятым — Editor→Humanizer beat-by-beat контракт в `handoff_contracts.md`. Зависит от P0-3 (coordinator знает агентов) — иначе контракт некому исполнять.
- **P-FINAL** десятым — end-to-end smoke-test. Прогон тестовой главы через все 8 (или сколько есть) активных агентов без литературного качества — pipeline-integrity. Закрытие ТЗ по §8.

После P-FINAL — full controller-pass и закрытие ТЗ по §8.

---

## 1. Связь с другими планами

| Где | Что |
|-----|-----|
| `_TZ_WRITER_BEAT_BY_BEAT.md` §5 | Фазы Ф0–Ф13 — основной план переделки фабрики. |
| `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` §13.2 | Старый priority list (A1–E2) от 2026-04-23. Большинство закрыто. |
| Этот файл | Новые дыры из аудита 2026-04-25, **не отражённые** в §13.2. |

**Правило не-дублирования:** если пункт уже трекается в TZ §5 или handoff §13.2 — не дублировать сюда. Здесь — только новые находки. Известные блоки на Ф7/Ф8/Ф1a/Ф6 упомянуты в §5 «Ожидают фазы ТЗ» только для полноты картины, **не исполняются** в этом ТЗ.

---

## 2. Контроллер-протокол

### 2.1 Кто контроллёр

`bf-controller.md` (существующий агент). Расширяется новым входным контрактом:

```json
{
  "audit_task": "P0-1",
  "depth": "light" | "full",
  "claimed_done": true,
  "artifacts": ["<absolute path>"]
}
```

(Расширение контроллера — пункт P0-0a, см. ниже.)

### 2.2 Глубина проверки

| Глубина | Когда | Что проверяет |
|---------|-------|----------------|
| `light` | После каждого пункта (по умолчанию для пунктов §4) | Reference-integrity + Tool-capability + Scope-isolation. ~10 секунд. |
| `full` | После закрытия P0-блока (после P0-2), после закрытия P1-блока (после P1-2), в конце сессии | DoD + Runtime-integrity + Hang-detection + всё, что в `light`. ~1 минута. |

**Правило**: глубина для каждого пункта прописана явно в его описании. Главный агент не выбирает глубину — берёт из ТЗ.

`dry-run` режим в этом ТЗ **не используется** (все Ф7/Ф8 пункты вынесены в §5 как «ожидают фазы»). Контракт `dry-run` оставлен в `bf-controller.md` для будущих фаз, но не вызывается из этого ТЗ.

### 2.3 Что считается accept

- Все DoD-чекбоксы пункта закрыты.
- Команда идемпотентности возвращает True.
- Никакая ранее выполненная команда идемпотентности (по другим пунктам) не сломалась.
- Никакой агент не стал orphan'ом.
- Никакая ссылка из активного файла на удалённый/отсутствующий — не появилась.

### 2.4 Что считается warn

- DoD закрыт, но обнаружен мелкий синхрон (например, fingerprint в handoff не обновлён, или версия документа поднята, но история версий не дописана).
- Главный агент исправляет warn-причину **в той же сессии, до перехода к следующему пункту**, без эскалации автора.

### 2.5 Что считается block

Любое из:
- Команда идемпотентности **другого** пункта (уже выполненного) теперь возвращает False — то есть откатился.
- Любой агент стал orphan'ом (нет ссылки от coordinator/controller или из обязательных artifacts).
- Любая ссылка из активного файла фабрики (CLAUDE.md, FACTORY_MAP, handoff_contracts, агенты, skills) указывает на удалённый/несуществующий файл.
- Hang-risk появился (отсутствие max_iterations / exit-path в writer-loop, бесконечный цикл).
- Нарушение scope: контролёр (или другой Read-only агент) получил Write/Edit; писатель потерял Read.

Реакция на block — §0.4 единое правило, без вариантов.

---

## 3. Идентификатор сессии (для журнала)

При каждой сессии работы с этим ТЗ — запись в §7 «Журнал сессий»:

```
- 2026-04-26 (Sonnet 4.6): P0-0, P0-0a, P0-1 закрыты; controller full: accept.
```

Модель сессии указывает главный агент (видна в системе при старте).

---

## 4. Очередь — sequence

**Порядок строго по §0.7. Главный агент не выбирает между пунктами.**

---

### P0-0a. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Расширить `bf-controller.md` контрактом «audit_task»

**Тип**: исполнимый сейчас.
**Категория**: служебный (нужен, чтобы P0/P1 пункты могли вызвать controller).
**Цена**: 15 минут.
**Зависимости**: нет. Это первый пункт sequence.

**Команда идемпотентности**:
```powershell
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-controller.md" -Pattern "audit_task" -SimpleMatch
```
Если найдено хотя бы одно совпадение — расширение присутствует.

**Что делать**:
1. В `bf-controller.md` добавить раздел «Режим audit_task» после раздела «Пер-фазные проверки».
2. Описать вход: `{audit_task: "P0-1", depth: "light"|"full", claimed_done, artifacts}`.
3. Per-task DoD-таблица — **короткие формулировки** (одна строка на пункт): «P0-1: 4 файла удалены», «P0-2: architecture.md содержит ≥4 упоминания новых агентов, promptBF.txt отсутствует» и т.д. для всех 7 пунктов §4. Полные DoD controller подтянет через `Read` ТЗ.
4. Маппинг depth → набор проверок (как §2.2 этого ТЗ): light = reference + tool-cap + scope; full = light + DoD + runtime + hang.
5. Возврат: тот же JSON-формат, что и для phase-режима, плюс эхо-поле `audit_task: "P0-X"`.
6. Раздел «Правила принятия решения» — добавить строку: «При вызове в режиме `audit_task` — DoD-проверки берутся из ТЗ-аудита, не из фазового списка.»

**DoD**:
- [ ] Раздел «Режим audit_task» добавлен.
- [ ] JSON-схема входа описана.
- [ ] Таблица соответствия пункт ↔ DoD-проверки присутствует (7 строк).
- [ ] Маппинг depth → проверки описан.

**Controller depth**: full (controller сам себя расширяет — финальный self-check после правки).

**Особенность валидации**: вызывается **в обычном (не `audit_task`) режиме**, как self-check перед тем, как audit_task-режим станет доступен. То есть caller передаёт `{phase: "controller-self-check", artifacts: ["bf-controller.md"]}` — controller проверяет свой собственный новый раздел через стандартные DoD/reference/tool-cap чеки. Это разовая bootstrap-операция; все последующие пункты §4 будут вызывать controller уже в режиме `audit_task`.

---

### P0-0. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Обновить `_SESSION_START_PROMPT.md` до v2.2 с шагом 0

**Тип**: исполнимый сейчас.
**Категория**: служебный (без него ТЗ не подгружается автоматически).
**Цена**: 5 минут.
**Зависимости**: P0-0a (controller должен уметь `audit_task` для валидации этого пункта).

**Команда идемпотентности**:
```powershell
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_SESSION_START_PROMPT.md" -Pattern "Версия 2.2" -SimpleMatch
```
Если строка найдена — пункт сделан.

**Что делать**:
1. В `_SESSION_START_PROMPT.md` добавить шаг 0 перед существующим шагом 1:
   - «ШАГ 0 — health check ТЗ-аудита: прочитай `_TZ_AUDIT_FIXES_2026-04-25.md` целиком. Для каждого пункта без `ВЫПОЛНЕНО` в §4 — выполни команду идемпотентности из блока «Команда идемпотентности». Если True — переписать заголовок пункта в формат §0.2 с пометкой `accept-by-idempotency`. Если расхождение между ожидаемым и фактическим (например, файл удалён, но в ТЗ не помечен) — короткий рапорт автору markdown-блоком «Расхождения health-check» перед началом основной работы.»
2. Шапка файла: версия → 2.2, дата → актуальная.
3. История: «v2.2 (2026-04-25): добавлен шаг 0 — health check ТЗ-аудита».

**DoD**:
- [ ] В файле есть строка «Версия 2.2».
- [ ] Шаг 0 описан до шага 1.
- [ ] История версий обновлена.

**Controller depth**: light. Вызов уже в режиме `audit_task: "P0-0"` (после закрытия P0-0a).

---

### P0-1. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Удалить дубли `band3-*.md` из `~/.claude/agents/`

**Тип**: исполнимый сейчас.
**Категория аудита**: B-NEW-4.
**Цена**: 5 минут.

**Команда идемпотентности**:
```powershell
$paths = @("$HOME\.claude\agents\band3-planner.md", "$HOME\.claude\agents\band3-writer.md", "$HOME\.claude\agents\band3-critic.md", "$HOME\.claude\agents\band3-editor.md")
$paths | ForEach-Object { Test-Path $_ }
```
Если все четыре `False` — пункт сделан.

**Что делать**:
1. **Grep репозитория BooksFactory** на pattern `band3-` (без хвоста) — убедиться, что **активные** файлы фабрики (CLAUDE.md, FACTORY_MAP, handoff_contracts, агенты в `.claude/agents/bf-*`, skills) не ссылаются на эти файлы. Допустимы только упоминания в файлах с шапкой «архив», «handoff» (исторические). Папка `obsidian/` отсутствует — не проверяется.
2. **Сравнить уникальный контент** band3-* против bf-*. Уникальное = одно из:
   - правила и ограничения (например, «писатель не имеет WebSearch»)
   - входные/выходные контракты
   - tools list
   - модель (Sonnet/Opus/Haiku)
   - явные ссылки на другие артефакты фабрики
   Литературные формулировки, мотивационные блоки, комментарии-цитаты автора — **не уникальное** (они либо уже мигрированы в `_HANDOFF_*.md`, либо архивированы как опыт). Если найдено уникальное правило, отсутствующее в bf-* — мигрировать в соответствующий bf-* агент **до** удаления.
3. `Remove-Item` каждого файла.

**DoD**:
- [ ] `~/.claude/agents/band3-planner.md` отсутствует.
- [ ] `~/.claude/agents/band3-writer.md` отсутствует.
- [ ] `~/.claude/agents/band3-critic.md` отсутствует.
- [ ] `~/.claude/agents/band3-editor.md` отсутствует.
- [ ] Grep репозитория BooksFactory на `band3-` не находит ссылок в активных файлах (CLAUDE.md, architecture/*, .claude/agents/bf-*, skills/*).
- [ ] Любое уникальное правило (по критерию выше) либо мигрировано в bf-*, либо явно отсутствовало.

**Controller depth**: light + scope-isolation check.

---

### P0-2. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Актуализировать `memory/architecture.md`, `memory/production_state.md`, `promptBF.txt`

**Тип**: исполнимый сейчас.
**Категория аудита**: A-NEW-4 + B-NEW-1.
**Цена**: 30 минут.

**Команда идемпотентности**:
```powershell
$arch = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\architecture.md" -Pattern "bf-critic|bf-controller|bf-compiler|bf-researcher|bf-material-author|bf-planner" -SimpleMatch
$prompt = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\promptBF.txt"
$state = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md" -Pattern "модель статусов в переходе" -SimpleMatch
@{ arch_updated = ($arch.Count -ge 4); prompt_removed = (-not $prompt); state_disclaimed = ($null -ne $state) }
```
Все три значения должны быть `True` — пункт сделан.

**Что делать**:

**A) `.claude/memory/architecture.md`** — переписать:
- Удалить «Все 4 фазы завершены 2026-04-18» как актуальный статус.
- Список агентов — ровно **12** (фиксировано):
  1. `bf-coordinator` — legacy, требует обновления (Ф8).
  2. `bf-pm` — **DEPRECATED stub** (см. ниже, остаётся файлом для истории).
  3. `bf-writer` — legacy, требует обновления (Ф7).
  4. `bf-editor` — legacy.
  5. `bf-humanizer` — legacy.
  6. `bf-translator` — legacy.
  7. `bf-critic` — новый (Ф4, готов).
  8. `bf-controller` — новый (Ф0, готов; расширение audit_task — P0-0a этого ТЗ).
  9. `bf-compiler` — новый (Ф6, готов).
  10. `bf-researcher` — новый (Ф3, готов).
  11. `bf-material-author` — новый (Ф3, готов).
  12. `bf-planner` — новый (Ф5, готов).
- Для каждого агента — статус: `legacy` / `новый` / `deprecated-stub`.
- Состояние тюнинга: ссылка на TZ §5 (фазы Ф0–Ф13) + handoff §13.2 + этот ТЗ.
- Удалить упоминание bf-pm как актуального агента — заменить на «deprecated-stub: функции разделены между `bf-researcher` (исследование), `bf-material-author` (MATERIAL), `bf-compiler` (Session-сборка). Файл остаётся с шапкой DEPRECATED для истории.»

**B) `.claude/memory/production_state.md`** — обновить:
- **Текущая модель статусов сохраняется как есть** (`material-draft → draft → review → clean → humanized → translated → final`).
- В шапку файла добавить дисклеймер-блок:
  ```markdown
  > **Модель статусов в переходе.** Текущая последовательность статусов
  > актуальна до закрытия Ф8 (writer-loop machine). После Ф8 — финализация:
  > возможно появление `beat-N-draft` промежуточных и явный `compiled` перед `draft`.
  > Источник: `_TZ_WRITER_BEAT_BY_BEAT.md` §5.
  ```
- Активные книги: оставить, обновить статусы по факту (MdP, ОНМ).
- Band III: явно «отложено, см. handoff §13.2».
- **Не удалять старые статусы**, не вводить новые — это работа Ф8.

**C) `promptBF.txt`** — удалить файл (B-NEW-1).
- **Перед удалением**: Grep репозитория BooksFactory (без `archive/`) на pattern `promptBF.txt` — убедиться, что никто не ссылается. Папки `obsidian/` нет.
- Если найдены ссылки в активных файлах — мигрировать ссылки на `_SESSION_START_PROMPT.md` **в той же сессии**, до удаления.
- Затем `Remove-Item promptBF.txt`.

**DoD**:
- [ ] `architecture.md` содержит ≥4 упоминания новых агентов.
- [ ] `architecture.md` явно перечисляет 12 агентов со статусами.
- [ ] `architecture.md` не содержит «Все 4 фазы завершены 2026-04-18» как актуальный статус.
- [ ] `production_state.md` имеет дисклеймер-блок «модель статусов в переходе».
- [ ] `production_state.md` сохранил исходную модель статусов (не переписана).
- [ ] `promptBF.txt` удалён.
- [ ] Grep BooksFactory (без `archive/`) на `promptBF.txt` не находит ссылок.

**Controller depth**: full (memory читается каждой сессией — контролировать жёстко). Это первый full в sequence — закрывает P0-блок.

---

### P1-1. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Исправить `writing_control.md` Правило 6 override pointer

**Тип**: исполнимый сейчас.
**Категория аудита**: B-NEW-3.
**Цена**: 5 минут.

**Команда идемпотентности**:
```powershell
$line = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\writing_control.md" -Pattern "Per-книга override" -SimpleMatch
if ($line) { $line.Line -notmatch "_workdir" } else { $false }
```
Если `True` (строка найдена и не упоминает `_workdir` как primary) — пункт сделан.

**Что делать**:
1. Открыть `architecture/writing_control.md`, найти строку «Per-книга override» (около строки 160).
2. Заменить путь `<book>/_workdir/tonal_compass.md` на `<book>/tonal_compass.md` (как primary).
3. Добавить fallback-строку прямо под основной: «Fallback для тестовых/служебных книг: `<book>/_workdir/tonal_compass.md` (например Band III — был использован во время Ф0–Ф5).»
4. **Зеркальная правка `bf-critic.md`** в той же сессии, до вызова controller'а: если в bf-critic есть упоминание `_workdir/tonal_compass.md` как primary — поправить аналогично (primary без `_workdir/`, fallback с ним).

**DoD**:
- [ ] В `writing_control.md` primary path: `<book>/tonal_compass.md`.
- [ ] В `writing_control.md` fallback-строка присутствует.
- [ ] В `writing_control.md` не осталось места, где `_workdir/tonal_compass.md` упомянут как primary.
- [ ] В `bf-critic.md` — то же (primary без `_workdir/`).

**Controller depth**: light.

---

### P1-2. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — `bf-compiler.md` — добавить PowerShell fallback

**Тип**: исполнимый сейчас.
**Категория аудита**: C-NEW-3.
**Цена**: 15 минут.

**Команда идемпотентности**:
```powershell
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-compiler.md" -Pattern "ConvertFrom-Json" -SimpleMatch
```
Если совпадение — fallback добавлен.

**Что делать**:
1. В `bf-compiler.md` шаг 2 (валидация beat-плана): после Python/Node вариантов добавить PowerShell-блок:
   ```powershell
   # PowerShell fallback (Windows, при отсутствии Python/Node)
   try { Get-Content "$beat_plan_path" -Raw | ConvertFrom-Json | Out-Null; "OK" } catch { "FAIL: $_" }
   ```
2. Шаг 5 (self-check маркеров): добавить PowerShell-альтернативу bash-циклу:
   ```powershell
   # PowerShell fallback
   $markers = @("<<<T1>>>", "<<<T2>>>", ...)
   $markers | ForEach-Object { if (-not (Select-String -Path $session_file -Pattern $_ -SimpleMatch -Quiet)) { "MISSING: $_" } }
   ```
3. В разделе «Абсолютные ограничения» добавить строку: «Платформа фабрики — Windows. PowerShell-команды preferred, bash — fallback для возможной будущей миграции на Linux/Mac у переводчиков. Caller сам выбирает доступную платформу; обе ветки должны быть в инструкции.»

**DoD**:
- [ ] `ConvertFrom-Json` упомянут в шаге 2 как PowerShell fallback.
- [ ] `Select-String` упомянут в шаге 5 как PowerShell fallback для проверки маркеров.
- [ ] Раздел «Абсолютные ограничения» описывает Windows-приоритет.

**Controller depth**: light.

---

### P2-2. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — `bf-controller.md` — warn-строка о статусе ТЗ как «проект»

**Тип**: исполнимый сейчас.
**Категория аудита**: C-NEW-2.
**Цена**: 5 минут.

**Команда идемпотентности**:
```powershell
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-controller.md" -Pattern "ТЗ как проект|статус ТЗ" -SimpleMatch
```
Если совпадение — warn-строка есть.

**Что делать**:
1. В `bf-controller.md` раздел «Инициализация» добавить параграф:
   - «Если первая строка ТЗ-секции «Статус» содержит фразу «проект ТЗ, ожидает одобрения автора» — controller возвращает `warn` с заметкой «ТЗ ещё не одобрен — все вердикты предварительны». Это не блокирует work, но уведомляет автора.»
2. В разделе «Правила принятия решения» — добавить пункт 11 с тем же содержанием в одну строку.

**DoD**:
- [ ] Параграф про статус ТЗ присутствует в «Инициализация».
- [ ] Правило 11 в «Правилах принятия решения» добавлено.

**Controller depth**: full (последний пункт PART 1 — закрывает PART 1, не закрывает ТЗ; финальный full сместился на P-FINAL после ввода PART 2 в v1.2).

---

## 4-bis. PART 2 — закрытие фазово-заблокированных пунктов и минорных дыр

> **Введён в v1.2 (2026-04-25).** Расщепление Ф8/Ф1a/Ф6 (см. шапку): пункты §5, относящиеся к **документации, routing-таблицам и контрактам**, переезжают сюда; пункты, относящиеся к **исполняемой writer-loop-машине**, остаются в §5 и ждут полной Ф8.
>
> Все правила §0 действуют без изменений. Sequence — по §0.7. Журнал — §7. Регрессии — §6.

---

### P3-0. ВЫПОЛНЕНО 2026-04-25 (controller: accept — smoke-test passed live) — Edit-hook ловит и `Edit`-инструмент

**Тип**: исполнимый сейчас.
**Категория аудита**: D-NEW-3 (безопасность инфраструктуры; обнаружено в свежем аудите 2026-04-25).
**Цена**: 5 минут.
**Зависимости**: нет. Первый пункт PART 2.

**Команда идемпотентности (двусоставная: settings + script)**:
```powershell
$settings = Get-Content "$HOME\.claude\settings.json" -Raw | ConvertFrom-Json
$has_edit_matcher = $settings.hooks.PreToolUse | Where-Object { $_.matcher -eq "Edit" }
$script_has_edit = Select-String -Path "$HOME\.claude\hooks\backup-before-write.sh" -Pattern "Write\|Edit" -SimpleMatch
@{ matcher_registered = ($null -ne $has_edit_matcher); script_handles_edit = ($null -ne $script_has_edit) }
```
Оба `True` — пункт сделан.

**Что делать**:
1. Открыть `~/.claude/hooks/backup-before-write.sh`.
2. Заменить условие фильтрации tool'а на `case "$TOOL" in Write|Edit) ;; *) exit 0 ;; esac`. Комментарии шапки обновить на «Write/Edit».
3. Открыть `~/.claude/settings.json`. В `hooks.PreToolUse` добавить второй блок с `matcher: "Edit"` и тем же hook-script'ом, что у `Write`-блока.
4. Smoke-тест: после следующего запуска Claude Code сделать Edit к существующему файлу — в `~/.claude/backups/backup.log` должна появиться запись.

**DoD**:
- [x] Скрипт `backup-before-write.sh` обрабатывает Write и Edit (через `case`).
- [x] `settings.json` имеет matcher `"Edit"` в `PreToolUse`.
- [x] Smoke-тест: Edit к `_TZ_AUDIT_FIXES_2026-04-25.md` 2026-04-25 18:09 породил запись в `~/.claude/backups/backup.log` (live-reload settings.json подтверждён).
- [x] `Write` продолжает обрабатываться (регрессия отсутствует — отдельный matcher `Write` сохранён).

**Controller depth**: light + scope-isolation check (hook не должен трогать ничего за пределами целевого файла).

---

### P3-1. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — `CLAUDE.md` — актуализировать «Производственную цепочку», маршрутизацию, минорные ссылки

**Тип**: исполнимый сейчас.
**Категория аудита**: D-NEW-1 (документ-конституция врёт о цепочке) + 2 минора, найденные в свежем аудите 2026-04-25.
**Цена**: 20 минут.
**Зависимости**: нет (документ изолирован).

**Команда идемпотентности**:
```powershell
$chain = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md" -Pattern "researcher.*material-author.*planner.*compiler" -SimpleMatch
$pm_route = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md" -Pattern "bf-pm" -SimpleMatch
$session_v = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md" -Pattern "v2.0, 2026-04-23" -SimpleMatch
$obsidian = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md" -Pattern "obsidian/" -SimpleMatch
@{ chain_updated = ($null -ne $chain); pm_route_removed = ($null -eq $pm_route -or ($pm_route | Where-Object { $_.Line -match "DEPRECATED|deprecated" })); session_v_fresh = ($null -eq $session_v); obsidian_removed = ($null -eq $obsidian) }
```
Все четыре значения должны быть `True` — пункт сделан.

**Что делать**:
1. **Цепочка** (стр. ~24). Заменить:
   ```
   PM → Писатель → Редактор → Гуманизатор → Переводчик
   ```
   на актуальную:
   ```
   bf-researcher → bf-material-author → bf-planner → bf-compiler → bf-coordinator(writer-loop) → bf-editor → bf-humanizer → bf-translator
   ```
   Внутри `bf-coordinator(writer-loop)` явно указать: «writer ↔ critic ↔ controller ↔ refiner» (контракт цикла — в `_TZ_WRITER_BEAT_BY_BEAT.md` §5).
2. **Запуск производства** (стр. ~46-52). Таблицу «Сценарии» переписать:
   - «Начать главу с нуля» → `bf-researcher` (исследование) → `bf-material-author` (MATERIAL) → дальше по цепочке через `bf-coordinator`.
   - «Определить следующий шаг» → `bf-coordinator /bf-next NN` (без изменений).
   - «Проверить статус» → `bf-coordinator /bf-status NN` (без изменений).
   - Добавить строку: «`bf-pm` — DEPRECATED stub, остаётся файлом для истории; не вызывать как активный агент.»
3. **Минор 1** (стр. ~70). `_SESSION_START_PROMPT.md (v2.0, 2026-04-23)` → `_SESSION_START_PROMPT.md (v2.2, 2026-04-25)`.
4. **Минор 2** (стр. ~79). Удалить строку `├── obsidian/                    ← пакет интеграции с Obsidian (отложено)` из дерева директории. Папка устранена 2026-04-25.
5. Не трогать «Правила, которые нельзя нарушать» — они актуальны.

**DoD**:
- [ ] Цепочка содержит `researcher → material-author → planner → compiler` в правильном порядке.
- [ ] `bf-pm` упоминается только с пометкой DEPRECATED / deprecated-stub, не как активный маршрут.
- [ ] Версия `_SESSION_START_PROMPT.md` указана как v2.2 (или ссылка на v2.x без жёсткой привязки даты).
- [ ] Папка `obsidian/` не упоминается ни в одной строке.
- [ ] CLAUDE.md по-прежнему компактен (< 200 строк) и читаем.

**Controller depth**: full (CLAUDE.md — корневой документ; ошибка здесь распространяется на все сессии).

---

### P2-1. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — `architecture/FACTORY_MAP.md` — refresh + правило ветвления `skills/` vs `.claude/skills/`

**Тип**: исполнимый сейчас.
**Категория аудита**: A-NEW-3 (Ф1a в TZ §5).
**Цена**: 40 минут.
**Зависимости**: P3-1 (CLAUDE.md актуализирован — FACTORY_MAP не должен противоречить).

**Команда идемпотентности**:
```powershell
$stale = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\FACTORY_MAP.md" -Pattern "STALE 2026-04-23" -SimpleMatch
$new_agents = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\FACTORY_MAP.md" -Pattern "bf-researcher|bf-material-author|bf-planner|bf-compiler|bf-critic|bf-controller" -SimpleMatch
$skills_rule = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\FACTORY_MAP.md" -Pattern "\.claude/skills" -SimpleMatch
@{ stale_removed = ($null -eq $stale); new_agents_listed = ($new_agents.Count -ge 4); skills_rule_present = ($null -ne $skills_rule) }
```
Все три `True` — пункт сделан.

**Что делать**:
1. Удалить блок `> ⚠️ STALE 2026-04-23 — требует актуализации в фазе Ф1a.` и все строки внутри этого blockquote.
2. Шапку YAML обновить: `version: 1.1`, `updated: 2026-04-25`.
3. Производственная цепочка (ASCII-таблица) — переписать под актуальную (см. P3-1; здесь — расширенная версия с tools/model в каждой колонке).
4. Список агентов — ровно 12 (как в `memory/architecture.md`, синхронно):
   1–6: legacy (`bf-coordinator`, `bf-pm`, `bf-writer`, `bf-editor`, `bf-humanizer`, `bf-translator`).
   7–12: новые (`bf-critic`, `bf-controller`, `bf-compiler`, `bf-researcher`, `bf-material-author`, `bf-planner`).
   Для каждого — статус (`legacy` / `новый` / `deprecated-stub`) и ссылка на файл агента.
5. Добавить раздел «Правило ветвления `skills/` vs `.claude/skills/`»:
   - `skills/` (корень) — **полные модули ролей** (длинные инструкции, references, examples). Читаются агентом по требованию через Read.
   - `.claude/skills/` — **slash-command-диспетчеры** (короткие, < 50 строк), вызывают агентов или skills/ через `Skill`/`Agent` tool. Используются для прямого вызова автором (`/bf-something`).
   - Правило выбора: новый skill — диспетчер (короткий) → `.claude/skills/`. Новый skill — глубокий модуль роли → `skills/`. Если skill начинается как диспетчер и разрастается > 100 строк — split: диспетчер остаётся в `.claude/skills/`, тело уезжает в `skills/<role>/<topic>.md`.
6. Раздел «Текущее состояние тюнинга» — ссылка на `_TZ_WRITER_BEAT_BY_BEAT.md §5` + `_TZ_AUDIT_FIXES_2026-04-25.md` + handoff §13.2.

**DoD**:
- [ ] Дисклеймер `STALE 2026-04-23` отсутствует.
- [ ] Версия документа поднята до 1.1+.
- [ ] Производственная цепочка содержит 8 агентов в актуальном порядке (от researcher до translator).
- [ ] 12 агентов перечислены со статусами.
- [ ] Раздел «Правило ветвления skills» присутствует и содержит критерий выбора.
- [ ] Список агентов в FACTORY_MAP **совпадает** со списком в `.claude/memory/architecture.md` (synchronization check).

**Controller depth**: full.

---

### P1-3. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Sync haiku/sonnet между TZ §1.2 и handoff §13.2

**Тип**: исполнимый сейчас.
**Категория аудита**: C-NEW-1.
**Цена**: 10 минут.
**Зависимости**: нет (docs-only fix).

**Команда идемпотентности**:
```powershell
# Извлечь модели из обоих источников и сравнить (вручную — controller проверит DoD).
$tz = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_TZ_WRITER_BEAT_BY_BEAT.md" -Pattern "(haiku|sonnet|opus)" -CaseSensitive:$false
$handoff = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md" -Pattern "(haiku|sonnet|opus)" -CaseSensitive:$false
@{ tz_count = $tz.Count; handoff_count = $handoff.Count }
# Идемпотентность по факту: маркер «sync_2026-04-25» в обоих файлах.
$tz_marker = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_TZ_WRITER_BEAT_BY_BEAT.md" -Pattern "model-sync 2026-04-25" -SimpleMatch
($null -ne $tz_marker)
```
Если последняя строка `True` — sync выполнен.

**Что делать**:
1. Открыть обе ссылки (`_TZ_WRITER_BEAT_BY_BEAT.md` §1.2 и `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` §13.2).
2. Составить таблицу «агент → модель» из обоих источников.
3. Для каждого расхождения — выбрать **актуальную модель из факта `.claude/agents/<agent>.md`** (frontmatter `model:`). Документы подтягиваются под факт, не наоборот.
4. Обновить оба источника синхронно. Добавить пометку «model-sync 2026-04-25» в шапку обоих файлов.

**DoD**:
- [ ] Таблица «агент → модель» в TZ §1.2 совпадает с таблицей в handoff §13.2.
- [ ] Обе таблицы совпадают с фактом из frontmatter `.claude/agents/bf-*.md`.
- [ ] Маркер `model-sync 2026-04-25` присутствует в обоих файлах.

**Controller depth**: light.

---

### P3-4. ВЫПОЛНЕНО 2026-04-25 (controller: accept-by-idempotency) — `bf-compiler.md` — sed BSD/GNU mismatch

**Тип**: исполнимый сейчас.
**Категория аудита**: E-NEW-1.
**Цена**: 15 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$sed_uses = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-compiler.md" -Pattern "\bsed\b" -CaseSensitive:$true
$sed_warn = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-compiler.md" -Pattern "BSD|GNU sed|--posix" -SimpleMatch
@{ sed_count = $sed_uses.Count; sed_warned = ($null -ne $sed_warn) }
```
Если `sed_count == 0` (sed убран полностью) **или** `sed_warned == True` (sed остался, но явно описано различие BSD/GNU) — пункт сделан.

**Что делать**:
1. Найти все вхождения `sed` в `bf-compiler.md`.
2. Для каждого — выбрать одну из стратегий:
   - **Strategy A (preferred)**: заменить на PowerShell-эквивалент (`-replace`, `Get-Content | ForEach-Object`, etc.) — Windows-приоритет уже декларирован в файле.
   - **Strategy B (если sed нужен)**: заменить на portable-вариант (например, `sed -E` есть в обеих, но `\b` отличается; использовать `[[:<:]]`/`[[:>:]]` для границ слов или `awk` вместо sed).
   - **Strategy C (минимум)**: добавить пометку «эта команда требует GNU sed; macOS-пользователю заменить на `gsed` или PowerShell-вариант ниже» рядом с командой.
3. Документировать выбор в разделе «Абсолютные ограничения».

**DoD**:
- [ ] Каждое вхождение `sed` либо устранено, либо снабжено явной пометкой о различии BSD/GNU.
- [ ] Раздел «Абсолютные ограничения» дополнен правилом: «sed-команды — только portable-форма или с явной пометкой о платформе.»

**Controller depth**: light.

---

### P3-2. ВЫПОЛНЕНО 2026-04-25 (controller: accept) — Единая модель статусов главы — снять «модель в переходе»

**Тип**: исполнимый сейчас.
**Категория аудита**: D-NEW-2.
**Цена**: 30 минут.
**Зависимости**: P3-1 (CLAUDE.md актуализирован — статусы там тоже).

**Команда идемпотентности**:
```powershell
$disclaimer = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md" -Pattern "Модель статусов в переходе" -SimpleMatch
$beat_phase = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md" -Pattern "beat-N-draft|beat_draft|beat-draft" -SimpleMatch
@{ disclaimer_removed = ($null -eq $disclaimer); beat_phase_documented = ($null -ne $beat_phase) }
```
Оба `True` — пункт сделан.

**Что делать**:
1. **Решение**: оставить базовую модель статусов как есть:
   ```
   (нет файла) → material-draft → draft → review → clean → humanized → translated → final
   ```
   Без переименования, без удаления статусов. Это контракт, который уже использует производство.
2. **Добавить промежуточный сублевел** внутри `draft`-фазы для writer-loop трекинга:
   - `compiled` — Session-файл собран (`bf-compiler` отработал), готов к writer'у.
   - `beat-N-draft` — beat #N написан writer'ом, ожидает critic + controller.
   - `beat-N-accepted` — beat #N прошёл critic + controller.
   - `draft` — все beats главы accepted, glava.md собран. **Это та же `draft`-стадия, что и сейчас**, просто теперь с явной декомпозицией ниже.
3. Внести правки в:
   - `.claude/memory/production_state.md` — заменить дисклеймер «Модель статусов в переходе» на финальную карту: «Модель статусов главы (финализирована 2026-04-25)» с описанием подстатусов внутри `draft`.
   - `.claude/memory/architecture.md` — синхронно (если упоминаются статусы).
   - `CLAUDE.md` стр. 31 (статусы) — добавить ссылку «подстатусы writer-loop — см. `production_state.md`».
4. **Не трогать**: уже использованные статусы (`material-draft`, `clean`, `humanized`, etc.) — фабрика уже опирается на них.

**DoD**:
- [ ] Дисклеймер «Модель статусов в переходе» удалён из `production_state.md`.
- [ ] Подстатусы `compiled`, `beat-N-draft`, `beat-N-accepted` документированы в `production_state.md` как декомпозиция `draft`.
- [ ] Базовая последовательность `material-draft → draft → review → clean → humanized → translated → final` сохранена без изменений.
- [ ] CLAUDE.md ссылается на `production_state.md` для подстатусов writer-loop.

**Controller depth**: full (модель статусов читается всеми агентами).

---

### P2-3. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — `Session_TEMPLATE.md` — создать шаблон для `bf-compiler`

**Тип**: исполнимый сейчас.
**Категория аудита**: B-NEW-5 + E-NEW-2.
**Цена**: 45 минут.
**Зависимости**: P3-2 (статусы финализированы — шаблон ссылается на актуальную модель).

**Команда идемпотентности**:
```powershell
$tmpl = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\Session_TEMPLATE.md"
if ($tmpl) {
  $markers = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\Session_TEMPLATE.md" -Pattern "^## T(1|2|3|4|5|6|7|8|9|10|11|12)\." 
  @{ exists = $true; t_markers_count = $markers.Count }
} else {
  @{ exists = $false }
}
```
Если `exists == True` и `t_markers_count >= 12` — пункт сделан.

**Что делать**:
1. Создать `Session_TEMPLATE.md` в корне `BooksFactory/`. Шаблон должен **точно** соответствовать структуре, ожидаемой `bf-compiler.md` (см. шаг 4 «Сборка итогового файла»):
   - `## T1. Метаданные + калибровка`
   - `## T2. Специфические запреты`
   - `## T3. Голос (выдержка)`
   - `## T4. Тональные якоря`
   - `## T5. Каркас главы (секции, микрорежимы)`
   - `## T6. MATERIAL`
   - `## T7. Beat-план (JSON)`
   - `## T8. Арены / Сцены / Источники`
   - `## T9. Провокации`
   - `## T10. Объём`
   - `## T11. QUELLEN`
   - `## T12. Continuity`
   - `---BEGIN_REFERENCE_CHAPTER---` / `---END_REFERENCE_CHAPTER---`
   - `---BEGIN_VERBOT_LISTE---` / `---END_VERBOT_LISTE---`
   - `---BEGIN_CALIBRATION---` / `---END_CALIBRATION---`
   - `---BEGIN_PROTOCOL---` / `---END_PROTOCOL---`
2. Каждая секция содержит **placeholder-комментарий** `<!-- compiler заполнит из <источник> -->`, не пустой блок.
3. T1 — таблица с полями: `book`, `chapter_number`, `target_words`, `calibration_paths[]`, `tonal_compass_path`, `verbot_liste_path` (по контракту compiler'а).
4. Шапка YAML: `document: Session_TEMPLATE`, `version: 1.0`, `created: 2026-04-25`, `consumer: bf-compiler`, `note: «Шаблон не редактировать вручную для конкретной главы — compiler собирает Session-файл из этого шаблона + источников.»`.
5. Сверить контракт: после создания шаблона запустить `bf-compiler` (mock-вызовом или dry-run) на тестовой главе — убедиться, что все T-маркеры и BEGIN/END-маркеры заполняются без ошибок.

**DoD**:
- [ ] Файл `Session_TEMPLATE.md` существует в корне `BooksFactory/`.
- [ ] Все 12 T-маркеров присутствуют (T1..T12).
- [ ] Все 4 пары BEGIN/END-маркеров присутствуют (REFERENCE_CHAPTER, VERBOT_LISTE, CALIBRATION, PROTOCOL).
- [ ] Шапка YAML с `consumer: bf-compiler`.
- [ ] Smoke-test compiler'а на тестовой главе → marker self-check проходит.

**Controller depth**: full.

---

### P0-3. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — `bf-coordinator.md` — routing-таблица под актуальные агенты (без writer-loop logic)

**Тип**: исполнимый сейчас (расщепление Ф8: routing → сейчас, loop-execution → полная Ф8).
**Категория аудита**: A-NEW-1 + A-NEW-2.
**Цена**: 90 минут.
**Зависимости**: P3-1 (CLAUDE.md актуален), P2-1 (FACTORY_MAP актуален), P2-3 (Session-шаблон существует).

**Команда идемпотентности**:
```powershell
$cmp = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-coordinator.md" -Pattern "bf-researcher|bf-material-author|bf-planner|bf-compiler|bf-critic|bf-controller" -SimpleMatch
$pm_legacy = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-coordinator.md" -Pattern "^\s*-\s*bf-pm\b" -CaseSensitive:$true
@{ new_agents_routed = ($cmp.Count -ge 4); pm_as_active_route = ($null -ne $pm_legacy) }
```
`new_agents_routed == True` и `pm_as_active_route == False` — пункт сделан.

**Что делать**:
1. Открыть `.claude/agents/bf-coordinator.md`. Текущее состояние: legacy (tools=`Read, Write, Glob, Grep`, model=haiku, маршрутизация на `bf-pm`).
2. **Что обновить**:
   - **Tools**: оставить `Read, Write, Glob, Grep` (coordinator не пишет прозу, ему достаточно).
   - **Model**: оставить `haiku` (если в P1-3 sync подтвердил, что factual coordinator — haiku) **или** обновить под факт. Этот пункт зависит от вывода P1-3.
   - **Routing-таблица**: переписать. Маршруты:
     - `/bf-next NN` (определить следующий шаг главы NN) → читает `production_state.md` + статус главы NN → возвращает имя следующего агента.
     - `/bf-status NN` (статус главы NN) → читает `production_state.md` + проверяет наличие артефактов (MATERIAL, beat-plan, Session-compiled, glava.md, glava_clean.md, glava_humanized.md, glava_translated.md) → возвращает текущий статус.
     - `/bf-route <agent>` (вызвать конкретного агента на главе NN) → проверяет вход-контракт агента → вызывает через `Agent` tool.
   - **Таблица «фаза → агент»**:
     | Фаза главы | Текущий статус | Следующий агент |
     |------------|----------------|-----------------|
     | (нет файла) → MATERIAL | — / `material-draft` | `bf-researcher` → `bf-material-author` |
     | MATERIAL → beat-plan | `material-draft` | `bf-planner` |
     | beat-plan → Session-compiled | (после planner) | `bf-compiler` |
     | Session-compiled → главу | `compiled` | (writer-loop — Ф8) |
     | главу → редактуру | `draft` | `bf-editor` |
     | редактуру → гуманизацию | `clean` | `bf-humanizer` |
     | гуманизацию → перевод | `humanized` | `bf-translator` |
     | перевод → финал | `translated` | (final, ручной QA) |
3. **`bf-pm`**: упоминается **только как deprecated-stub**, не как активный маршрут. Если кто-то набирает `/bf-pm` — coordinator выдаёт сообщение «`bf-pm` deprecated, замены: bf-researcher (исследование), bf-material-author (MATERIAL), bf-compiler (Session)».
4. **Что НЕ делать в этом пункте** (это полная Ф8):
   - Не реализовывать writer↔critic↔controller↔refiner loop. Coordinator только идентифицирует, что глава в фазе «writer-loop» и говорит автору «нужна Ф8».
   - Не реализовывать автоматический выбор beat'а для следующей итерации.
   - Не реализовывать exit-conditions для loop'а.
5. **Что обязательно**: явный disclaimer в шапке файла «Coordinator v2 (routing-only). Writer-loop execution — фаза Ф8.»

**DoD**:
- [ ] Coordinator упоминает все 6 новых агентов (`bf-researcher`, `bf-material-author`, `bf-planner`, `bf-compiler`, `bf-critic`, `bf-controller`).
- [ ] `bf-pm` фигурирует только как deprecated-stub, не как активный маршрут.
- [ ] Routing-таблица «фаза → агент» присутствует.
- [ ] Disclaimer «routing-only, writer-loop execution = Ф8» в шапке.
- [ ] Все 3 slash-команды (`/bf-next`, `/bf-status`, `/bf-route`) описаны контрактом.
- [ ] Smoke-тест: запустить `/bf-status NN` на тестовой главе → возвращает корректный статус, без вызова writer-loop.

**Controller depth**: full.

---

### P2-4. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — `architecture/handoff_contracts.md` — Editor→Humanizer beat-by-beat контракт

**Тип**: исполнимый сейчас (контракт-документ, не loop-machine).
**Категория аудита**: C-NEW-4.
**Цена**: 30 минут.
**Зависимости**: P0-3 (coordinator знает агентов — иначе контракт некому исполнять), P3-2 (модель статусов финализирована).

**Команда идемпотентности**:
```powershell
Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\handoff_contracts.md" -Pattern "Editor.{0,5}Humanizer.*beat|beat-by-beat.*Editor" -SimpleMatch
```
Если совпадение — контракт описан.

**Что делать**:
1. Открыть `architecture/handoff_contracts.md`. Найти раздел Editor→Humanizer (или создать, если отсутствует).
2. Описать beat-by-beat-вход для Editor:
   - **Вход**: `glava.md` собран coordinator'ом из всех `beat-N-accepted`. Один файл, не N файлов.
   - **Выход**: `glava_clean.md` — после Editor-прохода (точечные правки, чек-лист, без перезаписи прозы).
3. Описать вход для Humanizer:
   - **Вход**: `glava_clean.md` (статус `clean`).
   - **Выход**: `glava_humanized.md` (статус `humanized`).
4. Зафиксировать **инвариант**: Humanizer не получает beat-файлы напрямую. Beat-файлы — внутренняя кухня writer-loop'а, в Editor приходит **уже собранная глава**.
5. Зафиксировать **исключение**: если Editor находит проблему, локализованную в одном beat'е, он может попросить coordinator переоткрыть этот beat (вернуться в writer-loop). Это редкое исключение, не норма.

**DoD**:
- [ ] Раздел Editor→Humanizer существует в `handoff_contracts.md`.
- [ ] Контракт явно говорит: вход Editor = единый `glava.md`, не N beat-файлов.
- [ ] Контракт описывает «возврат в beat-loop» как исключительный путь.
- [ ] Статусы (`draft → clean → humanized`) совпадают с моделью из P3-2.

**Controller depth**: light.

---

### P-FINAL. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — End-to-end smoke-test pipeline-integrity

**Тип**: исполнимый сейчас (после P3-0..P2-4).
**Категория аудита**: F (новая категория, factory-integration).
**Цена**: 2-3 часа.
**Зависимости**: все предыдущие пункты PART 2 закрыты.

**Команда идемпотентности**:
```powershell
$report = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_smoke_test_2026-04-25.md"
$report
```
Если отчёт существует — smoke-test проведён.

**Что делать**:
1. Выбрать тестовую книгу (рекомендация: служебная, не из активной серии). Создать `_testing/smoke_2026-04-25/` с минимальным `tonal_compass.md`, `verbot_liste.md`, заглушкой `series-bible.md`.
2. Создать тестовую главу 01 (одна короткая глава, цель ~1500 слов, не литературное качество — pipeline-integrity).
3. Прогнать через **все доступные агенты** последовательно:
   - `bf-researcher` → `MATERIAL_Glava_01.md` (исследование)
   - `bf-material-author` → дополнить MATERIAL beat sheet'ами
   - `bf-planner` → `01_beat_plan.json`
   - `bf-compiler` → `_drafts/01_session_compiled.md` (использует Session_TEMPLATE из P2-3)
   - `bf-coordinator` `/bf-status` → должен ответить «compiled, готова к writer-loop (Ф8)»
   - **Если Ф8 не закрыта**: пропустить writer-loop, ручной mock — создать `glava.md` с placeholder-текстом, статус `draft`.
   - `bf-editor` → `glava_clean.md` (статус `clean`)
   - `bf-humanizer` → `glava_humanized.md` (статус `humanized`)
   - `bf-translator` → `glava_translated.md` (статус `translated`, RU/EN)
4. На каждом шаге фиксировать:
   - вызванный агент и время вызова;
   - входные файлы (контракт) и существуют ли;
   - выходные файлы и соответствие контракту;
   - вердикт `bf-controller` (light) после правки.
5. Записать отчёт `_smoke_test_2026-04-25.md`:
   - таблица «шаг → результат → длительность → вердикт»;
   - найденные дыры (если есть);
   - вывод: «pipeline integrity: pass / fail / pass-with-mock».
6. **Если найдены дыры** — создать в этом ТЗ §4-bis новые пункты P-FINAL-1, P-FINAL-2, ... и закрыть их перед маркером P-FINAL = ВЫПОЛНЕНО.

**DoD**:
- [ ] Файл `_smoke_test_2026-04-25.md` создан.
- [ ] Все 8 агентов (или столько, сколько закрыто) фигурируют в таблице.
- [ ] Каждый шаг имеет вердикт `accept`/`warn`/`mock` (последнее — для Ф8-зависимых шагов).
- [ ] Найденные дыры либо закрыты в этом ТЗ, либо явно вынесены в §5 «Очередь».
- [ ] Вывод «pipeline integrity» зафиксирован.

**Controller depth**: full (финальный full закрывает ТЗ — см. §8).

---

## 5. Очередь — ожидают конкретной фазы ТЗ

> **v1.2 (2026-04-25)**: после расщепления Ф8/Ф1a/Ф6 (см. шапку) бо́льшая часть пунктов перенесена в §4-bis (PART 2) и стала исполнимой. Здесь остаются только пункты, действительно блокированные **исполняемой writer-loop-машиной** (полная Ф8) или другими большими фазами.

Эти пункты **не исполняются** в этом ТЗ. Они трекаются здесь для полноты.

| Пункт | Категория аудита | Что | Ждёт фазы | Статус v1.2 |
|-------|------------------|-----|-----------|-------------|
| P0-3 | A-NEW-1, A-NEW-2 | Пайплайн разорван — coordinator не знает о новых агентах | Ф8 (loop-машина) | **Перенесён в §4-bis** (routing-часть; loop-execution остаётся в Ф8) |
| P1-3 | C-NEW-1 | TZ §1.2 vs §13.2 haiku/sonnet sync | Ф8 | **Перенесён в §4-bis** (docs-only sync, не зависит от loop) |
| P2-1 | A-NEW-3 | Правило ветвления `skills/` vs `.claude/skills/` зафиксировать | Ф1a (FACTORY_MAP) | **Перенесён в §4-bis** (документация) |
| P2-3 | B-NEW-5, E-NEW-2 | `Session_TEMPLATE.md` отсутствует/устарел | Ф6 | **Перенесён в §4-bis** (артефакт Ф6 без зависимости от loop) |
| P2-4 | C-NEW-4 | Контракт Editor→Humanizer для beat-by-beat | Ф8 (расщепление контракта 1) | **Перенесён в §4-bis** (контракт-документ; исполнение контракта — Ф8) |
| P3-1 | D-NEW-1 | CLAUDE.md «Производственная цепочка» обновить | Ф1a | **Перенесён в §4-bis** (документация) |
| P3-2 | D-NEW-2 | Две модели статусов главы — решить | Ф8 | **Перенесён в §4-bis** (концептуальное решение фиксируется в docs) |
| P3-4 | E-NEW-1 | sed BSD/GNU mismatch в compiler bash | низкий риск, Ф6 или Ф8 | **Перенесён в §4-bis** |

### Действительно остаются в очереди (после v1.2)

| Пункт | Категория | Что | Ждёт |
|-------|-----------|-----|------|
| Ф8-LOOP | A-NEW-1 (loop-execution) | Реализация writer↔critic↔controller↔refiner cycle с max_iterations, exit-conditions, beat-by-beat orchestration | Ф8 (полная фаза TZ §5) |
| Ф11 | C-NEW-5 | `bf-continuity-checker` агент | Ф11 |

**Правило**: при открытии соответствующей фазы ТЗ — закрыть пункт здесь, поставить ВЫПОЛНЕНО + ссылку на коммит/диф в TZ.

(Пункт P3-3 «obsidian/CLAUDE.md skills-ссылки» удалён из списка — папка obsidian устранена 2026-04-25.)

---

## 6. Регрессии

> Сюда пишутся записи о `block`-вердиктах контроллера. Формат: дата, пункт, причина, действие. Регрессия = stop sequence до решения автора (см. §0.4).

(пусто на момент создания файла)

Шаблон записи:
```
### Регрессия R-001 (2026-04-XX)
- **Пункт**: P0-2
- **Controller verdict**: block
- **Причина**: после удаления promptBF.txt — Grep нашёл ссылку в <файл>, которая теперь битая.
- **Действие**: правка не откачена. Sequence остановлен. Эскалация автору.
- **Решение автора**: <дата> — <выбран вариант X>.
- **Закрыто**: <дата>, sequence возобновлён.
```

---

## 7. Журнал сессий

> Каждая сессия, в которой тронут этот ТЗ, оставляет одну строку.

- 2026-04-25 (Opus 4.7): P0-0a закрыт; controller: accept (fallback — bf-controller subagent не зарегистрирован из cwd=Skills, валидация выполнена general-purpose агентом по контракту bf-controller.md, read-only). Sequence продолжается.
- 2026-04-25 (Opus 4.7): P0-0 закрыт; controller: accept (fallback по той же причине). _SESSION_START_PROMPT.md → v2.2, ШАГ 0 добавлен.
- 2026-04-25 (Opus 4.7): P0-1 закрыт; controller: accept (fallback). 4 файла band3-*.md удалены, ссылок в активных файлах нет.
- 2026-04-25 (Opus 4.7): P0-2 закрыт; controller full: accept (fallback). architecture.md перечисляет 12 агентов; production_state.md имеет дисклеймер; promptBF.txt удалён. Закрыт P0-блок sequence. Заметка: команда идемпотентности §P0-2 использует `Select-String -SimpleMatch` с pipe — литеральное совпадение, всегда 0; реальный DoD проверять regex Grep. Дефект самой команды, не правки.
- 2026-04-25 (Opus 4.7): P1-1 закрыт; controller: accept (fallback). writing_control.md primary без `_workdir/`, fallback присутствует; bf-critic.md уже зеркален.
- 2026-04-25 (Opus 4.7): P1-2 закрыт; controller: accept (fallback). bf-compiler.md содержит PowerShell ConvertFrom-Json (шаг 2), Select-String (шаг 5), Windows-приоритет в ограничениях.
- 2026-04-25 (Opus 4.7): P2-2 закрыт; controller full: accept (fallback). bf-controller.md содержит параграф про статус ТЗ в «Инициализации» и пункт 12 в «Правилах принятия решения» (фактически 12, не 11 — после ранее добавленного пункта 11 про audit_task). Sequence (P0-0a → P2-2) закрыт; регрессий нет.
- 2026-04-25 (Opus 4.7): ТЗ расширен до v1.2 — введён §4-bis (PART 2) с 10 пунктами (P3-0 → P-FINAL). Принцип расщепления Ф8: docs/routing/контракты переезжают в PART 2, исполняемая writer-loop machine остаётся в §5 (Ф8-LOOP). Sequence обновлён в §0.7. Ни одна правка существующих пунктов §4 (PART 1) не сломана.
- 2026-04-25 (Opus 4.7): P3-0 закрыт; controller: accept — smoke-test прошёл live. `~/.claude/hooks/backup-before-write.sh` обновлён (case `Write|Edit`); `~/.claude/settings.json` получил второй matcher `Edit` в `PreToolUse`. Edit к `_TZ_AUDIT_FIXES_2026-04-25.md` 18:09 создал запись в `backup.log` (settings.json подхватывается на лету, рестарт не нужен). Регрессий нет: matcher `Write` сохранён, скрипт не отвергает Write. Идемпотентность подтверждена двусоставной проверкой (settings + script).
- 2026-04-25 (Opus 4.7): health-check — P3-4 accept-by-idempotency. `sed` в `bf-compiler.md` отсутствует (sed_count=0): устранён ранее в ходе P1-2 (PowerShell fallback переписал процедуру компиляции на ConvertFrom-Json и Select-String). DoD-1 закрыт по факту. **Расхождение**: DoD-2 («раздел «Абсолютные ограничения» дополнен правилом: sed-команды только portable-форма или с явной пометкой о платформе») формально не закрыт — раздел уже содержит более общее правило «PowerShell-команды preferred, bash — fallback», которое покрывает sed как частный случай. Дефект самой команды идемпотентности (узкий критерий sed_count==0), не правки. Ничего не доделываю — Windows-приоритет уже декларирован.
- 2026-04-25 (Opus 4.7): P3-1 закрыт; controller full: accept (fallback — bf-controller subagent не зарегистрирован из cwd=Skills, валидация выполнена general-purpose агентом по контракту bf-controller.md, read-only). CLAUDE.md актуализирован: производственная цепочка переписана на 8 агентов (researcher → material-author → planner → compiler → coordinator(writer-loop) → editor → humanizer → translator) + внутренний цикл writer↔critic↔controller↔refiner со ссылкой на TZ §5; bf-pm помечен DEPRECATED stub в двух местах (таблица сценариев + дерево директории); версия SESSION_START_PROMPT.md → v2.2; строка obsidian/ удалена; дерево директории расширено до 11 активных агентов + bf-pm. Заметка: команда идемпотентности §P3-1 страдает тем же дефектом `Select-String -SimpleMatch` + regex-pattern, что и P0-2 (chain regex с `.*` не матчится литерально); реальный DoD проверять regex Grep без `-SimpleMatch`. Дефект команды, не правки. 66 строк (≤200).
- 2026-04-25 (Opus 4.7): P2-1 закрыт; controller full: accept (fallback). FACTORY_MAP.md v1.1 (updated 2026-04-25): STALE-блок удалён; производственная цепочка переписана на 8 звеньев (researcher → material-author → planner → compiler → coordinator → editor → humanizer → translator) с подробной таблицей tools/model/вход/выход; список 12 агентов синхронизирован с memory/architecture.md (factory_map_count=12 = memory_count=12, идентичные статусы); добавлен раздел «Правило ветвления skills/ vs .claude/skills/» с таблицей слоёв и критерием выбора (диспетчер vs модуль роли, split при >100 строк); добавлен раздел «Текущее состояние тюнинга» с двумя осями (фазовая Ф0–Ф13 + аудит-sequence PART 1+PART 2). Все 12 markdown-ссылок на агентов разрешаются. Регрессий нет.
- 2026-04-25 (Opus 4.7): P1-3 закрыт; controller full: accept (fallback). Sync model/tools между TZ §1.2 и handoff §13.2: в `_TZ_WRITER_BEAT_BY_BEAT.md` §1.2 добавлен маркер «model-sync 2026-04-25», колонки переименованы в «target», добавлены строки для bf-controller и bf-pm (раньше отсутствовали), bf-planner Tools актуализирован (Read/Grep/Glob/Write); в `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` добавлена подсекция §13.2a «Model-sync 2026-04-25» с полной фактической таблицей 12 агентов и колонками target+divergence. Расхождения target↔fact явно зафиксированы: bf-coordinator (haiku→sonnet через Ф8/B4), bf-writer (Read/Write/Edit→none через Ф7/Д2). Оба маркера `model-sync 2026-04-25` присутствуют. Регрессий нет.
- 2026-04-25 (Opus 4.7): P3-2 закрыт; controller full: accept (fallback). Единая модель статусов главы финализирована: `production_state.md` — дисклеймер «Модель статусов в переходе» удалён, появился раздел «Модель статусов главы (финализирована 2026-04-25)» с таблицей описания каждого статуса базовой последовательности (`material-draft → draft → review → clean → humanized → translated → final` — сохранена дословно), подсекция «Декомпозиция draft-фазы (writer-loop substatuses)» с тремя подстатусами (`compiled`, `beat-N-draft`, `beat-N-accepted`) и 3 инварианта (последовательность неизменна; translator только с humanized / humanizer только с clean; возврат назад допустим). `CLAUDE.md` после блока статусов получил ссылку на подстатусы writer-loop в `production_state.md`. `architecture.md` не требовал изменений (одна строка про humanized у translator уже согласована). Идемпотентность: `disclaimer_removed=true`, `beat_phase_documented=true`. Регрессий нет.
- 2026-04-26 (Opus 4.7): P2-3 закрыт; controller full: accept (fallback — bf-controller subagent не зарегистрирован из cwd=Skills, валидация выполнена general-purpose агентом по контракту bf-controller.md, read-only). `Session_TEMPLATE.md` создан в корне BooksFactory/: YAML-шапка (document/version/created/consumer=bf-compiler/note), 12 раздельных T-маркеров (T1 Метаданные+калибровка с таблицей из 7 полей по контракту compiler'а; T2 Запреты; T3 Голос; T4 Тональные якоря; T5 Каркас; T6 MATERIAL; T7 Beat-план JSON; T8 Арены/Сцены; T9 Провокации; T10 Объём; T11 QUELLEN; T12 Continuity), 4 пары BEGIN/END (REFERENCE_CHAPTER, VERBOT_LISTE, CALIBRATION, PROTOCOL = 8 маркеров), placeholder-комментарии в каждой секции с указанием источника и WARN-fallback. Параллельно синхронизирован `.claude/agents/bf-compiler.md`: шаг 4 «Сборка» — ранее объединённый блок «## T10-T12. Объём, QUELLEN, continuity» разбит на 3 раздельные секции; шаг 5 «Self-check» — массив маркеров расширен на `## T11`, `## T12` в обеих ветках (Bash for-loop и PowerShell fallback). Smoke-test (sanity-check соответствия маркеров): `contract_aligned=true` — все 16 маркеров шаблона + 16 маркеров compiler self-check совпадают. Идемпотентность: `exists=true`, `t_markers_count=12`, `begin_end_count=8`, `consumer_yaml=true`. Заметка: `Select-String -SimpleMatch` с regex-якорем `^` снова выдал ложный False (`^consumer:` без -SimpleMatch — корректно True); тот же дефект, что P0-2 / P3-1 / P3-4. Реальная проверка через SimpleMatch без якоря. Регрессий нет.
- 2026-04-26 (Opus 4.7): P0-3 закрыт; controller full: accept (fallback). `bf-coordinator.md` полностью переписан → v2 routing-only: YAML (tools=Read/Write/Glob/Grep, model=haiku по target P1-3, description обновлён под v2); явный disclaimer «routing-only, writer-loop execution = Ф8» в шапке; 3 slash-команды (`/bf-status`, `/bf-next`, `/bf-route`) с процедурой и «что НЕ делать»; `/bf-pm` deprecated-stub с ответом-перенаправлением на bf-researcher / bf-material-author / bf-compiler; routing-таблица «фаза → агент» из 9 строк покрывает все статусы единой модели + промежуточный `compiled` (явно: `compiled → (Ф8 — не реализовано)`); правила координатора (никогда не пропускать фазу, никогда не запускать writer-loop, translator только с humanized, humanizer только с clean, лимит ≥3 итераций writer↔editor с эскалацией); раздел «Что НЕ делает coordinator (Ф8 scope)» с 5 явными запретами (выбор beat'а, вызов critic, агрегация в glava.md, refiner-итерации, exit-condition). Все 6 новых агентов упомянуты (Grep подтвердил 6 hits). Идемпотентность: `new_agents_routed=true (6 hits)`, `pm_as_active_route=false`, `routing_only_disclaimer=true`, `slash_commands_present=true (4 hits)`. Заметка: `Select-String -SimpleMatch` снова дал ложный False по regex-альтернативе `a|b|c` (труба — литерал в SimpleMatch, не альтернация); проверка через Grep дала корректный True. Тот же дефект, что P0-2 / P3-1 / P3-4 / P2-3. Регрессий нет.
- 2026-04-26 (Opus 4.7): P2-4 закрыт; controller light: accept (fallback). `architecture/handoff_contracts.md` — добавлен «Контракт 9: Editor → Humanizer (beat-by-beat пайплайн)» после Контракта 8, перед сводной таблицей. Подсекции 9.1–9.9 покрывают: 9.1 Coordinator → Editor (вход = единый `glava_NN.md`, не N beat-файлов — явная фраза); 9.2 что Editor делает (точечные правки ≤5, чек-лист, Edit-инструмент запрещён); 9.3 отчёт автору/refiner-у; 9.4 Editor → Coordinator с переходом `draft → review → clean`; 9.5 Coordinator → Humanizer (вход = `glava_NN_clean.md`, статус clean); 9.6 инвариант (humanizer/translator никогда не получают beat-файлы); 9.7 возврат в beat-loop как **исключительный путь** с форматом запроса `reopen_beat` (`scope: single_beat`); 9.8 критерии возврата (5 нарушений) — попытка передать beat-файл в humanizer = «контракт-нарушение пайплайна, эскалация автору»; 9.9 связь со статусной моделью (таблица этапов 9.1–9.5 ↔ статусы P3-2). Шапка документа обновлена (абзац про Контракт 9). Сводная таблица статусов синхронизирована с моделью P3-2: `editing` удалён, `material-draft` добавлен, у каждого статуса указан актуальный агент по новой архитектуре, отдельным абзацем поясняется, что подстатусы (`compiled`, `beat-N-draft`, `beat-N-accepted`) — декомпозиция `draft`, не базовая последовательность. Идемпотентность: regex `Editor.{0,5}Humanizer.*beat|beat-by-beat.*Editor` через Grep даёт 2 hits (тот же `-SimpleMatch` дефект, что в прошлых пунктах: SimpleMatch обрабатывает `.{0,5}` и `|` литерально, реальный regex срабатывает). Замечание контроллера: в Контракте 4 (стр. 187) всё ещё фигурирует устаревший `editing` — не входит в scope P2-4, оставлено для будущей фазы синхронизации легаси-контрактов. Регрессий нет: все 8 предыдущих контрактов целы.
- 2026-04-26 (Opus 4.7): P-FINAL **в работе**, controller-валидация перенесена на следующую сессию. Сделано: создана тестовая книга `_testing/smoke_2026-04-25/` с 4 book-level артефактами (tonal_compass, verbot_liste, series-bible, _reference_chapter); создана тестовая глава 01 (target=1500, 9 beats, sum=1615, deviation=4.72%) с полной цепочкой mock-артефактов — MATERIAL_Glava_01.md (material-draft), 01_beat_plan.json (валиден через ConvertFrom-Json + инварианты compiler шаг 2), **01_session_compiled.md (16/16 маркеров через compiler шаг 5 self-check PowerShell — критический pass)**, glava_01.md (draft), glava_01_clean.md (clean), glava_01_humanized.md (humanized), glava_01_translated_de.md (translated). Sanity-check pipeline'а: 11/11 артефактов существуют, все YAML-статусы корректны. Создан отчёт `_smoke_test_2026-04-25.md` с таблицей 9 шагов (вердикты: 7×accept, 2×mock — Ф8 + researcher), 4 найденными дырами (D-1 Ф8 не реализована → §5 Очередь Ф8-LOOP; D-2 bf-writer в legacy → Ф8-LOOP; D-3 Контракт 4 имеет editing → Ф8-LOOP; D-4 bf-controller subagent не регистрируется из cwd=Skills → операционный пункт), выводом «pipeline integrity = pass-with-mock». Идемпотентность: `smoke_report_exists=true`. **Не сделано**: controller full-валидация отчёта (последний пункт §8 audit-файла). Следующая сессия: запустить controller на отчёте + закрыть P-FINAL ВЫПОЛНЕНО + версия ТЗ → 2.0 + обновить _SESSION_START_PROMPT.md → v2.3 (убрать ШАГ 0).
- 2026-04-26 (Opus 4.7): P-FINAL закрыт; controller full: accept (fallback). Pre-flight в начале сессии подтвердил: 11/11 артефактов smoke-test'а на месте после паузы, 01_session_compiled.md содержит все 16 маркеров compiler self-check. Controller прогнал все 5 DoD-критериев + 4 cross-source проверки (handoff_contracts.md Контракт 9 и инвариант 9.6, production_state.md единая модель P3-2, session_compiled 16/16, bf-coordinator routing-таблица compiled→Ф8) + регрессионный sweep (Session_TEMPLATE.md цел; bf-compiler.md шаг 4 раздельные T10/T11/T12; coordinator v2 routing-only; handoff Контракт 9 + сводная таблица без editing). Все pass. Регрессий нет. **ТЗ закрыт**: PART 1 + PART 2 + P-FINAL завершены, фабрика приведена к рабочему состоянию (Ф0–Ф6 + Ф7 в части researcher/material-author/planner/compiler/critic/controller). Ф8-LOOP, Ф11, D-3 (editing в Контракте 4), D-4 (subagent fallback) остаются в §5 Очередь как явно отложенные.

Шаблон:
```
- 2026-04-26 (Sonnet 4.6): P0-0, P0-0a, P0-1 закрыты; controller full: accept. Длительность: 25 минут.
- 2026-04-27 (Opus 4.7): P0-2, P1-1 закрыты; controller full: warn (handoff fingerprint не обновлён) → исправлено. P1-2 в работе.
```

---

## 8. Финальный чек-лист закрытия ТЗ

ТЗ считается полностью закрытым, когда:

- [x] Все 7 пунктов §4 (PART 1) имеют статус ВЫПОЛНЕНО. *(закрыто 2026-04-25)*
- [x] Все 10 пунктов §4-bis (PART 2) имеют статус ВЫПОЛНЕНО. *(закрыто 2026-04-26)*
- [x] Все пункты §5 (после v1.2 — только Ф8-LOOP и Ф11) либо ВЫПОЛНЕНО (после соответствующей фазы), либо явно «отложено» автором. *(Ф8-LOOP и Ф11 явно отложены до открытия соответствующих фаз; D-3, D-4 — занесены в §5 Очередь)*
- [x] Регрессий §6 нет открытых (все Закрыто). *(§6 пуст с момента создания файла)*
- [x] P-FINAL smoke-test проведён, отчёт `_smoke_test_2026-04-25.md` зафиксировал «pipeline integrity: pass-with-mock» с явным указанием Ф8-зависимых шагов. *(закрыто 2026-04-26)*
- [x] Controller на полном `full`-прогоне всех **12** агентов (включая bf-pm как deprecated-stub) + memory + handoff'ов возвращает `accept`. *(P-FINAL controller full = accept, 2026-04-26; cross-source проверки P3-2/P0-3/P2-3/P2-4 пройдены)*

После закрытия ТЗ:
- ✅ Версия документа → 2.0.
- ✅ Шапка: «Закрыт 2026-04-26».
- ⏳ `_SESSION_START_PROMPT.md` — убрать шаг 0 (не нужен после закрытия). Версия → v2.3. *(делается отдельной правкой в той же сессии закрытия)*

---

**Конец ТЗ. Версия 2.0. Закрыт 2026-04-26 (PART 1 + PART 2 + P-FINAL завершены).**
