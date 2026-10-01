---
document: SESSION2B_LOCAL
created: 2026-10-01
purpose: Доводка сессии 2. Команда автора: «выполни _SESSION2B_LOCAL.md».
---

# Сессия 2b — доводка

Работай только в директории BooksFactory. Ничего не удаляй — только перемещай.
**Вопросов автору не задавай.** Всё — в отчёт.

## A. Установка

1. Скопируй `_session2b_patch/claude_dir/workflows/write-chapter.js` → `.claude/workflows/write-chapter.js` (с перезаписью).
2. Перемести `_session2b_patch/` в `archive/2026-10-01_session2/`.

## B. Проверка

1. Убедись, что `tools/verify_sources.py` — новая версия: в файле должна встречаться строка `confirmed_manual`. Если её нет — отметь в отчёте «tools/verify_sources.py старой версии» и пропусти пункт 3.
2. `python tools/validate_factory.py` — ожидается «ЧИСТО».
3. `python tools/verify_sources.py --pool _outbound/Test3_05.05.2026/quellen_pool_KS.md --verified _outbound/Test3_05.05.2026/SOURCES_VERIFIED_KS.md --out _outbound/Test3_05.05.2026/SOURCES_CHECK_KS.md` — ожидается 14 × ✅, код выхода 0.
4. `claude --version` — запиши версию.
5. Проверь, доступен ли тебе инструмент Workflow (есть ли он среди твоих инструментов). Запиши: да / нет.

## C. Отчёт

Запиши `_SESSION2B_LOCAL_REPORT.md`: A, B1–B5.
