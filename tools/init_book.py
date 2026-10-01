"""
BooksFactory — инициализация книжного проекта из book_config.json.

Автор заполняет форму (starter_form.html) → скачивает book_config.json → кидает в Claude.
Claude запускает: python tools/init_book.py <путь к book_config.json>

Скрипт создаёт директорию проекта и заготовки файлов.
"""

import os
import sys
import json
import shutil
from datetime import date


def init_book(config_path):
    if not os.path.exists(config_path):
        print(f'Файл не найден: {config_path}')
        sys.exit(1)

    with open(config_path, encoding='utf-8') as f:
        config = json.load(f)

    meta = config['meta']
    title = meta['title']
    code = meta['code']
    lang = meta['language']
    series = config.get('series', {})
    voice = config.get('voice', {})
    structure = config.get('structure', {})
    content = config.get('content', {})

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    book_dir = os.path.join(root, code)

    if os.path.exists(book_dir):
        print(f'Директория {code}/ уже существует. Прерываю.')
        sys.exit(1)

    os.makedirs(book_dir)
    os.makedirs(os.path.join(book_dir, '_drafts'))

    today = meta.get('created') or date.today().isoformat()
    meta['created'] = today

    # ── Сохраняем config в директорию книги ──
    config_dest = os.path.join(book_dir, 'book_config.json')
    with open(config_dest, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # ── Операционная инструкция ──
    series_note = f'{series.get("name", "")}, том {series.get("volume", "")}' if series.get('enabled') else 'отдельная книга'
    tones_str = ', '.join(voice.get('tones', [])) or '(не задано)'

    anweisungen = f"""---
document: anweisungen
book: "{title}"
code: {code}
language: {lang}
series: {series_note}
created: {today}
---

# Операционная инструкция: {title}

## Идентификация

- **Название:** {title}
- **Код:** {code}
- **Язык:** {lang}
- **Серия:** {series_note}

## Целевая аудитория

{voice.get('target_audience', '(заполняется bf-researcher)')}

## Тон

{tones_str}
Провокация: {voice.get('provocation_level', 3)}/5
Wow-фактор: {'да' if voice.get('wow_factor') else 'нет'}
Обращение: {voice.get('address_form', 'du')}

## Основные идеи

{chr(10).join(f'- {idea}' for idea in content.get('core_ideas', []) if idea.strip()) or '(заполняется bf-researcher)'}

## Запреты

{chr(10).join(f'- {f}' for f in content.get('forbidden', []) if f.strip()) or '(нет стартовых запретов)'}
"""

    # ── Тональная карта (заглушка) ──
    micros_str = ', '.join(voice.get('micro_modes', [])) or '(определяются тонами)'
    stil = f"""---
document: stil_und_ton
book: "{title}"
code: {code}
language: {lang}
created: {today}
status: outline-ready
---

# Стиль и тон: {title}

## Тона
{tones_str}

## Микрорежимы
{micros_str}

## Провокация
Уровень: {voice.get('provocation_level', 3)}/5

(детализируется bf-researcher после исследования)
"""

    # ── План книги (заглушка) ──
    layout = structure.get('layout', 'flat')
    parts = structure.get('parts', [])
    if layout == 'parts' and parts:
        struct_str = f'Части: {len(parts)} ({" + ".join(str(p) + " глав" for p in parts)})'
    else:
        struct_str = f'Плоская структура: {structure.get("chapters_planned", 20)} глав'

    arbeitsplan = f"""---
document: arbeitsplan
book: "{title}"
code: {code}
created: {today}
---

# Рабочий план: {title}

## Структура
{struct_str}
Слов / глава: {structure.get('words_per_chapter', 6000)}
Введение: {structure.get('intro_words', 3000)} слов
Заключение: {structure.get('outro_words', 3000)} слов

(заполняется bf-researcher после исследования)
"""

    files = {
        f'anweisungen_{code}.md': anweisungen,
        f'stil_und_ton_{code}.md': stil,
        f'arbeitsplan_{code}.md': arbeitsplan,
    }

    for fn, file_content in files.items():
        with open(os.path.join(book_dir, fn), 'w', encoding='utf-8') as f:
            f.write(file_content)

    # ── _SESSION_STATE.md ──
    tpl_path = os.path.join(root, 'templates', 'tpl-session-state.md')
    state_path = os.path.join(book_dir, '_SESSION_STATE.md')
    if os.path.exists(tpl_path):
        shutil.copy2(tpl_path, state_path)
    with open(state_path, 'a', encoding='utf-8') as f:
        f.write(f"\n## {today}\n")
        f.write("status: completed\n")
        f.write("step: книга инициализирована из book_config.json\n")
        f.write("agent: init_book.py\n")
        f.write("next: bf-researcher (исследование)\n")
        artifacts = ', '.join([f'book_config.json'] + list(files.keys()))
        f.write(f"artifacts_created: {artifacts}\n")

    print(f'Проект инициализирован: {code}/')
    print(f'Созданы файлы:')
    print(f'  {code}/book_config.json')
    for fn in files:
        print(f'  {code}/{fn}')
    print(f'  {code}/_SESSION_STATE.md')
    print(f'  {code}/_drafts/')
    if series.get('enabled') and not series.get('bible_path'):
        print(f'\nВНИМАНИЕ: серийный канон не указан (series.bible_path = null).')
    print(f'\nСледующий шаг: bf-researcher.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Использование: python tools/init_book.py <путь к book_config.json>')
        sys.exit(1)
    init_book(sys.argv[1])
