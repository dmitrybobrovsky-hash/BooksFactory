# Архив 2026-05-08: эксперимент critic sonnet vs opus

## Что здесь

Артефакты эксперимента 2026-05-08 по сравнению моделей critic (sonnet vs opus) на Главе 1 KS.

### Содержимое
- `Glava_01_KS_draft_sonnet.md`, `Glava_01_KS_draft_opus.md` — два финальных draft-а
- `_critic_log_Glava_01_*.json` — логи вердиктов critic для каждой модели
- `glava_01_build_*.log.json` — build-логи прогонов
- `_critic_comparison_2026-05-08.md` — сравнительный отчёт от Code
- `prompt_critic_experiment_1.md` — промпт эксперимента
- `01_beats/`, `01_beats_opus/` — beat-уровневые черновики
- `01_beat_plan.json` — план beats (старая архитектура)
- `Session_Glava_01_KS.md` — собранный session-файл (старая архитектура)

## Почему в архиве

Эксперимент проведён в **inline-режиме** writer+critic (single-model self-critique). После Ф14 (2026-05-08) фабрика переведена на изоляцию critic как subagent + новые флаги + meta-critic в editor. Старые draft-ы устарели по архитектуре, но зафиксировали важные выводы:

1. Inline writer+critic = ложные accept на тонких дефектах.
2. Разница в драфтах — между writer-моделями (opus плотнее), не critic-моделями.
3. У старого bf-critic.md отсутствовали флаги для cross-chapter повторов, структурных паттернов, отсутствия атрибуции.

## Дальнейшие действия

Глава 1 KS будет переписана с нуля по новой архитектуре. См. `_SESSION_STATE.md` записи (26)–(27) и `BOOKSFACTORY_AI.md` §13 Ф14.

Файлы НЕ удалять — это история эволюции фабрики.
