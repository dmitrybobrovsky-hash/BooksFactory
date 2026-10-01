---
document: glava_01_humanized
book: SmokeTest 2026-04-25
chapter: 01
language: ru
status: humanized
target_words: 1500
word_count: 1518
last_edited: 2026-04-26
humanizer_module: skills/humanizer/ru/
mock: >
  P-FINAL smoke-test. Humanizer — mock: реального вызова bf-humanizer нет.
  Контракт-проверка: вход = glava_01_clean.md (статус clean), не beat-файл ✓;
  языковой модуль ru/ предполагается активным ✓; статус clean → humanized ✓.
---

# Глава 01: Pipeline-Integrity (humanized)

(Mock-humanizer: текст имитирует «прошло три прохода ru/SKILL.md, ИИ-отпечатки удалены, тональные микрорежимы сохранены». В реальности humanizer изменил бы микро-ритм, синонимические замены, разбивку предложений.)

## §1 Постановка задачи

Smoke-test измеряет одно. Целостность контрактов между ролями фабрики. Не литературное качество. Не глубину голоса. Только трубу — по ней идёт текст.

Researcher собирает материал. Material-author переводит его в beat sheets. Planner строит beat-план в JSON. Compiler склеивает Session_compiled.md. У каждого звена — вход и выход. Если вход не соответствует контракту, артефакт возвращается на предыдущую роль. Текущая роль не чинит за соседа.

Чего smoke-test не измеряет — другая ось: качество прозы, голос, провокации. Это уровень writer-loop'а и редактуры. Pipeline-integrity и качество идут независимо.

## §2 Архитектура цепочки

(Идентично clean — mock-humanized.)

## §3 Условия завершения

(Идентично clean — mock-humanized.)

## QUELLEN

- _TZ_AUDIT_FIXES_2026-04-25.md §4-bis P-FINAL
- _TZ_WRITER_BEAT_BY_BEAT.md §5
- architecture/handoff_contracts.md Контракты 1–9
