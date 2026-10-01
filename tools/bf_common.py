"""
BooksFactory — общие функции для детерминированных инструментов (сессия 1, 2026-10-01).

Только стандартная библиотека Python. Всё, что можно посчитать, считается здесь,
а не моделью: слова, совпадения, повторы, структура файлов.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿĀ-žА-Яа-яЁё]+(?:[-'’][0-9A-Za-zÀ-ÿĀ-žА-Яа-яЁё]+)*")
QUOTED_RE = re.compile(r"«([^»]+)»")
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)


def setup_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def write_text(path: str | Path, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8", newline="\n")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def word_count(text: str) -> int:
    return len(words(strip_frontmatter(text)))


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", strip_frontmatter(text)).strip()
    parts = re.split(r"(?<=[.!?…])\s+(?=[«\"„(]?[A-ZÀ-ÞА-ЯЁ0-9])", flat)
    return [p.strip() for p in parts if p.strip()]


def load_json(path: str | Path):
    return json.loads(read_text(path))


def dump_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def beat_files(beats_dir: str | Path) -> list[Path]:
    """beat_1.md … beat_N.md в числовом порядке."""
    files = list(Path(beats_dir).glob("beat_*.md"))

    def key(p: Path) -> int:
        m = re.search(r"beat_(\d+)", p.stem)
        return int(m.group(1)) if m else 10**6

    return sorted(files, key=key)


def normalize_phrase(raw: str) -> str | None:
    """«МАК помогает...» -> 'мак помогает'. Убирает многоточия, скобки, кавычки."""
    s = raw.replace("…", " ").replace("...", " ")
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[\"“”„]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" .,;:—-").lower()
    return s if len(s) >= 4 else None


def find_phrase(text_lower: str, phrase: str) -> list[int]:
    """Позиции вхождений фразы (по границам слов)."""
    pat = r"(?<![\wА-Яа-яЁё])" + re.escape(phrase) + r"(?![\wА-Яа-яЁё])"
    return [m.start() for m in re.finditer(pat, text_lower)]
