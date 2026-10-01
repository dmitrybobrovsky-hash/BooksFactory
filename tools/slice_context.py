"""
BooksFactory — контекст для одного beat-а (замена монолитного Session-файла).

Вместо Session на 175 КБ, который собирала модель, скрипт за доли секунды
собирает для писателя ровно то, что нужно для ОДНОГО beat-а:
  описание beat-а из плана, его секцию MATERIAL, два последних принятых beat-а,
  голос книги, запреты (только фразы), разовые формулы, которые нельзя повторять.

Использование:
  python tools/slice_context.py --plan <NN_beat_plan.json> --beat-id 5 \
      --material <MATERIAL_Glava_NN.md> --beats-dir <NN_beats/> \
      [--voice <stil_und_ton.md>] [--verbot <verbot_liste.md>] [--formulas <_skvoznye_formuly.md>] \
      [--reference <эталонная_глава.md> --reference-chars 6000] [--out <файл>]

Без --out печатает в stdout. Размер пакета пишется в stderr.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bf_common import (beat_files, dump_json, load_json, read_text, setup_stdout,
                       strip_frontmatter, write_text)
from lint_beat import formula_registry, verbot_phrases


def material_section(material: str, section_label: str) -> str:
    """'§2 Проекция…' -> блок '### Секция 2: …' до следующего заголовка того же или старшего уровня."""
    m = re.search(r"§\s*(\d+)", section_label or "")
    if not m:
        return ""
    num = m.group(1)
    lines = material.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if re.match(rf"^###\s+(?:Секция|Section|Abschnitt|Kapitelabschnitt)\s+{num}\b", l, re.I)), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^#{1,3}\s", lines[i])), len(lines))
    return "\n".join(lines[start:end]).strip()


def previous_beats(beats_dir: str | None, beat_id: int, n: int = 2) -> list[tuple[int, str]]:
    if not beats_dir or not Path(beats_dir).is_dir():
        return []
    out = []
    for p in beat_files(beats_dir):
        num = int(re.search(r"beat_(\d+)", p.stem).group(1))
        if num < beat_id:
            out.append((num, strip_frontmatter(read_text(p)).strip()))
    return out[-n:]


def build(args) -> str:
    plan = load_json(args.plan)
    beat = next((b for b in plan.get("beats", []) if b.get("beat_id") == args.beat_id), None)
    if beat is None:
        raise SystemExit(f"beat {args.beat_id} не найден в {args.plan}")

    parts = [f"# Контекст beat-а {args.beat_id} — глава {plan.get('chapter_number')}: {plan.get('chapter_title', '')}",
             "", "## 1. Задание beat-а", "", "```json", dump_json(beat), "```"]
    if beat.get("quote_before"):
        parts += ["", "## 2. Quote-before-you-speak", "", f"> {beat['quote_before']}"]

    sec = material_section(read_text(args.material), beat.get("section", "")) if args.material else ""
    parts += ["", "## 3. MATERIAL — секция этого beat-а", "", sec or "_(секция не найдена — сообщи координатору)_"]

    prev = previous_beats(args.beats_dir, args.beat_id)
    parts += ["", "## 4. Два последних принятых beat-а (для связности)"]
    if prev:
        for num, txt in prev:
            parts += ["", f"### beat {num}", "", txt]
    else:
        parts += ["", "_(это первый beat главы)_"]

    if args.voice:
        parts += ["", "## 5. Голос книги", "", strip_frontmatter(read_text(args.voice)).strip()]
    if args.reference:
        ref = strip_frontmatter(read_text(args.reference)).strip()[: args.reference_chars]
        parts += ["", f"## 6. Эталон голоса (первые {args.reference_chars} знаков)", "", ref]
    if args.verbot:
        phrases = sorted({p for p, _ in verbot_phrases(Path(args.verbot))})
        parts += ["", "## 7. Запрещённые фразы книги (и их вариации)", ""] + [f"- {p}" for p in phrases]
    if args.formulas:
        singles = [f for f in formula_registry(Path(args.formulas)) if f["kind"] == "single"]
        if singles:
            parts += ["", "## 8. Разовые формулы других глав — не повторять буквально", ""]
            parts += [f"- {f['id']}: {f['phrase']}" for f in singles]
    return "\n".join(parts) + "\n"


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--beat-id", type=int, required=True)
    ap.add_argument("--material")
    ap.add_argument("--beats-dir")
    ap.add_argument("--voice")
    ap.add_argument("--verbot")
    ap.add_argument("--formulas")
    ap.add_argument("--reference")
    ap.add_argument("--reference-chars", type=int, default=6000)
    ap.add_argument("--out")
    args = ap.parse_args()
    packet = build(args)
    if args.out:
        write_text(args.out, packet)
    else:
        print(packet)
    print(f"[slice_context] beat {args.beat_id}: {len(packet.encode('utf-8')) / 1024:.1f} КБ", file=sys.stderr)


if __name__ == "__main__":
    main()
