---
document: memory/production_state
layer: BooksFactory
purpose: >
  Текущее состояние производства. Обновлять после каждой смены статуса главы.
  Агент bf-coordinator читает этот файл при /bf-status.
---

# Производственное состояние

## Модель статусов главы (финализирована 2026-04-25)

Базовая последовательность — единый контракт фабрики, читаемый всеми агентами:

```
(нет файла) → outline-ready → material-draft → draft → review → clean → humanized → final
```

| Статус | Источник | Что значит |
|--------|----------|-----------|
| `outline-ready` | `bf-researcher` | Outline главы готов, `tonal_compass.md` актуален, пул источников собран. MATERIAL ещё не написан. Готов к `bf-material-author`. |
| `material-draft` | `bf-material-author` | `MATERIAL_Glava_NN.md` собран (секции, beat sheets, арены, quote-anchors). Готов к `bf-planner`. |
| `draft` | `bf-coordinator(writer-loop)` | Все beats главы прошли writer↔critic, `glava.md` собран из принятых beats. Готов к `bf-editor`. |
| `review` | `bf-editor` | Отчёт редактора (≤5 точек) выдан. Автор/refiner вносит правки. |
| `clean` | `bf-editor` | Правки внесены автором/refiner, повторная проверка редактором пройдена. Готов к `bf-humanizer`. |
| `humanized` | `bf-humanizer` | Языковой модуль (ru/de/en) отработал. Готов к финализации автором. |
| `final` | автор | Глава закрыта в серии. |

### Декомпозиция `draft`-фазы (writer-loop substatuses)

Внутри `draft` writer-loop проходит несколько подсостояний — для трекинга `bf-coordinator /bf-status`:

| Подстатус | Что произошло | Кто переводит |
|-----------|---------------|---------------|
| `compiled` | `bf-compiler` собрал Session-файл из MATERIAL + beat_plan + tonal_compass + verbot_liste + reference_chapter. Готов к writer'у. | `bf-compiler` |
| `beat-N-draft` | Beat #N написан writer'ом, ожидает bf-critic. | `bf-writer` |
| `beat-N-accepted` | Beat #N принят bf-critic, попадает в pool принятых beats главы. | `bf-coordinator` |
| `draft` | Все beats главы accepted, `glava.md` собран. Совпадает с базовой `draft`-стадией. | `bf-coordinator` (loop-exit) |

Источник деталей writer-loop: `architecture/_TZ_WRITER_BEAT_BY_BEAT.md` §5.

### Инварианты

1. Базовая последовательность не переименовывается и не сокращается. Подстатусы — только декомпозиция `draft`, не замена.
2. `bf-humanizer` работает только с `clean`.
3. Возврат назад по статусу допустим (например, `review → draft` если editor вернул главу) — фиксируется в журнале.

## Активные книги

| Книга | Язык | Путь | Фаза |
|-------|------|------|------|
| MdP (Management durch Panik) | DE | `Serie/01_Книга Империя страха/` | `draft` — нужна редактура перед гуманизацией |
| ОНМ (Она не монстр) | RU | `Abuse/` | Завершена |
| Band III «Manipulationen? Noch nie gehört…» | DE | `_outbound/03_Manipulationen/` | **Отложено** (см. `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md`) — была пилотом writer-loop, ждёт закрытия Ф7/Ф8 |
| IU (Иллюзия ума) | RU | `_outbound/Test1_27042026/` | Глава 01: `draft` (writer-loop завершён 2026-05-03) |
| KS (Карты на стол) | RU | `_outbound/Test3_05.05.2026/` | Глава 01: **`draft`** (ПРОГОН A завершён 2026-05-08; ПРОГОН B завершён 2026-05-09) |

## Статус глав MdP

> Обновить после первого запуска гуманизатора.

| Глава | Статус | Итераций Writer↔Editor | Примечания |
|-------|--------|----------------------|------------|
| Гл. 1–20 + Заключение | `draft` | — | Нужна гуманизация (humanizer/de) |

## Статус глав IU (Иллюзия ума)

| Глава | Статус | Слов | Beats | Итераций | Дата | Примечания |
|-------|--------|------|-------|----------|------|-----------|
| Гл. 01 | `draft` | 3556 | 13/13 | 28 | 2026-05-03 | writer-loop завершён; объём ниже target 4500 (79%); следующий: bf-editor |

## Статус глав KS (Карты на стол) — Test3_05.05.2026

| Глава | Статус | Слов | Beats | Итераций | Дата | Примечания |
|-------|--------|------|-------|----------|------|-----------|
| Гл. 01 | `draft` | 6110 | 15/15 | 15 | 2026-05-08 | ПРОГОН A (critic sonnet): `Glava_01_KS_draft_sonnet.md`; все 15 beats приняты с первой итерации; в архиве |
| Гл. 01 | `draft` | 6145 | 16/16 | 20 | 2026-05-09 | ПРОГОН B (Ф14 test, изолированный critic): `Glava_01_KS_draft_v2.md`; 4 флага на beats 2/3/6; новые флаги (cross_chapter_phrase_repeat, attribution_missing) — 0 срабатываний |

## Известные проблемы (из диагностики)

- 19 дублированных аннотаций в блоках «Für die vertiefende Lektüre» (разные главы, одинаковый текст)
- «Und jetzt dein Büro.» — дословный повтор в гл. 6 и гл. 7
- Гл. 3 «Loyalität aus Angst» — 15 вхождений «nicht weil/sondern weil» (лимит: 8)

## Следующий шаг

**IU Глава 01:** Запустить `bf-editor`. Предусловие: `glava_01.md` существует (статус `draft`).
Внимание: объём главы 3556 слов при chapter_target 4500 (79%). Editor решает: принять плотность или запросить расширение отдельных beats.

**MdP:** Нужна редактура перед гуманизацией.

**KS Глава 01 ПРОГОН B:** Завершён. Следующий шаг — по решению автора: сравнительный анализ ПРОГОН A vs ПРОГОН B / запуск `bf-editor` / продолжение на Гл. 02.

---

*Обновлено: 2026-05-09 после завершения writer-loop KS Глава 01 ПРОГОН B (Ф14 test, изолированный critic).*
