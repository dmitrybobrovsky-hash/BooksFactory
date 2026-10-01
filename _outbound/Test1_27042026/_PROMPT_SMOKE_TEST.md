---
document: prompt_claude_code_smoke_test
created: 2026-05-01
purpose: Промпт для Claude Code — smoke test writer-loop на Главе 1 книги IU
usage: скопировать содержимое в первое сообщение Claude Code
---

# Smoke Test: Writer-Loop на Главе 1 IU

## Контекст

BooksFactory обновлена до v0.9:
- bf-writer.md переписан (beat-by-beat, pure LLM, tagged output)
- bf-coordinator.md обновлён (v3: routing + writer-loop, sonnet)
- arenen_pool_IU.md исправлен (3 арены на главу)

Тестовый проект: `_testing/Test1_27042026/`

Текущее состояние главы 1: bf-researcher завершён (outline-ready). Следующие этапы не запускались.

## Задача

Довести Главу 1 книги IU от текущего состояния (`outline-ready`) до `draft` — через полный цикл:

```
bf-material-author → bf-planner → bf-compiler → /bf-write-loop 01
```

Это smoke test writer-loop (Ф7+Ф8). Цель — проверить, что цепочка работает от начала до конца.

## Пошаговый план

### Шаг 0. Инициализация

Читай в этом порядке:
1. `CLAUDE.md`
2. `BOOKSFACTORY_AI.md` — статусы элементов, не трогать ✅
3. `_HANDOFF_AUDIT_2026-05-01.md` — аудит закрыт, не трогать пункты A1–A9
4. `.claude/memory/production_state.md`
5. `architecture/FACTORY_MAP.md`

### Шаг 1. Создать stil_und_ton_IU.md

В `_testing/Test1_27042026/` отсутствует тональная карта. Нужна для bf-compiler.

На основе `_testing/Test1_27042026/anweisungen_IU.md` и `brand-voice.md`:
- Создать `_testing/Test1_27042026/stil_und_ton_IU.md`
- Голос: адаптация «Интеллигентный сукин сын» под подростковую аудиторию 14–17
- Язык книги: RU
- Reference chapter: нет (первая книга) — использовать brand-voice.md как эталон

### Шаг 2. bf-material-author → MATERIAL_Kapitel01.md

Вызвать `bf-material-author` для Главы 1.

Вход:
- `_testing/Test1_27042026/arbeitsplan_IU.md` — план книги
- `_testing/Test1_27042026/arenen_pool_IU.md` — пул арен (исправленный, 3 на главу)
- `_testing/Test1_27042026/quellen_pool_IU.md` — источники
- `_testing/Test1_27042026/stil_und_ton_IU.md` — тональная карта (из Шага 1)

Выход: `_testing/Test1_27042026/MATERIAL_Kapitel01.md`

### Шаг 3. bf-planner → 01_beat_plan.json

Вызвать `bf-planner` для Главы 1.

Вход: `MATERIAL_Kapitel01.md`
Выход: `_testing/Test1_27042026/01_beat_plan.json`

Self-check: sum(target_words) ≈ 1.13 × target_chapter_words (3500–5000 слов для Главы 1).

### Шаг 4. bf-compiler → 01_session_compiled.md

Вызвать `bf-compiler` для Главы 1.

Вход: MATERIAL + beat_plan + stil_und_ton + verbot_liste (если есть) + brand-voice.md (как reference)
Выход: `_testing/Test1_27042026/01_session_compiled.md`

Self-check: все маркеры T1–T12 на месте, BEGIN_REFERENCE, BEGIN_VERBOT, BEGIN_CALIBRATION.

### Шаг 5. /bf-write-loop 01

Запустить writer-loop через bf-coordinator.

Координатор:
1. Читает `01_session_compiled.md` и `01_beat_plan.json`
2. Для каждого beat-а: вызывает bf-writer → bf-critic → accept/revise/rewrite
3. Max 3 итерации на beat
4. После всех accepted beats → compile_draft → `_testing/Test1_27042026/glava_01.md`

При эскалации (rewrite или 3 неудачных итерации) — остановиться и отчитаться.

### Шаг 6. Отчёт

После завершения (успешного или с эскалацией) — написать отчёт:
- Сколько beats в плане
- Сколько beats принято
- Итерации на каждом beat-е
- Общий word count
- Флаги critic-а (если были)
- Проблемы (если были)

Сохранить отчёт: `_testing/Test1_27042026/_smoke_test_write_loop.md`

## Жёсткие правила

1. **Не править файлы фабрики** (bf-*.md, architecture/*, CLAUDE.md, BOOKSFACTORY*.md). Это smoke test — тестируем, не чиним.
2. **Если дефект найден** — зафиксировать в отчёте, не чинить на лету. Дефекты чинятся в отдельной сессии.
3. **Все файлы создавать в `_testing/Test1_27042026/`**, не в корне фабрики.
4. **Кириллические файлы читать через Python**, не PowerShell.
5. **Если контекст заканчивается** — остановиться, написать отчёт с текущим прогрессом, не пытаться «дожать».
