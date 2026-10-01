"""
BooksFactory — сборка главы из принятых beat-ов.

Склеивает NN_beats/beat_*.md по порядку, расставляет заголовки секций из beat-плана,
считает слова ФАКТИЧЕСКИ (не со слов модели) и пишет главу со статусом draft
и журнал сборки.

Использование:
  python tools/assemble_chapter.py --plan <NN_beat_plan.json> --beats-dir <NN_beats/> \
      --out <Glava_NN_CODE_draft.md> [--log <glava_NN_build.log.json>] [--lang ru]
"""
from __future__ import annotations

import argparse
import datetime as dt
import re

from bf_common import (beat_files, dump_json, load_json, read_text, setup_stdout,
                       strip_frontmatter, word_count, write_text)


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--beats-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log")
    ap.add_argument("--lang", default="ru")
    args = ap.parse_args()

    plan = load_json(args.plan)
    beats = {b["beat_id"]: b for b in plan.get("beats", [])}
    files = {int(re.search(r"beat_(\d+)", p.stem).group(1)): p for p in beat_files(args.beats_dir)}

    missing = sorted(set(beats) - set(files))
    if missing:
        raise SystemExit(f"Нет принятых beat-ов: {missing}. Глава не собирается.")

    body, log_beats, last_section, total = [], [], None, 0
    for bid in sorted(beats):
        b, text = beats[bid], strip_frontmatter(read_text(files[bid])).strip()
        if b.get("section") and b["section"] != last_section:
            body += ["", f"## {b['section']}", ""]
            last_section = b["section"]
        body += [text, ""]
        wc = word_count(text)
        total += wc
        log_beats.append({"beat_id": bid, "section": b.get("section"), "target_words": b.get("target_words"),
                          "actual_words": wc,
                          "ratio": round(wc / b["target_words"], 3) if b.get("target_words") else None})

    target = plan.get("chapter_target_words")
    today = dt.date.today().isoformat()
    title = plan.get("chapter_title", "")
    head = ["---", f'title: "Глава {plan.get("chapter_number")} — {title}"', "status: draft",
            f"language: {args.lang.upper()}", f"total_words: {total}", f"beats_count: {len(beats)}",
            f"date: {today}", "words_counted_by: tools/assemble_chapter.py", "---", "",
            f"# Глава {plan.get('chapter_number')}", f"# {title}"]
    write_text(args.out, "\n".join(head + body).rstrip() + "\n")

    log = {"chapter": plan.get("chapter_number"), "date": today, "output_draft": args.out,
           "total_words": total, "chapter_target_words": target,
           "ratio_to_chapter_target": round(total / target, 3) if target else None,
           "sum_target_words": plan.get("sum_target_words"), "beats": log_beats}
    if args.log:
        write_text(args.log, dump_json(log) + "\n")
    short = [b["beat_id"] for b in log_beats if b["ratio"] and b["ratio"] < 0.85]
    print(f"Глава собрана: {total} слов" + (f" из {target} ({log['ratio_to_chapter_target']:.0%})" if target else ""))
    if short:
        print(f"Короче плана (<85%): beats {short}")


if __name__ == "__main__":
    main()
