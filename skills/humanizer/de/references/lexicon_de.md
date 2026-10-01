---
document: humanizer/de/references/lexicon_de.md
layer: BooksFactory
version: 1.0
created: 2026-04-18
sources:
  - glebis/claude-skills De-AI Humanizer (german markers)
  - humanizer/ru/references/lexicon.md (структурный образец)
description: >
  Немецкие AI-маркеры, 3 уровня. Использовать в Проходе 1 гуманизатора.
---

# Lexikon DE — Немецкие AI-маркеры

## Tier 1 — Всегда флаг (заменять без обсуждения)

### Шаблонные фразы-связки

| Маркер | Почему проблема |
|--------|----------------|
| Es ist wichtig zu beachten, dass | Клише T1, русский аналог «важно отметить» |
| Es ist wichtig zu erwähnen | То же |
| Man sollte bedenken | Безличное обращение + AI-клише |
| Vor diesem Hintergrund | Бюрократический переход |
| Im Hinblick auf | Канцелярский коннектор |
| In Anbetracht dessen | То же |
| Es sei darauf hingewiesen | Пассивно-официальный маркер |
| Es lässt sich festhalten | AI-завершение абзаца |
| Es lässt sich sagen | То же |
| Zusammenfassend lässt sich sagen | AI-резюме |
| Abschließend sei bemerkt | AI-заключение |
| Es ist anzumerken | Официально-пассивный маркер |

### Избыточные прилагательные-интенсификаторы

| Маркер | Замена |
|--------|--------|
| umfassend (в каждом абзаце) | конкретный атрибут; убрать |
| ganzheitlich | конкретный атрибут |
| nachhaltig (вне экологического контекста) | конкретный атрибут |
| zielgerichtet | конкретный атрибут |
| effektiv (как ритуальное слово) | убрать или конкретизировать |
| tiefgreifend | часто без смысла |
| maßgeblich | клише |

### Безличные переходники (Tier 1 при кластеризации в одном абзаце)

| Маркер |
|--------|
| Darüber hinaus |
| Ferner |
| Zudem |
| Des Weiteren |
| Im Weiteren |
| Außerdem (при плотности > 2 на 500 слов) |

---

## Tier 2 — Флаг при кластеризации (≥ 2 в 500 словах)

### Переходники среднего риска

| Маркер | Норма |
|--------|-------|
| Jedoch | 1 на 500 слов |
| Allerdings | 1 на 500 слов |
| Dennoch | 1 на 500 слов |
| Nichtsdestotrotz | 1 на главу |
| Infolgedessen | 1 на 500 слов |
| Dementsprechend | 1 на 500 слов |
| Letztendlich | 1 на главу |
| Grundsätzlich | 1 на главу |
| Im Grunde | 1 на главу |
| Im Wesentlichen | 1 на 500 слов |

### Псевдо-академические маркеры

| Маркер | Проблема |
|--------|---------|
| Es zeigt sich, dass | AI-шаблон для «выводов» |
| Es wird deutlich, dass | То же |
| Dies verdeutlicht | Неодушевлённый субъект |
| Dies unterstreicht | То же |
| Dies zeigt | То же |
| Dies macht deutlich | То же |
| In diesem Zusammenhang | Пустой переход |
| Im Rahmen dieser Betrachtung | Академический балласт |

---

## Tier 3 — Флаг при высокой плотности (> 3 на 1000 слов)

| Маркер | Норма |
|--------|-------|
| natürlich | ≤ 2 на 1000 слов |
| selbstverständlich | ≤ 1 на 1000 слов |
| tatsächlich | ≤ 2 на 1000 слов |
| durchaus | ≤ 2 на 1000 слов |
| gewissermaßen | ≤ 1 на главу |
| sozusagen | ≤ 1 на главу |
| quasi | ≤ 2 на главу |
| sicherlich | ≤ 1 на 1000 слов |
| offensichtlich | ≤ 2 на 1000 слов |

---

## Серийные инварианты (не маркеры — правила)

| Правило | Что делать |
|---------|-----------|
| «du» — единственная форма обращения | При нахождении «Sie» (обращение) — заменить на «du» + соответствующий глагол |
| «man» в обращении к читателю | Заменить на «du» конструкцию |
| «der Leser» как обращение | «du» конструкция |
| «nicht weil X — sondern weil Y» | НЕ трогать, только посчитать |

---

## Коучинговые маркеры (Tier 1 в контексте BooksFactory)

| Маркер |
|--------|
| Versuchen Sie |
| Versuche (в обращении-совете) |
| Beachten Sie |
| Beachte (в мягком совете) |
| Es empfiehlt sich |
| Man könnte erwägen |
| Vielleicht möchten Sie |
| Es wäre ratsam |
