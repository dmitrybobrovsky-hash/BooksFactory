# Промпт продолжения: Smoke Test Writer-Loop, Глава 01

## ПРИОРИТЕТ
**Это тест фабрики. Цель — мониторинг работы пайплайна и фиксация дефектов.**
- НЕ обходить проблемы, НЕ оптимизировать, НЕ менять файлы фабрики
- Каждый сбой фиксировать в отчёте `_smoke_test_report_PARTIAL.md` (потом переименовать в `_smoke_test_report.md`)
- Работать качественно, по спецификациям агентов, без сокращений

## Контекст

Книга: **IU — Иллюзия ума**, Глава 01 «Эффект Даннинга-Крюгера: эксперимент 1999 года»
Рабочая директория: `BooksFactory/_testing/Test1_27042026/`

Steps 1–4 выполнены. Артефакты на диске:
- `stil_und_ton_IU.md` — tonal compass
- `MATERIAL_Kapitel01.md` — material
- `01_beat_plan.json` — 13 beats, sum=5100w, chapter_target=4500w
- `01_session_compiled.md` — session file, все 16 маркеров

## Текущее состояние writer-loop

**Scratchpad:**
- Beat 1: ACCEPTED (530 слов, iter 1, 0 flags). Текст начинается: «Учительница несёт стопку тетрадей...»
- Beat 2: ACCEPTED (410 слов, iter 3). Текст начинается: «Вот что интересно. В том задании не было ни секунды колебания...»
- Beat 3: НАПИСАН (395 слов), НЕ ОЦЕНЁН critic-ом. Текст начинается: «А теперь перемотай.»
- Beats 4–13: НЕ НАЧАТЫ

**Тексты beats 1-3 потеряны (D3 — нет persistence на диск).** Session-файл и beat-plan на диске. Перегенерировать все 13 beats с нуля.

## Зафиксированные дефекты (D1–D2)

- **D1:** bf-critic не получает файловые пути для Read-инициализации. Рассинхрон контрактов coordinator↔critic.
- **D2:** Writer при revise чинит указанный флаг, но создаёт тот же флаг в другом месте текста (anaphora_storm).
- **D3:** Coordinator не персистирует accepted beats на диск. При обрыве сессии — всё теряется. HIGH priority.

Подробности — в `_smoke_test_report_PARTIAL.md`.

## Задание

### ШАГ 0 (ПЕРЕД writer-loop): Ремонт D3

Дефект D3: bf-coordinator.md хранит accepted beats только в памяти сессии. При обрыве — всё теряется. 13 beats не влезают в одну сессию.

**Ремонт:**
1. Открыть `BooksFactory/.claude/agents/bf-coordinator.md`
2. В секции §Writer-loop → §Loop-механика → Шаг 5, после `accept`:
   - Добавить: «Записать принятый beat-текст в `<book>/_drafts/NN_beats/beat_<beat_id>.md` через Write tool. Файл содержит только prose (без тегов, без мета).»
3. В секции §Scratchpad: добавить поле `beats_dir` и инструкцию «При старте loop-а проверить `<book>/_drafts/NN_beats/` — если папка содержит beat-файлы, восстановить scratchpad.accepted_beats из них и продолжить с первого отсутствующего beat_id.»
4. В секции §Compile_draft: изменить «Объединить тексты из scratchpad.accepted_beats» → «Объединить тексты из `<book>/_drafts/NN_beats/beat_*.md` в порядке beat_id».
5. Проверить что ничего другого не сломано.

**После ремонта D3** — перейти к шагу 1.

### ШАГ 1+: Writer-loop

1. Перегенерировать ВСЕ beats с нуля (1–13). Session-файл и beat-plan на диске.
2. Writer-loop: beat 1 → critic → ... → beat 13 → critic, полный цикл
3. compile_draft: объединить все accepted beats в `glava_01.md` с frontmatter
4. Обновить `_smoke_test_report_PARTIAL.md` → `_smoke_test_report.md` с полными данными
5. Фиксировать ВСЕ новые дефекты (D3, D4, ...) в отчёте

## Спецификации агентов (читать обязательно)

- `BooksFactory/.claude/agents/bf-coordinator.md` — логика loop-а
- `BooksFactory/.claude/agents/bf-writer.md` — формат вызова и ответа writer-а
- `BooksFactory/.claude/agents/bf-critic.md` — флаги, JSON-формат, правила решения
- `BooksFactory/Session_TEMPLATE.md` — структура session-файла

## Формат вызова writer-а

Передать в промпте bf-writer (Agent tool, subagent_type: bf-writer):
1. Beat-описание (JSON из `01_beat_plan.json`)
2. 2 последних accepted beat-а (для continuity)
3. Эталонная глава — null (первая глава, нет эталона)
4. Tonal-выдержка (T3+T4 из `01_session_compiled.md`)
5. Verbot-Liste — null (книга без собственного списка; кросс-книжная база в critic-е)
6. Quote-before-you-speak (из beat-описания, поле `quote_before`)
7. Калибровочные фрагменты — null (первая глава)
8. is_last_beat = true/false

## Формат вызова critic-а

Передать в промпте bf-critic (Agent tool, subagent_type: bf-critic):
1. Beat-описание (JSON)
2. beat_text (проза)
3. actual_words (пересчитать самостоятельно)
4. Голос книги (T3 из session)
5. Контрольные вопросы (BEGIN_PROTOCOL из session)
6. Verbot-Liste или пометка «кросс-книжная база»
7. Путь к `stil_und_ton_IU.md` для Read-инициализации (тест D1 — проверить, заработает ли)
