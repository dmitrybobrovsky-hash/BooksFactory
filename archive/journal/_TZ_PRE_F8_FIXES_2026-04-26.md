# ТЗ — Pre-Ф8 Cleanup (устранение дефектов аудита 2026-04-26)

> **Версия 2.0** (создан 2026-04-26, **закрыт 2026-04-26**).
> Автор: Dmitry Bobrovsky.
> Источник: независимый аудит фабрики 2026-04-26 (после закрытия `_TZ_AUDIT_FIXES_2026-04-25.md` v2.0).
> Цель: закрыть 4 критических + 4 средних + 4 минорных дефекта **до** открытия Ф8 (writer-loop machine). 3 критических дефекта блокировали Ф8: C-1 (compiler false positive), C-2 (Контракт 4 vs 9 двусмысленность), C-3 (системный дефект команд идемпотентности).
>
> **Статус**: 13/13 пунктов закрыты, controller=accept на всех. Регрессий нет. Финальный отчёт: `_pre_f8_validation_2026-04-26.md`. Возможно открытие ТЗ Ф8.
>
> Этот файл — одновременно ТЗ и лог. Читать в начале каждой сессии. Помечать выполненные пункты по правилам §0.

---

## §0. Правила исполнения

### §0.1. Формат заголовка пункта

Когда пункт сделан, заголовок переписывается **в одну строку**:

```
### C-1. ВЫПОЛНЕНО 2026-04-XX (controller: accept) — Compiler self-check substring bug
```

### §0.2. Sequence (линейный, без выбора)

`C-1 → C-2 → C-3 → C-4 → M-5 → M-6 → M-7 → M-8 → m-9 → m-10 → m-11 → m-12 → P-FINAL-PRE-F8`.

Block — единственная причина остановки. См. §0.4.

### §0.3. Команды идемпотентности — корректный синтаксис

**Системное правило (закрывает C-3)**: PowerShell-команды идемпотентности с regex-паттернами **никогда не используют `-SimpleMatch`**. SimpleMatch обрабатывает `^`, `$`, `|`, `.`, `*`, `+`, `()`, `\b` и `{}` **литерально**, что даёт ложные False.

| Случай | Корректный синтаксис |
|--------|---------------------|
| Regex с альтернативой/якорем/квантификатором | `Select-String -Path X -Pattern "a\|b\|c"` (БЕЗ `-SimpleMatch`) |
| Литерал без метасимволов | `Select-String -Path X -Pattern "literal" -SimpleMatch` |
| Word boundary | `Select-String -Path X -Pattern "## T1\b"` (БЕЗ `-SimpleMatch`) |
| Anchor начала строки | `Select-String -Path X -Pattern "^consumer:"` (БЕЗ `-SimpleMatch`) |
| Файл существует | `Test-Path X` |

Перед каждой командой идемпотентности в этом ТЗ — указано, что используется regex или литерал.

### §0.4. Block

Если controller возвращает `block` — sequence останавливается, эскалация автору. Запись в §6 «Регрессии» с шаблоном из закрытого ТЗ-аудита.

### §0.5. Журнал

Каждая сессия — запись в §7. Шаблон в конце.

### §0.6. Принцип «чёрный ящик»

Все архитектурные решения внутри scope ТЗ — Claude. Без вопросов автору. Block — единственный путь паузы.

---

## §1. Пункты

### C-1. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Compiler self-check substring bug

**Тип**: исполнимый сейчас.
**Категория**: critical / logic.
**Цена**: 10 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-compiler.md"
$bash_buggy = Select-String -Path $path -Pattern '"## T1"\s+"## T2"'
$bash_fixed = Select-String -Path $path -Pattern '## T1\\b|## T1\\\.'
$ps_buggy = Select-String -Path $path -Pattern '"## T1","## T2"'
@{ bash_uses_word_boundary_or_dot = ($null -ne $bash_fixed); ps_array_still_naive = ($null -ne $ps_buggy) } | ConvertTo-Json
```
DoD выполнен, если `bash_uses_word_boundary_or_dot=true` И bash-цикл не использует голые `## T1`/`## T2`.

**Что делать**:
1. Открыть `.claude/agents/bf-compiler.md` шаг 5 «Self-check».
2. **Bash-ветку** заменить:
   ```bash
   for marker in "## T1\\b" "## T2\\b" "## T3\\b" "## T4\\b" "## T5\\b" "## T6\\b" "## T7\\b" "## T8\\b" "## T9\\b" "## T10\\b" "## T11\\b" "## T12\\b" "---BEGIN_REFERENCE_CHAPTER---" "---BEGIN_VERBOT_LISTE---" "---BEGIN_CALIBRATION---" "---BEGIN_PROTOCOL---"; do
     grep -qE "$marker" "$output_path" || echo "MISSING: $marker"
   done
   ```
   Ключ: `grep -qE` (extended regex) + `\b` (word boundary). `## T1\b` уже не матчит `## T10`.
3. **PowerShell-ветку** заменить (БЕЗ `-SimpleMatch` для T-маркеров):
   ```powershell
   $regex_markers = @("^## T1\b","^## T2\b","^## T3\b","^## T4\b","^## T5\b","^## T6\b","^## T7\b","^## T8\b","^## T9\b","^## T10\b","^## T11\b","^## T12\b")
   $literal_markers = @("---BEGIN_REFERENCE_CHAPTER---","---BEGIN_VERBOT_LISTE---","---BEGIN_CALIBRATION---","---BEGIN_PROTOCOL---")
   $regex_markers | ForEach-Object { if (-not (Select-String -Path $output_path -Pattern $_ -Quiet)) { "MISSING: $_" } }
   $literal_markers | ForEach-Object { if (-not (Select-String -Path $output_path -Pattern $_ -SimpleMatch -Quiet)) { "MISSING: $_" } }
   ```
   T-маркеры через regex с `^` и `\b`. BEGIN/END через `-SimpleMatch` (литералы без метасимволов).
4. Добавить в раздел «Абсолютно запрещено» строку: «Использовать `grep -q "## T1"` без word boundary или `Select-String "## T1" -SimpleMatch` — это даёт false positive из-за подстроки `## T10`/`## T11`/`## T12`.»

**DoD**:
- [ ] Bash-цикл использует `grep -qE` + `\b`.
- [ ] PowerShell разделён на regex_markers (T1..T12) и literal_markers (BEGIN/END).
- [ ] В «Абсолютно запрещено» зафиксирован запрет голого `## T1`.
- [ ] Smoke-test: создать тестовый файл с одним только `## T10` без T1..T9 → новый self-check рапортует MISSING для T1..T9.

**Controller depth**: full (compiler — критический агент).

---

### C-2. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Контракт 4 в `handoff_contracts.md` помечен DEPRECATED

**Тип**: исполнимый сейчас.
**Категория**: critical / architectural.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\handoff_contracts.md"
$dep = Select-String -Path $path -Pattern "Контракт 4.*DEPRECATED|DEPRECATED.*P3-2.*Контракт 9"
@{ contract4_deprecated_marked = ($null -ne $dep) } | ConvertTo-Json
```

**Что делать**:
1. Открыть `architecture/handoff_contracts.md`.
2. В начало раздела «## Контракт 4: Писатель → Гуманизатор» добавить блокquote:
   ```markdown
   > **⚠️ DEPRECATED после P3-2 + P2-4 (2026-04-26).**
   > Маршрут «Писатель → Гуманизатор» через статусы `editing`/`review` замещён цепочкой Coordinator → Editor → Coordinator → Humanizer (см. Контракт 9). Статус `editing` исключён из единой модели статусов (`production_state.md`).
   > Контракт 4 сохранён до Ф8-расщепления Контракта 1. Не использовать как активный маршрут. При чтении — следовать Контракту 9.
   ```
3. Не удалять Контракт 4 — это история. Только пометка.

**DoD**:
- [ ] DEPRECATED-блок в начале Контракта 4 присутствует.
- [ ] Ссылка на Контракт 9 как активный маршрут.
- [ ] Контракт 4 не удалён (архивная справка).

**Controller depth**: light.

---

### C-3. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Системное правило команд идемпотентности задокументировано в `bf-controller.md`

**Тип**: исполнимый сейчас.
**Категория**: critical / systemic.
**Цена**: 15 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-controller.md"
$rule = Select-String -Path $path -Pattern "SimpleMatch.*regex|regex.*SimpleMatch"
@{ idempotency_rule_present = ($null -ne $rule) } | ConvertTo-Json
```

**Что делать**:
1. Открыть `.claude/agents/bf-controller.md`. Найти раздел «Правила принятия решения».
2. Добавить новый пункт (или раздел «## Правила команд идемпотентности»):
   ```markdown
   ## Правила команд идемпотентности

   Команды идемпотентности в ТЗ используют PowerShell `Select-String`. Системное правило:

   - `-SimpleMatch` обрабатывает `^`, `$`, `|`, `.`, `*`, `+`, `()`, `\b`, `{}` **литерально**.
   - Если паттерн содержит regex-метасимволы (альтернатива `a|b`, якоря `^X`, квантификаторы `.{0,5}`, word boundary `\b`) — `-SimpleMatch` НЕ использовать. Иначе ложный False.
   - `-SimpleMatch` допустим только для строго-литеральных строк без метасимволов (например `---BEGIN_REFERENCE_CHAPTER---`).

   Controller при валидации audit_task запускает команды идемпотентности **повторно через regex Grep** при подозрении на ложный False. Конкретно: если команда вернула False, но артефакт визуально соответствует DoD — controller выполняет верификацию через Grep regex (без SimpleMatch) и фиксирует «дефект команды, не правки» в notes.

   Прецеденты в `_TZ_AUDIT_FIXES_2026-04-25.md`: P0-2, P3-1, P3-4, P2-3, P0-3 — все имели ложный False из-за этого дефекта.
   ```
3. Также добавить в `_SESSION_START_PROMPT.md` v2.4 короткую памятку (одна строка): «При написании команд идемпотентности — БЕЗ `-SimpleMatch` для regex-паттернов (см. `bf-controller.md` правило команд идемпотентности).»

**DoD**:
- [ ] Раздел «Правила команд идемпотентности» в `bf-controller.md` существует.
- [ ] 5 прецедентов из audit-ТЗ перечислены.
- [ ] `_SESSION_START_PROMPT.md` → v2.4 с памяткой.

**Controller depth**: full (controller — носитель правила, критично).

---

### C-4. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Архивация `_testing/smoke_2026-04-25/`

**Тип**: исполнимый сейчас.
**Категория**: critical / hygiene.
**Цена**: 2 минуты.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$active = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_testing\smoke_2026-04-25"
$archived = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\archive\smoke_2026-04-25"
@{ active_dir_removed = (-not $active); archived = $archived } | ConvertTo-Json
```
DoD выполнен, если `active_dir_removed=true` И `archived=true`.

**Что делать**:
1. Создать `BooksFactory/archive/` (если не существует).
2. Переместить `BooksFactory/_testing/smoke_2026-04-25/` → `BooksFactory/archive/smoke_2026-04-25/`.
3. Если в `_testing/` пусто после переноса — оставить директорию (она зарезервирована под будущие smoke-тесты Ф8/Ф11).

**DoD**:
- [ ] `_testing/smoke_2026-04-25/` отсутствует.
- [ ] `archive/smoke_2026-04-25/` содержит все 11 артефактов.
- [ ] Отчёт `_smoke_test_2026-04-25.md` в корне фабрики не тронут (он самодостаточный).

**Controller depth**: light.

---

### M-5. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Промежуточный статус между researcher и material-author

**Тип**: исполнимый сейчас.
**Категория**: middle / architectural.
**Цена**: 10 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md"
$res = Select-String -Path $path -Pattern "researched|outline-ready" -Quiet
@{ researched_status_documented = $res } | ConvertTo-Json
```

**Что делать**:
1. **Решение**: ввести промежуточный статус `outline-ready` (после `bf-researcher`, до `bf-material-author`). Он описывает: outline и tonal_compass готовы, MATERIAL ещё нет.
2. Обновить `production_state.md` модель статусов: добавить `outline-ready` между «(нет файла)» и `material-draft`. Базовая последовательность становится: `(нет файла) → outline-ready → material-draft → draft → review → clean → humanized → translated → final`.
3. Обновить таблицу описания статусов: `outline-ready` ставит `bf-researcher`, означает «outline главы готов, tonal_compass актуален, готов к material-author».
4. Обновить `bf-coordinator.md` routing-таблицу — добавить строку для `outline-ready → bf-material-author`.
5. Обновить `architecture/handoff_contracts.md` сводную таблицу статусов.

**DoD**:
- [ ] `outline-ready` в `production_state.md` базовой последовательности.
- [ ] `bf-coordinator.md` routing-таблица содержит строку для `outline-ready`.
- [ ] `handoff_contracts.md` сводная таблица обновлена.
- [ ] `CLAUDE.md` статус-цепочка обновлена.

**Controller depth**: full (статусная модель — cross-cutting).

---

### M-6. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Контракт 9.7 — судьба `glava_NN.md` при reopen_beat

**Тип**: исполнимый сейчас.
**Категория**: middle / logic.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\handoff_contracts.md"
$res = Select-String -Path $path -Pattern "_history|backup.*reopen_beat|reopen_beat.*backup"
@{ history_backup_documented = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. В Контракт 9.7 (`handoff_contracts.md`) добавить шаг перед откатом статуса:
   > Перед откатом `draft → compiled` Coordinator сохраняет старый `<book>/_drafts/glava_NN.md` в `<book>/_drafts/_history/glava_NN_v<unix_timestamp>.md`. Это позволяет автору сравнить версии и откатить решение reopen_beat при ошибке Editor-а.
2. Создать соответствующий вход-выход формат:
   ```json
   {
     "action": "reopen_beat",
     "beat_id": 5,
     "reason": "...",
     "scope": "single_beat",
     "preserve_old_glava_path": "<book>/_drafts/_history/glava_05_v<timestamp>.md"
   }
   ```

**DoD**:
- [ ] §9.7 содержит явное описание `_history/` сохранения.
- [ ] Формат запроса `reopen_beat` расширен полем `preserve_old_glava_path`.

**Controller depth**: light.

---

### M-7. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — `bf-controller` fallback задокументирован как штатный режим

**Тип**: исполнимый сейчас.
**Категория**: middle / architectural.
**Цена**: 10 минут.
**Зависимости**: C-3 (правила команд идемпотентности).

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-controller.md"
$res = Select-String -Path $path -Pattern "Способы вызова|fallback|general-purpose"
@{ fallback_documented = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. Добавить в `bf-controller.md` секцию «## Способы вызова»:
   ```markdown
   ## Способы вызова

   Controller вызывается двумя путями:

   ### Путь 1 — прямой subagent
   ```
   Agent({ subagent_type: "bf-controller", description: "...", prompt: "..." })
   ```
   Работает, если `.claude/agents/bf-controller.md` доступен из cwd процесса Claude. По состоянию 2026-04-26 cwd по умолчанию = `Skills/`, поэтому требуется симлинк `Skills/.claude/agents/bf-controller.md → BooksFactory/.claude/agents/bf-controller.md` (см. D-4 ниже).

   ### Путь 2 — fallback через general-purpose proxy
   ```
   Agent({ subagent_type: "general-purpose", description: "bf-controller proxy", prompt: "Ты выполняешь роль bf-controller... Контракт ты найдёшь в <путь>/bf-controller.md — прочитай и следуй ему. Read-only..." })
   ```
   Используется, если Путь 1 недоступен. Все 11 валидаций PART 1+PART 2+P-FINAL `_TZ_AUDIT_FIXES_2026-04-25.md` прошли через Путь 2 без потери качества вердиктов.

   Оба пути возвращают строго JSON-вердикт. Caller выбирает доступный.
   ```
2. D-4 (симлинк) — переводится в M-7-A как **опциональный** пункт после M-7. Если симлинк сделан — Путь 1 активен; если нет — Путь 2 штатный.

**DoD**:
- [ ] Секция «Способы вызова» в `bf-controller.md` присутствует.
- [ ] Оба пути описаны с примерами.
- [ ] Явно зафиксировано, что Путь 2 — штатный fallback, не аварийный.

**Controller depth**: light (документация контроллера).

---

### M-8. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Compiler: уточнение «не интерпретировать»

**Тип**: исполнимый сейчас.
**Категория**: middle / wording.
**Цена**: 3 минуты.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-compiler.md"
$res = Select-String -Path $path -Pattern "не интерпретировать СОДЕРЖИМОЕ|placeholder.*допустим"
@{ wording_clarified = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. В `bf-compiler.md` §«Абсолютные ограничения» заменить «**НЕ интерпретировать beat-план.**» на «**НЕ интерпретировать СОДЕРЖИМОЕ артефактов** (MATERIAL, beat-план, tonal_compass — копировать побайтово). Подстановка значений из входного промпта в placeholder'ы Session_TEMPLATE — допускается как механическая операция (substitution, не interpretation).»
2. То же самое уточнение в шаге 4 «Сборка»: при копии T1-блока пометить «механическая подстановка значений из входного промпта в `<...>`-placeholder'ы; не модификация контента».

**DoD**:
- [ ] §«Абсолютные ограничения» уточнено.
- [ ] §«Сборка» Шаг 4 содержит пометку про substitution vs interpretation.

**Controller depth**: light.

---

### m-9. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Ссылка в `production_state.md` на `_HANDOFF_*_PART2.md §13.2`

**Тип**: исполнимый сейчас.
**Категория**: minor / doc.
**Цена**: 1 минута.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md"
$res = Select-String -Path $path -Pattern "§13\.2"
@{ stale_ref_present = ($null -ne $res) } | ConvertTo-Json
```
DoD: после фикса `stale_ref_present=false` или ссылка ведёт на §13.1 / актуальный раздел.

**Что делать**:
1. Открыть `production_state.md` строку про Band III.
2. Заменить «§13.2» на «§13.1» (раздел «Band III статус», если он там) или удалить ссылку на конкретный параграф, оставив имя файла.

**DoD**:
- [ ] Ссылка на §13.2 не указывает на закрытую priority-таблицу.

**Controller depth**: light.

---

### m-10. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — PowerShell encoding sanity-check

**Тип**: исполнимый сейчас.
**Категория**: minor / tech.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$ps_version = $PSVersionTable.PSVersion.Major
$test = Get-Content "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md" -Raw
$cyrillic_ok = $test.Contains("Модель статусов")
@{ ps_version = $ps_version; cyrillic_ok = $cyrillic_ok; needs_explicit_utf8 = ($ps_version -lt 7 -and (-not $cyrillic_ok)) } | ConvertTo-Json
```

**Что делать**:
1. Зафиксировать в `bf-compiler.md` §«Абсолютные ограничения»: «PowerShell 5.x: для чтения кириллических файлов использовать `Get-Content -Encoding UTF8`. PowerShell 7+ читает UTF-8 по умолчанию.»
2. Если test показывает `needs_explicit_utf8=true` — добавить `-Encoding UTF8` во все `Get-Content` вызовы compiler-а.

**DoD**:
- [ ] Памятка про PowerShell encoding в `bf-compiler.md`.
- [ ] Get-Content вызовы используют корректный Encoding (если v5).

**Controller depth**: light.

---

### m-11. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — `bf-coordinator.md` правило 5 — снять двусмысленность с writer-loop

**Тип**: исполнимый сейчас.
**Категория**: minor / wording.
**Цена**: 1 минута.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-coordinator.md"
$res = Select-String -Path $path -Pattern "review-итераций|Контракт 6\.5"
@{ disambiguation_present = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. В `bf-coordinator.md` правило 5 заменить:
   > **Лимит итераций writer↔editor**: ≥ 3 цикла без закрытия критических нарушений → эскалация автору. (Применимо к фазе review, не к Ф8 writer-loop.)
   на:
   > **Лимит review-итераций author↔editor**: ≥ 3 цикла без закрытия критических нарушений Editor-а → эскалация автору. **Не путать** с лимитом Контракта 6.5 (max_iterations=3 в writer-loop) — это разные счётные машины.

**DoD**:
- [ ] Правило 5 явно отделяет review от writer-loop.

**Controller depth**: light.

---

### m-12. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Контракт series-bible vs tonal_compass

**Тип**: исполнимый сейчас (требует архитектурного решения).
**Категория**: minor / doc.
**Цена**: 15 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\shared_vocabulary.md"
$res = Select-String -Path $path -Pattern "series-bible.*tonal_compass|tonal_compass.*series-bible"
@{ relationship_documented = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. **Решение**: иерархия трёх уровней голоса.
   - `brand-voice.md` (фабрика) — голос «Интеллигентный сукин сын», дефолт серии.
   - `series-bible.md` (серия) — терминология, инварианты обращения, кросс-книжные правила.
   - `<book>/tonal_compass.md` (книга) — голос конкретной книги, побеждает дефолты.
   - Правило конфликта: книжный tonal_compass > серийный series-bible > фабричный brand-voice.
2. Зафиксировать в `architecture/shared_vocabulary.md` секцию «Иерархия голоса».
3. Сослаться из `CLAUDE.md` правила 5 на эту секцию.

**DoD**:
- [ ] `shared_vocabulary.md` содержит секцию «Иерархия голоса» с тремя уровнями.
- [ ] CLAUDE.md правило 5 обновлено.

**Controller depth**: light.

---

### P-FINAL-PRE-F8. ВЫПОЛНЕНО 2026-04-26 (controller: accept) — Sanity-check после всех правок

**Тип**: финальный.
**Категория**: validation.
**Цена**: 15 минут.
**Зависимости**: все C-/M-/m- закрыты.

**Команда идемпотентности**:
```powershell
$report = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_pre_f8_validation_2026-04-XX.md"
@{ validation_report_exists = $report } | ConvertTo-Json
```

**Что делать**:
1. Создать тестовый Session_compiled.md с одной отсутствующей секцией T3 (`## T3` удалена). Прогнать обновлённый compiler self-check (C-1) → должен сообщить `MISSING: ^## T3\b`.
2. Прогнать health-check всех команд идемпотентности этого ТЗ (12 команд) — должны давать True для закрытых пунктов.
3. Прогнать controller full-валидацию обновлённых артефактов (compiler.md, controller.md, coordinator.md, handoff_contracts.md, production_state.md, shared_vocabulary.md, CLAUDE.md, _SESSION_START_PROMPT.md).
4. Записать отчёт `_pre_f8_validation_2026-04-XX.md` со списком: что изменилось, какие smoke-проверки пройдены, готовность к открытию ТЗ Ф8.

**DoD**:
- [ ] Smoke-test C-1 fix подтверждает поимку отсутствующей секции.
- [ ] Все 12 команд идемпотентности возвращают True.
- [ ] Controller full = accept на 8 артефактах.
- [ ] Отчёт `_pre_f8_validation_*.md` создан.
- [ ] В отчёте явная формулировка: «Pre-Ф8 cleanup закрыт, готовность к Ф8 = 100% на оси целостности контрактов».

**Controller depth**: full (закрывающий).

---

## §6. Регрессии

(пусто на момент создания)

Шаблон записи (как в audit-ТЗ):
```
### Регрессия R-001 (2026-04-XX)
- **Пункт**: C-X
- **Controller verdict**: block
- **Причина**: <конкретно>
- **Действие**: правка не откачена. Sequence остановлен. Эскалация автору.
- **Решение автора**: <дата> — <выбран вариант X>.
- **Закрыто**: <дата>, sequence возобновлён.
```

---

## §7. Журнал сессий

> Каждая сессия — одна строка.

- 2026-04-26 (Opus 4.7): C-1 закрыт; controller full: accept. Bash-ветка self-check переведена на `grep -qE` + `\b`; PowerShell-ветка разделена на regex_markers (T1..T12 с `^` и `\b`, без -SimpleMatch) и literal_markers (BEGIN/END через -SimpleMatch); в «Абсолютно запрещено» добавлен запрет голого `## T1`.
- 2026-04-26 (Opus 4.7): C-2 закрыт; controller light: accept. В начало раздела «Контракт 4: Писатель → Гуманизатор» (`handoff_contracts.md`) добавлен blockquote DEPRECATED со ссылкой на Контракт 9 как активный маршрут. Контракт 4 сохранён архивно. Команда идемпотентности ТЗ дала ложный False (Select-String построчно, `.*` не пересекает `\n`) — дефект команды, не правки; системно закрывается в C-3.
- 2026-04-26 (Opus 4.7): C-3 закрыт; controller full: accept. В `bf-controller.md` добавлен раздел «Правила команд идемпотентности» с правилом про -SimpleMatch, multiline-оговоркой и 5 прецедентами (P0-2, P3-1, P3-4, P2-3, P0-3). `_SESSION_START_PROMPT.md` повышен до v2.4 с памяткой в «ЖЁСТКИЕ РАМКИ».
- 2026-04-26 (Opus 4.7): C-4 закрыт; controller light: accept. `_testing/smoke_2026-04-25/` перемещена в `archive/smoke_2026-04-25/` (11 файлов сохранены). `_testing/03_Manipulationen/` не тронута, `_smoke_test_2026-04-25.md` в корне фабрики не тронут.
- 2026-04-26 (Opus 4.7): M-5 закрыт; controller full: accept (2 косметических warning). Введён статус `outline-ready` (после `bf-researcher`, до `bf-material-author`). Базовая последовательность обновлена в 4 файлах: `production_state.md`, `bf-coordinator.md` (routing-таблица), `handoff_contracts.md` (сводная таблица), `CLAUDE.md`.
- 2026-04-26 (Opus 4.7): M-6 закрыт; controller light: accept (1 warning). Контракт 9.7 расширен: JSON `reopen_beat` получил поле `preserve_old_glava_path`; добавлен шаг сохранения текущего `glava_NN.md` в `_drafts/_history/glava_NN_v<timestamp>.md` перед откатом статуса.
- 2026-04-26 (Opus 4.7): M-7 закрыт; controller light: accept. В `bf-controller.md` добавлена секция «Способы вызова»: Путь 1 (прямой subagent) и Путь 2 (general-purpose proxy) с примерами; зафиксировано «Путь 2 — штатный fallback, не аварийный». Idempotency-команда ТЗ давала ложный True (паттерн `fallback` слишком широкий, ловил существующие упоминания) — проверено более узким `Способы вызова|general-purpose proxy`.
- 2026-04-26 (Opus 4.7): M-8 закрыт; controller light: accept. В `bf-compiler.md` §«Абсолютные ограничения» уточнено: «НЕ интерпретировать СОДЕРЖИМОЕ артефактов» + явное разрешение на substitution в placeholder'ах Session_TEMPLATE. В Шаг 4 «Сборка» (T1-блок) добавлен HTML-комментарий-пометка про substitution vs interpretation.
- 2026-04-26 (Opus 4.7): сессия прервана автором на m-9 (~9% контекста). Закрыто 8 из 13 пунктов: C-1, C-2, C-3, C-4, M-5, M-6, M-7, M-8 — все controller=accept (M-5: 2 косметических warning, M-6: 1 warning, остальные — без warning). Открыты: m-9, m-10, m-11, m-12, P-FINAL-PRE-F8. Регрессий нет. m-9 начат не был (правка отклонена автором). Sequence продолжается с m-9 в следующей сессии.
- 2026-04-26 (Opus 4.7): m-9 закрыт; controller light: accept. В `production_state.md` строка 55 (Band III) — ссылка `§13.2` удалена (это закрытая priority-таблица), имя файла `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` сохранено. Альтернатива из ТЗ (`§13.1` — «Категории найденных проблем») отвергнута: там нет «Band III статус», ссылка вела бы на нерелевантный раздел.
- 2026-04-26 (Opus 4.7): m-10 закрыт; controller light: accept. В `bf-compiler.md` §«Абсолютные ограничения» добавлен bullet про PowerShell encoding кириллицы: PS 5.x требует `-Encoding UTF8`, PS 7+ читает UTF-8 по умолчанию (флаг безвредный, поэтому ставится всегда — защита PS 5.x deployments). Единственный `Get-Content` в Шаге 2 (валидация beat-плана) дополнен `-Encoding UTF8`. Текущая система: `ps_version=7`, `cyrillic_ok=true`, `needs_explicit_utf8=false`.
- 2026-04-26 (Opus 4.7): m-11 закрыт; controller light: accept (1 непредметный warning про статус шапки ТЗ). В `bf-coordinator.md` правило 5 (стр. 98) переформулировано: «Лимит review-итераций author↔editor ≥ 3 → эскалация автору» + явное «Не путать с лимитом Контракта 6.5 (max_iterations=3 в writer-loop Ф8) — это разные счётные машины». Сверка с `handoff_contracts.md` §6.5 подтвердила корректность ссылки.
- 2026-04-26 (Opus 4.7): m-12 закрыт; controller light: accept (1 предметный warning про возможный ложный False idempotency-команды на других системах — у меня True, потому что параграф конфликта помещается в одну строку). В `shared_vocabulary.md` после §4 добавлена подсекция «4.1. Иерархия голоса (приоритет при конфликте)» — таблица трёх уровней (фабрика `brand-voice` → серия `series-bible` → книга `tonal_compass`/`stil_und_ton_XX`) с правилом «книга > серия > фабрика» и оговоркой про неотменяемые серийные инварианты (du/ты). CLAUDE.md правило 5 расширено ссылкой на §4.1.
- 2026-04-26 (Opus 4.7): P-FINAL-PRE-F8 закрыт; controller full: accept (15/15 прицельных проверок, 2 косметических warning без блока). Smoke-test C-1: T10-only сессия даёт 15 MISSING (T1..T9, T11, T12, 4 BEGIN), T10 НЕ помечен — word boundary работает. 12/12 команд идемпотентности возвращают True. Controller full на 8 артефактах подтвердил консистентность статусной модели (`outline-ready` в 4 файлах), Контракт 4 DEPRECATED vs Контракт 9 активный, разделение review-итераций vs Контракт 6.5, иерархию голоса 3-х уровней. Отчёт `_pre_f8_validation_2026-04-26.md` создан. Регрессий 0. Сессия закрыла все 5 оставшихся пунктов (m-9..m-12, P-FINAL); ТЗ закрыт целиком 13/13.

Шаблон:
```
- 2026-04-XX (Sonnet/Opus): C-1 закрыт; controller full: accept. <детали в 1-2 предложения>.
```

---

## §8. Финальный чек-лист закрытия ТЗ

- [ ] Все 12 пунктов §1 (C-1..C-4, M-5..M-8, m-9..m-12) имеют статус ВЫПОЛНЕНО.
- [ ] P-FINAL-PRE-F8 выполнен, отчёт `_pre_f8_validation_*.md` зафиксировал «Pre-Ф8 cleanup закрыт».
- [ ] Регрессий §6 нет открытых.
- [ ] `_SESSION_START_PROMPT.md` обновлён до v2.4 (включает памятку C-3).
- [ ] Controller full на 8 артефактах возвращает `accept`.

После закрытия:
- Версия документа → 2.0.
- Шапка: «Закрыт YYYY-MM-DD».
- Возможно открытие ТЗ Ф8 (writer-loop machine) без блокирующих дефектов.

---

**Конец ТЗ. Версия 1.0. 2026-04-26 (Pre-Ф8 cleanup на основе независимого аудита).**
