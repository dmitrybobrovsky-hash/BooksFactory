"""
BooksFactory — валидация чистоты фабрики от проектных хардкодов.
Проверяет, что файлы фабрики не содержат привязок к конкретным проектам.

Использование:
  python tools/validate_factory.py          # полная проверка
  python tools/validate_factory.py --fix    # показать, что нужно исправить

Возвращает exit code 0 (чисто) или 1 (найдены нарушения).
"""

import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Директории фабрики (проверяются)
FACTORY_DIRS = [
    '.claude/agents',
    '.claude/skills',
    '.claude/memory',
    'architecture',
    'skills',
    'templates',
    'method',
]

FACTORY_FILES = [
    'CLAUDE.md',
    'BOOKSFACTORY.md',
    'BOOKSFACTORY_AI.md',
    'Session_TEMPLATE.md',
]

# НЕ проверяются
SKIP_DIRS = {'_outbound', '_backups', 'backups', 'archive', '.vscode', '__pycache__'}
SKIP_FILES = {
    'CHANGELOG.md',                  # история изменений
    '_HANDOFF_NEXT_SESSION.md',      # задание для следующей сессии
    '_HANDOFF_PARAMETRIZATION.md',   # план параметризации
}
SKIP_PATHS = {
    '.claude/memory/production_state.md',  # оперативная память координатора, содержит проектные данные по назначению
}

# Запрещённые паттерны: хардкоды конкретных проектов
FORBIDDEN_PATTERNS = [
    # Конкретные книги серии
    (r'\bBand\s+I{1,3}V?\b', 'хардкод тома серии (Band I/II/III/IV)'),
    (r'\bManipulationen\b', 'хардкод названия книги'),
    (r'\bImmuner\s+Geist\b', 'хардкод названия книги'),
    (r'\bKomplize\b', 'хардкод названия книги'),
    (r'Карты на стол', 'хардкод названия книги'),

    # Коды конкретных книг
    (r'_KS(?![A-Za-z0-9])', 'хардкод кода книги'),
    (r'_IU(?![A-Za-z0-9])', 'хардкод кода книги'),
    (r'_KNS(?![A-Za-z0-9])', 'хардкод кода книги'),
    (r'_IG(?![A-Za-z0-9])', 'хардкод кода книги'),
    (r'\barenen_pool_I[GU]\b', 'хардкод пула арен конкретной книги'),

    # Пути к конкретным проектам
    (r'_outbound/', 'путь к тестовой директории'),
    (r'Serie/', 'путь к директории серии'),

    # Удалённые проектные файлы (ссылки на них битые)
    (r'\bseries-bible\.md\b', 'ссылка на удалённый файл series-bible.md'),
    (r'\bbrand-voice\.md\b', 'ссылка на удалённый файл brand-voice.md'),
    (r'\bABGRENZUNG\.md\b', 'ссылка на удалённый файл ABGRENZUNG.md'),
    (r'\bvoice_principles\.md\b', 'ссылка на удалённый файл voice_principles.md'),
    (r'\bprovocation_principles\.md\b', 'ссылка на удалённый файл provocation_principles.md'),
    (r'\bglossary\.md\b', 'ссылка на удалённый файл glossary.md'),

    # Удалённый агент
    (r'\bbf-translator\b', 'ссылка на удалённый агент bf-translator'),
]

# Исключения: паттерны, которые допустимы в определённых контекстах
ALLOWED_EXCEPTIONS = {
    # ABGRENZUNG как название секции шаблона (T7), не как ссылка на файл
    'templates/tpl-session-template.md': [r'\bABGRENZUNG\b'],
    # translation как лингвистический термин в humanizer/en
    'skills/humanizer/en/SKILL.md': [r'\btranslation\b'],
    'skills/humanizer/en/references/english_specific.md': [r'\btranslation\b'],
    # BOOKSFACTORY_AI.md §11b-§11d — историческая документация событий
    'BOOKSFACTORY_AI.md': [r'Band', r'Manipulationen', r'_outbound', r'Карты на стол'],
    # Дерево директорий в конституции — описание структуры, не путь к проекту
    'CLAUDE.md': [r'_outbound/\s+←'],
    # Исторический ТЗ writer-loop (2026-04): упоминания тестового тома и удалённого переводчика
    'architecture/_TZ_WRITER_BEAT_BY_BEAT.md': [r'Band', r'Manipulationen', r'bf-translator'],
    # Историческая справка об INCIDENT-04 (Test3)
    'architecture/handoff_contracts.md': [r'INCIDENT-04'],
}


def validate():
    violations = []

    # Collect all factory files
    files_to_check = []

    for rel in FACTORY_FILES:
        path = os.path.join(ROOT, rel)
        if os.path.exists(path):
            files_to_check.append((rel, path))

    for dir_rel in FACTORY_DIRS:
        dir_path = os.path.join(ROOT, dir_rel)
        if not os.path.isdir(dir_path):
            continue
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                if not fname.endswith(('.md', '.json', '.py', '.sh')):
                    continue
                if fname in SKIP_FILES:
                    continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, ROOT).replace(os.sep, '/')
                if rel in SKIP_PATHS:
                    continue
                files_to_check.append((rel, fpath))

    # Check each file
    for rel, fpath in files_to_check:
        try:
            with open(fpath, encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            continue

        exceptions = ALLOWED_EXCEPTIONS.get(rel, [])

        for i, line in enumerate(lines):
            for pattern, description in FORBIDDEN_PATTERNS:
                if re.search(pattern, line):
                    # Check exceptions
                    is_exception = any(re.search(exc, line) for exc in exceptions)
                    if not is_exception:
                        violations.append({
                            'file': rel,
                            'line': i + 1,
                            'pattern': description,
                            'text': line.strip()[:120],
                        })

    return violations


# ── Проверка фронтматтера агентов и скиллов (добавлено 2026-10-01) ──
# Claude Code молча пропускает агента без description и даёт агенту без
# tools ВСЕ инструменты; неизвестные поля SKILL.md молча игнорируются.
AGENT_REQUIRED = ('name', 'description', 'tools')
SKILL_KNOWN = {
    'name', 'description', 'when_to_use', 'disable-model-invocation',
    'user-invocable', 'allowed-tools', 'disallowed-tools', 'model', 'effort',
    'context', 'agent', 'background', 'argument-hint', 'arguments', 'paths',
    'shell', 'hooks', 'metadata', 'license', 'compatibility',
}


def _frontmatter_keys(path):
    with open(path, encoding='utf-8-sig') as f:
        text = f.read()
    if not text.startswith('---'):
        return None
    end = text.find('\n---', 3)
    if end == -1:
        return None
    keys = set()
    for line in text[3:end].splitlines():
        m = re.match(r'^([A-Za-z_][\w-]*)\s*:', line)
        if m:
            keys.add(m.group(1))
    return keys


def validate_frontmatter():
    problems = []
    agents_dir = os.path.join(ROOT, '.claude', 'agents')
    if os.path.isdir(agents_dir):
        for fname in sorted(os.listdir(agents_dir)):
            if not fname.endswith('.md'):
                continue
            rel = f'.claude/agents/{fname}'
            keys = _frontmatter_keys(os.path.join(agents_dir, fname))
            if keys is None:
                problems.append((rel, 'нет фронтматтера — агент не загрузится'))
                continue
            for k in AGENT_REQUIRED:
                if k not in keys:
                    why = {'name': 'агент не загрузится',
                           'description': 'Claude Code молча пропустит агента',
                           'tools': 'агент получит ВСЕ инструменты'}[k]
                    problems.append((rel, f'нет поля {k} — {why}'))
    skills_dir = os.path.join(ROOT, '.claude', 'skills')
    if os.path.isdir(skills_dir):
        for d in sorted(os.listdir(skills_dir)):
            path = os.path.join(skills_dir, d, 'SKILL.md')
            if not os.path.isfile(path):
                continue
            keys = _frontmatter_keys(path) or set()
            unknown = sorted(keys - SKILL_KNOWN)
            if unknown:
                problems.append((f'.claude/skills/{d}/SKILL.md',
                                 'поля игнорируются платформой: ' + ', '.join(unknown)))
    return problems


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print('BooksFactory — валидация чистоты фабрики')
    print('=' * 60)

    violations = validate()
    fm = validate_frontmatter()
    if fm:
        print(f'\nФРОНТМАТТЕР: {len(fm)} проблем')
        for rel, msg in fm:
            print(f'  {rel}: {msg}')
        for rel, msg in fm:
            violations.append({'file': rel, 'line': 1, 'pattern': 'фронтматтер', 'text': msg})

    if not violations:
        print('\nРЕЗУЛЬТАТ: ЧИСТО (0 нарушений)')
        sys.exit(0)
    else:
        print(f'\nНАЙДЕНО НАРУШЕНИЙ: {len(violations)}\n')
        current_file = None
        for v in violations:
            if v['file'] != current_file:
                current_file = v['file']
                print(f'  {current_file}')
            print(f'    L{v["line"]}: [{v["pattern"]}]')
            print(f'      {v["text"]}')
        print(f'\nИТОГО: {len(violations)} нарушений в {len(set(v["file"] for v in violations))} файлах')
        sys.exit(1)


if __name__ == '__main__':
    main()
