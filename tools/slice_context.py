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
from bf_common import find_phrase
from lint_beat import FIGURES, antithesis_sentences, formula_registry, verbot_phrases


def section_number(section_label: str) -> str | None:
    """'§2 Проекция', '2. Проекция', 'Секция 2: …' -> '2'."""
    m = (re.search(r"§\s*(\d+)", section_label or "")
         or re.match(r"^\s*(?:Секция|Section|Abschnitt)?\s*(\d+)\s*[.:)]", section_label or "", re.I))
    return m.group(1) if m else None


def block(material: str, heading_re: str) -> str:
    """Блок от заголовка, совпавшего с heading_re, до следующего заголовка того же или старшего уровня."""
    lines = material.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(heading_re, l, re.I)), None)
    if start is None:
        return ""
    level = len(re.match(r"^(#+)", lines[start]).group(1))
    end = next((i for i in range(start + 1, len(lines))
                if re.match(rf"^#{{1,{level}}}\s", lines[i])), len(lines))
    return "\n".join(lines[start:end]).strip()


def material_section(material: str, section_label: str) -> str:
    num = section_number(section_label)
    if not num:
        return ""
    return block(material, rf"^###\s+(?:Секция|Section|Abschnitt|Kapitelabschnitt)\s+{num}\b")


def material_extras(material: str, section_label: str) -> list[str]:
    """Общие для главы блоки MATERIAL, нужные писателю: арены, якоря этой секции, запреты повторов."""
    out = []
    arenas = block(material, r"^##\s+(?:Арены|Arenen|Arenas)")
    if arenas:
        out += ["", "## 3a. Арены главы (MATERIAL)", "", re.sub(r"^##\s+.*\n", "", arenas, count=1).strip()]
    num = section_number(section_label)
    anchors = block(material, r"^##\s+Quote-before-you-speak")
    rows = [l for l in anchors.splitlines() if num and re.match(rf"^\|\s*{num}\.\d", l)]
    if rows:
        out += ["", "## 3b. Якоря этой секции (MATERIAL, сводная таблица)", "",
                "| Beat | Якорь | Источник / форма |", "|---|---|---|"] + rows
    repeats = block(material, r"^###\s+Запрещённые буквальные повторы")
    if repeats:
        out += ["", "## 3c. Запрещённые буквальные повторы (MATERIAL)", "",
                re.sub(r"^###\s+.*\n", "", repeats, count=1).strip()]
    return out


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

    material = read_text(args.material) if args.material else ""
    sec = material_section(material, beat.get("section", "")) if material else ""
    if material and not sec:
        # без MATERIAL писатель сочиняет главу по одному плану — так глава 02 KS была написана в пилоте
        raise SystemExit(f"Секция «{beat.get('section')}» не найдена в {args.material}. Контекст не собран.")
    parts += ["", "## 3. MATERIAL — секция этого beat-а", "", sec or "_(MATERIAL не передан)_"]
    if material:
        parts += material_extras(material, beat.get("section", ""))

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
    parts += budget_block(args, plan, beat)
    return "\n".join(parts) + "\n"


def budget_block(args, plan: dict, beat: dict) -> list[str]:
    """Счётчики главы до этого beat-а: писатель знает остаток бюджета ДО написания."""
    if not args.beats_dir or not Path(args.beats_dir).is_dir():
        return []
    before = [strip_frontmatter(read_text(p)) for p in beat_files(args.beats_dir)
              if int(re.search(r"beat_(\d+)", p.stem).group(1)) < args.beat_id]
    text = "\n".join(before)
    remaining = sum(1 for b in plan.get("beats", []) if b.get("beat_id", 0) >= args.beat_id)
    used = len(antithesis_sentences(text, args.lang)) if text else 0
    left = max(0, args.antithesis_budget - used)
    allow = 1 if left else 0
    lines = ["", "## 9. Бюджет главы до этого beat-а (посчитано скриптом)", "",
             f"- Антитезы «не X, а Y» / «Это не X — это Y» / «X, а не Y» / «Не X — Y»: использовано {used} "
             f"из {args.antithesis_budget} на главу; осталось {left} на {remaining} beat(ов). "
             f"В этом beat-е — не больше {allow}. Мысль формулируй прямым утверждением."]
    sig_rx = FIGURES.get(args.lang, {}).get("не_потому_что_X_а_потому_что_Y")
    planned = next((p["planned_count"] for p in plan.get("pattern_budget", []) or [] if "потому" in p.get("pattern", "")), None)
    if sig_rx and planned is not None:
        n = len(re.findall(sig_rx, text))
        lines.append(f"- Сигнатурная фигура «не потому что X — а потому что Y»: использовано {n} из {planned} "
                     f"по плану; ставь её только там, где её требует задание beat-а.")
    for spec in args.limit or []:
        word, _, mx = spec.partition("=")
        n = len(find_phrase(text.lower(), word.lower()))
        lines.append(f"- «{word}»: в главе уже {n} из {mx or '?'}.")
    return lines


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
    ap.add_argument("--lang", default="ru", choices=["ru", "de", "en"])
    ap.add_argument("--antithesis-budget", type=int, default=8)
    ap.add_argument("--limit", action="append", help="слово=максимум на главу (как в lint_beat)")
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
