"""Quote checks: code confirms every quote the model returns (kickoff section 6, D-046).

Normalization is whitespace, quote marks and Markdown emphasis markers (`*`) only: the
citation-precision rule in metrics.md, plus the asterisks the committed label quotes already
drop. Nothing else is forgiven: a paraphrase fails.
"""

from __future__ import annotations

import re
from datetime import date

MIN_QUOTE_CHARS = 8  # "Ht 70 in." is a real, complete quote

_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(_QUOTES).replace("*", "")).strip()


def quote_in(docs: dict[str, str], doc_id: str, quote: str) -> bool:
    """True when the quote is long enough and appears verbatim in that document."""
    q = norm(quote)
    if len(q) < MIN_QUOTE_CHARS or doc_id not in docs:
        return False
    doc = norm(docs[doc_id])
    # A quote lifted from mid-sentence often gains a capital first letter; only that first
    # character is allowed to differ in case (D-061). Everything else stays exact.
    return q in doc or (q[0].swapcase() + q[1:]) in doc


_NUM = re.compile(r"(?<![\d.])\d+(?:\.\d+)?")


def number_in(quote: str, value: float) -> bool:
    """The value appears as a number in the quote (31.2 matches '31.2' and '31.20')."""
    return any(abs(float(m) - value) < 1e-9 for m in _NUM.findall(quote.replace(",", "")))


_MONTHS = {
    m: i + 1
    for i, names in enumerate(
        [
            ("jan", "january"),
            ("feb", "february"),
            ("mar", "march"),
            ("apr", "april"),
            ("may",),
            ("jun", "june"),
            ("jul", "july"),
            ("aug", "august"),
            ("sep", "sept", "september"),
            ("oct", "october"),
            ("nov", "november"),
            ("dec", "december"),
        ]
    )
    for m in names
}


def dates_in(text: str) -> set[date]:
    """Full and month-only dates written in common clinical formats."""
    found: set[date] = set()

    def add(y: int, m: int, d: int) -> None:
        try:
            found.add(date(y, m, d))
        except ValueError:
            pass

    for y, m, d in re.findall(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text):
        add(int(y), int(m), int(d))
    for m, d, y in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", text):
        add(int(y), int(m), int(d))
    for mon, d, y in re.findall(r"\b([A-Za-z]{3,9})\.? (\d{1,2}),? (\d{4})\b", text):
        if mon.lower() in _MONTHS:
            add(int(y), _MONTHS[mon.lower()], int(d))
    for d, mon, y in re.findall(r"\b(\d{1,2}) ([A-Za-z]{3,9})\.? (\d{4})\b", text):
        if mon.lower() in _MONTHS:
            add(int(y), _MONTHS[mon.lower()], int(d))
    return found


def months_in(text: str) -> set[tuple[int, int]]:
    """(year, month) pairs, including month-only forms such as '05/2023' or 'May 2023'."""
    out = {(d.year, d.month) for d in dates_in(text)}
    for m, y in re.findall(r"(?<![/\d])(\d{1,2})/(\d{4})\b", text):
        if 1 <= int(m) <= 12:
            out.add((int(y), int(m)))
    for mon, y in re.findall(r"\b([A-Za-z]{3,9})\.? (\d{4})\b", text):
        if mon.lower() in _MONTHS:
            out.add((int(y), _MONTHS[mon.lower()]))
    return out


def date_in(quote: str, value: date) -> bool:
    """The date appears in the quote; a month-only date counts (policy: missing day rule)."""
    return value in dates_in(quote) or (value.year, value.month) in months_in(quote)
