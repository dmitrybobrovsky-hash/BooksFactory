#!/bin/bash
# PreToolUse hook — блокирует Write/Edit для глав со статусом 'final'.
# Claude Code передаёт данные через stdin как JSON.
# Формат stdin: {"tool_name": "Write", "tool_input": {"file_path": "..."}}
#
# Что делает сейчас:
#   - Распознаёт производственные файлы (frontmatter с полем status:)
#   - Блокирует редактирование глав со статусом 'final'
#   - Все остальные статусы пропускает
#
# TODO (Ф10): реализовать полную проверку переходов статусов и ролей.
#   Переменная VALID_TRANSITIONS подготовлена, но пока не используется.
#   Поле role_required в frontmatter — зарезервировано, не проверяется.

# Подготовлено для Ф10 — пока не используется
VALID_TRANSITIONS="outline-ready:material-draft material-draft:draft draft:review review:clean clean:humanized humanized:translated"

# Читаем stdin
INPUT=$(cat)

# Извлекаем путь к файлу
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Если не файл главы (нет frontmatter с 'status:') — пропускаем
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

CURRENT_STATUS=$(grep -m1 "^status:" "$FILE_PATH" 2>/dev/null | sed 's/status:[[:space:]]*//' | tr -d '"' | tr -d "'")

# Если нет поля status — не производственный файл, пропускаем
if [ -z "$CURRENT_STATUS" ]; then
  exit 0
fi

# Проверяем что статус — один из производственных
PRODUCTION_STATUSES="outline-ready material-draft draft review clean humanized translated final"
if ! echo "$PRODUCTION_STATUSES" | grep -qw "$CURRENT_STATUS"; then
  exit 0
fi

# Финальный статус — блокируем редактирование
if [ "$CURRENT_STATUS" = "final" ]; then
  echo "BLOCK: Глава имеет статус 'final'. Редактирование запрещено без явного подтверждения автора." >&2
  exit 2
fi

echo "OK: статус '$CURRENT_STATUS'" >&2
exit 0
