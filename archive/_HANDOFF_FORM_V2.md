---
document: handoff_form_v2
date: 2026-05-15
status: ЗАВЕРШЕНО
---

# Handoff: React-форма стартового пакета v2 — ЗАВЕРШЕНО

## Что сделано

1. ✅ `templates/tpl-book-config.md` — обновлена схема v2 (voice.tones[], micro_modes[], structure.layout/parts, content.*)
2. ✅ `templates/tpl-book-config.json` — JSON-шаблон v2
3. ✅ `tools/init_book.py` — генерация v2 config (tones, micro_modes, intro/outro, layout, parts, content)
4. ✅ React-форма v2 (booksfactory_init_form_v2.jsx) — все 11 дополнений
5. ✅ `validate_factory.py` → 0 нарушений

## Что добавлено в форму v2

### Новые поля
1. Объём введения (слов)
2. Объём заключения (слов)
3. Литература: per-chapter / общая в конце
4. Основные идеи (3–7 тезисов, ListInput)
5. Запреты (TagInput → verbot_liste)
6. Метафорические территории (use + avoid, TagInput)
7. Структура: плоская / иерархическая (части → главы с кол-вом глав в каждой)
8. Обязательный жанровый блок главы
9. Ведущая техника (или null → bf-researcher предложит)
10. Палитра микрорежимов (пресеты + свои, мультичойс)

### Изменения в существующих
11. Голос → мультичойс с чипами (стенд-ап, саркастический, циник + 5 существующих + свой вариант)
