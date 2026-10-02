"""
BooksFactory — детерминированная проверка beat-а («пол» качества).

Считает то, что модель-критик считает плохо: объём, запрещённые фразы, повторы,
сквозные формулы, синтаксические фигуры, обращение к читателю. Критик получает
этот отчёт как факты и судит только о голосе, ритме и провокации.

Использование:
  python tools/lint_beat.py --beat <beat.md> --plan <NN_beat_plan.json> --beat-id 3 \
      [--verbot <verbot_liste.md>] [--formulas <_skvoznye_formuly.md>] \
      [--chapter-beats <NN_beats/>] [--lang ru|de|en] [--limit паттерн=2]

Вывод: JSON в stdout. Код выхода 0 — блокирующих нарушений нет, 1 — есть.
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from bf_common import (QUOTED_RE, beat_files, dump_json, find_phrase, find_word_forms, load_json,
                       normalize_phrase, read_text, sentences, setup_stdout,
                       strip_frontmatter, word_count, words)

# Синтаксические фигуры по умолчанию (счётчик на главу, порог 6 — bf-critic §C)
FIGURES = {
    "ru": {
        "не_X_а_Y": r"(?<![А-Яа-яЁё])[Нн]е\s[^.!?\n]{1,80}?(?:—|,)\s*а\s",
        "это_не_X_это_Y": r"Это не [^.!?\n]{1,100}[.!?]\s+Это\s",
        "не_потому_что_X_а_потому_что_Y": r"(?<![А-Яа-яЁё])[Нн]е (?:потому|на том|о том|в том),? что[^.!?\n]{1,120}?а (?:потому|на том|о том|в том),? что",
    },
    "de": {
        "nicht_X_sondern_Y": r"\bnicht\b[^.!?\n]{1,80}?,?\s*sondern\b",
        "das_ist_nicht_X_das_ist_Y": r"Das ist nicht [^.!?\n]{1,100}[.!?]\s+Das ist\s",
    },
    "en": {
        "not_X_but_Y": r"\bnot\b[^.!?\n]{1,80}?,?\s*but\b",
        "this_is_not_X_this_is_Y": r"This is not [^.!?\n]{1,100}[.!?]\s+This is\s",
    },
}
# Антитеза «не X, а Y» во всех формах — счётчик по ПРЕДЛОЖЕНИЯМ, бюджет на главу.
# В пилоте (2026-10-01) per-beat фигуры не ловили «Это не X — это Y», «X, а не Y», «Не X — Y»:
# скрипт видел 8, редактор насчитал ~20 (детектор ниже даёт 27, с запасом на ложные срабатывания).
_W = r"[^.!?\n]"
ANTITHESIS = {
    "ru": [
        rf"(?<![А-Яа-яЁё])[Нн]е\s{_W}{{1,80}}?(?:—|,)\s*а\s",
        r",\s*а не\s",
        rf"(?:^|\s)[Ээ]то не\s{_W}{{1,120}}—\s*это\s",
        rf"(?:^|[.!?]\s+)Не\s[^.!?\n—,]{{1,40}}[—,]\s*[а-яё]",
        rf"(?<![А-Яа-яЁё])не\s[^.!?\n,—]{{1,40}}—\s*(?:он|она|оно|они|это)\s",
        r"\s—\s*не\s(?:в|о|об|на|про)\s",
        r"\s—\s*не\s[^.!?\n]{1,80}[.!?]?$",
        rf"(?<![А-Яа-яЁё])не\s{_W}{{1,80}}?,\s*(?:а\s)?это\s",          # не X, это Y
        r"[А-Яа-яЁё],\s*не\s[А-Яа-яЁё]+(?:ый|ий|ой|ая|яя|ое|ее|ые|ие)?,\s",  # профессиональный, не научный,
    ],
    "de": [r"\bnicht\b[^.!?\n]{1,80}?,?\s*sondern\b", r"\bkein\w*\b[^.!?\n]{1,80}?,?\s*sondern\b",
           r"(?:^|\s)Das ist nicht\b"],
    "en": [r"\bnot\b[^.!?\n]{1,80}?,?\s*but\b", r",\s*not\s", r"(?:^|\s)This is not\b"],
}
# Вторая фраза пары «X — не Y. Это Z.» / «Это не X. Это Y.»
ANTITHESIS_NEXT = {"ru": r"^(?:Это|Она|Он|Оно|Они)\s", "de": r"^Das ist\b", "en": r"^(?:This|It) is\b"}


def antithesis_sentences(text: str, lang: str = "ru", with_signature: bool = False) -> list[str]:
    """Предложения с антитезой. Сигнатурная фигура «не потому что… а потому что» — только при with_signature."""
    pats = ANTITHESIS.get(lang, [])
    sig = None if with_signature else FIGURES.get(lang, {}).get("не_потому_что_X_а_потому_что_Y")
    # цитату внутри фразы заменяем словом-заглушкой: «МАК не «говорит» — он…» остаётся антитезой
    flat = re.sub(r"(?m)^\s*[—–]\s.*$", " ", text)
    flat = re.sub(r"«[^»]*»|„[^“]*“", "цитата", flat)
    ss = sentences(flat)
    out = []
    for i, s in enumerate(ss):
        if sig and re.search(sig, s):
            continue
        nxt = ss[i + 1] if i + 1 < len(ss) else ""
        pair = bool(re.search(r"(?:^|\s)(?:[Ээ]то не|—\s*не|[а-яё]+\s+не\s+[а-яё]+\s+не)\s", s)
                    or re.search(r"(?<![А-Яа-яЁё])не\s(?:список|повод|вопрос|тест|приговор|дефект|сбой|метод|инструмент)\b", s)) \
            and bool(re.match(ANTITHESIS_NEXT.get(lang, "^$"), nxt))
        sig_hit = with_signature and re.search(FIGURES.get(lang, {}).get("не_потому_что_X_а_потому_что_Y", "^$"), s)
        if pair or sig_hit or any(re.search(p, s) for p in pats):
            out.append(s)
    return out


FORMAL_ADDRESS = {
    "ru": r"(?<![А-Яа-яЁё])(?:[Вв]ы|[Вв]ас|[Вв]ам|[Вв]ами|[Вв]аш[а-яё]*)(?![А-Яа-яЁё])",
    "de": r"(?<=[a-zäöüß,;:]\s)(?:Sie|Ihnen|Ihr[a-z]*)\b",
    "en": None,
}
ATTRIBUTION_MARKERS = {
    "ru": ["исследования показывают", "согласно данным", "учёные доказали", "доказано, что"],
    "de": ["studien zeigen", "nachweislich", "forscher haben herausgefunden"],
    "en": ["studies show", "research shows", "scientists have proven"],
}


def outside_quotes(text: str) -> str:
    """Текст без прямой речи: цитаты в «…» и „…“, реплики диалога (абзац, начатый тире)."""
    text = re.sub(r"(?m)^\s*[—–]\s.*$", " ", text)
    text = re.sub(r"«[^»]*»", " ", text)
    return re.sub(r"„[^“]*“", " ", text)


def verbot_phrases(path: Path) -> list[tuple[str, str]]:
    """Фразы из первого столбца таблиц verbot_liste: [(фраза, раздел)]."""
    out, section = [], ""
    for line in read_text(path).splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        if not line.startswith("|") or line.startswith("|--"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() in ("запрет", "verbot", "фраза"):
            continue
        for raw in QUOTED_RE.findall(cells[0]):
            ph = normalize_phrase(raw)
            if ph:
                out.append((ph, section))
    return out


def formula_registry(path: Path) -> list[dict]:
    """Реестр сквозных формул: [{id, phrase, kind}] (kind: allowed|single)."""
    out, kind = [], None
    for line in read_text(path).splitlines():
        if line.startswith("## "):
            low = line.lower()
            kind = "allowed" if "повтор разрешён" in low else ("single" if "запрещ" in low or "разов" in low else None)
        if kind is None or not line.startswith("|") or line.startswith("|--"):
            continue
        cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
        if len(cells) < 2 or not re.match(r"[A-ZА-Я]-\d+", cells[0]):
            continue
        for raw in QUOTED_RE.findall(cells[1]):
            ph = normalize_phrase(raw)
            if ph:
                out.append({"id": cells[0], "phrase": ph, "kind": kind})
    return out


NUM_WORDS = {"один": 1, "одного": 1, "одной": 1, "два": 2, "двух": 2, "три": 3, "трёх": 3, "трех": 3}


def plan_word_limits(plan: dict) -> dict[str, int]:
    """Лимиты слов на главу из constraints ВСЕХ beat-ов плана: «Роршах» — один раз; «Таро» — не более 3 раз.
    В пилоте лимит имени стоял только у одного beat-а и в соседнем не действовал (5 употреблений при плане 1)."""
    limits: dict[str, int] = {}
    locked: set[str] = set()  # «Решение автора …» главнее остальных ограничений плана
    rx = re.compile(r"«([^»]{2,40})»[^;«]{0,80}?(?:(один|одного|одной)\s+раз|(?:не более|не больше|максимум|≤)\s*(\d+|одного|одной|двух|трёх|трех)|(\d+)\s+раз)", re.I)
    for b in plan.get("beats", []):
        for c in b.get("constraints") or []:
            for m in rx.finditer(c):
                word = m.group(1).strip()
                if len(word.split()) > 3 or re.search(r"\b(не X|X —|потому что)\b", word):
                    continue  # фигуры и длинные формулы считаются отдельно
                raw = m.group(2) or m.group(3) or m.group(4)
                n = int(raw) if raw.isdigit() else NUM_WORDS.get(raw.lower(), 1)
                if "решение автора" in c.lower():
                    limits[word] = n
                    locked.add(word)
                elif word not in locked:
                    limits[word] = min(n, limits.get(word, n))
    return limits


def constraint_phrases(constraints: list[str]) -> list[str]:
    """«без 'давайте разберёмся'» -> 'давайте разберёмся'."""
    out = []
    for c in constraints or []:
        m = re.match(r"\s*без\s+(?:слова\s+)?['\"«](.+?)['\"»]\s*$", c, re.I)
        if m:
            ph = normalize_phrase(m.group(1))
            if ph:
                out.append(ph)
    return out


def lint(args) -> dict:
    text_raw = read_text(args.beat)
    text = strip_frontmatter(text_raw)
    low = text.lower()
    low_unquoted = outside_quotes(text).lower()
    lang = args.lang

    beat = {}
    if args.plan:
        plan = load_json(args.plan)
        beat = next((b for b in plan.get("beats", []) if b.get("beat_id") == args.beat_id), {})

    hard, candidates, facts = [], [], {}

    # A. Объём
    wc = word_count(text)
    target = beat.get("target_words")
    facts["word_count"] = wc
    if target:
        ratio = round(wc / target, 3)
        facts.update(target_words=target, ratio=ratio)
        if ratio < 0.70:
            hard.append({"flag": "volume_critical_short", "detail": f"{wc}/{target}"})
        elif ratio < 0.85:
            hard.append({"flag": "volume_short", "detail": f"{wc}/{target}"})
        elif ratio > 1.30:
            hard.append({"flag": "volume_long", "detail": f"{wc}/{target}"})

    # B. Лексика
    if args.verbot:
        for ph, sec in verbot_phrases(Path(args.verbot)):
            for pos in find_phrase(low_unquoted, ph):
                candidates.append({"flag": "forbidden_phrase", "phrase": ph, "section": sec,
                                   "context": low_unquoted[max(0, pos - 40):pos + len(ph) + 40].strip()})
    for ph in constraint_phrases(beat.get("constraints")):
        if find_phrase(low_unquoted, ph):
            hard.append({"flag": "constraint_violated", "detail": f"без «{ph}»"})
    thema = (beat.get("thema") or "").strip().lower()
    if thema and len(thema) > 12 and thema in low:
        hard.append({"flag": "headline_echo", "detail": thema})
    excl = outside_quotes(text).count("!")
    if excl:
        hard.append({"flag": "exclamation_outside_quote", "detail": f"{excl}×"})
    if FORMAL_ADDRESS.get(lang):
        hits = re.findall(FORMAL_ADDRESS[lang], outside_quotes(text))
        if hits:
            hard.append({"flag": "formal_address", "detail": ", ".join(sorted(set(hits)))})
    for marker in ATTRIBUTION_MARKERS.get(lang, []):
        if marker in low:
            candidates.append({"flag": "attribution_missing", "phrase": marker})

    # C. Ритм внутри beat-а
    sents = sentences(text)
    first = [(words(s)[:1] or [""])[0].lower() for s in sents]
    run = 1
    for i in range(1, len(first)):
        run = run + 1 if first[i] and first[i] == first[i - 1] else 1
        if run == 3:
            candidates.append({"flag": "anaphora_storm", "phrase": first[i], "sentence_no": i + 1})
    toks = [w.lower() for w in words(text)]
    tri = Counter(zip(toks, toks[1:], toks[2:]))
    for t, n in tri.items():
        if n >= 3 and not all(len(w) <= 3 for w in t):
            candidates.append({"flag": "repetition_local", "phrase": " ".join(t), "count": n})

    # C. Уровень главы: текущий beat + уже принятые
    chapter_text = text
    if args.chapter_beats:
        others = [p for p in beat_files(args.chapter_beats) if p.resolve() != Path(args.beat).resolve()]
        chapter_text = "\n".join(strip_frontmatter(read_text(p)) for p in others) + "\n" + text
    ch_low = chapter_text.lower()

    anti_beat = antithesis_sentences(text, lang, True)
    anti_chapter = len(antithesis_sentences(chapter_text, lang, True))
    budget = args.antithesis_budget
    facts["antithesis"] = {"beat": len(anti_beat), "chapter": anti_chapter, "budget_chapter": budget}
    if anti_beat:
        over = anti_chapter > budget
        if len(anti_beat) >= 3 or (over and len(anti_beat) >= 2):
            hard.append({"flag": "antithesis_overuse",
                         "detail": f"«не X, а Y» в beat-е {len(anti_beat)}×, в главе {anti_chapter} (бюджет {budget})",
                         "sentences": [x[:120] for x in anti_beat]})
        elif over or len(anti_beat) == 2:
            candidates.append({"flag": "antithesis_overuse", "count_beat": len(anti_beat), "count_chapter": anti_chapter,
                               "budget": budget, "sentences": [x[:120] for x in anti_beat]})

    # Сигнатурная фигура книги («не потому что X — а потому что Y»): счёт против pattern_budget плана
    sig_rx = FIGURES.get(lang, {}).get("не_потому_что_X_а_потому_что_Y")
    if sig_rx:
        n = len(re.findall(sig_rx, chapter_text))
        planned = next((p["planned_count"] for p in (args.planned or []) if "потому" in p.get("pattern", "")), None)
        facts["signature_figure"] = {"chapter": n, "planned": planned}
        if planned is not None and n > planned + 1 and re.search(sig_rx, text):
            candidates.append({"flag": "structural_pattern_repeat", "pattern": "не потому что X — а потому что Y",
                               "count": n, "planned": planned})

    specs = list(args.limit or [])
    given = {sp.partition("=")[0].lower() for sp in specs}
    specs += [f"{w}={n}" for w, n in getattr(args, "plan_limits", {}).items() if w.lower() not in given]
    for spec in specs:
        word, _, mx = spec.partition("=")
        n = len(find_word_forms(ch_low, word))
        facts.setdefault("word_limits", {})[word] = n
        in_beat = len(find_word_forms(low, word))
        if mx.isdigit() and n > int(mx) and in_beat:
            hard.append({"flag": "word_limit", "detail": f"«{word}» {n}× в главе, из них {in_beat} в этом beat-е (лимит {mx})"})

    if args.formulas:
        for f in formula_registry(Path(args.formulas)):
            in_beat = len(find_phrase(low, f["phrase"]))
            if not in_beat:
                continue
            in_chapter = len(find_phrase(ch_low, f["phrase"]))
            if f["kind"] == "single" or in_chapter > 2:
                candidates.append({"flag": "cross_chapter_phrase_repeat", "id": f["id"], "phrase": f["phrase"],
                                   "kind": f["kind"], "in_chapter": in_chapter})

    return {
        "beat": str(args.beat),
        "beat_id": args.beat_id,
        "facts": facts,
        "hard_flags": hard,
        "candidates_for_critic": candidates,
        "verdict_floor": "fail" if hard else "pass",
    }


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--beat", required=True)
    ap.add_argument("--plan")
    ap.add_argument("--beat-id", type=int)
    ap.add_argument("--verbot")
    ap.add_argument("--formulas")
    ap.add_argument("--chapter-beats")
    ap.add_argument("--lang", default="ru", choices=["ru", "de", "en"])
    ap.add_argument("--limit", action="append", help="слово=максимум на главу, напр. паттерн=2")
    ap.add_argument("--antithesis-budget", type=int, default=8,
                    help="антитез на главу, включая сигнатурную фигуру (так считает редактор)")
    args = ap.parse_args()
    args.planned, args.plan_limits = [], {}
    if args.plan:
        plan = load_json(args.plan)
        args.planned = plan.get("pattern_budget", []) or []
        args.plan_limits = plan_word_limits(plan)
    report = lint(args)
    print(dump_json(report))
    raise SystemExit(1 if report["hard_flags"] else 0)


if __name__ == "__main__":
    main()
