#!/bin/bash
# PostToolUse hook — логирует изменения файлов глав в production_state.md.
# Claude Code передаёт данные через stdin как JSON.
# Формат stdin: {"tool_name": "Write", "tool_input": {"file_path": "...", "content": "..."}}
#
# Что делает:
#   - Записывает timestamp с точностью до минуты (YYYY-MM-DD HH:MM)
#   - Удаляет записи старше 45 дней (ротация)

MEMORY_FILE="$(dirname "$0")/../memory/production_state.md"
INPUT=$(cat)

# Извлекаем путь
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Читаем новый статус из файла
NEW_STATUS=$(grep -m1 "^status:" "$FILE_PATH" 2>/dev/null | sed 's/status:[[:space:]]*//' | tr -d '"' | tr -d "'")

# Только производственные статусы
PRODUCTION_STATUSES="outline-ready material-draft draft review clean humanized translated final"
if [ -z "$NEW_STATUS" ] || ! echo "$PRODUCTION_STATUSES" | grep -qw "$NEW_STATUS"; then
  exit 0
fi

TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
BASENAME=$(basename "$FILE_PATH")

# Ротация: удалить записи старше 45 дней
CUTOFF=$(date -d "45 days ago" "+%Y-%m-%d" 2>/dev/null || date -v-45d "+%Y-%m-%d" 2>/dev/null)
if [ -n "$CUTOFF" ] && [ -f "$MEMORY_FILE" ]; then
  python3 -c "
import sys, re
from datetime import datetime

cutoff = datetime.strptime('$CUTOFF', '%Y-%m-%d')
keep = []
with open('$MEMORY_FILE', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'<!-- auto: (\d{4}-\d{2}-\d{2})', line)
        if m:
            entry_date = datetime.strptime(m.group(1), '%Y-%m-%d')
            if entry_date < cutoff:
                continue
        keep.append(line)

with open('$MEMORY_FILE', 'w', encoding='utf-8') as f:
    f.writelines(keep)
" 2>/dev/null
fi

# Дописываем запись с точным временем
echo "" >> "$MEMORY_FILE"
echo "<!-- auto: $TIMESTAMP $BASENAME → $NEW_STATUS -->" >> "$MEMORY_FILE"

exit 0
