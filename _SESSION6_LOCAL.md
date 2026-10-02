---
document: SESSION6_LOCAL
created: 2026-10-02
purpose: Запасной вариант _SESSION6_CLOUD.md на компьютере. Команда автора: «выполни _SESSION6_LOCAL.md».
---

# Сессия 6 (локально) — правки цикла 2 и финальная проверка главы 02 (KS)

Работай только в BooksFactory и в папке книги. **Вопросов автору не задавай.** Ничего не удаляй. Проверь, что на C: ≥ 5 ГБ.

## 0. Установка
Скопируй с заменой `_session6_patch/claude_dir/workflows/write-chapter.js` → `.claude/workflows/`, `_session6_patch/claude_dir/agents/bf-writer.md` → `.claude/agents/`; перемести `_session6_patch/` в `archive/2026-10-02_session6/`; `python tools/validate_factory.py` — «ЧИСТО». Скопируй `02_beats/` в `archive/2026-10-02_session6/02_beats_before_fixes/`.

## 1. Правки цикла 2 (с проверкой)
Запусти `/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], max_words: 6000, antithesis_budget: 8, fixes_file: "_outbound/Test3_05.05.2026/_work/02/editor_fixes_cycle2.json" }`
Ожидается после правок: объём ≤ 6000, антитез ≤ 8 (сейчас 6090 и 11 — скрипт и редактор совпадают).

## 2. Редактор, цикл 3 из 3
`bf-editor` по `Glava_02_KS_draft.md`: проверить точки цикла 2 (`Glava_02_KS_editor_report_cycle2.md`); отчёт — `Glava_02_KS_editor_report_cycle3.md`. Если глава чистая — `manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status clean --by bf-editor`. Если нет — статус не трогать, в отчёте перечислить, что осталось (эскалация к автору).

## 3. Отчёт — `_SESSION6_LOCAL_REPORT.md` (как в облачном варианте).
