---
document: SESSION2_LOCAL
created: 2026-10-01
purpose: Локальный шаг сессии 2. Команда автора: «выполни _SESSION2_LOCAL.md».
---

# Сессия 2 — локальный шаг

Работай только в директории BooksFactory. Ничего не удаляй — только перемещай.
**Вопросов автору не задавай.** Всё, что заметишь, — в отчёт; вопрос допустим только если без решения автора шаг невозможен.

## A. Установка (затем перезапуск)

1. Скопируй с перезаписью из `_session2_patch/claude_dir/` в `.claude/`:
   - `workflows/write-chapter.js` → `.claude/workflows/write-chapter.js` (папку создать)
   - `agents/bf-writer.md`, `agents/bf-critic.md`, `agents/bf-coordinator.md` → `.claude/agents/`
   - `settings.json` → `.claude/settings.json`
2. Перемести `_session2_patch/` в `archive/2026-10-01_session2/`.
3. Попроси автора перезапустить Claude Code и дать команду «выполни _SESSION2_LOCAL.md, начиная с шага B».

## B. Проверка

1. `python tools/validate_factory.py` — ожидается «ЧИСТО».
2. `python tools/verify_sources.py --pool _outbound/Test3_05.05.2026/quellen_pool_KS.md --verified _outbound/Test3_05.05.2026/SOURCES_VERIFIED_KS.md --out _outbound/Test3_05.05.2026/SOURCES_CHECK_KS.md` — ожидается: все 14 со значком ✅, код выхода 0.
3. Проверь, что workflow виден: команда `/write-chapter` есть в списке команд (`/` автодополнение). Если нет — выполни `/reload-skills` и проверь снова. **Не запускай его** — запуск будет в пробном прогоне.
4. Выполни `/workflow-authoring` и сверь `.claude/workflows/write-chapter.js` с правилами из этого скилла (meta, функции, запреты). Ничего не меняй — несоответствия запиши в отчёт дословно.

## C. Отчёт

Запиши `_SESSION2_LOCAL_REPORT.md`: результат A и B1–B4.
