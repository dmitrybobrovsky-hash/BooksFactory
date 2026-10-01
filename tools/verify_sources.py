"""
BooksFactory — сверка списка литературы по каталогам (правило №1).

Для каждой книги из quellen_pool ищет издание в открытых каталогах
(Open Library, Google Books) и сравнивает автора и год. В книгу идут только
подтверждённые позиции; остальное — в отчёт с причиной.

Если рядом лежит протокол SOURCES_VERIFIED_<CODE>.md с ISBN, сверка идёт
по ISBN (надёжнее), иначе — по названию и автору.

Использование:
  python tools/verify_sources.py --pool <quellen_pool_CODE.md> [--verified <SOURCES_VERIFIED_CODE.md>] \
      [--out <SOURCES_CHECK_CODE.md>] [--offline]

Код выхода: 0 — все позиции подтверждены; 1 — есть неподтверждённые; 2 — каталоги недоступны.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from bf_common import read_text, setup_stdout, write_text

ENTRY_RE = re.compile(r"^\*\s+\*\*(?P<authors>.+?),\s*(?P<year>\d{4}):\*\*\s+\*(?P<title>[^*]+?)\.?\*", re.M)
ISBN_ROW_RE = re.compile(r"^\|\s*\d+\s*\|\s*(?P<entry>[^|]+?)\s*\|[^|]*\|\s*(?P<isbn>97[89]\d{10})\s*\|", re.M)
UA = {"User-Agent": "BooksFactory-verify/1.0 (SpellText Verlag)"}


def fetch_json(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def surname(authors: str) -> str:
    first = re.split(r",|\s+и\s+|\s+and\s+|\s+&\s+", authors.strip())[0]
    return first.strip().split()[0].strip(".").lower()


def all_surnames(authors: str) -> list[str]:
    """'Freudenberger, H., Richelson, G.' -> ['freudenberger', 'richelson']"""
    parts = [p.strip() for p in re.split(r",|\s+и\s+|\s+and\s+|&", authors) if p.strip()]
    return [p.split()[0].strip(".").lower() for p in parts if not re.fullmatch(r"[A-ZА-ЯЁ]\.?(\s*[A-ZА-ЯЁ]\.)*", p)]


def by_isbn(isbn: str) -> list[dict]:
    hits = []
    try:
        d = fetch_json(f"https://openlibrary.org/isbn/{isbn}.json")
        hits.append({"source": "Open Library", "title": d.get("title", ""), "year": d.get("publish_date", ""),
                     "authors": "", "publisher": ", ".join(d.get("publishers", []))})
    except Exception:
        pass
    try:
        d = fetch_json(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
        for it in d.get("items", [])[:1]:
            v = it.get("volumeInfo", {})
            hits.append({"source": "Google Books", "title": v.get("title", ""), "year": v.get("publishedDate", ""),
                         "authors": ", ".join(v.get("authors", [])), "publisher": v.get("publisher", "")})
    except Exception:
        pass
    return hits


def by_title(title: str, author: str) -> list[dict]:
    hits = []
    q = urllib.parse.urlencode({"title": title, "author": author, "limit": 5})
    try:
        d = fetch_json(f"https://openlibrary.org/search.json?{q}")
        for doc in d.get("docs", [])[:5]:
            hits.append({"source": "Open Library", "title": doc.get("title", ""),
                         "year": " ".join(str(y) for y in sorted(set(doc.get("publish_year", [])))[:30]),
                         "authors": ", ".join(doc.get("author_name", [])), "publisher": ""})
    except Exception:
        pass
    gq = urllib.parse.quote(f'intitle:"{title}" inauthor:{author}')
    try:
        d = fetch_json(f"https://www.googleapis.com/books/v1/volumes?q={gq}&maxResults=5")
        for it in d.get("items", [])[:5]:
            v = it.get("volumeInfo", {})
            hits.append({"source": "Google Books", "title": v.get("title", ""), "year": v.get("publishedDate", ""),
                         "authors": ", ".join(v.get("authors", [])), "publisher": v.get("publisher", "")})
    except Exception:
        pass
    return hits


def judge(entry: dict, hits: list[dict], isbn_hits: list[dict] | None = None) -> tuple[str, str]:
    sname = surname(entry["authors"])
    coauthors = all_surnames(entry["authors"])

    def authors_match(h: dict) -> bool:
        return not h["authors"] or all(c in h["authors"].lower() for c in coauthors)

    isbn_ok = [h for h in (isbn_hits or []) if authors_match(h)]
    if isbn_hits and not isbn_ok and any(h["authors"] for h in isbn_hits):
        return "mismatch", f"авторы по ISBN: {next(h['authors'] for h in isbn_hits if h['authors'])}"
    if any(entry["year"] in str(h["year"]) for h in isbn_ok):
        return "confirmed", ""
    if not hits:
        return "not_found", "каталоги не нашли издание — нужна ручная сверка"
    sname = surname(entry["authors"])
    author_ok = [h for h in hits if not h["authors"] or sname in h["authors"].lower()]
    if not author_ok:
        return "mismatch", f"автор в каталоге: {hits[0]['authors']}"
    if any(entry["year"] in str(h["year"]) for h in author_ok):
        return "confirmed", ""
    isbn_years = [int(y) for h in isbn_ok for y in re.findall(r"\d{4}", str(h["year"]))]
    if isbn_ok and isbn_years and int(entry["year"]) <= min(isbn_years):
        # указан год первого издания, ISBN — более позднее переиздание: данные корректны
        return "confirmed_reprint", f"ISBN — переиздание ({str(isbn_ok[0]['year'])[:20]}), в списке — год первого издания"
    years = "; ".join(str(h["year"])[:40] for h in author_ok[:3])
    return "mismatch", f"год {entry['year']} не найден; в каталоге: {years}"


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--verified")
    ap.add_argument("--out")
    ap.add_argument("--offline", action="store_true", help="только разбор списка, без запросов в каталоги")
    a = ap.parse_args()

    pool_text = read_text(a.pool)
    entries = [m.groupdict() for m in ENTRY_RE.finditer(pool_text)]
    isbns: dict[str, str] = {}
    manual: set[str] = set()  # позиции, подтверждённые вручную в протоколе SOURCES_VERIFIED
    for line in pool_text.splitlines():  # ISBN из заготовки Zotero: <!-- ISBN … -->
        m, e = re.search(r"<!--\s*ISBN\s+(97[89]\d{10})", line), ENTRY_RE.match(line)
        if m and e:
            isbns[surname(e.group("authors"))] = m.group(1)
    if a.verified and Path(a.verified).exists():
        for m in ISBN_ROW_RE.finditer(read_text(a.verified)):
            isbns[surname(m.group("entry"))] = m.group("isbn")
            manual.add(surname(m.group("entry")))

    rows, online = [], False
    for e in entries:
        isbn = isbns.get(surname(e["authors"]))
        if a.offline:
            status, note, hits = "offline", "", []
        else:
            isbn_hits = by_isbn(isbn) if isbn else []
            status, note = judge(e, isbn_hits) if isbn_hits else ("not_found", "")
            hits = isbn_hits
            if status != "confirmed":
                # ISBN часто принадлежит переизданию — год первого издания ищем по названию
                hits = isbn_hits + by_title(e["title"], surname(e["authors"]))
                status, note = judge(e, hits, isbn_hits)
            online = online or bool(hits)
            if status == "not_found" and isbn and surname(e["authors"]) in manual:
                status, note = "confirmed_manual", "нет в открытых каталогах; подтверждено по каталогам магазинов (протокол сверки)"
        rows.append((e, isbn or "", status, note))

    if not a.offline and not online:
        print("Каталоги недоступны (нет сети?). Сверка не выполнена.")
        raise SystemExit(2)

    mark = {"confirmed": "✅", "confirmed_reprint": "✅", "confirmed_manual": "✅", "mismatch": "⚠",
            "not_found": "❓", "offline": "·"}
    lines = ["# Сверка списка литературы", "", f"Источник: `{Path(a.pool).name}` — позиций: {len(rows)}", "",
             "| # | Книга | ISBN | Статус | Примечание |", "|---|---|---|---|---|"]
    for i, (e, isbn, st, note) in enumerate(rows, 1):
        lines.append(f"| {i} | {e['authors']}, {e['year']}: {e['title']} | {isbn} | {mark[st]} {st} | {note} |")
    report = "\n".join(lines) + "\n"
    if a.out:
        write_text(a.out, report)
    print(report)
    bad = [r for r in rows if r[2] in ("mismatch", "not_found")]
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
