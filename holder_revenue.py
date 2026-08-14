#!/usr/bin/env python3
"""Compare DefiLlama protocol revenue with holder revenue."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone

LLAMA = "https://api.llama.fi/summary/fees/{slug}?dataType={path}"
PATHS = {"protocol": "dailyRevenue", "holders": "dailyHoldersRevenue"}


def fetch(slug: str, path: str, opener=None) -> dict:
    url = LLAMA.format(slug=slug, path=path)
    req = urllib.request.Request(url, headers={"User-Agent": "holder-revenue/1.0"})
    get = opener or urllib.request.urlopen
    with get(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def last_n(chart, n: int = 30):
    rows = sorted(chart or [], key=lambda row: row[0])
    return rows[-n:]


def summarise(slug: str, opener=None, days: int = 30) -> dict:
    out = {"slug": slug, "days": days}
    for label, path in PATHS.items():
        data = fetch(slug, path, opener=opener)
        rows = last_n(data.get("totalDataChart"), days)
        total = sum(value for _, value in rows)
        nonzero = [(ts, value) for ts, value in (data.get("totalDataChart") or []) if value]
        last_nz = nonzero[-1] if nonzero else None
        out[label] = {
            "name": data.get("displayName") or data.get("name") or slug,
            "total": total,
            "n": len(rows),
            "from": _iso(rows[0][0]) if rows else None,
            "to": _iso(rows[-1][0]) if rows else None,
            "last_nonzero": None
            if last_nz is None
            else {"date": _iso(last_nz[0]), "value": last_nz[1]},
        }
    proto = out["protocol"]["total"]
    hold = out["holders"]["total"]
    out["paid"] = proto > 0 and abs(proto - hold) < 1
    out["asof"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    return out


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).date().isoformat()


def render(rows: list[dict]) -> str:
    lines = ["slug       protocol_30d    holder_30d  paid  last_holder"]
    for row in rows:
        last = row["holders"]["last_nonzero"]
        last_s = "-" if last is None else f"{last['date']} ${last['value']:,.0f}"
        lines.append(
            f"{row['slug']:<10} ${row['protocol']['total']:>12,.0f} ${row['holders']['total']:>12,.0f}  "
            f"{'yes' if row['paid'] else 'no':<4} {last_s}"
        )
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    rows = [summarise(slug) for slug in args.slugs]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
