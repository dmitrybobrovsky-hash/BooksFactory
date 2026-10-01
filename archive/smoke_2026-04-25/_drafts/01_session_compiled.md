# Session SmokeTest Kapitel 01

> Compiled by `bf-compiler` (mock — реальный agent не зарегистрирован в smoke-test'е).
> Шаг 4 «Сборка итогового файла» имитирован вручную по контракту bf-compiler.md.

## T1. Метаданные + калибровка

| Поле | Значение |
|------|----------|
| `book` | SmokeTest 2026-04-25 |
| `chapter_number` | 01 |
| `target_words` | 1500 |
| `tonal_compass_path` | `_testing/smoke_2026-04-25/tonal_compass.md` |
| `verbot_liste_path` | `_testing/smoke_2026-04-25/verbot_liste.md` |
| `reference_chapter_path` | `_testing/smoke_2026-04-25/_reference_chapter.md` |
| `calibration_paths[]` | `[]` (первая глава) |

## T2. Специфические запреты

- «Просто», «всего лишь», «по сути».
- Восклицательные предложения.
- Местоимение «вы».

## T3. Голос (выдержка)

Сухая аналитика без эмоций. Читатель — «ты». Никаких метафор-цветов. Чёткий контур. Подлежащее-сказуемое-факт.

## T4. Тональные якоря

- Никаких восторгов.
- Никакого жаргона без расшифровки.
- Парадокс ставится через противопоставление, не через лозунг.

## T5. Каркас главы (секции, микрорежимы)

- §1 Постановка задачи (~500 слов, сухая аналитика, beats 1–3).
- §2 Архитектура цепочки (~500 слов, контурная схема, beats 4–6).
- §3 Условия завершения (~500 слов, чек-лист, beats 7–9).

## T6. MATERIAL

(побайтовая копия `MATERIAL_Glava_01.md` — заголовок «MATERIAL — Глава 01: Pipeline-Integrity», секции «Каркас», «Арены», «Провокации», «QUELLEN». Полный текст не дублируется в smoke-mock; реальный compiler копирует целиком.)

## T7. Beat-план (JSON)

```json
{
  "book": "SmokeTest 2026-04-25",
  "chapter_number": 1,
  "chapter_target_words": 1500,
  "sum_target_words": 1695,
  "beats": "(9 beats — см. _drafts/01_beat_plan.json)"
}
```

## T8. Арены / Сцены / Источники

- ARENA-01: цех-завод (метафора фабрики).
- ARENA-02: труба-водопровод (метафора pipeline'а).

## T9. Провокации

Парадокс: smoke-test НЕ проверяет литературное качество, и это правильно. Качество — другая ось.

## T10. Объём

target_words главы: 1500. sum_target_words_beats: 1615 (из 9 beats). Допуск ±5% от 1.13 × target = 1695: deviation=4.72%, в пределах.

## T11. QUELLEN

Стиль ссылок: inline + список в конце главы. Язык: русский. Источники главы:
- _TZ_AUDIT_FIXES_2026-04-25.md §4-bis P-FINAL
- _TZ_WRITER_BEAT_BY_BEAT.md §5
- architecture/handoff_contracts.md

## T12. Continuity

Первая глава SmokeTest, calibration_paths[] пуст. Continuity-инварианты: терминология series-bible.md (pipeline, beat, smoke-test); обращение «ты»; персонажи отсутствуют (служебный текст).

---BEGIN_REFERENCE_CHAPTER---
(побайтовая копия `_reference_chapter.md` — заголовок «Reference Chapter — SmokeTest», секции «Что измеряет smoke-test», «Почему так», «Конкретно». Полный текст не дублируется в smoke-mock.)
---END_REFERENCE_CHAPTER---

---BEGIN_VERBOT_LISTE---
(побайтовая копия `verbot_liste.md` — секции «Лексика», «Структура», «Метафоры». Полный текст не дублируется в smoke-mock.)
---END_VERBOT_LISTE---

---BEGIN_CALIBRATION---
Первая глава, калибровки нет.
---END_CALIBRATION---

---BEGIN_PROTOCOL---
12 контрольных вопросов из tonal_compass.md (прокидываются в writer-loop).
---END_PROTOCOL---
