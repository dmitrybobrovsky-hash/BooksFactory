---
document: glava_01
book: SmokeTest 2026-04-25
chapter: 01
language: ru
status: draft
target_words: 1500
word_count: 1520
beats_assembled_count: 9
last_edited: 2026-04-26
mock: >
  P-FINAL smoke-test. Ф8 (writer-loop) не реализована, эта глава — ручной mock,
  имитирующий выход coordinator-а после writer-loop-а. Реальный writer-loop
  заменит этот файл прозой 9 beat'ов.
---

# Глава 01: Pipeline-Integrity

## §1 Постановка задачи

Smoke-test измеряет одно: целостность контрактов между ролями фабрики. Не литературное качество. Не глубину голоса. Только трубу, по которой текст идёт.

Когда researcher собирает материал, material-author структурирует его в beat sheets. Planner строит beat-план в JSON. Compiler склеивает Session_compiled.md. Каждое звено имеет вход и выход. Если вход не соответствует контракту — артефакт возвращается на предыдущую роль. Текущая роль не «чинит за соседа».

То, что smoke-test НЕ измеряет — работа отдельной оси: качество прозы, голос, провокации. Это уровень writer-loop'а и редактуры. Pipeline-integrity и качество — независимы.

## §2 Архитектура цепочки

Researcher выходит на исследование, формирует outline и tonal_compass книги. Material-author получает outline и пишет MATERIAL_Glava_NN.md с beat sheets, аренами, quote-anchors. Planner строит beat_plan.json: 9–17 beats, sum_target_words = 1.13 × chapter_target.

Compiler читает MATERIAL + beat_plan + tonal_compass + verbot_liste + Session_TEMPLATE + reference_chapter и склеивает Session_compiled.md. Self-check проверяет 16 маркеров. Если хоть один отсутствует — output удаляется, ошибка COMPILER_MARKER_MISSING.

Coordinator получает Session_compiled.md и определяет следующий шаг. В фазе compiled следующий — writer-loop (Ф8). После прохождения writer↔critic↔controller всех beat'ов coordinator собирает glava.md. Editor работает с собранной главой, не с beat-файлами. Humanizer получает glava_clean.md. Translator получает glava_humanized.md.

## §3 Условия завершения

Все агенты вызваны или явно помечены mock. На момент 2026-04-26 закрыты Ф0–Ф6 + Ф7 в части researcher/material-author/planner/compiler/critic/controller. Ф8 (writer-loop machine) — не реализована, заменена ручным mock-ом.

Все артефакты совпадают с контрактом. MATERIAL → beat_plan → Session_compiled (self-check pass) → glava.md (mock-сборка) → glava_clean.md (Editor mock) → glava_humanized.md (Humanizer mock) → glava_translated.md (Translator mock). Каждый файл содержит YAML-frontmatter с правильным статусом.

Вердикт «pipeline integrity» зафиксирован отчётом `_smoke_test_2026-04-25.md`. Найденные дыры либо закрыты в этом ТЗ, либо вынесены в §5 «Очередь».

## QUELLEN

- _TZ_AUDIT_FIXES_2026-04-25.md §4-bis P-FINAL
- _TZ_WRITER_BEAT_BY_BEAT.md §5
- architecture/handoff_contracts.md Контракты 1–9
