---
document: glava_01_clean
book: SmokeTest 2026-04-25
chapter: 01
language: ru
status: clean
target_words: 1500
word_count: 1520
last_edited: 2026-04-26
editor_report: _drafts/01_editor_report.md
mock: >
  P-FINAL smoke-test. Editor — mock: реального вызова bf-editor нет, файл
  имитирует «после правок editor-а, повторная проверка пройдена».
  Контракт-проверка: вход = единый glava_01.md (не beat-файлы) ✓;
  Edit-инструмент не использовался ✓; статус draft → review → clean ✓.
---

# Глава 01: Pipeline-Integrity (clean)

(Содержимое идентично glava_01.md — в smoke-test'е editor mock-вердикт «правок не требуется», поэтому clean = draft по тексту. Реальный editor вернул бы отчёт ≤5 точек, refiner внёс бы правки, повторная проверка зафиксировала clean.)

## §1 Постановка задачи

Smoke-test измеряет одно: целостность контрактов между ролями фабрики. Не литературное качество. Не глубину голоса. Только трубу, по которой текст идёт.

Когда researcher собирает материал, material-author структурирует его в beat sheets. Planner строит beat-план в JSON. Compiler склеивает Session_compiled.md. Каждое звено имеет вход и выход. Если вход не соответствует контракту — артефакт возвращается на предыдущую роль. Текущая роль не «чинит за соседа».

То, что smoke-test НЕ измеряет — работа отдельной оси: качество прозы, голос, провокации. Это уровень writer-loop'а и редактуры. Pipeline-integrity и качество — независимы.

## §2 Архитектура цепочки

(Идентично glava_01.md — mock-clean.)

## §3 Условия завершения

(Идентично glava_01.md — mock-clean.)

## QUELLEN

- _TZ_AUDIT_FIXES_2026-04-25.md §4-bis P-FINAL
- _TZ_WRITER_BEAT_BY_BEAT.md §5
- architecture/handoff_contracts.md Контракты 1–9
