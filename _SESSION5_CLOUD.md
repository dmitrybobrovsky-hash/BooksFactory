---
document: SESSION5_CLOUD
created: 2026-10-02
purpose: То же, что _SESSION5_LOCAL.md, но в облачной сессии Claude Code на репозитории BooksFactory. Команда автора: «выполни _SESSION5_CLOUD.md».
---

# Сессия 5 (облако) — правки главы 02 (KS)

Ты работаешь в облачной копии репозитория. Фабрика v2.10 уже в репозитории — установка не нужна.
**Вопросов автору не задавай.** Останавливайся только если шаг невозможен; всё остальное — в отчёт. Ничего не удаляй.

## 0. Проверка среды
`python3 --version`; `python3 tools/validate_factory.py` — «ЧИСТО»;
`python3 tools/lint_chapter.py --plan _outbound/Test3_05.05.2026/02_beat_plan.json --beats-dir _outbound/Test3_05.05.2026/02_beats --max-words 6000` — ожидается: антитез ≈14, «Роршах» 5 > 1, связка «отсюда» 6, объём 6135 > 6000.
Если вызов `python` не работает, а `python3` работает — в командах workflow это не проблема, исполнитель сам выберет рабочую команду; отметь в отчёте.

## 1. Правки по отчёту редактора
Скопируй `02_beats/` в `archive/2026-10-02_session5/02_beats_before_fixes/`.
Запусти `/write-chapter` с данными:
`{ book_dir: "_outbound/Test3_05.05.2026", code: "KS", chapter: "02", lang: "ru", word_limits: ["паттерн=2", "Таро=3"], max_words: 6000, antithesis_budget: 8, fixes_file: "_outbound/Test3_05.05.2026/_work/02/editor_fixes_cycle1.json" }`
Если `/write-chapter` в облаке недоступен — остановись и запиши это в отчёт первой строкой (это главный вопрос пробного прогона).

## 2. Редактор, цикл 2
`bf-editor` по `Glava_02_KS_draft.md`, цикл 2 из 3: выполнены ли точки цикла 1 (отчёт — `Glava_02_KS_editor_report_cycle2.md`). Если глава чистая — `python3 tools/manifest.py set --book-dir _outbound/Test3_05.05.2026 --chapter 02 --status clean --by bf-editor`.

## 3. Отчёт и сохранение
`_SESSION5_CLOUD_REPORT.md`: среда (шаг 0), итог workflow, какие beat-ы правились, объём до/после, `problems`, токены, время; вердикт редактора и закрытые точки; всё необычное.
Сохрани всё в репозиторий: commit и push (в текущую ветку сессии). Автору напиши одну строку: «Готово, отчёт в репозитории».
