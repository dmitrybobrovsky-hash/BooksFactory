# book_config.json — схема манифеста проекта v2

Единственный источник проектного контекста для агентов фабрики.
Создаётся `init_book.py` при инициализации книги.
Агенты НЕ хардкодят имена проектных файлов — читают пути из этого конфига.
Поля `null` = не применимо (например, series для standalone книги).

## Кто что читает

| Поле config | Агенты, которые его используют |
|-------------|-------------------------------|
| `meta.code` | все (для naming convention файлов) |
| `meta.language` | bf-humanizer (выбор языкового модуля), bf-compiler |
| `series.*` | bf-researcher (исследование серийного контекста), bf-compiler (T7 ABGRENZUNG), bf-editor (терминология) |
| `voice.*` | bf-researcher (stil_und_ton), bf-writer (тон), bf-critic (проверка тона), bf-editor (трёхзонная модель) |
| `voice.tones[]` | bf-writer (регистр), bf-critic (проверка допустимости), bf-material-author (назначение микрорежимов секций) |
| `voice.micro_modes[]` | bf-material-author (палитра микрорежимов секций), bf-writer (исполнение), bf-critic (проверка) |
| `structure.*` | bf-researcher (arbeitsplan), bf-planner (beat budget), bf-critic (signature_figure_limit) |
| `structure.parts[]` | bf-researcher (arbeitsplan), bf-planner (навигация по частям) |
| `content.core_ideas[]` | bf-researcher (формирование arbeitsplan), bf-material-author (MATERIAL) |
| `content.forbidden[]` | bf-researcher → verbot_liste, bf-writer (запреты), bf-editor (проверка) |
| `content.metaphor_territories` | bf-material-author (выбор арен), bf-writer (образный ряд) |
| `content.bibliography_mode` | bf-compiler (session template: per-chapter или unified) |
| `content.chapter_genre_block` | bf-planner (обязательный блок в каждой главе), bf-writer (исполнение) |
| `content.lead_technique` | bf-researcher (если задано — использовать; если null — предложить) |
| `paths.*` | все агенты — каждый читает только нужные ему файлы по путям из config |

## Схема JSON

```json
{
  "meta": {
    "title": "<название книги>",
    "code": "<2-3 буквы>",
    "language": "<ru / de / en>",
    "created": "<YYYY-MM-DD>",
    "factory_version": "<версия BooksFactory>"
  },

  "series": {
    "enabled": false,
    "name": null,
    "volume": null,
    "bible_path": null,
    "abgrenzung_path": null
  },

  "voice": {
    "tones": ["интеллигентный провокатор"],
    "provocation_level": 3,
    "wow_factor": false,
    "target_audience": "<описание аудитории>",
    "address_form": "du",
    "micro_modes": [
      "ледяная клиническая фиксация",
      "горькая усмешка",
      "тихая констатация"
    ]
  },

  "structure": {
    "chapters_planned": 20,
    "words_per_chapter": 6000,
    "intro_words": 3000,
    "outro_words": 3000,
    "arenas_target": 3,
    "signature_figure_limit": 8,
    "layout": "flat",
    "parts": []
  },

  "content": {
    "core_ideas": [],
    "forbidden": [],
    "metaphor_territories": {
      "use": [],
      "avoid": []
    },
    "bibliography_mode": "unified",
    "chapter_genre_block": null,
    "lead_technique": null
  },

  "paths": {
    "tonal_compass": "stil_und_ton_<CODE>.md",
    "verbot_liste": "verbot_liste_<CODE>.md",
    "anweisungen": "anweisungen_<CODE>.md",
    "arbeitsplan": "arbeitsplan_<CODE>.md",
    "session_template": "session_template_<CODE>.md",
    "arenen_pool": "arenen_pool_<CODE>.md",
    "quellen_pool": "quellen_pool_<CODE>.md",
    "reference_chapter": null,
    "skvoznye_formuly": "_skvoznye_formuly_<CODE>.md",
    "case_protocol": null,
    "session_state": "_SESSION_STATE.md",
    "drafts_dir": "_drafts/"
  }
}
```

## Правила

1. Все пути в `paths` — относительные от корня книги (`<CODE>/`).
2. `null` = файл не создан или не нужен. Агент пропускает шаг, а не падает.
3. `series.enabled: false` → агенты игнорируют все поля `series.*`.
4. `paths.reference_chapter` заполняется вручную автором после написания первой главы.
5. `init_book.py` создаёт config с заглушками, bf-researcher заполняет при исследовании.
6. `voice.tones` — массив (мультичойс). Автор может выбрать несколько тонов + добавить свой.
7. `voice.micro_modes` — палитра допустимых микрорежимов секций. bf-material-author назначает из этой палитры.
8. `structure.layout`: `"flat"` (20 глав подряд) или `"parts"` (части → главы). Если `"parts"` — заполнить `structure.parts[]`.
9. `content.bibliography_mode`: `"per_chapter"` (литература в каждой главе) или `"unified"` (общая в конце книги).
10. `content.chapter_genre_block`: если не null — обязательный повторяющийся блок в каждой главе (например `"PRAKTISCHE ANWENDUNG"`).
11. `content.lead_technique`: если null — bf-researcher предложит.
