"""
BooksFactory — объём готовой главы (чистовик, гуманизированная версия) и попадание в диапазон.

Считает слова тела главы так же, как сборщик: без frontmatter и без строк-заголовков (#).
Диапазон — из аргументов или из word_range плана главы.

Использование:
  python tools/chapter_words.py --file <Glava_NN_..._humanized.md> [--plan <NN_beat_plan.json>] [--min 5800] [--max 6200]

Вывод: JSON {words, min, max, in_range, delta}. Код выхода 0 — в диапазоне (или диапазон не задан), 1 — вне.
"""
from __future__ import annotations

import argparse
import json
import sys

from bf_common import load_json, read_text, setup_stdout, strip_frontmatter, word_count


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True)
    ap.add_argument("--plan")
    ap.add_argument("--min", type=int)
    ap.add_argument("--max", type=int)
    a = ap.parse_args()

    rng = (load_json(a.plan).get("word_range") or []) if a.plan else []
    lo = a.min if a.min is not None else (rng[0] if len(rng) == 2 else None)
    hi = a.max if a.max is not None else (rng[1] if len(rng) == 2 else None)

    body = strip_frontmatter(read_text(a.file))
    body = "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("#"))
    n = word_count(body)

    in_range = (lo is None or n >= lo) and (hi is None or n <= hi)
    delta = 0 if in_range else (n - hi if hi is not None and n > hi else n - lo)
    print(json.dumps({"words": n, "min": lo, "max": hi, "in_range": in_range, "delta": delta}, ensure_ascii=False))
    sys.exit(0 if in_range else 1)


if __name__ == "__main__":
    main()
