---
name: draft-chapter
description: >
  Написать черновик главы по MATERIAL и Session. Активирует роль Писателя
  BooksFactory: секция за секцией, beat sheet, контроль плотности.
  Требует наличия MATERIAL-файла. Без MATERIAL — не запускать.
triggers:
  - "/draft-chapter"
  - "напиши черновик главы"
  - "пиши главу"
layer: BooksFactory
role: writer
depends_on_skill: .claude/skills/writer/SKILL.md
---

# Draft Chapter — Написание черновика главы

## Предусловия

- [ ] Существует `MATERIAL_Glava_NN.md` с beat sheet всех секций
- [ ] Существует `Session_KapitelN.md`
- [ ] Прочитана тональная карта книги (если существует)

Если MATERIAL не существует → запусти `.claude/skills/project-manager/SKILL.md` сначала.

## Процедура

1. Прочитай `architecture/shared_vocabulary.md`
3. Прочитай `architecture/writing_control.md` (beat sheet, пост-контроль)
4. Прочитай MATERIAL указанной главы
5. Прочитай Session-файл
6. Прочитай тональную карту книги
7. Прочитай калибровочные главы (указаны в T1 Session)

**Пиши секцию за секцией**:
- Применяй beat sheet
- Соблюдай микрорежим
- После каждой секции: пост-контроль плотности
- Если раздута: удалить воду, не переписывать
- Переходить к следующей секции только после прохождения контрольных ворот

## Формат вывода

Файл `NN_Glava_XX_Title.md` с правильным YAML frontmatter:
```yaml
status: draft
word-count: [реальный подсчёт]
last-edited: YYYY-MM-DD
```

Блок «Для углублённого изучения» в конце — из MATERIAL, побайтово.

## Полный скилл Писателя

`.claude/skills/writer/SKILL.md` — все правила написания, failure modes, контракты.
