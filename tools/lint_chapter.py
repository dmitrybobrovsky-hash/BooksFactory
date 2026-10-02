"""
BooksFactory — проверка главы целиком (до сборки чистовика и до редактора).

Per-beat проверка не видит того, что складывается из многих beat-ов: превышение
бюджета антитез, общий объём выше потолка, один и тот же реквизит в разных сценах
(«четверг», «логист», 90 минут против двух часов), дословные повторы мыслей.
Скрипт собирает эти факты; критик главы решает, что из них — дефект.

Использование:
  python tools/lint_chapter.py --plan <NN_beat_plan.json> --beats-dir <NN_beats/> \
      [--lang ru] [--min-words 5800] [--max-words 6200] [--antithesis-budget 8] [--limit Таро=3] [--out <json>]

Вывод: JSON. Код выхода 0 — превышений нет, 1 — есть (объём, бюджет, лимиты).
"""
from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict

from bf_common import (beat_files, dump_json, find_phrase, find_word_forms, load_json, read_text, setup_stdout,
                       sentences, strip_frontmatter, word_count, words, write_text)
from lint_beat import FIGURES, antithesis_sentences, plan_word_limits

PROPS = {
    "ru": {
        "день недели": r"(?<![а-яё])(?:понедельник|вторник|четверг|пятниц[аеуы]|суббот[аеуы]|воскресень[ея])[а-яё]*|(?<![а-яё])(?:в|по|до|к|со)\s+сред(?:у|ам|ы|е)(?![а-яё])",
        "длительность": r"(?:\d+|[а-яё]*(?:сто|десят[иь]?|надцат[иь]|два|две|три|четыре|пять|шесть|семь|восемь|девять|полтора|полчаса))\s+(?:минут[аы]?|час(?:а|ов)?|дн(?:я|ей)|недел[иьюя])",
        "время": r"(?:в|без)\s+(?:\d+|[а-яё]+)\s+(?:минут\s+)?(?:час(?:а|ов)?|утра|вечера|[а-яё]+(?=\s+вечера|\s+утра))",
        "число людей": r"(?:\d+|[а-яё]+(?:надцать|десят|сорок|двадцать|тридцать))\s+(?:человек|участник[а-яё]*|руководител[а-яё]*|сотрудник[а-яё]*)",
    },
    "de": {
        "Wochentag": r"\b(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)\w*",
        "Dauer": r"\b(?:\d+|\w+)\s+(?:Minuten|Stunden?|Tage?n?|Wochen?)\b",
    },
    "en": {
        "weekday": r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)s?\b",
        "duration": r"\b(?:\d+|\w+)\s+(?:minutes?|hours?|days?|weeks?)\b",
    },
}
CONNECTORS = {
    "ru": r"^(Отсюда|Поэтому|Значит|Итак|Следовательно|Таким образом|Иначе говоря|Другими словами|При этом|Кроме того|Именно поэтому|Вот почему)\b",
    "de": r"^(Daher|Deshalb|Also|Folglich|Somit|Mit anderen Worten|Dabei|Außerdem)\b",
    "en": r"^(Hence|Therefore|Thus|So|In other words|Moreover|That is why)\b",
}
STOP = {"ru": set("который которая которое которые этого этому этот эта это эти того тому тоже также потому "
                  "чтобы когда если только можно нельзя нужно своей свой свою своих себя всего всех каждый "
                  "более менее очень может могут будет будут было были есть".split()),
        "de": set(), "en": set()}


def ngrams(toks: list[str], n: int):
    return zip(*(toks[i:] for i in range(n)))


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--beats-dir", required=True)
    ap.add_argument("--lang", default="ru", choices=["ru", "de", "en"])
    ap.add_argument("--max-words", type=int, help="потолок главы (по умолчанию — word_range плана)")
    ap.add_argument("--min-words", type=int, help="нижняя граница главы (по умолчанию — word_range плана)")
    ap.add_argument("--antithesis-budget", type=int, default=8)
    ap.add_argument("--limit", action="append", help="слово=максимум на главу")
    ap.add_argument("--max-connector", type=int, default=2, help="одна связка-мостик в начале предложения — не чаще")
    ap.add_argument("--out")
    a = ap.parse_args()

    plan = load_json(a.plan)
    given = {sp.partition("=")[0].lower() for sp in (a.limit or [])}
    a.limit = list(a.limit or []) + [f"{w}={n}" for w, n in plan_word_limits(plan).items() if w.lower() not in given]
    sec_of = {b["beat_id"]: b.get("section", "") for b in plan.get("beats", [])}
    beats = {int(re.search(r"beat_(\d+)", p.stem).group(1)): strip_frontmatter(read_text(p)).strip()
             for p in beat_files(a.beats_dir)}
    problems, report = [], {"beats": []}

    total = sum(word_count(t) for t in beats.values())
    target = plan.get("chapter_target_words")
    rng = plan.get("word_range") or []
    if a.min_words is None and len(rng) == 2:
        a.min_words = rng[0]
    if a.max_words is None and len(rng) == 2:
        a.max_words = rng[1]
    report["volume"] = {"total_words": total, "target": target, "min_words": a.min_words, "max_words": a.max_words,
                        "ratio_to_target": round(total / target, 3) if target else None}
    if a.max_words and total > a.max_words:
        problems.append(f"объём {total} > потолка {a.max_words} (сократить ≈{total - a.max_words})")
    if a.min_words and total < a.min_words:
        problems.append(f"объём {total} < нижней границы {a.min_words} (добавить ≈{a.min_words - total})")

    sig_rx = FIGURES.get(a.lang, {}).get("не_потому_что_X_а_потому_что_Y")
    anti_total, sig_total = 0, 0
    props = defaultdict(lambda: defaultdict(list))  # тип -> значение -> [beat_id]
    for bid, t in sorted(beats.items()):
        anti = antithesis_sentences(t, a.lang, True)
        sig = len(re.findall(sig_rx, t)) if sig_rx else 0
        anti_total += len(anti)
        sig_total += sig
        row = {"beat_id": bid, "section": sec_of.get(bid), "words": word_count(t),
               "antithesis": len(anti), "antithesis_sentences": [s[:140] for s in anti], "signature": sig}
        for spec in a.limit or []:
            w = spec.partition("=")[0]
            row.setdefault("word_limits", {})[w] = len(find_word_forms(t.lower(), w))
        report["beats"].append(row)
        for kind, rx in PROPS.get(a.lang, {}).items():
            for m in re.finditer(rx, t, re.I):
                props[kind][m.group(0).lower().strip()].append(bid)

    report["antithesis"] = {"chapter": anti_total, "budget": a.antithesis_budget}
    if anti_total > a.antithesis_budget:
        problems.append(f"антитез {anti_total} > бюджета {a.antithesis_budget}")
    planned = next((p["planned_count"] for p in plan.get("pattern_budget", []) or [] if "потому" in p.get("pattern", "")), None)
    report["signature_figure"] = {"chapter": sig_total, "planned": planned}
    for spec in a.limit or []:
        w, _, mx = spec.partition("=")
        n = sum(r["word_limits"][w] for r in report["beats"])
        report.setdefault("word_limits", {})[w] = {"chapter": n, "limit": mx}
        if mx.isdigit() and n > int(mx):
            problems.append(f"«{w}» {n}× > лимита {mx}")

    # Повтор связок-мостиков в начале предложений (в пилоте v2.9 — «Отсюда…» ×6)
    conn_rx = CONNECTORS.get(a.lang)
    if conn_rx:
        cnt = Counter()
        for t in beats.values():
            for snt in sentences(t):
                m = re.match(conn_rx, snt)
                if m:
                    cnt[m.group(1).lower()] += 1
        report["connectors"] = dict(cnt)
        for w, n in cnt.items():
            if n > a.max_connector:
                problems.append(f"связка «{w}» в начале предложения {n}× (лимит {a.max_connector})")

    # Реквизит сцен: значения, которые встречаются в нескольких секциях, и разные значения одного типа
    report["props"] = {kind: {v: sorted(set(ids)) for v, ids in vals.items()} for kind, vals in props.items()}

    # Общие сочетания слов в разных секциях (кандидаты на слияние сцен: «производственная компания», «начальник логистики»)
    stop = STOP.get(a.lang, set())
    pair_secs = defaultdict(set)
    pair_beats = defaultdict(set)
    for bid, t in beats.items():
        toks = [w.lower() for w in words(t)]
        for x, y in ngrams(toks, 2):
            if len(x) >= 5 and len(y) >= 5 and x not in stop and y not in stop:
                pair_secs[(x, y)].add(sec_of.get(bid))
                pair_beats[(x, y)].add(bid)
    shared = sorted(((p, s) for p, s in pair_secs.items() if len(s) >= 2), key=lambda ps: -len(pair_beats[ps[0]]))
    report["shared_word_pairs"] = [{"pair": " ".join(p), "beats": sorted(pair_beats[p])} for p, _ in shared[:30]]

    # Дословные повторы (5-граммы в разных beat-ах) — повтор формулировки мысли
    owner = defaultdict(set)
    for bid, t in beats.items():
        toks = [w.lower() for w in words(t)]
        for g in set(ngrams(toks, 5)):
            if sum(len(w) >= 5 for w in g) >= 2:
                owner[g].add(bid)
    report["repeated_phrases"] = [{"phrase": " ".join(g), "beats": sorted(b)}
                                  for g, b in sorted(owner.items(), key=lambda gb: -len(gb[1])) if len(b) >= 2][:30]

    report["problems"] = problems
    out = dump_json(report)
    if a.out:
        write_text(a.out, out + "\n")
    print(out)
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
