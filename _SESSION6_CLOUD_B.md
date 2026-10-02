---
document: SESSION6_CLOUD_B
created: 2026-10-02
purpose: Цикл 3 главы 02 KS в облачной сессии БЕЗ инструмента Workflow — тот же алгоритм, что режим правки write-chapter.js, но вручную через агентов. Команда автора: «выполни _SESSION6_CLOUD_B.md».
---

# Сессия 6B (облако, без Workflow) — правки цикла 2 и финальная проверка главы 02 (KS)

В облачной сессии нет инструмента Workflow (проверено в сессии 6). Ты сам исполняешь алгоритм режима правки из `.claude/workflows/write-chapter.js` (блок `applyFix` и «Контроль после правок»), запуская агентов через инструмент Agent/Task.
**Вопросов автору не задавай.** Ничего не удаляй. Команды — `python3`. Пиши журнал своих шагов в `_outbound/Test3_05.05.2026/_critic_log_Glava_02_fixes2.json`.
Хуки PowerShell в облаке не работают — это ожидаемо, не останавливайся из-за их ошибок.

Обозначения: B=`_outbound/Test3_05.05.2026`, план `B/02_beat_plan.json`, beat-ы `B/02_beats/`, контексты `B/_work/02/beat_N_context.md`, правки `B/_work/02/editor_fixes_cycle2.json`.
Флаги lint: `--verbot B/verbot_liste_KS.md --formulas B/_skvoznye_formuly_KS.md --lang ru --antithesis-budget 8 --limit паттерн=2 --limit Таро=3`.

## 0. Подготовка
Скопируй `B/02_beats/` в `archive/2026-10-02_session6/02_beats_before_fixes/`. `python3 tools/lint_chapter.py --plan B/02_beat_plan.json --beats-dir B/02_beats --max-words 6000` — ожидается 6090 > 6000, антитез 11 > 8.

## 1. Правки (по очереди, для каждой записи файла правок)
1. Запусти агента `bf-writer` (модель opus) с заданием: роль — `.claude/agents/bf-writer.md`; контекст — `B/_work/02/beat_N_context.md`; «В файле `B/02_beats/beat_N.md` — принятый вариант. Исправь ТОЛЬКО это: Проблема: … Инструкция: …» (из файла правок дословно); «Объём — не больше прежнего, если инструкция прямо не требует вставки; вставку компенсируй сокращением в этом же beat-е. Новых антитез («не X, а Y», «X, а не Y», «это не X, это Y») не добавляй. Можно прочитать `beat_{N-1}.md` и `beat_{N+1}.md`, только чтобы не порвать стык. Запиши только прозу beat-а в тот же файл».
2. Проверь: `python3 tools/lint_beat.py --beat B/02_beats/beat_N.md --plan B/02_beat_plan.json --beat-id N <флаги lint>`. Если есть `hard_flags` (кроме `volume_short`) или в правке был `target_words` и объём > target×1.05 — ещё один вызов писателя с этими замечаниями. Больше двух попыток на правку не делай.
3. Запиши в журнал: beat, попытка, слова, hard_flags.

## 2. Контроль после правок
`python3 tools/lint_chapter.py --plan B/02_beat_plan.json --beats-dir B/02_beats --max-words 6000 <флаги lint> --out B/_work/02/chapter_lint_after_fixes2.json`.
Если `problems` не пусто — сам (как критик главы) выбери не больше 4 точечных правок, которые снимают ИМЕННО эти превышения (сокращение повторов и служебных мостиков; антитезы — в прямое утверждение, кроме сигнатурных фигур и quote_before плана), и выполни их по шагу 1.

## 3. Сборка
`python3 tools/assemble_chapter.py --plan B/02_beat_plan.json --beats-dir B/02_beats --out B/Glava_02_KS_draft.md --log B/glava_02_build.log.json --lang ru`, затем финальный `lint_chapter` (как в шаге 2, `--out B/_work/02/chapter_lint_final2.json`).

## 4. Редактор, цикл 3 из 3
Агент `bf-editor`: проверить точки цикла 2 (`B/Glava_02_KS_editor_report_cycle2.md`) по новому `B/Glava_02_KS_draft.md`; отчёт — `B/Glava_02_KS_editor_report_cycle3.md`. Если глава чистая — `python3 tools/manifest.py set --book-dir B --chapter 02 --status clean --by bf-editor`.

## 5. Отчёт и сохранение
`_SESSION6_CLOUD_B_REPORT.md`: какие beat-ы правились и сколько попыток, объём и антитезы до/после, `problems`, добор; вердикт редактора; число агентов и токены, если видны; время. Commit и push в ветку сессии. Автору — одна строка: «Готово, отчёт в репозитории».
