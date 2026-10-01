"""
BooksFactory — backup федеральных документов.
Создаёт timestamped копию всех ключевых файлов фабрики.
Использование: python tools/backup.py

Бэкап сохраняется в .claude/backups/YYYY-MM-DD_HHMM/
Для отката: python tools/rollback.py
"""

import os
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(ROOT, '.claude', 'backups')

# Файлы, которые бэкапятся (федеральные документы + конституция)
FEDERAL_FILES = [
    'CLAUDE.md',
    'BOOKSFACTORY.md',
    'BOOKSFACTORY_AI.md',
    'CHANGELOG.md',
    'Session_TEMPLATE.md',
    '_SESSION_START_PROMPT.md',
    'architecture/FACTORY_MAP.md',
    'architecture/shared_vocabulary.md',
    'architecture/handoff_contracts.md',
    'architecture/writing_control.md',
]

# Директории, которые бэкапятся целиком
FEDERAL_DIRS_EXTRA = [
    'templates',
    'tools',
    'skills',
    'method',
]

# Директории, которые бэкапятся целиком
FEDERAL_DIRS = [
    '.claude/agents',
    '.claude/skills',
    '.claude/hooks',
    '.claude/memory',
]


def backup():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    dest = os.path.join(BACKUP_DIR, timestamp)
    os.makedirs(dest, exist_ok=True)

    count = 0

    # Копируем файлы
    for rel in FEDERAL_FILES:
        src = os.path.join(ROOT, rel.replace('/', os.sep))
        if os.path.exists(src):
            dst = os.path.join(dest, rel.replace('/', os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1

    # Копируем директории
    for rel in FEDERAL_DIRS + FEDERAL_DIRS_EXTRA:
        src = os.path.join(ROOT, rel.replace('/', os.sep))
        if os.path.isdir(src):
            dst = os.path.join(dest, rel.replace('/', os.sep))
            shutil.copytree(src, dst, dirs_exist_ok=True)
            dir_count = sum(len(files) for _, _, files in os.walk(src))
            count += dir_count

    print(f'Backup создан: {dest}')
    print(f'Скопировано: {count} файлов')
    return dest


if __name__ == '__main__':
    backup()
