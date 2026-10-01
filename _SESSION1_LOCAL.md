---
document: SESSION1_LOCAL
created: 2026-10-01
purpose: Локальный шаг сессии 1. Команда автора: «выполни _SESSION1_LOCAL.md».
---

# Сессия 1 — локальный шаг

Работай только в директории BooksFactory. Ничего не удаляй — только перемещай.

## A. Установка

1. Скопируй с перезаписью:
   - `_session1_patch/claude_dir/agents/bf-researcher.md` → `.claude/agents/bf-researcher.md`
   - `_session1_patch/claude_dir/settings.json` → `.claude/settings.json`
2. Перемести `_session1_patch/` в `archive/2026-10-01_session1/`.
3. Перемести `_outbound/Test3_05.05.2026/ZOTERO_KS.md` и `_outbound/Test3_05.05.2026/ZOTERO_KS_ISBN.txt` в `archive/2026-10-01_session1/`.

## B. Проверка инструментов на книге KS

Папка книги: `_outbound/Test3_05.05.2026`.

1. `python tools/validate_factory.py` — ожидается «ЧИСТО».
2. `python tools/verify_sources.py --pool _outbound/Test3_05.05.2026/quellen_pool_KS.md --verified _outbound/Test3_05.05.2026/SOURCES_VERIFIED_KS.md --out _outbound/Test3_05.05.2026/SOURCES_CHECK_KS.md` — сохрани вывод (здесь каталоги доступны, в облаке — нет).
3. `python tools/manifest.py init --book-dir _outbound/Test3_05.05.2026 --code KS --title "Карты на стол" --lang ru --scan` — сохрани вывод.
4. `python tools/assemble_chapter.py --plan _outbound/Test3_05.05.2026/01_beat_plan.json --beats-dir _outbound/Test3_05.05.2026/01_beats --out _testing/glava01_check.md` — сохрани вывод; затем перемести `_testing/glava01_check.md` в `archive/2026-10-01_session1/`.

## C. Отчёт

Запиши `_SESSION1_LOCAL_REPORT.md`: результат A и полный вывод B1–B4. Больше ничего не меняй.
