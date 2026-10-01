---
document: SESSION0_LOCAL_STEP2
created: 2026-10-01
purpose: >
  Продолжение локального шага сессии 0. Node.js на компьютере нет, поэтому хуки
  переписаны на PowerShell (есть на любом Windows). Команда автора:
  «выполни _SESSION0_LOCAL_STEP2.md».
---

# Сессия 0 — локальный шаг, часть 2

Работай только в директории BooksFactory. Ничего не удаляй — только перемещай. Используй PowerShell.

## A. Установка (затем перезапуск)

1. Скопируй с перезаписью:
   - `_session0_patch2/claude_dir/settings.json` → `.claude/settings.json`
   - `_session0_patch2/claude_dir/hooks/check_chapter_status.ps1` → `.claude/hooks/`
   - `_session0_patch2/claude_dir/hooks/update_production_state.ps1` → `.claude/hooks/`
2. Перемести `.claude/hooks/check_chapter_status.mjs` и `.claude/hooks/update_production_state.mjs` в `archive/2026-10-01_session0/hooks/`.
3. Перемести папку `_session0_patch2/` в `archive/2026-10-01_session0/`.
4. Попроси автора перезапустить Claude Code и дать команду «выполни _SESSION0_LOCAL_STEP2.md, начиная с шага B».

## B. Проверка хуков

1. Создай `_testing/hooktest.md`:
   ```
   ---
   status: final
   ---
   тест
   ```
2. Попробуй изменить его инструментом Edit («тест» → «тест2»).
   - **Ожидаемо:** правка заблокирована с сообщением «BLOCK: Глава имеет статус 'final'».
   - Если прошла — зафиксируй дословно все уведомления о hook error.
3. Создай `_testing/hooktest2.md` со `status: draft` и любым текстом. Проверь, что в конце `.claude/memory/production_state.md` появилась строка `<!-- auto: … hooktest2.md -> draft -->`.
4. Перемести оба тестовых файла в `archive/2026-10-01_session0/`. Строку `auto:` в production_state.md удали.

## C. Валидатор

1. `python --version` (если не найден — `py --version`). Если Python нет — зафиксируй и пропусти пункт 2.
2. `python tools/validate_factory.py` — сохрани вывод.

## D. Отчёт

Запиши `_SESSION0_LOCAL_REPORT.md`: результаты A–C (блокировка да/нет, запись в журнал да/нет, версия Python, полный вывод валидатора). Больше ничего не меняй.
