#!/usr/bin/env python3
"""
Find job-description keywords that recur across saved applications and check
whether a base resume covers them, so the base can be improved once instead of
patched per application.

Reads <workspace>/applications/*/keywords.txt (the must:/nice: files written for
each application). A term is named by the first spelling on its line; the
alternates after "|" count as the same term. Terms from different applications
are merged by that first spelling, ignoring case.

Coverage uses the same matching as verify.py: "bullet" means the term (or an
alternate) appears in the Experience or Projects section, "skills" means it
appears only in Skills, "-" means it is not in the base at all.

Usage:
    keyword_trends.py --base profile/bases/<name>/resume.md
    keyword_trends.py --workspace ~/career --base profile/bases/<name>/resume.md --since 2026-10-01 --min 2 --top 40
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import section_map, term_re  # noqa: E402  same matching as the per-application check


def parse_keywords(path: Path) -> list[tuple[str, list[str]]]:
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        prio = "must"
        m = re.match(r"^(must|nice)\s*:\s*(.+)$", raw, re.I)
        if m:
            prio, raw = m.group(1).lower(), m.group(2)
        terms = [t.strip() for t in raw.split("|") if t.strip()]
        if terms:
            out.append((prio, terms))
    return out


def coverage(terms: list[str], md: str) -> str:
    secs = section_map(md)
    hits = {name for name, body in secs.items() if any(term_re(t).search(body) for t in terms)}
    if any("experience" in h or "project" in h for h in hits):
        return "bullet"
    if any("skill" in h for h in hits):
        return "skills"
    if hits:
        return "other"
    return "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", type=Path, default=Path("."))
    ap.add_argument("--base", type=Path, help="base resume.md to check coverage against")
    ap.add_argument("--since", help="only applications whose folder date (YYYY-MM-DD) is on or after this")
    ap.add_argument("--min", type=int, default=2, help="only terms seen in at least this many applications")
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()

    files = sorted((a.workspace / "applications").glob("*/keywords.txt"))
    if a.since:
        files = [f for f in files if f.parent.name[:10] >= a.since]
    if not files:
        sys.exit(f"no applications/*/keywords.txt under {a.workspace.resolve()}")

    agg: dict[str, dict] = {}
    for f in files:
        seen_here = set()
        for prio, terms in parse_keywords(f):
            key = terms[0].lower()
            if key in seen_here:
                continue
            seen_here.add(key)
            row = agg.setdefault(key, {"name": terms[0], "alts": set(), "must": 0, "nice": 0})
            row["alts"].update(terms)
            row[prio] += 1

    md = ""
    if a.base:
        md = re.sub(r"<!--.*?-->", "", a.base.read_text(encoding="utf-8"), flags=re.S)

    rows = [r for r in agg.values() if r["must"] + r["nice"] >= a.min]
    rows.sort(key=lambda r: (-(r["must"] + r["nice"]), -r["must"], r["name"].lower()))
    rows = rows[: a.top]

    print(f"{len(files)} applications, {len(agg)} distinct terms, showing {len(rows)} seen in >= {a.min}\n")
    head = f"{'apps':>4} {'must':>4} {'nice':>4}  {'base':<6}  term (alternates)"
    print(head)
    print("-" * len(head))
    missing = []
    for r in rows:
        cov = coverage(sorted(r["alts"]), md) if md else "n/a"
        alts = sorted(t for t in r["alts"] if t.lower() != r["name"].lower())
        print(f"{r['must'] + r['nice']:>4} {r['must']:>4} {r['nice']:>4}  {cov:<6}  {r['name']}"
              + (f" ({', '.join(alts)})" if alts else ""))
        if md and cov in ("-", "skills"):
            missing.append((r["name"], cov))

    if md:
        print(f"\nRecurring terms the base doesn't prove in a bullet ({len(missing)}):")
        for name, cov in missing:
            print(f"  - {name}" + (" (Skills only)" if cov == "skills" else ""))
        print("\nAdd only the ones the user can back up with a real fact; never add a term to fill the list.")


if __name__ == "__main__":
    main()
