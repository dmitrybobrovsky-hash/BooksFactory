---
document: Session_TEMPLATE
version: 1.0
created: 2026-04-25
consumer: bf-compiler
note: >
  Шаблон не редактировать вручную для конкретной главы — compiler собирает
  Session-файл из этого шаблона + источников (MATERIAL, beat_plan,
  tonal_compass, verbot_liste, reference_chapter, calibration_paths).
  Любая правка структуры T-маркеров и BEGIN/END-маркеров требует
  синхронной правки `.claude/agents/bf-compiler.md` шаг 4 «Сборка»
  и шаг 5 «Self-check».
---

# Session <Book> Kapitel NN

> Compiled by `bf-compiler` from Session_TEMPLATE + источники главы.
> Единственный вход writer-loop'а. Writer больше ничего не читает сам.

## T1. Метаданные + калибровка

<!-- compiler заполнит из входного промпта координатора (см. bf-compiler.md «Вход») -->

| Поле | Значение |
|------|----------|
| `book` | `<имя книги>` |
| `chapter_number` | `<NN>` |
| `target_words` | `<целевой объём главы в словах>` |
| `tonal_compass_path` | `<абсолютный путь до tonal_compass.md>` |
| `verbot_liste_path` | `<абсолютный путь до verbot_liste.md или null>` |
| `reference_chapter_path` | `<абсолютный путь до reference-главы из tonal_compass>` |
| `calibration_paths[]` | `<список путей до 1–2 ранее принятых глав, или [] для первой>` |

## T2. Специфические запреты

<!-- compiler заполнит из секции «запреты» / «verbot» в tonal_compass.md; если секция отсутствует — warning «секция «запреты» не найдена в tonal_compass.md», блок остаётся пустым -->

## T3. Голос (выдержка)

<!-- compiler заполнит из голос-блока tonal_compass.md (секция, в заголовке которой слово «голос» или «voice»); побайтово, без редактирования; при отсутствии — WARN-маркер -->

## T4. Тональные якоря

<!-- compiler заполнит из секции «тональные якоря» / «tonal anchors» в tonal_compass.md; при отсутствии — WARN-маркер -->

## T5. Каркас главы (секции, микрорежимы)

<!-- compiler заполнит из секции «каркас» (или аналога) в MATERIAL_Glava_NN.md; иначе сгенерирует группировку beats по секциям из beat_plan.json -->

## T6. MATERIAL

<!-- compiler скопирует полное содержимое MATERIAL_Glava_NN.md побайтово, без модификации -->

## T7. Beat-план (JSON)

<!-- compiler вставит полное содержимое beat_plan.json внутри fenced-блока ```json ... ``` -->

```json
<!-- placeholder: содержимое beat_plan.json -->
```

## T8. Арены / Сцены / Источники

<!-- compiler заполнит из секции «арены» или «сцены» MATERIAL_Glava_NN.md; если в MATERIAL секции нет — пустой блок с пометкой «⚠ не заполнено material-author-ом» -->

## T9. Провокации

<!-- compiler заполнит из секции «провокации» MATERIAL_Glava_NN.md (приоритет) или tonal_compass.md (fallback) -->

## T10. Объём

<!-- compiler заполнит: target_words главы (число) + sum_target_words_beats из beat_plan (= round(1.13 × target_words) ±5 %) + краткое напоминание о Правиле 6 (writing_control.md) -->

## T11. QUELLEN

<!-- compiler заполнит формат секции QUELLEN, ожидаемый книгой:
     - стиль ссылок (DOI / автор-год / inline);
     - язык библиографии;
     - правила сокращений;
     источник: tonal_compass.md секция «quellen-format» (если есть) или дефолт серии. -->

## T12. Continuity

<!-- compiler заполнит ссылки на calibration_paths[] (последние 2 секции каждой ранее принятой главы) и continuity-инварианты:
     - терминология серии (если книга в серии);
     - инварианты обращения («ты/du/you»);
     - персонажи / арены, прошедшие через ранние главы;
     при первой главе — пометка «calibration отсутствует, continuity = чистый старт». -->

---BEGIN_REFERENCE_CHAPTER---
<!-- compiler скопирует полный текст reference_chapter_path побайтово; это эталон голоса для writer-а; модификация запрещена -->
---END_REFERENCE_CHAPTER---

---BEGIN_VERBOT_LISTE---
<!-- compiler заполнит полным содержимым verbot_liste_path; если файла нет — пометка «книга не имеет собственного списка; critic использует кросс-книжную базу» -->
---END_VERBOT_LISTE---

---BEGIN_CALIBRATION---
<!-- compiler для каждого calibration_paths[i] вставит последние 2 секции главы побайтово; если массив пуст — пометка «первая глава, калибровки нет» -->
---END_CALIBRATION---

---BEGIN_PROTOCOL---
<!-- compiler заполнит выдержкой из tonal_compass.md секции «протокол» или «12 контрольных вопросов» (пронумерованный список); при отсутствии — WARN-маркер -->
---END_PROTOCOL---
