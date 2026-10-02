---
document: SESSION5_LOCAL
created: 2026-10-02
purpose: Фабрика v2.10 и правка главы 02 KS по отчёту редактора. Команда автора: «выполни _SESSION5_LOCAL.md».
---

# Сессия 5 — v2.10 и правки главы 02 (KS)

Работай только в BooksFactory и в папке книги `_outbound/Test3_05.05.2026`.
**Вопросов автору не задавай.** Останавливайся только если шаг невозможен; всё остальное — в отчёт. Ничего не удаляй — только перемещай.
Перед стартом проверь свободное место на C: (нужно ≥ 5 ГБ); если меньше — остановись и запиши в отчёт.

## A. Установка
1. Скопируй с заменой: `_session5_patch/claude_dir/workflows/write-chapter.js` → `.claude/workflows/write-chapter.js`; `_session5_patch/claude_dir/agents/bf-planner.md` → `.claude/agents/bf-planner.md`.
2. Перемести `_session5_patch/` в `archive/2026-10-02_session5/`.
3. `python tools/validate_factory.py` — «ЧИСТО».
4. `python tools/lint_chapter.py --plan _outbound/Test3_05.05.2026/02_beat_plan.json --beats-dir _outbound/Test3_05.05.2026/02_beats --max-words 6000` — ожидается: антитез ≈14, «Роршах» 5 > 1, связка «отсюда» 6, объём 6135 > 6000. Если цифры другие — запиши в отчёт.

## B. Правки по отчёту редактора
1. Скопируй папку `02_beats` в `archive/2026-10-02_session5/02_beats_before_fixes/` (копия, не перенос).
2. Запусти `/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], max_words: 6000, antithesis_budget: 8, fixes_file: "_outbound/Test3_05.05.2026/_work/02/editor_fixes_cycle1.json" }`
Это режим правки: пишутся только beat-ы из файла правок, затем сборка. Статус главы не меняется.

## C. Редактор, цикл 2
`bf-editor` по `Glava_02_KS_draft.md`, цикл 2 из 3: проверить, выполнены ли точки цикла 1 (отчёт — `Glava_02_KS_editor_report_cycle2.md`). Если редактор признаёт главу чистой —
`python tools/manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status clean --by bf-editor`. Иначе статус не трогать.

## D. Отчёт — `_SESSION5_LOCAL_REPORT.md`
A: результат и цифры шага 4. B: итог workflow, какие beat-ы правились, объём до/после, `problems` финальной проверки, токены и время. C: вердикт и точки редактора кратко; какие точки цикла 1 закрыты. Всё необычное.
