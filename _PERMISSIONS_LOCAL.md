---
document: PERMISSIONS_LOCAL
created: 2026-10-02
purpose: Права фабрики без подтверждений. Команда автора: «выполни _PERMISSIONS_LOCAL.md».
---

# Права фабрики — без подтверждений

1. Скопируй `_permissions_patch/settings.local.json` → `.claude/settings.local.json` (прежний файл уже сохранён в `archive/2026-10-02_session9_permissions/settings.local.before.json`).
2. Перемести `_permissions_patch/` и этот файл в `archive/2026-10-02_session9_permissions/`.
3. Скажи автору одной строкой: «Права обновлены. Перезапустите Claude Code в папке BooksFactory и введите: выполни _SESSION9_LOCAL.md».

Что это даёт: в папке BooksFactory Claude Code работает без запросов подтверждения (чтение, запись, команды, агенты).
Запрещено даже без вопроса: удаление файлов и папок, `git push`, `git reset --hard`.
