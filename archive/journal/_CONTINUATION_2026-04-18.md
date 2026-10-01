---
document: continuation-log
created: 2026-04-18
purpose: Передача состояния между сессиями по редизайну BooksFactory
next_session_start_here: true
---

# ЛОГ ПРОДОЛЖЕНИЯ — редизайн фабрики для zero-delay воркфлоу

## Цель пользователя (одна строка)

«Я даю идею книги → получаю весь материал на утверждение → следующий участник (роль) приступает без задержек, обладая всем необходимым».

## Что УЖЕ сделано в этой сессии

1. **series-bible.md v2.0 переписан** — 6 томов серии «Die Psychologie der korporativen Psychopathen» с фокусами, уникальными углами, территориями, матрицей отграничений.
2. **Humanizer SKILL.md** — статусы DE/EN обновлены с «TODO» на «ГОТОВ (2026-04-18)».
3. **Memory создано:**
   - `feedback_factory_vs_books.md` — не смешивать аудит фабрики и проверку книг
   - `feedback_editor_creative_not_linewise.md` — редактор старых книг работает творчески
   - `feedback_editor_lite_scope.md` — 4 предмета: читабельность / спотыкания / дубли / херня
4. **Инвентарь SpellBooks/ проведён** — см. секцию ниже.

## Решённые развилки (утверждено пользователем)

- **Слой A per-book = обязательный** с обязательным слотом `<technique>_XX.md` (книжная фишка).
- **PM = один скилл с ветвлением** research/compose (не два отдельных).
- **Writer получает ОДИН файл** — `Session_KapitelNN.md` (MATERIAL + T1 + T2-T12 склеены). Никакого чтения 7 файлов. Подтверждено примером `Abuse/Session_TEMPLATE_v2_ONM.md`.
- **abgrenzung_XX.md — обязателен только для книги в серии.** Для standalone — нет.
- **Серия = 6 томов законченных.** Band VII (Etholog) — вне скопа, в проекте.
- **Реальные названия томов:**
  - I — Rendite der Angst
  - II — Kultur der Vergiftung
  - III — Manipulationen? Noch nie gehört…
  - IV — Zeitalter der Zyniker
  - V — Immuner Geist
  - VI — Unschuld des Komplizen
- **Band IV (ZdZ) и Band V (IG) — не трогать**, они закончены.
- **«Она не монстр» (Abuse)** — standalone, закончена, **не часть серии**. Но Session_TEMPLATE_v2_ONM — **референс зрелого шаблона**.

## ФИНАЛЬНАЯ КАРТА (согласована)

### Слой A — per-book (производит PM-research до старта)

| Файл | Обязателен |
|---|---|
| `anweisungen_XX.md` | ✅ |
| `stil_und_ton_XX.md` | ✅ |
| `arbeitsplan_XX.md` | ✅ |
| `quellen_pool_XX.md` | ✅ |
| `arenen_pool_XX.md` | ✅ |
| `<technique>_XX.md` (книжная фишка, обязательный слот) | ✅ |
| `session_template_XX.md` (T2-T12 как в ONM v2) | ✅ |
| `MATERIAL_KapitelNN.md` × N (beat sheets всех глав) | ✅ |
| `abgrenzung_XX.md` | ⚠️ только для серии |
| `konzept.md` | опц. |

### Слой B — per-chapter (PM-compose склеивает непосредственно перед отдачей Writer'у)

`Session_KapitelNN.md` = `MATERIAL_KapitelNN` + T1 (выходной файл, калибровочные главы, уникальные правила) + T2-T12 из `session_template_XX.md`. **Побайтовый копипаст.**

### Роль → вход/выход

| Роль | Вход | Выход |
|---|---|---|
| PM-research | идея + series-bible (если серия) + brand-voice | весь слой A |
| PM-compose | `MATERIAL_NN` + `session_template_XX` | `Session_KapitelNN.md` |
| Writer | **один** `Session_KapitelNN.md` | `Draft_KapitelNN.md` |
| Editor | Session + Draft + Editorial_Registry | clean + Registry update |
| Editor-Lite (старые книги) | Draft | 4-пунктный отчёт |
| Humanizer | clean Draft + языковой модуль | Humanized |
| Translator | Humanized + glossary | Translated |

### Воркфлоу

```
Ты: идея → PM-research: слой A → ✋ GATE → 
по каждой главе: PM-compose → Session → Writer → Editor → Humanizer → (Translator)
```

## Сделано в сессии 2 (2026-04-18, продолжение)

### ✅ 1. editor-lite — было сделано в сессии 1
- `skills/editor-lite/SKILL.md` + диспетчер `.claude/skills/editor-lite/SKILL.md`

### ✅ 2. series-bible.md — правки закончены
- DE-названия Band IV/V добавлены в заголовки секций
- Band VI переименован в «Unschuld des Komplizen»
- Все 6 путей `Band-XX_*/ABGRENZUNG.md` удалены (отграничения принимаются по умолчанию)
- Frontmatter обновлён: больше не ссылается на файл в папке книги
- Секция «Обязательные артефакты» переписана под новую карту (слой A + слой B)
- Открытые вопросы почищены (убраны пункты про DE названия и ABGRENZUNG)

### ✅ 3. PM-скилл с двумя режимами (готов)
- `.claude/skills/project-manager/SKILL.md` — диспетчер с автовыбором режима по `ls arbeitsplan_*.md session_template_*.md`
- `skills/project_manager/SKILL.md` — полный скилл, версия 2.0
  - **Research-режим:** 11 шагов от pre-mortem до `_PACKAGE_INDEX.md`; gate на утверждение
  - **Compose-режим:** побайтовая склейка `Session = MATERIAL + T1 + T2-T12` через bash/sed/cat
  - Референс: `Abuse/Session_TEMPLATE_v2_ONM.md`

### ✅ 4. `architecture/shared_vocabulary.md` обновлён
- Секция 3 разбита на 3.1 (слой A — 9 артефактов per-book) и 3.2 (слой B — Session как единый файл)
- Добавлены термины: `anweisungen`, `stil_und_ton`, `arbeitsplan`, `quellen_pool`, `arenen_pool`, `<technique>`, `session_template`, `abgrenzung` (условный), `MATERIAL-блок`
- Добавлено правило: Писатель читает только Session_KapitelNN
- Статусы Humanizer DE/EN обновлены на «готов»

### ✅ 5. `templates/tpl-session-template.md` создан
- Универсальный каркас: инструкция PM-compose (часть 1) + маркер `---BEGIN_PROTOCOL---` + T2-T12 (часть 2)
- Все T2-T12 имеют плейсхолдеры `[ЗАПОЛНИТЬ]` для PM-research
- Структура совместима с `Abuse/Session_TEMPLATE_v2_ONM.md`

### ✅ 6. `architecture/handoff_contracts.md` — Контракты 1 и 4 обновлены
- Контракт 1: теперь один файл `Session_KapitelNN.md` (не два отдельных MATERIAL + Session)
- Контракт 4: ссылка на `tonal_compass.md` заменена на `stil_und_ton_XX.md`

## Сделано в сессии 2 (2026-04-18, блок 2 — финализация ролей)

### ✅ 7. Editor SKILL переписан (новое производство)
- `skills/editor/SKILL.md` v2.0: входные данные = один Session-файл + Draft + Editorial_Registry (+ опц. `stil_und_ton_XX.md` при кросс-главной проверке). Шаг 1 (тональная калибровка) переключён на T2/T7 Session-файла. Q3 ссылается на T2. Tип 3 — на T2. R8 универсальные запреты — источники перевязаны на MATERIAL-блок и T2.
- `.claude/skills/editor/SKILL.md` диспетчер: FM-07 переименован «Нарушение тональных правил книги» (T2 / stil_und_ton). Failure modes самого Редактора: добавлена строка-ловушка «Запросить tonal_compass.md → артефакт упразднён». Description уточнён: новое производство; для старых книг — editor-lite.

### ✅ 8. Writer SKILL проверен и переписан
- `skills/writer/SKILL.md` v2.0: входные данные = единственный `Session_KapitelNN.md`. Описание структуры (MATERIAL-блок + T1 + T2–T12). Порядок чтения переделан на чтение одного файла. Все ссылки на `tonal_compass.md` сняты (заменены на T2/T7 + MATERIAL-блок). Правило №6 — «Правила Session-файла побеждают дефолты». Таблица ссылок обновлена.
- `.claude/skills/writer/SKILL.md` диспетчер: полностью переписан. Позиция в цепочке уточнена («один файл»). Процедура написания секции — одно чтение Session-файла. Добавлена failure mode «Чтение файлов помимо Session». Добавлен антипаттерн «Запрос tonal_compass.md → артефакт упразднён». Правила Session-файла приоритетнее дефолтов.

### ✅ 9. Humanizer диспетчер обновлён
- `.claude/skills/humanizer/SKILL.md`: предусловие «tonal_compass.md прочитан» → «`stil_und_ton_XX.md` книги (слой A) прочитан». Правило приоритета: `stil_und_ton_XX.md` > языковой модуль.

### ✅ 10. Глоссарий создан
- `architecture/glossary.md` — полный глоссарий серии DE↔RU↔EN. 10 секций:
  1. Инварианты серии (обращение, сигнатурная фигура — по 3 языкам)
  2. Название серии и 6 томов в 3 языках
  3. Ключевые термины по томам I–VI
  4. Arenes (переводные соответствия)
  5. Микрорежимы (аналитические регистры)
  6. Failure modes (редакторские термины)
  7. Метапонятия фабрики
  8. Локализация имён и кейсов
  9. Анти-словарь AI-отпечатков целевого языка (RU→DE, RU→EN, DE→RU, DE→EN)
  10. Кандидаты (процедура пополнения)
- `skills/translator/SKILL.md` и `.claude/skills/translator/SKILL.md` — обновлены: ссылаются на `architecture/glossary.md` как на главный источник, `tonal_compass.md` заменён на `stil_und_ton_XX.md` + Session-файл.

## Что ОСТАЛОСЬ сделать (низкий приоритет, фабрика готова к первой книге через неё)

- [ ] Основной тезис серии — одно предложение (открытый вопрос в series-bible)
- [ ] Язык Band III — DE или RU (открытый вопрос)
- [ ] После запуска первой книги через фабрику — ретро-проверка: не всплыл ли забытый артефакт старой карты

## Инвентарь SpellBooks/ (полный, не терять)

**Серия (6 томов в папках `Serie/`):**
- Band I: **Rendite der Angst (MdP)** —  Полный пакет (Anweisungen, STIL_UND_TON, ABGRENZUNG, QUELLEN_POOL, STREET_CALIBRATION, Arbeitsplan, Session_Einleitung + 20 + Session_Schluss).
- Band II: **Kultur der Vergiftung (KdV)** — полный пакет.
- Band III: **Manipulationen? Noch nie gehört…** — полноценная книга, 22 главы `.md` + титул, немецкий (`_chapter_deutsch_epub.md`). Копия для теста editor-lite (2026-04-19): `BooksFactory/_testing/03_Manipulationen/`. Отдельно существует папка `Manipulation_Project/` с video-repurposing (reels, скрипты) — это параллельный слой проекта, не замена книге. Поправка инвентаря внесена 2026-04-19: ранее книга ошибочно считалась отсутствующей.
- Band IV: **Zeitalter der Zyniker (ZdZ)** — закончена, не трогать (статус: ARBEITSLOG активен, но пользователь сказал «не трогать 4 — закончена»).
- Band V: **Immuner Geist (IG)** — закончена, полный пакет в `Serie/05_Immuner_Geist/`.
- Band VI: **Unschuld des Komplizen (DK)** — полный пакет.
- Band VII: **Etholog (FN)** — в проекте, не скоп.

**Standalone:**
- `Abuse/` — «Она не монстр» (ONM) — **закончена, не трогать**. Референс шаблона: `Session_TEMPLATE_v2_ONM.md`. 30 MATERIAL-файлов + Editorial_Registry + Editorial_Protocol + HANDOFF'ы.
- `SOS_Abuse/` — 20 глав, reference material.
- `Reiki/`, `Vargan/`, `Print/`, `Свечи/` — вне скопа фабрики.

**Архивы (не трогать):**
- `Serie/Архив/Tom1-NEW/`, `Оргпсих/` — устарело.

## Важные feedback-правила (действуют в следующей сессии)

Все в memory, читаются автоматически. Ключевые:
- **Не путать аудит фабрики и проверку книг** (factory ≠ books)
- **Старые книги редактор проверяет творчески**, не построчно
- **Editor-Lite для старых книг** = 4 пункта (читабельность / спотыкания / дубли / херня), не запрашивать MATERIAL/Session/tonal_compass
- ABGRENZUNG папок книг считать правильным по умолчанию

## Ошибки, которые я уже совершил — не повторять

1. ❌ Выдумал 6 путей к `Band-XX_*/ABGRENZUNG.md` в series-bible v2.0. Папок не существует. Правка отложена в этой сессии — **сделать в следующей**.
2. ❌ Ложно утверждал, что hook-скрипты не существуют. Они существуют и работают (`check_chapter_status.sh`, `update_production_state.sh`).
3. ❌ Предположил, что пул источников IG хуже per-chapter подбора. Пользователь поправил: пул в IG именно под каждую главу, для копипаста.

## Файлы, которые надо прочитать в начале следующей сессии

1. `C:\Users\dmitr\.claude\projects\C--Users-dmitr-OneDrive-Dokumente-Projects-Skills\memory\MEMORY.md`
2. Этот файл (`_CONTINUATION_2026-04-18.md`)
3. `BooksFactory/series-bible.md` — текущее состояние
4. `BooksFactory/architecture/shared_vocabulary.md` — словарь терминов
5. `BooksFactory/architecture/handoff_contracts.md` — контракты между ролями
6. `Abuse/Session_TEMPLATE_v2_ONM.md` — референс зрелого Session-шаблона

## Стартовая команда следующей сессии

«Читай `BooksFactory/_CONTINUATION_2026-04-18.md`, продолжай с пункта X».
