---
document: SESSION6_CLOUD
created: 2026-10-02
purpose: Цикл 3 главы 02 KS в облачной сессии Claude Code на репозитории BooksFactory. Команда автора: «выполни _SESSION6_CLOUD.md».
---

# Сессия 6 (облако) — правки цикла 2 и финальная проверка главы 02 (KS)

Ты работаешь в облачной копии репозитория; фабрика v2.10.1 уже в нём, установка не нужна.
**Вопросов автору не задавай.** Останавливайся только если шаг невозможен; всё остальное — в отчёт. Ничего не удаляй.

## 0. Среда
`python3 --version`; `python3 tools/validate_factory.py` — «ЧИСТО»;
`python3 tools/lint_chapter.py --plan _outbound/Test3_05.05.2026/02_beat_plan.json --beats-dir _outbound/Test3_05.05.2026/02_beats --max-words 6000` — ожидается: объём 6090 > 6000, антитез 11 > 8.
Если `/write-chapter` в облаке недоступен — остановись и напиши это первой строкой отчёта (главный вопрос пробы облака).
Скопируй `_outbound/Test3_05.05.2026/02_beats/` в `archive/2026-10-02_session6/02_beats_before_fixes/`.

## 1. Правки цикла 2 (с проверкой)
Запусти `/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], max_words: 6000, antithesis_budget: 8, fixes_file: "_outbound/Test3_05.05.2026/_work/02/editor_fixes_cycle2.json" }`
Ожидается после правок: объём ≤ 6000, антитез ≤ 8 (сейчас 6090 и 11 — скрипт и редактор совпадают).

## 2. Редактор, цикл 3 из 3
`bf-editor` по `Glava_02_KS_draft.md`: проверить точки цикла 2 (`Glava_02_KS_editor_report_cycle2.md`); отчёт — `Glava_02_KS_editor_report_cycle3.md`. Если глава чистая — `manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status clean --by bf-editor`. Если нет — статус не трогать, в отчёте перечислить, что осталось (эскалация к автору).

## 3. Отчёт и сохранение
`_SESSION6_CLOUD_REPORT.md`: среда; итог workflow (какие beat-ы правились, повторы после проверки, добор), объём и антитезы до/после, `problems`; токены и время; вердикт редактора. Сохрани всё: commit и push в ветку сессии. Автору — одна строка: «Готово, отчёт в репозитории».
