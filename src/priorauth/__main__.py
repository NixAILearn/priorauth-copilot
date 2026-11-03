"""Command line: review one case with the configured backend.

    PRIORAUTH_BACKEND=lmstudio python -m priorauth review data/cases/CASE-021-01
    python -m priorauth review data/cases/CASE-021-01 --audit runs.db --json

The output is a recommendation for a human reviewer. It never denies (kickoff section 8).
"""

from __future__ import annotations

import argparse
import sys

from priorauth.audit import AuditLog
from priorauth.backends import make_client
from priorauth.config import ConfigError, load_config
from priorauth.intake import IntakeError
from priorauth.pipeline import review_case


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="priorauth")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review", help="review one case directory")
    r.add_argument("case_dir")
    r.add_argument("--audit", help="SQLite file to append the run to")
    r.add_argument("--json", action="store_true", help="print the full recommendation JSON")
    args = p.parse_args(argv)

    try:
        cfg = load_config()
        client = make_client(cfg)
        audit = AuditLog(args.audit) if args.audit else None
        rec = review_case(args.case_dir, client, audit, official=cfg.official)
    except (ConfigError, IntakeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(rec.model_dump_json(indent=2))
        return 0
    tag = "" if cfg.official else f"  [dev run on {cfg.backend}: not a scorecard result]"
    print(f"{rec.case_id}  {rec.policy_id} v{rec.policy_version}  ->  {rec.route.value}{tag}")
    for reason in rec.reasons:
        print(f"  - {reason}")
    for m in rec.missing:
        unit = f" ({m.unit_id})" if m.unit_id else ""
        print(f"  request: {m.name}{unit}, policy section {m.section}: {m.must_show}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
