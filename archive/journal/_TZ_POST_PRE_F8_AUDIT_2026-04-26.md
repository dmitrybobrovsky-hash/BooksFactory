# ТЗ — Post-Pre-Ф8 Audit Fixes (независимый аудит 2026-04-26)

> **Версия 1.0** (создан 2026-04-26).
> Автор: Dmitry Bobrovsky.
> Источник: независимый аудит фабрики 2026-04-26 (после закрытия `_TZ_PRE_F8_FIXES_2026-04-26.md` v2.0). Отчёт — раздел «Аудит BooksFactory 2026-04-26 — пересмотр» в журнале сессий BooksFactory.
> Цель: устранить 3 критических + 4 средних + 3 минорных + 2 отметки, найденные после закрытия Pre-Ф8 cleanup. Главный системный сдвиг: **фабрика самодостаточна** — она производит НОВЫЕ книги, ничего не знает о существующей серии, не ссылается на её файлы.
>
> Этот файл — одновременно ТЗ и лог. Читать в начале каждой сессии. Помечать выполненные пункты по правилам §0.

---

## §0. Правила исполнения

### §0.1. Формат заголовка пункта

Когда пункт сделан, заголовок переписывается **в одну строку**:

```
### C-1. ВЫПОЛНЕНО 2026-04-XX (controller: accept) — Контракт review-цикла
```

### §0.2. Sequence (линейный, без выбора)

`A-1 → C-1 → C-2 → C-3 → M-1 → M-2 → M-3 → M-4 → m-1 → m-2 → m-3 → I-1 → I-2 → P-FINAL`.

`A-1` идёт первым, потому что может изменить scope других пунктов: если глоссарий или другой архитектурный артефакт окажется ссылающимся на серию — его правка поглотит часть M-1.

Block — единственная причина остановки. См. §0.5.

### §0.3. Принцип самодостаточности фабрики (главный)

**Фабрика — это инструмент производства НОВЫХ книг с нуля.** Серия книг автора (MdP, ОНМ, IG, DK, Manipulation_Project, Band III и любые другие тома) — материал-источник опыта, использованный при проектировании фабрики, **не объект работы фабрики**.

Любая ссылка из файла фабрики (`BooksFactory/**`) на путь вне фабрики (`SpellBooks/Serie/...`, `SpellBooks/Abuse/...`, `SpellBooks/_testing/...`, `Obsidian/...` и т. д.) с целью «прочитать», «открыть», «свериться» — **дефект**. Декоративные упоминания серии в комментариях/воспоминаниях агентов («так делалось раньше в книге X») допустимы только как пример без читаемой ссылки.

Правильный паттерн: если в файле серии есть полезный материал — он **копируется внутрь фабрики** (в `architecture/`, `brand-voice.md`, `series-bible.md` или соответствующий агент) и адаптируется как фабричное знание. После копирования файл серии больше не нужен фабрике.

Этот принцип закрывает риск: «фабрику переносят в другую среду / другой автор открывает её → ссылка на серию ведёт в никуда».

### §0.4. Команды идемпотентности — корректный синтаксис

Системное правило C-3 закрытого Pre-Ф8 ТЗ остаётся в силе:

- `-SimpleMatch` обрабатывает `^`, `$`, `|`, `.`, `*`, `+`, `()`, `\b`, `{}` **литерально**. Для regex-паттернов — БЕЗ `-SimpleMatch`.
- `Select-String` работает построчно → multiline-проверки через `Get-Content -Raw -Encoding UTF8` + `-match '(?s)X.*?Y'`.
- См. полное правило в `.claude/agents/bf-controller.md` раздел «Правила команд идемпотентности».

### §0.5. Block

Если controller возвращает `block` — sequence останавливается, эскалация автору. Запись в §6 «Регрессии» с шаблоном.

### §0.6. Журнал

Каждая сессия — запись в §7. Шаблон в конце.

### §0.7. Принцип «чёрный ящик»

Все архитектурные решения внутри scope ТЗ — Claude. Без вопросов автору. Block — единственный путь паузы.

---

## §1. Пункты

### A-1. Сканирование фабрики на ссылки за пределы фабрики

**Тип**: исполнимый сейчас.
**Категория**: autonomy / systemic.
**Цена**: 30–45 минут.
**Зависимости**: нет.

**Команда идемпотентности** (полный сканер):
```powershell
$root = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory"
$forbidden = @("Serie/","Serie\\","Abuse/","Abuse\\","SpellBooks/_testing","Obsidian/","..\\Serie","..\\Abuse","..\\Obsidian")
$pattern = ($forbidden | ForEach-Object { [regex]::Escape($_) }) -join "|"
$hits = Get-ChildItem -Path $root -Recurse -Include *.md -File |
    Where-Object { $_.FullName -notmatch "\\archive\\" -and $_.FullName -notmatch "\\_testing\\" -and $_.FullName -notmatch "_HANDOFF_" -and $_.FullName -notmatch "_TZ_" -and $_.FullName -notmatch "_pre_f8_validation" } |
    Select-String -Pattern $pattern
@{ external_refs_count = ($hits | Measure-Object).Count; sample = ($hits | Select-Object -First 5 | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }) } | ConvertTo-Json -Depth 4
```
DoD: `external_refs_count = 0` (все ссылки на серию в активной инфре фабрики удалены или контент интегрирован).

**Что делать**:
1. Прогнать сканер. Получить полный список нарушений с путями и строками.
2. Для каждого нарушения принять одно из решений:
   - **Удалить ссылку**, если она декоративная («раньше в IG было так-то») и контекст не теряется.
   - **Скопировать материал внутрь фабрики** и заменить ссылку на внутренний путь. Целевые места: `architecture/brand-voice.md` (для голосовых принципов), `architecture/series-bible.md` (для серийных инвариантов), `architecture/voice_principles.md`/`provocation_principles.md` (для механики), агенты `.claude/agents/bf-*.md` (для специфики ролей).
   - **Заменить на абстрактный пример**, если ссылка иллюстративная («книга X» → «книга-пример»).
3. Особо проверить:
   - `brand-voice.md`, `series-bible.md` — не ссылаются ли они сами на конкретные тома серии? Если да — обобщить (вместо «Band III» писать «книга в работе», вместо «MdP пример» — переписать пример своими словами).
   - `glossary.md` — содержит ли разделы про конкретные книги (§3.2 Band I, §3.3 Band II, §3.4 Band III…)? Если да — превратить в обобщённую таблицу терминов «по теме» (страх, отравление, манипуляция, цинизм, иммунитет, соучастие) без привязки к томам.
   - агенты — есть ли в инструкциях `bf-*.md` пути типа `Serie/...` или `Abuse/...`?
4. Если в результате обнаружены файлы серии, ссылки на которые удалены, но контент полезен — записать в `BooksFactory/_imported_from_series_2026-04-26.md` краткую справку «откуда что взято», для исторического следа без операционной зависимости.

**DoD**:
- [ ] `external_refs_count = 0` (за исключением заявленных исключений: архивы, ТЗ-логи, _HANDOFF — эти файлы исторические, фабрика не читает их операционно).
- [ ] Создана справка `_imported_from_series_2026-04-26.md` (если был контент-перенос).
- [ ] Принцип §0.3 ТЗ задокументирован в `CLAUDE.md` как новое правило (правило 7 или правило 0).

**Controller depth**: full (системный сдвиг, cross-cutting).

---

### C-1. Контракт review-цикла: устранить противоречие author↔editor vs writer↔editor

**Тип**: исполнимый сейчас.
**Категория**: critical / contracts.
**Цена**: 10 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$ed = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-editor.md" -Pattern "Возврат к кому|writer.{0,3}\(применение"
$co = Select-String -Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-coordinator.md" -Pattern "review-итераций author"
$contract3_path = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\handoff_contracts.md"
$raw = Get-Content $contract3_path -Raw -Encoding UTF8
$contract3_disambiguated = $raw -match "(?s)Контракт 3.*?(применяет правки|вносит правки).*?(refiner|автор)"
@{ editor_returns_to = ($ed | ForEach-Object { $_.Line.Trim() }); coordinator_says_author = ($null -ne $co); contract3_disambiguated = $contract3_disambiguated } | ConvertTo-Json -Depth 4
```
DoD: editor и coordinator говорят про **одного и того же** актора применения правок; Контракт 3 в `handoff_contracts.md` явно фиксирует кого.

**Что делать**:
1. **Решение** (внутри scope «чёрный ящик»): применяющий правки — **refiner-роль внутри bf-coordinator** (не writer, не автор). В Ф8 writer-loop refiner-revise существует как часть архитектуры (см. FACTORY_MAP §36). До Ф8 — заглушка: «правки применяет автор вручную, coordinator маршрутизирует».
2. В `bf-editor.md` строки 22–23 (таблица «Параметр / bf-critic / bf-editor») столбец «Возврат к кому» для bf-editor: заменить «**writer (применение правок)**» на «**refiner (Ф8 — внутри bf-coordinator) или автор (до Ф8)**».
3. В `bf-coordinator.md` правило 5 расширить уточнением: «Применяющий правки в review-цикле = `refiner` внутри Ф8-машины coordinator-а; до закрытия Ф8 — автор вручную. Не writer.»
4. В `handoff_contracts.md` Контракт 3 (Редактор → Писатель) — заменить заголовок и тело на «Контракт 3: Редактор → Refiner (применение правок)». Шапка явно фиксирует: правки идут не writer-у, а refiner-роли coordinator-а; легаси-имя «Писатель» сохраняется как комментарий для исторической читаемости.

**DoD**:
- [ ] bf-editor.md строки 22–23 исправлены.
- [ ] bf-coordinator.md правило 5 расширено упоминанием refiner.
- [ ] handoff_contracts.md Контракт 3 переименован.
- [ ] Все три источника говорят одно и то же.

**Controller depth**: full (контракт — cross-cutting).

---

### C-2. Status gap: ввести верхнеуровневые статусы `beat-plan-ready` и `compiled`

**Тип**: исполнимый сейчас.
**Категория**: critical / status-model.
**Цена**: 25 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$ps = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\memory\production_state.md"
$raw = Get-Content $ps -Raw -Encoding UTF8
$has_chain = $raw -match "(?s)outline-ready.{0,30}material-draft.{0,30}beat-plan-ready.{0,30}compiled.{0,30}draft"
$co = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-coordinator.md"
$has_routing_compiled = (Select-String -Path $co -Pattern "compiled.*bf-(writer|coordinator)|beat-plan-ready.*bf-compiler" -Quiet)
@{ chain_includes_new_states = $has_chain; routing_for_new_states = $has_routing_compiled } | ConvertTo-Json
```

**Что делать**:
1. **Решение**: статусы `beat-plan-ready` и `compiled` повышаются с подстатусов до верхнеуровневых. Новая базовая последовательность:
   ```
   (нет файла) → outline-ready → material-draft → beat-plan-ready → compiled → draft → review → clean → humanized → translated → final
   ```
2. В `production_state.md` обновить:
   - Базовую последовательность (строка 16).
   - Таблицу описания статусов: добавить строки `beat-plan-ready` (источник bf-planner, что значит «beat_plan.json валиден, готов к bf-compiler») и `compiled` (источник bf-compiler, «Session-файл собран, прошёл self-check, готов к Ф8 writer-loop»).
   - Раздел «Декомпозиция draft-фазы» — оставить только подстатусы `beat-N-draft` и `beat-N-accepted`. Удалить `compiled` из подстатусов (он теперь верхнеуровневый).
3. В `bf-coordinator.md` routing-таблицу обновить:
   - Заменить «(после planner)» на явный статус `beat-plan-ready` для строки compiler.
   - Добавить строку: «Session-compiled → writer-loop | `compiled` | (Ф8 — не реализовано) | NN_session_compiled.md валиден».
4. В `bf-planner.md` и `bf-compiler.md` инструкциях явно указать: «по успешному завершению ставит статус `beat-plan-ready` / `compiled` в `production_state.md` через bf-coordinator или прямой Write».
5. В `handoff_contracts.md` сводную таблицу статусов обновить.
6. В `CLAUDE.md` цепочку статусов (если упоминается) обновить.

**DoD**:
- [ ] `production_state.md` базовая последовательность включает оба новых статуса.
- [ ] Таблица описания статусов содержит `beat-plan-ready` и `compiled`.
- [ ] Подстатус `compiled` удалён из декомпозиции `draft`.
- [ ] `bf-coordinator.md` routing-таблица не содержит «(после planner)».
- [ ] bf-planner и bf-compiler знают, какой статус ставить.
- [ ] handoff_contracts.md и CLAUDE.md синхронизированы.

**Controller depth**: full (статусная модель — cross-cutting; M-5 закрытого ТЗ её уже трогал, теперь второе расширение).

---

### C-3. Агенты, читающие голос книги, должны принимать оба имени файла (`stil_und_ton_XX.md` и `tonal_compass.md`)

**Тип**: исполнимый сейчас.
**Категория**: critical / blocker.
**Цена**: 20 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$agents = @("bf-editor","bf-writer","bf-critic","bf-humanizer","bf-translator","bf-compiler","bf-planner","bf-material-author")
$results = @{}
foreach ($a in $agents) {
    $p = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\$a.md"
    $raw = Get-Content $p -Raw -Encoding UTF8
    $mentions_tc = $raw -match "tonal_compass"
    $mentions_st = $raw -match "stil_und_ton"
    $robust = (-not $mentions_tc) -or ($mentions_tc -and $mentions_st)
    $results[$a] = @{ tc = $mentions_tc; st = $mentions_st; robust = $robust }
}
$results | ConvertTo-Json -Depth 3
```
DoD: каждый агент, упоминающий `tonal_compass`, **также** упоминает `stil_und_ton` (либо обобщённо «файл голоса книги»).

**Что делать**:
1. По результатам сканера для каждого агента, где `robust=false`, переписать упоминания `tonal_compass.md` на «файл голоса книги: `stil_und_ton_XX.md` (новая модель слоя A) или `tonal_compass.md` (legacy)». Хороший шаблон фразы: «Прочитай файл голоса книги (`<book>/stil_und_ton_*.md` если существует, иначе `<book>/tonal_compass.md`)».
2. **Конкретное место для bf-editor**: строка 48 шага 4 инициализации.
3. После этого пункта зафиксировать в `architecture/shared_vocabulary.md` §3.1 явно: «Агенты выбирают существующий файл из двух — приоритет `stil_und_ton_XX.md`, fallback `tonal_compass.md`».

**DoD**:
- [ ] Все 8 агентов из списка прошли проверку `robust=true`.
- [ ] shared_vocabulary.md §3.1 содержит правило выбора файла.

**Controller depth**: full (затрагивает 8 агентов, блокирует первый прогон фабрики).

---

### M-1. `glossary.md` — переделать в чистую таблицу переводов без определений

**Тип**: исполнимый сейчас (зависит от A-1, потому что glossary.md разделы §3.2–§3.7 содержат привязку к томам серии — она уйдёт в A-1).
**Категория**: middle / single-source-of-truth.
**Цена**: 25 минут.
**Зависимости**: A-1 (если A-1 уже почистил привязку к томам, M-1 чистит только дубли определений).

**Команда идемпотентности**:
```powershell
$g = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\glossary.md"
$raw = Get-Content $g -Raw -Encoding UTF8
$has_def_metaponyatia = $raw -match "(?s)## 7\. Метапонятия фабрики.{0,200}Сигнатурная фигура"
$has_def_failure_modes = $raw -match "(?s)## 6\. Failure modes.{0,200}Демонизация"
$has_band_sections = $raw -match "## 3\.[2-7]"
$ref_to_sv = $raw -match "shared_vocabulary"
@{ has_definitions_in_metaponyatia = $has_def_metaponyatia; has_definitions_in_failure_modes = $has_def_failure_modes; still_has_band_sections = $has_band_sections; references_shared_vocabulary = $ref_to_sv } | ConvertTo-Json
```

**Что делать**:
1. В `glossary.md` оставить **только**:
   - Шапку с пояснением: «трёхязычные эквиваленты для bf-translator; определения — в shared_vocabulary.md».
   - §1 (инварианты обращения du/ты/you).
   - §2 (название серии и томов — если осталось после A-1; иначе — обобщённое).
   - §3.1 «Системные понятия» как чистая таблица RU/DE/EN без описаний.
   - §4 (arenes — правила перевода).
   - §6 переписать как чистую таблицу RU/DE/EN failure modes без определений; колонка «Определение» → удалить, заменить ссылкой «см. shared_vocabulary.md §5».
   - §7 переписать аналогично: таблица переводов RU/DE/EN, без описаний; ссылка «см. shared_vocabulary.md §4».
   - §8 (локализация имён) — оставить.
   - §9 (AI-отпечатки целевого языка) — оставить (это правда переводческая специфика).
2. Удалить разделы §3.2–§3.7 (они привязаны к томам). Если у фабрики останутся универсальные «системные термины из этой темы» — они должны попасть в shared_vocabulary, не в glossary. **Это решение A-1 принимает первым**.

**DoD**:
- [ ] `has_definitions_in_metaponyatia = false`.
- [ ] `has_definitions_in_failure_modes = false`.
- [ ] `still_has_band_sections = false`.
- [ ] `references_shared_vocabulary = true` (минимум 2 ссылки на §4 и §5 shared_vocabulary).

**Controller depth**: light.

---

### M-2. `FACTORY_MAP.md` — синхронизация stale-данных

**Тип**: исполнимый сейчас.
**Категория**: middle / doc-sync.
**Цена**: 10 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$fm = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\FACTORY_MAP.md"
$raw = Get-Content $fm -Raw -Encoding UTF8
$stale_13_2 = $raw -match "§13\.2"
$stale_writer_no_tools = $raw -match "\(нет, после Ф7\)"
$stale_coord_legacy = $raw -match "bf-coordinator.{0,40}legacy, требует обновления"
@{ stale_ref_13_2 = $stale_13_2; stale_writer_no_tools_promise = $stale_writer_no_tools; stale_coord_legacy = $stale_coord_legacy } | ConvertTo-Json
```
DoD: все три False.

**Что делать**:
1. Удалить `§13.2` из строки 19 (или заменить на «см. PART2.md (исторический, закрыт 2026-04-26)»).
2. Строка 54: `bf-writer | opus | Read, Write, Edit (целевое после Ф7: pure-LLM без tools)`.
3. Строка 71: статус bf-coordinator → «v2 routing-only (готов 2026-04-26); расширение writer-loop в Ф8».
4. Также проверить остальные строки на устаревшие пометки про «legacy» — после Pre-Ф8 cleanup большинство агентов получили правки.

**DoD**:
- [ ] Команда идемпотентности возвращает все три False.

**Controller depth**: light.

---

### M-3. `bf-controller.md` — `Get-Content -Encoding UTF8` в примерах multiline-проверок

**Тип**: исполнимый сейчас.
**Категория**: middle / tech.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$c = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-controller.md"
$raw = Get-Content $c -Raw -Encoding UTF8
$bad = $raw -match "Get-Content -Raw[^|]*\|\s*-match"
$good = $raw -match "Get-Content -Raw -Encoding UTF8"
@{ has_unsafe_get_content = $bad; has_safe_example = $good } | ConvertTo-Json
```
DoD: `has_safe_example = true`; `has_unsafe_get_content = false`.

**Что делать**:
1. В `bf-controller.md` все примеры `Get-Content -Raw` дополнить `-Encoding UTF8`.
2. В раздел «Правила команд идемпотентности» добавить отдельный bullet: «Multiline-проверки — `Get-Content -Raw -Encoding UTF8` (страховка PS 5.x, безвредно на PS 7+; см. m-10 закрытого Pre-Ф8 ТЗ)».

**DoD**:
- [ ] Команда идемпотентности возвращает безопасный паттерн.

**Controller depth**: light.

---

### M-4. `bf-editor.md` — beat-by-beat режим: убрать дублирующее чтение MATERIAL

**Тип**: исполнимый сейчас.
**Категория**: middle / efficiency.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$e = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-editor.md"
$raw = Get-Content $e -Raw -Encoding UTF8
$has_note = $raw -match "MATERIAL.{0,30}(уже в Session|впечён|не нужно)"
@{ duplicate_read_note_present = $has_note } | ConvertTo-Json
```

**Что делать**:
1. В `bf-editor.md` раздел «Beat-by-beat (после Ф8 ТЗ)» добавить пометку: «MATERIAL отдельно читать НЕ нужно — он впечён в Session-блок T6 (см. Контракт 8). Читать только: beat_plan.json, log.json, собранный draft, файл голоса (правило C-3 этого ТЗ), verbot_liste».
2. Раздел «Инициализация» (legacy) оставить как есть — он применим только к старой section-by-section схеме.

**DoD**:
- [ ] Пометка про MATERIAL в Session T6 присутствует в beat-by-beat разделе.

**Controller depth**: light.

---

### m-1. `shared_vocabulary.md` §4 — убрать legacy-путь к tonal_compass

**Тип**: исполнимый сейчас.
**Категория**: minor / consistency.
**Цена**: 3 минуты.
**Зависимости**: C-3 (правило выбора файла).

**Команда идемпотентности**:
```powershell
$sv = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\shared_vocabulary.md"
$res = Select-String -Path $sv -Pattern "skills/writer-<book>/references/tonal_compass\.md"
@{ legacy_path_in_section_4 = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. В `shared_vocabulary.md` §4 «тональная карта» путь заменить на: «`<book>/stil_und_ton_XX.md` (новая модель слоя A) или `<book>/tonal_compass.md` (legacy fallback). См. §3.1 и §4.1».

**DoD**:
- [ ] Legacy-путь `skills/writer-<book>/references/tonal_compass.md` удалён.

**Controller depth**: light.

---

### m-2. `CLAUDE.md` правило 5 — добавить пояснение выбора файла голоса

**Тип**: исполнимый сейчас.
**Категория**: minor / wording.
**Цена**: 2 минуты.
**Зависимости**: C-3.

**Команда идемпотентности**:
```powershell
$cl = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\CLAUDE.md"
$res = Select-String -Path $cl -Pattern "приоритет.*stil_und_ton|stil_und_ton.*если существует"
@{ choice_explained = ($null -ne $res) } | ConvertTo-Json
```

**Что делать**:
1. В `CLAUDE.md` правило 5 расширить: «Файл голоса книги — `stil_und_ton_XX.md` если существует, иначе `tonal_compass.md` (legacy). …»

**DoD**:
- [ ] Команда идемпотентности возвращает True.

**Controller depth**: light.

---

### m-3. `voice_principles.md` — определить место в иерархии голоса

**Тип**: исполнимый сейчас (требует архитектурного решения).
**Категория**: minor / arch.
**Цена**: 10 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$vp = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\voice_principles.md"
$sv = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\architecture\shared_vocabulary.md"
$vp_exists = Test-Path $vp
$sv_raw = Get-Content $sv -Raw -Encoding UTF8
$mentioned = $sv_raw -match "voice_principles"
@{ voice_principles_exists = $vp_exists; mentioned_in_hierarchy = $mentioned } | ConvertTo-Json
```

**Что делать**:
1. **Решение**: `voice_principles.md` — это **развёрнутое объяснение** уровня 1 (фабричный голос). Не отдельный уровень. `brand-voice.md` — короткий эталон-карточка; `voice_principles.md` — теория за ним.
2. В `shared_vocabulary.md` §4.1 (иерархия голоса) уровень 1 расширить: «`brand-voice.md` (короткий эталон) + `voice_principles.md` (развёрнутая механика). Оба — фабричный дефолт».
3. В шапку `voice_principles.md` добавить frontmatter `parent: brand-voice.md` и явную фразу: «развёрнутое описание уровня 1 иерархии голоса (см. shared_vocabulary.md §4.1)».

**DoD**:
- [ ] `mentioned_in_hierarchy = true`.
- [ ] voice_principles.md содержит ссылку на shared_vocabulary §4.1.

**Controller depth**: light.

---

### I-1. `bf-pm.md` — проверить наличие явного crash-message

**Тип**: исполнимый сейчас.
**Категория**: information / hygiene.
**Цена**: 5 минут.
**Зависимости**: нет.

**Команда идемпотентности**:
```powershell
$pm = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\.claude\agents\bf-pm.md"
$raw = Get-Content $pm -Raw -Encoding UTF8
$has_crash = $raw -match "DEPRECATED|do not invoke|deprecated-stub|не вызывать|crash|выйти.*ошибк"
@{ has_explicit_crash_message = $has_crash } | ConvertTo-Json
```

**Что делать**:
1. Если `has_explicit_crash_message = false` — добавить в начало инструкции `bf-pm.md` явный блок: «Этот агент DEPRECATED с 2026-04-24. При вызове — немедленно вернуть сообщение `BF_PM_DEPRECATED_USE_RESEARCHER_OR_MATERIAL_AUTHOR` без выполнения каких-либо действий.»
2. Если `true` — пометить как уже OK.

**DoD**:
- [ ] Команда идемпотентности возвращает True.

**Controller depth**: light.

---

### I-2. `_SESSION_START_PROMPT.md` v2.5 — зафиксировать принцип самодостаточности

**Тип**: исполнимый сейчас.
**Категория**: information / process.
**Цена**: 5 минут.
**Зависимости**: A-1 (принцип сначала должен быть закреплён в CLAUDE.md).

**Команда идемпотентности**:
```powershell
$ssp = "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_SESSION_START_PROMPT.md"
$raw = Get-Content $ssp -Raw -Encoding UTF8
$v25 = $raw -match "v2\.5|Версия 2\.5"
$autonomy = $raw -match "самодостаточн|вне фабрики|не ссылаться.*серию"
@{ version_2_5 = $v25; autonomy_principle_present = $autonomy } | ConvertTo-Json
```

**Что делать**:
1. Bump версии до v2.5.
2. В раздел «ЖЁСТКИЕ РАМКИ» добавить: «Фабрика самодостаточна. Любая ссылка из файла фабрики на путь вне `BooksFactory/` для чтения — дефект. См. `CLAUDE.md` правило 7 (или то, куда A-1 положил принцип).»

**DoD**:
- [ ] Версия v2.5 в шапке.
- [ ] Принцип самодостаточности в ЖЁСТКИХ РАМКАХ.

**Controller depth**: light.

---

### P-FINAL. Sanity-check после всех правок

**Тип**: финальный.
**Категория**: validation.
**Цена**: 20 минут.
**Зависимости**: A-1, C-1, C-2, C-3, M-1..M-4, m-1..m-3, I-1, I-2 закрыты.

**Команда идемпотентности**:
```powershell
$report = Test-Path "C:\Users\dmitr\OneDrive\Dokumente\Projects\SpellBooks\BooksFactory\_post_pre_f8_validation_2026-04-XX.md"
@{ validation_report_exists = $report } | ConvertTo-Json
```

**Что делать**:
1. Прогнать сканер A-1 ещё раз — должен дать `external_refs_count = 0`.
2. Прогнать health-check всех 12 команд идемпотентности этого ТЗ — все True (DoD выполнен).
3. Прогнать controller full на 9 артефактах: `bf-editor.md`, `bf-coordinator.md`, `handoff_contracts.md`, `production_state.md`, `shared_vocabulary.md`, `glossary.md`, `FACTORY_MAP.md`, `CLAUDE.md`, `_SESSION_START_PROMPT.md`. Плюс light-проверка остальных 7 агентов на правило C-3.
4. Записать отчёт `_post_pre_f8_validation_2026-04-XX.md` со списком: что изменилось, какие smoke-проверки пройдены, готовность к Ф8 после второго аудита.
5. Финальная отметка: фабрика самодостаточна, статусная модель закрыта, контракт review однозначен — следующий шаг ТЗ Ф8 (writer-loop machine).

**DoD**:
- [ ] Сканер A-1: `external_refs_count = 0`.
- [ ] 12 команд идемпотентности возвращают True.
- [ ] Controller full = accept на 9 артефактах.
- [ ] Light-сверка 7 остальных агентов на C-3 = pass.
- [ ] Отчёт `_post_pre_f8_validation_*.md` создан.
- [ ] В отчёте явная формулировка: «Post-Pre-Ф8 audit fixes закрыт. Фабрика самодостаточна. Готовность к Ф8 = 100%».

**Controller depth**: full (закрывающий).

---

## §6. Регрессии

(пусто на момент создания)

Шаблон записи:
```
### Регрессия R-001 (2026-04-XX)
- **Пункт**: <X>
- **Controller verdict**: block
- **Причина**: <конкретно>
- **Действие**: правка не откачена. Sequence остановлен. Эскалация автору.
- **Решение автора**: <дата> — <выбран вариант X>.
- **Закрыто**: <дата>, sequence возобновлён.
```

---

## §7. Журнал сессий

> Каждая сессия — одна строка.

(пусто — открыт 2026-04-26)

Шаблон:
```
- 2026-04-XX (Sonnet/Opus): <X> закрыт; controller <depth>: accept. <детали в 1-2 предложения>.
```

---

## §8. Финальный чек-лист закрытия ТЗ

- [ ] Все 12 пунктов §1 (A-1, C-1..C-3, M-1..M-4, m-1..m-3, I-1, I-2) имеют статус ВЫПОЛНЕНО.
- [ ] P-FINAL выполнен, отчёт `_post_pre_f8_validation_*.md` зафиксировал «Фабрика самодостаточна, готова к Ф8».
- [ ] Регрессий §6 нет открытых.
- [ ] `_SESSION_START_PROMPT.md` обновлён до v2.5 (с принципом самодостаточности).
- [ ] Controller full на 9 артефактах возвращает `accept`.
- [ ] Сканер A-1 возвращает `external_refs_count = 0`.

После закрытия:
- Версия документа → 2.0.
- Шапка: «Закрыт YYYY-MM-DD».
- Возможно открытие ТЗ Ф8 (writer-loop machine) без блокирующих дефектов на оси целостности и самодостаточности.

---

**Конец ТЗ. Версия 1.0. 2026-04-26 (Post-Pre-Ф8 audit fixes на основе независимого аудита).**
