"""
BooksFactory — подборка автора из Zotero → заготовка списка литературы.

Автор собирает книги в Zotero и экспортирует подборку в папку книги:
  Zotero → правый клик по подборке → «Экспортировать подборку…» → формат CSL JSON
  → сохранить как zotero_<CODE>.json

Скрипт превращает экспорт в заготовку quellen_pool (автор, год, название, ISBN).
bf-researcher дописывает аннотации и НЕ добавляет книг сверх подборки —
дополнения он выносит отдельным списком «Предложения автору».

Использование:
  python tools/zotero_pool.py --zotero <zotero_CODE.json> --out <quellen_pool_CODE.md> [--code KS]
"""
from __future__ import annotations

import argparse
import re

from bf_common import load_json, setup_stdout, write_text


def authors_str(item: dict) -> str:
    names = []
    for a in item.get("author", []) or item.get("editor", []):
        fam, giv = a.get("family", ""), a.get("given", "")
        if fam:
            initials = " ".join(f"{p[0]}." for p in re.split(r"[\s-]+", giv) if p)
            names.append(f"{fam}, {initials}".strip(", "))
        elif a.get("literal"):
            names.append(a["literal"])
    return ", ".join(names) or "?"


def year_of(item: dict) -> str:
    parts = (item.get("issued") or {}).get("date-parts") or [[]]
    if parts and parts[0]:
        return str(parts[0][0])
    m = re.search(r"\d{4}", str((item.get("issued") or {}).get("raw", "")))
    return m.group(0) if m else "????"


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zotero", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--code", default="")
    a = ap.parse_args()

    items = load_json(a.zotero)
    books = [i for i in items if i.get("type") in ("book", "chapter", None)]
    skipped = [i for i in items if i not in books]
    lines = [f"# Quellen_pool{(': ' + a.code) if a.code else ''}", "",
             "_Заготовка из подборки автора в Zotero. Аннотации дописывает bf-researcher._", "",
             "## СЛУЖЕБНАЯ ИНФОРМАЦИЯ (не копировать в книгу)", "",
             f"- Источник: `{a.zotero}` — книг: {len(books)}" + (f"; пропущено не-книг: {len(skipped)}" if skipped else ""),
             "- Книги сверх подборки не добавлять; предложения — в раздел «Предложения автору».", "",
             "## БЛОК ДЛЯ КОПИПАСТЫ (вставлять дословно)", "", "## Для дополнительного изучения", ""]
    for b in sorted(books, key=lambda i: (authors_str(i), year_of(i))):
        isbn = (b.get("ISBN") or "").split()[0] if b.get("ISBN") else ""
        lines.append(f"* **{authors_str(b)}, {year_of(b)}:** *{b.get('title', '?').rstrip('.')}.* "
                     f"(аннотация){'  <!-- ISBN ' + isbn + ' -->' if isbn else ''}")
    lines += ["", "## Предложения автору (не входят в книгу без одобрения)", ""]
    write_text(a.out, "\n".join(lines) + "\n")
    print(f"Заготовка: {a.out} — книг {len(books)}" + (f", пропущено не-книг {len(skipped)}" if skipped else ""))


if __name__ == "__main__":
    main()
