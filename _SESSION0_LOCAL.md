---
document: SESSION0_LOCAL
created: 2026-10-01
purpose: >
  Локальный шаг сессии 0 (после AUDIT_2026-10-01). Выполняется Claude Code
  на компьютере автора — облачная сессия не может перемещать файлы.
  Команда автора: «выполни _SESSION0_LOCAL.md».
---

# Сессия 0 — локальный шаг

Работай только в директории BooksFactory. Ничего не удаляй — только перемещай. Используй PowerShell.

## 0. Установка подготовленных файлов

Облачная сессия не может писать в `.claude/` и `.vscode/` — эти файлы подготовлены в папке `_session0_patch/`: подпапка `claude_dir/` соответствует `.claude/`, `vscode_dir/` — `.vscode/`. Скопируй каждый файл поверх соответствующего файла в BooksFactory (с перезаписью):

- `claude_dir/agents/bf-researcher.md`, `bf-writer.md`, `bf-coordinator.md` → `.claude/agents/`
- `claude_dir/skills/humanizer/SKILL.md`, `claude_dir/skills/check-consistency/SKILL.md` → `.claude/skills/…`
- `claude_dir/hooks/check_chapter_status.mjs`, `update_production_state.mjs` → `.claude/hooks/` (новые)
- `claude_dir/settings.json` → `.claude/settings.json`
- `claude_dir/memory/production_state.md` → `.claude/memory/production_state.md`
- `vscode_dir/settings.json` → `.vscode/settings.json`

Затем перемести папку `_session0_patch/` целиком в `archive/2026-10-01_session0/`.

**Важно:** новые хуки и права начнут действовать только в новой сессии Claude Code. После шагов 0 и 1 попроси автора перезапустить Claude Code и снова дать команду «выполни _SESSION0_LOCAL.md, начиная с шага 2».

## 1. Архивирование

Создай `archive/2026-10-01_session0/` с подпапками `agents/`, `skills/`, `hooks/`, `backups/` и перемести туда:

| Откуда | Куда |
|---|---|
| `.claude/agents/bf-controller.md` | `archive/2026-10-01_session0/agents/` |
| `.claude/skills/` → папки `connect-to-existing`, `draft-chapter`, `edit-chapter`, `editor`, `generate-handout`, `outline-book`, `project-manager`, `repurpose-to-lecture`, `repurpose-to-podcast`, `repurpose-to-reels`, `synthesize-ideas`, `writer` | `archive/2026-10-01_session0/skills/` |
| `.claude/hooks/check_chapter_status.sh`, `.claude/hooks/update_production_state.sh` | `archive/2026-10-01_session0/hooks/` |
| всё содержимое `.claude/backups/` | `archive/2026-10-01_session0/backups/` |

В `.claude/skills/` должны остаться только `humanizer` и `check-consistency`.
В `.claude/agents/` — 9 файлов.

## 2. Проверка хуков

1. Выполни `node --version`. Если Node не найден — остановись на этом пункте и сообщи: хуки работать не будут, нужен Node.js.
2. Создай `_testing/hooktest.md` с содержимым:
   ```
   ---
   status: final
   ---
   тест
   ```
3. Попробуй изменить этот файл инструментом Edit (заменить «тест» на «тест2»).
   - **Ожидаемо:** правка заблокирована с сообщением «BLOCK: Глава имеет статус 'final'».
   - Если правка прошла — хук не работает; зафиксируй текст любых уведомлений о hook error.
4. Перемести `_testing/hooktest.md` в `archive/2026-10-01_session0/`.

## 3. Валидация

Выполни `python tools/validate_factory.py` и сохрани вывод.

## 4. Отчёт

Запиши `_SESSION0_LOCAL_REPORT.md` в корне BooksFactory:
- что перемещено (числа);
- версия Node; результат проверки хука (заблокировано / не заблокировано + сообщения);
- полный вывод валидатора.

Больше ничего не меняй.
