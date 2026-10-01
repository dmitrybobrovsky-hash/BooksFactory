"""
BooksFactory — манифест книги: единственный машиночитаемый источник статусов глав.

Правило single writer: статусы меняет ТОЛЬКО этот скрипт. Агенты вызывают его,
а не правят JSON руками. production_state.md — человекочитаемое зеркало.

Использование:
  python tools/manifest.py init  --book-dir <папка> --code KS --title "…" --lang ru [--scan]
  python tools/manifest.py show  --book-dir <папка>
  python tools/manifest.py set   --book-dir <папка> --chapter 01 --status clean --by bf-editor [--note "…"]
  python tools/manifest.py check --book-dir <папка>
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

from bf_common import dump_json, load_json, setup_stdout, write_text

STATUSES = ["outline-ready", "material-draft", "draft", "review", "clean", "humanized", "final"]
FILENAME = "book_manifest.json"


def now() -> str:
    return dt.datetime.now().isoformat(timespec="minutes")


def path_of(book_dir: str) -> Path:
    return Path(book_dir) / FILENAME


def load(book_dir: str) -> dict:
    p = path_of(book_dir)
    if not p.exists():
        raise SystemExit(f"Манифест не найден: {p}. Сначала: manifest.py init")
    return load_json(p)


def save(book_dir: str, data: dict) -> None:
    data["updated"] = now()
    errors = validate(data)
    if errors:
        raise SystemExit("Манифест не сохранён — ошибки:\n  " + "\n  ".join(errors))
    write_text(path_of(book_dir), dump_json(data) + "\n")


def validate(data: dict) -> list[str]:
    errs = []
    for key in ("book_code", "language", "chapters"):
        if key not in data:
            errs.append(f"нет поля {key}")
    for ch, info in (data.get("chapters") or {}).items():
        if not re.fullmatch(r"\d{2}", ch):
            errs.append(f"глава '{ch}': номер должен быть двузначным (01, 02…)")
        if info.get("status") not in STATUSES:
            errs.append(f"глава {ch}: неизвестный статус '{info.get('status')}'")
    return errs


def scan(book_dir: Path) -> dict:
    """Начальные статусы по существующим файлам (для книг, начатых до манифеста)."""
    rank = {s: i for i, s in enumerate(STATUSES)}
    found: dict[str, str] = {}

    def bump(ch: str, st: str):
        if ch not in found or rank[st] > rank[found[ch]]:
            found[ch] = st

    for p in book_dir.glob("*.md"):
        n = p.name
        m = re.search(r"(?:Glava|Kapitel|glava)_?(\d{1,2})", n)
        if not m:
            continue
        ch = f"{int(m.group(1)):02d}"
        low = n.lower()
        if low.startswith("material_"):
            bump(ch, "material-draft")
        elif "humanized" in low:
            bump(ch, "humanized")
        elif "clean" in low:
            bump(ch, "clean")
        elif "editor_report" in low:
            bump(ch, "review")
        elif "draft" in low:
            bump(ch, "draft")
    return {ch: {"status": st, "updated": now(), "history": [{"to": st, "at": now(), "by": "manifest.py scan"}]}
            for ch, st in sorted(found.items())}


def cmd_init(a):
    p = path_of(a.book_dir)
    if p.exists():
        raise SystemExit(f"Манифест уже есть: {p}")
    data = {"book_code": a.code, "title": a.title or "", "language": a.lang, "created": now(),
            "chapters": scan(Path(a.book_dir)) if a.scan else {}}
    save(a.book_dir, data)
    print(f"Создан {p}: глав {len(data['chapters'])}")
    cmd_show(a)


def cmd_show(a):
    data = load(a.book_dir)
    print(f"{data['book_code']} — {data.get('title', '')} [{data['language']}]")
    for ch, info in sorted(data["chapters"].items()):
        print(f"  Глава {ch}: {info['status']}  (обновлено {info.get('updated', '?')})")


def cmd_set(a):
    data = load(a.book_dir)
    ch = f"{int(a.chapter):02d}"
    if a.status not in STATUSES:
        raise SystemExit(f"Неизвестный статус '{a.status}'. Допустимы: {', '.join(STATUSES)}")
    cur = data["chapters"].get(ch, {}).get("status")
    if cur == "final" and a.by != "author":
        raise SystemExit(f"Глава {ch} в статусе final. Менять может только автор (--by author).")
    if a.status == "final" and a.by != "author":
        raise SystemExit("Статус final ставит только автор (--by author).")
    if cur:
        i, j = STATUSES.index(cur), STATUSES.index(a.status)
        if j > i + 1:
            raise SystemExit(f"Переход {cur} → {a.status} перескакивает этапы. Допустим только следующий: {STATUSES[i + 1]}")
    elif a.status not in ("outline-ready", "material-draft"):
        raise SystemExit(f"Новая глава начинается с outline-ready или material-draft, не с {a.status}")
    entry = data["chapters"].setdefault(ch, {"history": []})
    entry["history"].append({"from": cur, "to": a.status, "at": now(), "by": a.by, **({"note": a.note} if a.note else {})})
    entry["status"], entry["updated"] = a.status, now()
    save(a.book_dir, data)
    print(f"Глава {ch}: {cur or '—'} → {a.status} ({a.by})")


def cmd_check(a):
    errs = validate(load(a.book_dir))
    print("Манифест в порядке" if not errs else "Ошибки:\n  " + "\n  ".join(errs))
    raise SystemExit(1 if errs else 0)


def main():
    setup_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "show", "set", "check"):
        s = sub.add_parser(name)
        s.add_argument("--book-dir", required=True)
        if name == "init":
            s.add_argument("--code", required=True)
            s.add_argument("--title")
            s.add_argument("--lang", default="ru")
            s.add_argument("--scan", action="store_true")
        if name == "set":
            s.add_argument("--chapter", required=True)
            s.add_argument("--status", required=True)
            s.add_argument("--by", required=True)
            s.add_argument("--note")
    a = ap.parse_args()
    {"init": cmd_init, "show": cmd_show, "set": cmd_set, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
