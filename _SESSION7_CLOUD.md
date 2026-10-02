---
document: SESSION7_CLOUD
created: 2026-10-02
purpose: Полностью автономный прогон в облаке (вариант B, без Workflow) — гуманизация главы 02 и полный цикл главы 03 KS от плана до гуманизации. Команда автора: «выполни _SESSION7_CLOUD.md».
---

# Сессия 7 (облако, автономно) — глава 02 → humanized, глава 03 → план … humanized

## Режим: полная автономия

Автор поручил провести работу **без остановок и без вопросов**. Ты — **оркестратор**: в этой сессии ты отвечаешь и за стратега, и за решения, которые обычно ждут автора. Агенты (через Agent/Task) пишут и судят; цикл, счётчики, решения и контроль — твои.

1. **Вопросов не задавать. Не останавливаться на «ждать автора».** Там, где роль агента предписывает показать результат автору и ждать (bf-planner, bf-editor, bf-material-author), ты принимаешь решение сам:
   - есть рекомендация редактора или вариант по умолчанию — берёшь его;
   - нет — берёшь вариант, ближе всего к MATERIAL и `stil_und_ton_KS.md`;
   - каждое такое решение — строкой в раздел «Решения без автора» отчёта (что, почему, где в тексте). Автор пересмотрит их потом.
2. **Необратимого не делать.** Ничего не удалять — только перенос в `archive/2026-10-02_session7/`. Не трогать главы 00, 01, 04, 05; не менять `MATERIAL_*`, `verbot_liste_KS.md`, `stil_und_ton_KS.md`, `anweisungen_KS.md`, `_skvoznye_formuly_KS.md`, `quellen_pool_KS.md`, `.claude/`, `tools/`. Новых источников и имён учёных в текст не вносить (только то, что есть в MATERIAL и `quellen_pool_KS.md`).
3. **Сохранность прогресса.** После каждого этапа (A1…A4, B1…B7): запись в журнал `_SESSION7_LOG.md` (корень фабрики: этап, итог, ключевые числа, время) → `git commit` → `git push` в ветку сессии. **Если сессия запущена повторно** — прочитай `_SESSION7_LOG.md` и продолжи с первого незавершённого этапа, сделанное не повторяй.
4. **Предохранители.** Не больше 170 вызовов агентов за сессию (считай). Если лимит близко — доведи текущий этап до сохранённого состояния и переходи к финалу (аудит + отчёт). Застрявший шаг не блокирует остальное: правило выхода у каждого этапа ниже.
5. **Время** — по Берлину: команды `manifest.py` запускай как `TZ=Europe/Berlin python3 tools/manifest.py …`; после первой записи проверь `python3 tools/manifest.py show --book-dir B`, что время местное. Время в журнале и отчёте — `TZ=Europe/Berlin date`.
6. Команды — `python3`. Хуки PowerShell в облаке не работают — это ожидаемо.

## Обозначения

- `B` = `_outbound/Test3_05.05.2026`; `NN` — номер главы.
- План `B/NN_beat_plan.json`, beat-ы `B/NN_beats/`, рабочая папка `B/_work/NN/`, контексты `B/_work/NN/beat_N_context.md`.
- `FL` (флаги проверок) = `--verbot B/verbot_liste_KS.md --formulas B/_skvoznye_formuly_KS.md --lang ru --antithesis-budget 8 --limit паттерн=2` + для главы 02 ещё `--limit Таро=3` + для главы 03 лимиты из поля `word_limits` плана, если планировщик его задал.
- `lint_chapter.py` принимает из FL только `--lang`, `--antithesis-budget`, `--limit` (не `--verbot`/`--formulas`) + `--max-words 6000`.
- **Тексты заданий агентам бери из `.claude/workflows/write-chapter.js`** (это эталон алгоритма): `writerPrompt`, промпт критика с `CRITIC_POLICY`, промпт «критик главы», `applyFix`, «добор после правок». Ты исполняешь этот алгоритм вручную; где тут написано иначе — главнее эта инструкция.
- Писатель — `bf-writer`, модель **opus**. Критик beat-а и критик главы — модель **sonnet**. Редактор, планировщик, гуманизатор, проверяющий — **opus**.

## Подготовка

Создай `archive/2026-10-02_session7/`, скопируй туда `B/02_beats/`, `B/Glava_02_KS_draft.md`, `B/book_manifest.json`. `python3 tools/validate_factory.py` — должно быть ЧИСТО (если нет — запиши в журнал и продолжай). Заведи `_SESSION7_LOG.md`.

---

# ЧАСТЬ A. Глава 02: микроправки → гуманизация

## A1. Микроправки M1, M2
Источник — `B/Glava_02_KS_editor_report_cycle3.md`, раздел «Микроправки». Выполни по алгоритму `applyFix` (писатель видит соседние beat-ы; проверка `lint_beat.py … FL`; не больше 2 попыток):
- **beat 5 (M1):** «Упрёк … бил по пятнам точно, потому что тот диагностом себя заявлял» — у «тот» нет антецедента. Замени «по пятнам» на «по старому тесту». Больше ничего не меняй.
- **beat 8 (M2):** рамка кейса «Эта сцена иллюстрирует механизм. Такие истории … её …» — согласование и дальняя отсылка. Ориентир редактора: «Сцена с советом иллюстрирует механизм. Место таких историй — второй и третий уровень знания: выдай такую историю за результат, и она станет тем самым фольклором». ±3 слова, без антитезы.

Затем сборка и проверка главы:
`python3 tools/assemble_chapter.py --plan B/02_beat_plan.json --beats-dir B/02_beats --out B/Glava_02_KS_draft.md --log B/glava_02_build.log.json --lang ru`
`python3 tools/lint_chapter.py --plan B/02_beat_plan.json --beats-dir B/02_beats --max-words 6000 --lang ru --antithesis-budget 8 --limit паттерн=2 --limit Таро=3 --out B/_work/02/chapter_lint_session7.json` — `problems` должно быть пусто.
Выход: если правка не проходит за 2 попытки — верни beat из архива, запиши в «Решения без автора», передай пункт гуманизатору как обязательный.

## A2. Заморозка чистовика
Скопируй `B/Glava_02_KS_draft.md` → `B/Glava_02_KS_clean.md`; во frontmatter: `status: clean`, `clean_from: Glava_02_KS_draft.md`, `editor_cycle: 3`, `editor_verdict: clean`. Чистовик дальше не правится.

## A3. Гуманизация
Агент `bf-humanizer` (opus). Задание:
- роль — `.claude/agents/bf-humanizer.md`, модуль `skills/humanizer/ru/SKILL.md` и его references; голос — `B/stil_und_ton_KS.md`; запреты — `B/verbot_liste_KS.md`;
- вход `B/Glava_02_KS_clean.md` (только читать), выход — **новый файл** `B/Glava_02_KS_humanized.md` с frontmatter по образцу `B/Glava_00_KS_humanized.md` (`status: humanized`, `humanized_from`, `clean_from`, `total_words`, `language: RU`);
- **на усмотрение гуманизатора** — примечания П1–П6 из отчёта цикла 3 (перечисли их в задании полностью);
- рамки: смысл, порядок аргументов, заголовки `## N. …`, обращение «ты», цитируемые образы (список «Цитируемые фразы и образы» из отчёта цикла 3) — сохранить; антитез «не X, а Y» не добавлять (в главе ровно бюджет — 8); объём — не больше чистовика (допуск +1 %), сокращение до −8 % допустимо; новых утверждений об исследованиях, имён, чисел — нет;
- в конце — самопроверка на реинтродукцию (шаг модуля) и список сделанных изменений по типам в `B/_work/02/humanizer_notes.md`.

## A4. Контроль гуманизации
**Скрипт** (сравни чистовик и результат одинаковыми флагами):
`python3 tools/lint_beat.py --beat B/Glava_02_KS_clean.md FL > B/_work/02/lint_clean.json`
`python3 tools/lint_beat.py --beat B/Glava_02_KS_humanized.md FL > B/_work/02/lint_humanized.json`
(код выхода 1 — не ошибка: флаг `antithesis_overuse` срабатывает, потому что вся глава считается одним beat-ом.) Критерии прохода: `facts.antithesis.chapter` ≤ 8; `word_count` в пределах −8 %…+1 % от чистовика; `signature_figure.chapter` не больше, чем у чистовика; запрещённых фраз из verbot не прибавилось; заголовки `## ` совпадают (сравни `grep '^## '`).

**Независимая проверка** — свежий агент `bf-editor` (opus), который не видел работу гуманизатора. Задание: сравнить `B/Glava_02_KS_clean.md` и `B/Glava_02_KS_humanized.md` по абзацам; найти (1) сдвиги смысла и утраченные утверждения, (2) потерянные цитируемые образы, (3) вернувшиеся дефекты из отчётов редактора циклов 1–3 (`B/Glava_02_KS_editor_report*.md`), (4) новые неподтверждённые утверждения, (5) порчу голоса по `stil_und_ton_KS.md`; вердикт `pass` / `fail` со списком конкретных мест (цитата + что не так). Отчёт — `B/Glava_02_KS_humanizer_check.md`. Мелочь, не меняющая смысла, — не повод для `fail`.

**Решение:**
- скрипт ок и `pass` → `TZ=Europe/Berlin python3 tools/manifest.py set --book-dir B --chapter 02 --status humanized --by bf-humanizer`;
- иначе → ещё один проход `bf-humanizer` по `B/Glava_02_KS_humanized.md` строго по списку замечаний (прежний вариант — в архив), затем повтор контроля;
- после второго `fail` → статус остаётся `clean`, файл `_humanized` остаётся как черновик для автора; запиши в «Решения без автора» и переходи к части B.

---

# ЧАСТЬ B. Глава 03: полный цикл

Глава 03 сейчас `material-draft`. **MATERIAL принимается как есть** (решение без автора — запиши). Целевой объём главы 5500, потолок 6000, Draft Fat ≈ 6200.

## B1. План
Агент `bf-planner` (opus). Вход: `B/MATERIAL_Glava_03_KS.md` (длинный — читать частями), `B/stil_und_ton_KS.md`, `B/anweisungen_KS.md`, `B/case_protocol_KS.md`, `B/arenen_pool_KS.md`, `B/02_beat_plan.json` (образец формата и чтобы не повторять стиль-якоря подряд). **Выход — `B/03_beat_plan.json`** (не в `_drafts/`). Требования:
- формат как у `02_beat_plan.json`: верх — `chapter_number`, `chapter_title`, `chapter_target_words` (5500), `beats_count`, `sum_target_words`, `street_calibration_beats`, `pattern_budget`; у beat-а — `beat_id`, `section`, `thema`, `target_words`, `style_anchor`, `quote_before`, `material_refs`, `constraints`, `street_calibration`, `target_provocation`, `is_last_beat`;
- `section` — по канону «1. Название» (без «§», без «Секция»), т.к. сборщик выводит его заголовком;
- 13–17 beat-ов, сумма 5900–6500, каждая секция MATERIAL — минимум 2 beat-а; case_protocol KS-R02 и микрокейсы из MATERIAL — по beat-ам;
- по желанию — поле `word_limits` (["слово=N", …]) для слов, которые в главе легко пережать (например, имена теоретиков); `паттерн=2` действует всегда;
- self-check планировщика обязателен.

## B2. Проверка плана (ты)
JSON валиден; все поля на месте; сумма в коридоре; каждая секция MATERIAL покрыта ≥2 beat-ами; `section` без «§»; ровно один `is_last_beat: true`. Пробный срез: `python3 tools/slice_context.py --plan B/03_beat_plan.json --beat-id 1 --material B/MATERIAL_Glava_03_KS.md --beats-dir B/03_beats --voice B/stil_und_ton_KS.md --verbot B/verbot_liste_KS.md --formulas B/_skvoznye_formuly_KS.md --lang ru --antithesis-budget 8 --limit паттерн=2 --out B/_work/03/beat_1_context.md` — без ошибок, секция MATERIAL в контексте не пустая. Не прошло → один повтор планировщика со списком замечаний; после второго провала — исправь поля плана сам (структуру, не содержание) и запиши.

## B3. Beat-ы (алгоритм фазы «Beats» из write-chapter.js)
Для каждого beat-а по порядку: `slice_context.py` (как в B2, со своим `--beat-id` и лимитами) → писатель → критик (sonnet; сначала `lint_beat.py --beat … --plan … --beat-id … FL --chapter-beats B/03_beats`, его JSON — факты) → до 3 итераций.
- **Журнал главы** (реквизит и тезисы принятых beat-ов) веди в `B/_work/03/ledger.json` и передавай писателю и критику, как в `writerPrompt`.
- Журнал критика — `B/_critic_log_Glava_03.json` (beat, итерация, слова, вердикт, floor, hard_flags, notes, minor).
- **Выход вместо остановки** (в workflow здесь `needs_author`): после 3 итераций без принятия — если `verdict_floor: pass`, прими последний вариант, замечания критика перенеси в `minor`; если `fail` — 4-я попытка писателя только по `hard_flags`; если и она не прошла — прими, пометь beat как «открытый» в журнале: его обязан закрыть проход по главе. Всё — в «Решения без автора».

## B4. Проход по главе
Промпт «критик главы» из write-chapter.js (sonnet): `chapter_preview.md`, `lint_chapter.py … --out B/_work/03/chapter_lint.json`, план, `quellen_pool_KS.md`, все `minor` и «открытые» beat-ы. Не больше 8 правок → `applyFix` каждой (≤2 попытки) → `lint_chapter … --out B/_work/03/chapter_lint_after_fixes.json` → если `problems` не пусто — добор ≤4 правок с `target_words`.

## B5. Сборка
`python3 tools/assemble_chapter.py --plan B/03_beat_plan.json --beats-dir B/03_beats --out B/Glava_03_KS_draft.md --log B/glava_03_build.log.json --lang ru`; финальный `lint_chapter … --out B/_work/03/chapter_lint_final.json`; `TZ=Europe/Berlin python3 tools/manifest.py set --book-dir B --chapter 03 --status draft --by write-chapter`.

## B6. Редактор — до 3 циклов
**Цикл 1.** Агент `bf-editor` (opus), режим beat-by-beat из его роли: план, build log, черновик, MATERIAL, `anweisungen_KS.md`, `stil_und_ton_KS.md`, `verbot_liste_KS.md`, `chapter_lint_final.json` как факты. В задании прямо: «Автор в этой сессии не отвечает. Точки, где нужен выбор автора, дай с вариантом по умолчанию. В конце — вердикт clean / нужны правки и для каждой точки — beat-ы и инструкция писателю». Отчёт — `B/Glava_03_KS_editor_report.md`. Статус → `review` (`--by bf-editor`).
**Правки.** Ты переводишь точки отчёта в `B/_work/03/editor_fixes_cycleN.json` — `[{beat_id, problem, instruction, target_words?}]`, не больше 10 beat-ов; выбор по умолчанию — в «Решения без автора». Затем `applyFix` → контроль после правок → добор ≤4 → сборка → `lint_chapter` (`problems` пусто).
**Циклы 2–3.** `bf-editor` проверяет точки предыдущего цикла по новому черновику (образец формы — `B/Glava_02_KS_editor_report_cycle3.md`); отчёт `…_editor_report_cycleN.md`. Перед каждым циклом правок — копия `B/03_beats/` в архив сессии.
**Выход:** вердикт `clean` → `manifest … --chapter 03 --status clean --by bf-editor` → B7. Если после цикла 3 не `clean` — глава остаётся `review`, B7 не делается, запиши, какие точки открыты, и переходи к финалу.

## B7. Гуманизация главы 03
Как A2–A4, с заменой 02 → 03: `Glava_03_KS_clean.md` (`editor_cycle` — номер последнего цикла), `Glava_03_KS_humanized.md`, проверка `Glava_03_KS_humanizer_check.md`, лимиты FL главы 03 (без `Таро=3`). Микроправки последнего отчёта редактора, если он их назвал, — внести до заморозки (как A1).

---

# ФИНАЛ

## F1. Независимый аудит
Свежий агент `general-purpose` (opus), который не участвовал в работе. Задание: по `_SESSION7_LOG.md` и черновику отчёта проверить **каждое** число и утверждение по файлам — `python3 tools/manifest.py show`, json-файлы lint, журналы критика, наличие файлов, статусы во frontmatter, что главы 00/01/04/05, MATERIAL, verbot, stil_und_ton, `.claude/`, `tools/` не изменены (`git diff --stat` от начальной точки сессии), что ничего не удалено (`git diff --diff-filter=D`). Вердикт и расхождения — `_SESSION7_AUDIT.md`. Расхождения ты исправляешь **в отчёте** (текст глав по итогам аудита не правится).

## F2. Отчёт `_SESSION7_CLOUD_REPORT.md`
1. **Для автора** (вверху, 4–6 строк, простыми словами, без имён файлов): что с главой 02, что с главой 03, где автору стоит посмотреть в первую очередь.
2. **Решения без автора** — пронумерованный список: решение, причина, место в тексте.
3. По главам: объём и антитезы по этапам; итерации по beat-ам; «открытые» beat-ы; вердикты редактора по циклам; итог контроля гуманизации.
4. Ресурсы: число агентов по ролям, токены (если видны), время начала/конца по Берлину.
5. Итог аудита F1.
Запись в `B/_SESSION_STATE.md` (новая запись сверху, по образцу предыдущих). Commit, push в ветку сессии. Автору — одна строка: «Готово, отчёт в репозитории».
