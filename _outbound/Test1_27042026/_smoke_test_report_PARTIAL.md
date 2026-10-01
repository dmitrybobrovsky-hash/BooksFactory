# Smoke Test Writer-Loop — PARTIAL REPORT
**Дата начала:** 2026-05-02
**Статус:** ПРЕРВАН на beat 3 из 13 (critic ещё не оценил beat 3)
**Книга:** IU — Иллюзия ума, Глава 01

## ПРИОРИТЕТ ТЕСТА
**Цель — мониторинг и фиксация дефектов для последующего ремонта фабрики.**
НЕ обходить проблемы. НЕ оптимизировать. НЕ менять файлы фабрики. Только фиксировать.

---

## Выполненные этапы (Steps 1–4: OK)

| Шаг | Агент | Результат | Артефакт |
|-----|-------|-----------|----------|
| 1 | bf-material-author | OK | `MATERIAL_Kapitel01.md` — 4 секции, 13 beats, 4750w |
| 2 | bf-planner | OK | `01_beat_plan.json` — 13 beats, sum=5100w, ratio=1.133 |
| 3 | bf-compiler | OK (5 warnings) | `01_session_compiled.md` — все 16 маркеров на месте |
| 4 | writer-loop | В ПРОЦЕССЕ | beats 1-2 accepted, beat 3 написан но не оценён |

### Warnings компилятора (все ожидаемы для первой главы первого прогона):
- null reference_chapter (первая глава, эталона нет)
- null verbot_liste (книга без собственного списка)
- пустой calibration (первая глава)
- нет секции «quellen-format» в tonal_compass
- нет секции «12 вопросов» (использован fallback «Тест качества секции»)

---

## Writer-loop: прогресс по beats

| Beat | Target | Actual | Iter | Flags | Action | Статус |
|------|--------|--------|------|-------|--------|--------|
| 1 | 450 | 530 | 1 | 0 | accept | ✅ ACCEPTED |
| 2 | 350 | 410 | 3 | iter1: headline_echo+anaphora_storm; iter2: anaphora_storm; iter3: 0 | accept | ✅ ACCEPTED |
| 3 | 350 | 395 | — | — | — | ⏳ НАПИСАН, ОЖИДАЕТ CRITIC |
| 4–13 | — | — | — | — | — | ❌ НЕ НАЧАТЫ |

### Принятые тексты beat 1 и beat 2
Тексты были возвращены writer-ом и приняты critic-ом, но **НЕ сохранены на диск** в промежуточном виде. Они находятся только в транскрипте сессии:
- `C:\Users\dmitr\.claude\projects\C--Users-dmitr-OneDrive-Dokumente-Projects-Skills\65a5f517-2f7d-474c-968f-74f67c3a9212.jsonl`
- Beat 1: строка ~116, начинается с «Учительница несёт стопку тетрадей»
- Beat 2 (final, iter 3): строка ~185, начинается с «Вот что интересно. В том задании не было ни секунды колебания»
- Beat 3 (awaiting critic): строка ~200, начинается с «А теперь перемотай.»

---

## ДЕФЕКТЫ (D1–D2, confirmed)

### D1: Critic не получает файловые пути для Read-инициализации
**Серьёзность:** Medium
**Где:** Рассинхрон между bf-coordinator.md и bf-critic.md
**Суть:** bf-critic.md §Инициализация требует Read-доступ к файлам (tonal_compass, verbot_liste, reference chapter, beat_plan). Но bf-coordinator.md §Loop-механика Step 4 не специфицирует, что нужно передавать файловые пути. Координатор передаёт контекст inline в промпте. Critic сообщает «Файлы инициализации недоступны» и работает по переданному inline-контексту — функционально работает, но контракт нарушен.
**Ремонт:** Уточнить в bf-coordinator.md Step 4, что промпт для critic-а должен включать file paths для Read-инициализации ИЛИ обновить bf-critic.md, убрав требование Read-инициализации и заменив на inline-контекст.

### D2: Writer при revise чинит флаг, но создаёт тот же флаг в другом месте
**Серьёзность:** Medium
**Где:** bf-writer revise-режим
**Суть:** Beat 2 iter 1 имел anaphora_storm (3× «Ты» подряд). Writer исправил начала предложений, но в новом тексте появилась НОВАЯ anaphora_storm (3× «Она» подряд: «Она не болит. Она не скрипит. Она просто сидит»). Writer делает точечный fix указанного места, не пересканирует весь текст на тот же тип флага.
**Ремонт:** Добавить в revise-промпт координатора (bf-coordinator.md §Revise-промпт) явную инструкцию: «После исправления указанных флагов — пересканируй ВЕСЬ текст beat-а на наличие тех же типов флагов в других местах.»

---

### D3: Coordinator не персистирует accepted beats на диск между итерациями
**Серьёзность:** High
**Где:** bf-coordinator.md §Writer-loop, §Scratchpad
**Суть:** Спецификация хранит scratchpad (accepted_beats) в памяти сессии. compile_draft записывает файл только после ВСЕХ beats. При обрыве сессии (контекст, rate limit, таймаут) все принятые beats теряются. В данном прогоне: 2 accepted beats + 1 написанный = потеряны при обрыве на beat 3.
**Ремонт:** Добавить в bf-coordinator.md после каждого `accept`: запись beat-текста в `<book>/_drafts/01_beats/beat_NN.md`. compile_draft читает из этой папки, не из памяти. При рестарте сессии — продолжение с последнего несохранённого beat-а.

---

## Наблюдения (не дефекты)

1. **Writer на opus хорошо держит голос** — beat 1 принят с первой итерации, 530 слов при target 450.
2. **Critic на sonnet работает детерминированно** — флаги ставит корректно, JSON-формат стабилен.
3. **3 итерации на beat 2 — это максимум** — beat сошёлся ровно на лимите. Если бы iter 3 снова имел флаги → escalation к автору.
4. **Beat тексты не персистируются на диск до compile_draft** — если сессия падает, все accepted beats теряются. Это архитектурное решение (scratchpad в памяти), но риск для длинных глав.

---

## Что осталось (для продолжения)

1. **Beat 3** — текст написан (395 слов), нужно передать critic-у для оценки
2. **Beats 4–13** — полный цикл writer→critic для каждого
3. **compile_draft** — объединить все accepted beats в `glava_01.md`
4. **Финальный отчёт** — обновить этот файл полными данными по всем beats

---

## Файлы прогона

```
_testing/Test1_27042026/
├── stil_und_ton_IU.md          ← tonal compass (Step 0)
├── MATERIAL_Kapitel01.md       ← material (Step 1)
├── 01_beat_plan.json           ← beat plan (Step 2)
├── 01_session_compiled.md      ← session file (Step 3)
├── _PROMPT_SMOKE_TEST.md       ← исходное задание
├── _smoke_test_report_PARTIAL.md ← ЭТОТ ФАЙЛ
├── anweisungen_IU.md           ← исходные данные книги
├── arbeitsplan_IU.md           ← план работы книги
├── quellen_pool_IU.md          ← пул источников
├── arenen_pool_IU.md           ← пул арен
└── _extract_*.ps1              ← служебные скрипты (можно удалить)
```
