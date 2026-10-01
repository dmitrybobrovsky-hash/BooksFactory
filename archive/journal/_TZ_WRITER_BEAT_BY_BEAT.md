# ТЗ: Переход Writer на beat-by-beat архитектуру

Дата: 2026-04-23
Статус: проект ТЗ, ожидает одобрения автора
Автор: Dmitry Bobrovsky
Область: BooksFactory.fabric, слой агентов
Связанные документы:
- `_HANDOFF_FACTORY_TUNING_2026-04-23.md` (первый handoff)
- `_HANDOFF_FACTORY_TUNING_2026-04-23_PART2.md` (этот handoff)
- `_testing/03_Manipulationen/_workdir/_RESEARCH_LLM_WRITING.md` (обоснование)
- `Abuse/Session_TEMPLATE_v2_ONM.md` (референс-шаблон)
- `Abuse/PROMPT_create_MATERIAL_v4.md` (референс-промпт)

---

## 0. Зачем. Почему нельзя делать минимальный фикс

### 0.1 Обоснование перехода

Research-консенсус (`_RESEARCH_LLM_WRITING.md`, 488 строк) единогласно показывает:

1. **LLM ломается после ~2000 слов в одном вызове** (HelloBench, arxiv 2409.16191).
2. **Writer ≠ Editor = pipeline, не роль** (Google ADK, Agents' Room, LangGraph).
3. **Beat-decomposition индустриальный стандарт** (Sudowrite, NovelCrafter, AgentWrite): ~500 слов × 15–17 beats/глава.
4. **Tools signal** = структура поведения. Writer с Read/Grep/Edit ведёт себя как редактор (Session 2 провал: ×4 недобор объёма).

### 0.2 Почему не минимальный фикс

Минимальный фикс (убрать Edit, удалить шаг «Read MATERIAL») **не решает главное**: writer по-прежнему пишет всю главу целиком. Остаются:
- 7500-слов-задача в одном вызове → HelloBench failure mode.
- Нет per-beat quality gate (critic без loop бесполезен).
- Двойная работа: через 2–3 сессии всё равно переписывать полностью.

Правильно: **один раз спроектировать конечную форму**, перейти туда шагами с чёткими критериями готовности.

### 0.3 Что ПРЯМО ЗАПРЕЩЕНО делать в рамках этого ТЗ

- Править `bf-writer.md` точечно, не целиком.
- Делать «переходную форму» без даты отказа.
- Смешивать beat-level и section-level в одном агенте.
- Добавлять tools к writer-у «временно».
- Переписывать под одну книгу (Band III / Abuse / любую).

---

## 1. Целевая архитектура

### 1.1 Полный пайплайн beat-by-beat

```
┌─────────────────┐
│ Author идея     │ (человек)
└────────┬────────┘
         ↓
┌──────────────────┐
│ bf-researcher    │ (Opus) — исследует, план-оглавление, пул литературы
└────────┬─────────┘
         ↓ одобрение автора
┌──────────────────────┐
│ bf-material-author   │ (Opus) — MATERIAL для каждой главы
└────────┬─────────────┘
         ↓
┌──────────────────┐
│ bf-planner       │ (Opus) — beat-план JSON для главы (15–17 beats)
│                  │   self_check: sum_target_words = 1.13 × target
└────────┬─────────┘
         ↓ одобрение beat-плана автором
┌──────────────────┐
│ bf-compiler      │ (Sonnet, bash cp+sed) — собирает Session файл:
│                  │   T1..T12 + MATERIAL + beat-план + эталон + verbot
└────────┬─────────┘
         ↓
┌──────────────────────────────────────────────────┐
│ bf-coordinator — loop per-beat (max_iterations=3)│
│                                                   │
│  for beat in beat_plan:                           │
│    bf-writer(beat, ctx) → <beat_text>+<count>    │
│    bf-critic(beat_text) → JSON {action, flags}   │
│    if accept: save to scratchpad, next beat       │
│    if revise: bf-writer(revise, notes) → loop    │
│    if rewrite: STOP, эскалация автору             │
│                                                   │
│  compile_draft: concat(accepted_beats)            │
└────────┬─────────────────────────────────────────┘
         ↓
┌──────────────────┐
│ bf-editor        │ (Opus) — макро: King 10% cut, межбеатные швы
└────────┬─────────┘
         ↓ одобрение автора
┌──────────────────┐
│ bf-humanizer     │ (Opus) — гуманизация
└────────┬─────────┘
         ↓
┌──────────────────┐
│ bf-translator    │ (Opus, если нужно) — перевод
└──────────────────┘
```

### 1.2 Роли и тулсеты (окончательные)

> **model-sync 2026-04-25.** Таблица сверена с фактом (frontmatter `.claude/agents/bf-*.md`) в рамках P1-3 ТЗ-аудита. «Target»-колонки совпадают с фактом для всех закрытых фаз. Расхождения target vs факт явно помечены в столбце «Статус»: bf-writer (Ф7 не сделан — фактически tools `Read, Write, Edit`), bf-coordinator (Ф8 не сделан — модель `haiku`, после Ф8 → `sonnet`), bf-continuity-checker (Ф11 не сделан — файл отсутствует). Источник sync — `_TZ_AUDIT_FIXES_2026-04-25.md` P1-3.

| Агент | Модель (target) | Tools (target) | Статус |
|-------|--------|-------|--------|
| bf-researcher | opus | Read, Grep, Glob, WebSearch, WebFetch, Write | ✅ создан 2026-04-24 (Ф4/Д3 split) |
| bf-material-author | opus | Read, Grep, Write | ✅ создан 2026-04-24 (Ф4/Д3 split) |
| bf-planner | opus | Read, Grep, Glob, Write | ✅ создан (Ф5; факт включает Write) |
| bf-compiler | sonnet | Read, Write, Bash | ✅ создан 2026-04-24 (Ф3/Д4) |
| bf-coordinator | sonnet (target после Ф8) | Read, Write, Glob, Grep | ⚠️ haiku сейчас (Ф8 не сделан, B4) |
| **bf-writer** | **opus** | **НЕТ (target после Ф7)** | ⚠️ Read, Write, Edit сейчас (Ф7 не сделан, Д2) |
| bf-critic | sonnet | Read | ✅ создан 2026-04-23 (Ф1/Д9) |
| bf-controller | sonnet | Read, Grep, Glob | ✅ создан 2026-04-23 (Ф0; расширен audit_task 2026-04-25) |
| bf-editor | opus | Read, Grep, Write | ✅ корректен |
| bf-humanizer | opus | Read, Edit, Write | ✅ корректен |
| bf-translator | opus | Read, Write, Edit | ✅ корректен |
| bf-pm | opus | Read | 🪦 DEPRECATED stub (Ф4; tools урезаны до Read структурно) |
| bf-continuity-checker | sonnet | Read, Grep | ⬜ не создан (Ф11/Д11) |

---

## 2. Контракт bf-writer (beat-by-beat)

### 2.1 YAML-frontmatter

```yaml
---
name: bf-writer
description: "BooksFactory Writer: pure-LLM beat writer. One call = one beat. Zero filesystem tools — all context is supplied in the prompt by the coordinator. Returns tagged prose + word-count."
model: opus
---
```

**Поле `tools:` отсутствует полностью** (pure LLM). Это структурная защита, не стилистическая рекомендация.

### 2.2 Вход (координатор собирает в промпт)

Координатор обязан передать в промпте ВСЁ из этого списка. Writer не читает ничего сам:

1. **Beat-описание** (JSON-блок, из beat-плана):
   ```json
   {
     "beat_id": 5,
     "section": "§4 Центральная сцена",
     "thema": "описание одним-двумя предложениями",
     "target_words": 500,
     "style_anchor": "REFERENZ маркер №5 — трёхчастная отбивка",
     "quote_before": "§Диагностичность (61-70): ...",
     "material_refs": ["инвентарь §3 строки 40-55", "эталон §8.2"],
     "constraints": ["без Minenfeld-метафор", "безличная грамматика"],
     "street_calibration": true,
     "target_provocation": "среда"
   }
   ```

2. **2 последних принятых beat-а** текущей главы (для continuity внутри главы).

3. **Полный текст эталонной главы голоса книги** (из `tonal_compass.md → reference_chapter`).

4. **Выдержка из tonal_compass.md** (голос, запреты, 12 контрольных вопросов) — компилятор формирует сжатую версию.

5. **Verbot-Liste книги** (полный regex/substring-список запретов).

6. **Quote-before-you-speak-цитата** — буквальная цитата правила протокола, которое этот beat реализует.

7. **Калибровочные фрагменты** — последние 2 секции предыдущей принятой главы (если существует).

8. **Scratchpad-метка** — номер beat-а, последний ли в главе (`is_last_beat: true/false`).

### 2.3 Выход (тегированный формат)

**Обязательно в тегах, автоматически парсится координатором:**

```
<beat_text>
(немецкая проза beat-а — min target_words, без заголовков, без комментариев, без мета-пояснений)
</beat_text>

<word_count>NNN</word_count>

<notes>
(опционально, 1–3 строки на русском: о чём сомневался; стилевая находка)
</notes>
```

Если теги не соблюдены — координатор не сможет собрать главу. **Это контрактное требование.**

### 2.4 Режим работы: Draft Fat

> King's правило: «2nd Draft = 1st Draft − 10%». Writer производит первый draft — плотно, в голос. Editor режет 10%.

> Lamott: «Almost all good writing begins with terrible first efforts.» Разрешение на плотность — не на небрежность.

Практически:
- Писать **минимум target_words**, желательно 1.0–1.2×.
- **Не экономить.** Не ужимать.
- **Не критиковать себя.** Это задача `bf-critic`.
- **Не править.** Если critic вернёт revise — это другой вызов.
- **Один вызов = один beat.** Не писать несколько beats в одном ответе.

### 2.5 Самопроверка перед возвратом

Writer внутренне проверяет 7 пунктов:

1. **word_count ≥ target_words** из beat-описания. Если меньше — допиши.
2. **Хотя бы одна конкретная сцена**, если `street_calibration: true`.
3. **Ни одного запрета** из переданной Verbot-Liste.
4. **Quote-before-you-speak реализован** — цитата правила отражена предложением/абзацем.
5. **style_anchor реализован** — маркер эталона явно присутствует.
6. **target_provocation реализован** — провокация направлена на указанную мишень.
7. **Не оканчивать оптимистично**, если `is_last_beat: true`.

### 2.6 Типовые отказы

| Запрос | Ответ Writer-а |
|--------|----------------|
| «Напиши всю главу» | «Один вызов = один beat. Передай мне beats по очереди.» |
| «Пиши короче / экономь слова» | «Я пишу minimum target_words. Editor сократит. Экономия — задача editor-а.» |
| «Проверь этот текст» | «Я писатель, не критик. Вызови bf-critic.» |
| «Отредактируй beat X» | «Я пишу первый draft. Правка — новый вызов с revise-инструкциями.» |
| «Контекст недостаточен» | Валидный ответ координатору, если он не передал эталон / tonal / beat / continuity. Требуй недостающее. Не сочиняй. |

### 2.7 Revise-режим (повторный вызов от координатора)

Если critic вернул `action: "revise"`, координатор делает повторный вызов writer-а с промптом:

```
REVISE beat {beat_id}.

Предыдущий вариант: <предыдущий beat_text>
Word count предыдущего: {actual_words} (target: {target_words})

Критик указал флаги:
{flags со строками из critic.notes}

Требуется: исправить именно указанные флаги. Остальное по возможности оставить.
Вернуть в том же теговом формате.
```

Writer обрабатывает это как новый вызов. Не помнит предыдущий — он весь в промпте.

---

## 3. Контракт bf-coordinator (loop-машина)

### 3.1 Роль в beat-by-beat

Координатор перестаёт быть «роутером на основании статуса» (текущая форма) и становится **loop-оркестратором**.

Основные обязанности:
1. Собирать промпты для writer-а по контракту §2.2.
2. Парсить tagged-output writer-а (`<beat_text>`, `<word_count>`, `<notes>`).
3. Отправлять beat_text + beat-описание в critic.
4. Парсить JSON-вердикт critic-а.
5. Принимать решения: accept / revise / rewrite / эскалация.
6. Поддерживать scratchpad принятых beats.
7. Выполнять compile_draft после всех accepted.

### 3.2 Scratchpad (в памяти сессии)

```json
{
  "chapter": 1,
  "beat_plan_path": "Abuse/_drafts/01_beat_plan.json",
  "session_path": "Abuse/_drafts/01_session_compiled.md",
  "accepted_beats": [
    {"beat_id": 1, "text": "...", "word_count": 520, "iterations": 1},
    {"beat_id": 2, "text": "...", "word_count": 480, "iterations": 2}
  ],
  "current_beat_id": 3,
  "iterations_on_current": 0,
  "flags_history": [...]
}
```

### 3.3 Loop-механика (псевдокод)

```
for beat in beat_plan.beats:
    scratchpad.current_beat_id = beat.beat_id
    scratchpad.iterations_on_current = 0
    
    prompt = build_writer_prompt(
        beat=beat,
        last_2_accepted=scratchpad.accepted_beats[-2:],
        session=session_file_text,
        reference_chapter=book.reference_chapter_text,
        tonal_excerpt=book.tonal_compass_excerpt,
        verbot_liste=book.verbot_liste,
        calibration=prev_chapter.last_2_sections,
        is_last_beat=(beat.beat_id == beat_plan.beats_count)
    )
    
    while scratchpad.iterations_on_current < 3:
        writer_response = call_agent(bf-writer, prompt)
        beat_text, word_count = parse_tags(writer_response)
        
        critic_response = call_agent(bf-critic, {
            beat_description: beat,
            beat_text: beat_text,
            actual_words: word_count
        })
        verdict = parse_json(critic_response)
        
        if verdict.action == "accept":
            scratchpad.accepted_beats.append({
                beat_id: beat.beat_id,
                text: beat_text,
                word_count: word_count,
                iterations: scratchpad.iterations_on_current + 1
            })
            break
        
        elif verdict.action == "revise":
            prompt = build_revise_prompt(beat, beat_text, verdict.flags, verdict.notes)
            scratchpad.iterations_on_current += 1
        
        elif verdict.action == "rewrite":
            escalate_to_author("Beat {beat.beat_id} требует пересмотра плана. Причина: {verdict.notes}")
            STOP
    
    if scratchpad.iterations_on_current == 3:
        escalate_to_author("Beat {beat.beat_id} не сошёлся за 3 итерации")
        STOP

compile_draft(scratchpad.accepted_beats, output_path)
```

### 3.4 Exit conditions

| Условие | Действие |
|---------|----------|
| Все beats accepted | compile_draft → bf-editor |
| max_iterations на beat-е | эскалация автору |
| critic → rewrite | эскалация автору |
| автор выбирает «перегенерить план» | возврат к bf-planner |
| автор выбирает «скорректировать beat вручную» | continue с модифицированным beat |

### 3.5 Compile_draft

Механическое действие координатора (bash):
1. `cat` всех `accepted_beats[i].text` через пустую строку-разделитель.
2. Запись в `<book>/_drafts/NN_draft_v1.md`.
3. Подсчёт общего word_count.
4. Лог в `<book>/_drafts/NN_draft_v1.log.json`: количество beats, сумма слов, итерации на beat, длительность.

После compile_draft координатор вызывает bf-editor на собранный файл.

---

## 4. Адаптация Session-шаблона

### 4.1 Новая структура Session файла (собирает Compiler)

Compiler собирает Session из компонентов. Итоговый файл:

```
# Session <Book> Kapitel NN

## T1. Метаданные + калибровка
<заполняется PM/research>

## T2. Специфические запреты
<из tonal_compass>

## T3. Голос (выдержка)
<из tonal_compass голос-блок>

## T4. Тональные якоря
<из tonal_compass tonal-блок>

## T5. Каркас главы (секции, микрорежимы)
<из research/material>

## T6. MATERIAL
<заменяет отдельный MATERIAL_Glava_NN.md!>
<полный MATERIAL с beat sheets по секциям>

## T7. Beat-план (JSON)
<полный вывод bf-planner>

## T8. Арены / Сцены / Источники
<из research>

## T9. Провокации
<из tonal_compass и material>

## T10-T12. Объём, QUELLEN, continuity
<стандартные поля ONM>

---BEGIN_REFERENCE_CHAPTER---
<полный текст эталонной главы голоса книги>

---BEGIN_VERBOT_LISTE---
<regex/substring-список>

---BEGIN_CALIBRATION---
<последние 2 секции предыдущей принятой главы, если есть>

---BEGIN_PROTOCOL---
<выдержка из stil_chunks или tonal_compass>
```

### 4.2 Почему MATERIAL внутри Session (ONM)

Из цитаты автора: «писатель получает сессион и ему уже не надо ничего дополнительного, кроме написанных глав для калибровки».

MATERIAL как отдельный файл — лишняя файловая навигация для writer-а. В ONM-модели (`Abuse/Session_TEMPLATE_v2_ONM.md`) MATERIAL уже внутри.

### 4.3 Роль Compiler (bf-compiler)

Sonnet-агент с bash/Read/Write. Выполняет:
1. Читает `Session_TEMPLATE.md` книги (шаблон).
2. Читает `MATERIAL_Glava_NN.md` (от bf-material-author).
3. Читает `NN_beat_plan.json` (от bf-planner).
4. Читает `tonal_compass.md` книги.
5. Читает `verbot_liste.md` книги.
6. Читает эталон голоса (путь из tonal_compass).
7. Читает последнюю принятую главу (для калибровки).
8. Через `cp` + `sed` собирает все компоненты в `_drafts/NN_session_compiled.md`.
9. Self-check: все маркеры на месте, все секции заполнены, beat-план валиден JSON.

Compiler **не пишет прозу.** Не интерпретирует. Только сборка. Провал = точная ошибка (какой маркер не нашёлся, какая секция пустая).

---

## 5. Фазы перехода (порядок имплементации)

### 5.1 Таблица фаз

| Фаза | Дефект | Файл | Блокирует | Статус |
|------|--------|------|-----------|--------|
| Ф0 | (база) | Правило 6 writing_control.md | — | ✅ 2026-04-23 |
| Ф1 | Д9 | bf-critic.md | Д10 | ✅ 2026-04-23 |
| Ф2 | Д1 | CLAUDE.md строка 13 | — | ⬜ |
| Ф3 | Д4 | bf-compiler.md (новый) | Session compile | ⬜ |
| Ф4 | Д3 | bf-researcher.md + bf-material-author.md (новые), bf-pm.md deprecate | — | ⬜ |
| Ф5 | — | bf-planner.md (новый; возможно внутри bf-pm или отдельно) | Д10 | ⬜ |
| Ф6 | — | Session-шаблон добавить T7 beat-план + BEGIN_REFERENCE | Д10 | ⬜ |
| Ф7 | Д2 | **bf-writer.md полная переделка** (tools: —, beat-level, tagged) | Д10 | ⬜ |
| Ф8 | Д10 | **bf-coordinator.md переделка** в loop-машину | — | ⬜ |
| Ф9 | Д6 | маршрут Workflow B в bf-coordinator | — | ⬜ |
| Ф10 | Д7 | backup-hook покрытие Edit | — | ⬜ |
| Ф11 | Д11 | bf-continuity-checker.md | — | ⬜ |
| Ф12 | — | Миграция Abuse на новую схему (если в работе) | — | ⬜ |
| Ф13 | — | Band III Kapitel 01 через новую фабрику | — | ⬜ отложено |

### 5.2 Критические зависимости

```
Ф7 (writer) ────┐
                ├──→ Ф8 (coordinator loop)
Ф1 (critic) ────┘

Ф3 (compiler) ──→ Ф6 (Session template) ──→ Ф8

Ф4 (PM split) → Ф5 (planner)
```

### 5.3 Рекомендуемый порядок следующей сессии

**Если контекста много** (>60%):
1. Ф2 (Д1 — одна строка).
2. Ф3 (Д4 — bf-compiler.md, новый файл).
3. Ф4 (Д3 — split PM, новые файлы, старый deprecate).
4. Ф5 (planner — отдельный агент).
5. Пауза, составить промежуточный лог.

**Если контекста мало** (<40%):
1. Ф2 (одна строка).
2. Ф3 (compiler).
3. Лог.

**Никогда в одну сессию:** не трогать Ф7 (writer) + Ф8 (coordinator) одновременно — это сердце loop-а, риск сломать пайплайн.

---

## 6. Миграция существующих проектов

### 6.1 Abuse

Статус: по ONM, MATERIAL + Session_TEMPLATE_v2_ONM в работе.

Действия:
- Добавить в Session_TEMPLATE поле T7 (beat-план).
- Если главы в работе — закончить по старой схеме, новые по новой.
- Не ломать идущую работу.

### 6.2 Band III («Manipulationen? Noch nie gehört…»)

Статус: ни одна глава не начата (две сессии провалены).

Действия:
- Применяем новую схему с нуля, начиная с Kapitel 01.
- Diagnose старых провалов делать не нужно (инфраструктура другая).

### 6.3 Готовые книги серии

Не трогать. Готовое не переделываем.

---

## 7. Риски и смягчения

| Риск | Вероятность | Смягчение |
|------|-------------|-----------|
| Writer без tools «не сможет» восстановить контекст | средняя | Coordinator инжектит всё полным текстом. Writer отвечает «контекст недостаточен» если чего-то нет. Чёткий контракт §2.2. |
| Затраты: writer × 15 beats = ×15 API-calls | высокая | Research validates cost/quality tradeoff. Оцениваем на первой главе Abuse/Band III, если неподъёмно — оптимизируем (beat-packing, shared prefix cache). |
| Compiler-bash ломается на Windows | средняя | Использовать Node/PowerShell-совместимые команды. Тестировать compile на Abuse перед Band III. |
| Beat принят critic-ом, но шов к соседнему beat-у торчит | высокая | Editor-макро (bf-editor, существующий) занимается межбеатными швами после compile_draft. Новый flag в bf-editor: "межбеатные швы". |
| Planner неверно оценит target_words per beat | средняя | self_check (sum = 1.13 × target, ±5%) + одобрение beat-плана автором перед writer-loop. |
| Revise-loop не сходится за 3 итерации | низкая | Эскалация автору. Автор решает: корректировать вручную, или перегенерить beat план. |
| Инвалидация старого bf-pm.md сломает что-то | низкая | Старый bf-pm.md помечаем deprecated, не удаляем. Новые агенты создаём рядом. После подтверждения работы — удаляем. |

---

## 8. Что НЕ меняется

Явный список, чтобы не было скрытого scope creep:

- `bf-humanizer.md` — остаётся как есть.
- `bf-translator.md` — остаётся как есть.
- `bf-editor.md` — остаётся макро-отчётником для собранной главы.
- Editor-Lite (`skills/editor-lite/SKILL.md`) — остаётся как есть.
- Workflow B (внешние книги) — остаётся, через Editor-Lite.
- `tonal_compass.md` формат — остаётся (фабричный стандарт).
- `skills/writer`, `skills/editor` папки — остаются (опционально дополняем ref-файлами).
- Memory-файлы автора (`feedback_*.md`) — не трогаем.

---

## 9. Критерии готовности (per phase)

Каждая фаза считается готовой только когда:

1. Файлы существуют и читаемы (grep-проверка в таблице handoff §4).
2. YAML-frontmatter валиден.
3. В файле явно указаны входные/выходные контракты.
4. Показан diff автору, получено «ок».
5. Лог handoff обновлён (строки «Ф<N> ⬜» → «Ф<N> ✅ <дата>»).

---

**Конец ТЗ. Версия 1.0. 2026-04-23.**
