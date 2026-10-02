---
document: PERMISSIONS_LOCAL
created: 2026-10-02
purpose: Права фабрики без подтверждений, со строгими запретами. Команда автора: «выполни _PERMISSIONS_LOCAL.md».
---

# Права фабрики — без подтверждений, со строгими запретами

1. Скопируй текущий `.claude/settings.local.json` в `archive/2026-10-02_session9_permissions/settings.local.v2.json`.
2. Скопируй `_permissions_patch/settings.local.json` → `.claude/settings.local.json`.
3. Перемести `_permissions_patch/` и этот файл в `archive/2026-10-02_session9_permissions/` (если там уже есть одноимённые — добавь к имени `_v3`).
4. Скажи автору одной строкой: «Права обновлены. Перезапустите Claude Code в папке BooksFactory и введите: выполни _SESSION9_LOCAL.md».

Режим — без подтверждений. Запрещено даже без вопроса, в том числе внутри составных команд: удаление файлов и папок, очистка содержимого и дисков, `python -c`, `cmd /c`, `git push`, `git reset --hard`.
