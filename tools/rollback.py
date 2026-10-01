"""
BooksFactory — откат к последнему (или указанному) бэкапу.
Использование:
  python tools/rollback.py           — откат к последнему бэкапу
  python tools/rollback.py --list    — показать все бэкапы
  python tools/rollback.py 2026-05-01_1430  — откат к конкретному бэкапу

ВНИМАНИЕ: перед откатом автоматически создаётся бэкап текущего состояния (pre-rollback).
"""

import os
import sys
import shutil
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(ROOT, '.claude', 'backups')


def list_backups():
    if not os.path.isdir(BACKUP_DIR):
        print('Нет бэкапов.')
        return []
    backups = sorted([d for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))])
    if not backups:
        print('Нет бэкапов.')
        return []
    print(f'Доступные бэкапы ({len(backups)}):')
    for b in backups:
        bp = os.path.join(BACKUP_DIR, b)
        file_count = sum(len(files) for _, _, files in os.walk(bp))
        print(f'  {b}  ({file_count} файлов)')
    return backups


def rollback(target=None):
    backups = sorted([d for d in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, d))]) if os.path.isdir(BACKUP_DIR) else []

    if not backups:
        print('Нет бэкапов для отката.')
        return

    if target is None:
        target = backups[-1]
    elif target not in backups:
        print(f'Бэкап {target} не найден.')
        list_backups()
        return

    source = os.path.join(BACKUP_DIR, target)

    # Создаём pre-rollback бэкап
    pre_rollback = os.path.join(BACKUP_DIR, f'pre-rollback_{datetime.now().strftime("%Y-%m-%d_%H%M")}')
    print(f'Создаю pre-rollback бэкап: {os.path.basename(pre_rollback)}')

    # Импортируем backup функцию
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from backup import backup as do_backup
    do_backup()

    # Восстанавливаем файлы из бэкапа
    count = 0
    for dirpath, dirs, files in os.walk(source):
        for fn in files:
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, source)
            dst = os.path.join(ROOT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1

    print(f'Откат к {target}: восстановлено {count} файлов.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_backups()
        else:
            rollback(sys.argv[1])
    else:
        rollback()
