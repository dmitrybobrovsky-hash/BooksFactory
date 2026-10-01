---
document: SESSION4_LOCAL
created: 2026-10-01
purpose: Установка фабрики v2.9 и переписывание главы 02 KS. Команда автора: «выполни _SESSION4_LOCAL.md».
---

# Сессия 4 — фабрика v2.9 и новая глава 02 (KS)

Работай только в BooksFactory и в папке книги `_outbound/Test3_05.05.2026`.
**Вопросов автору не задавай.** Останавливайся только если шаг невозможен без его решения; всё остальное — в отчёт.
Ничего не удаляй — только перемещай. Глава 01 не трогается.

Почему переписываем: в пилоте писатель не получал секцию MATERIAL (ошибка в `slice_context.py`, исправлена в v2.9) — глава 02 написана по одному плану.

## A. Установка

1. Скопируй с заменой:
   - `_session4_patch/claude_dir/workflows/write-chapter.js` → `.claude/workflows/write-chapter.js`
   - `_session4_patch/claude_dir/agents/bf-critic.md` → `.claude/agents/bf-critic.md`
   - `_session4_patch/claude_dir/agents/bf-writer.md` → `.claude/agents/bf-writer.md`
2. Перемести `_session4_patch/` в `archive/2026-10-01_session4/`.
3. `python tools/validate_factory.py` — ожидается «ЧИСТО».

## B. Пилотную главу — в архив

1. Создай `archive/2026-10-01_session3/KS_glava02_pilot/` и перемести туда из папки книги:
   `02_beats/`, `_work/02/`, `Glava_02_KS_draft.md`, `Glava_02_KS_editor_report.md`, `glava_02_build.log.json`, `_critic_log_Glava_02.json`.
   `02_beat_plan.json` остаётся на месте (в нём уже решение автора по «Таро»).
2. `python tools/manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status material-draft --by session4 --note "пилот v2.8 в архиве: писатель не получал MATERIAL; переписывание на v2.9"`

## C. Проверка контекста

`python tools/slice_context.py --plan _outbound/Test3_05.05.2026/02_beat_plan.json --beat-id 13 --material _outbound/Test3_05.05.2026/MATERIAL_Glava_02_KS.md --out _outbound/Test3_05.05.2026/_work/02/check_13.md`
В файле в разделе «3. MATERIAL — секция этого beat-а» должен быть текст «Секции 5» (а не заглушка), есть разделы 3a–3c. Если нет — остановись, запиши в отчёт.

## D. Написание главы

Запусти `/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], max_words: 6325, antithesis_budget: 8 }`

Если workflow остановился из-за лимита сессии — после сброса лимита возобнови тот же прогон (`resumeFromRunId`), это не ошибка. Если `stopped` по другой причине или `needs_author` — не перезапускай, запиши в отчёт.

## E. Редактура

Если глава собрана: `bf-editor` по `Glava_02_KS_draft.md` (отчёт — в папку книги), затем
`python tools/manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status review --by bf-editor`.
Правки по отчёту не вносить.

## F. Сравнение писателей (только если лимит сессии позволяет; иначе пропусти и отметь)

`/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], antithesis_budget: 8, writer_model: "sonnet", beats_tag: "_sonnet", end_beat: 4 }`
Пишет beat-ы 1–4 в отдельную папку `02_beats_sonnet/`, основную главу не трогает.

## G. Отчёт — `_SESSION4_LOCAL_REPORT.md`

- A–C: результат.
- D: итог workflow; по каждому beat-у — слова, итерации, вердикты; что назначил критик главы (summary, какие beat-ы правились); `problems` финальной проверки главы; объём; время; расход токенов и число агентов (из уведомлений workflow), отдельно по каждому заходу.
- E: вердикт редактора и его точки кратко; сравни с отчётом пилота (`archive/2026-10-01_session3/KS_glava02_pilot/Glava_02_KS_editor_report.md`): какие из пяти прежних точек ушли, какие остались, что нового.
- F: сделано или нет; расход токенов.
- Всё необычное.
