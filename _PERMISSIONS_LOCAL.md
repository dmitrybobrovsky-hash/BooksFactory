---
document: PERMISSIONS_LOCAL
created: 2026-10-01
purpose: Права для работы фабрики без подтверждений. Команда автора: «выполни _PERMISSIONS_LOCAL.md» (после окончания пилота).
---

# Права фабрики — без подтверждений

1. Перемести текущий `.claude/settings.local.json` в `archive/2026-10-01_session3/settings.local.before.json`.
2. Скопируй `_permissions_patch/claude_dir/settings.local.json` → `.claude/settings.local.json`.
3. Перемести `_permissions_patch/` и этот файл в `archive/2026-10-01_session3/`.
4. Скажи автору: «Права обновлены. Перезапустите Claude Code в папке BooksFactory».

Что это даёт: внутри BooksFactory Claude Code работает без запросов подтверждения.
Запрещено полностью (даже без вопроса): удаление файлов и папок, `git push`, `git reset --hard`.
Действует только когда Claude Code открыт в папке BooksFactory; в других папках — обычные подтверждения.
