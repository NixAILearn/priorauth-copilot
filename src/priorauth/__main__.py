"""Command line: review one case with the configured backend.

    PRIORAUTH_BACKEND=lmstudio python -m priorauth review data/cases/CASE-021-01
    python -m priorauth review data/cases/CASE-021-01 --audit runs.db --json
    python -m priorauth snapshot export evals/runs/20261104T144821-all-lmstudio.sqlite
    python -m priorauth snapshot oracle

The output is a recommendation for a human reviewer. It never denies (kickoff section 8).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    s = sub.add_parser("snapshot", help="write a snapshot for the reviewer app (D-068)")
    s_sub = s.add_subparsers(dest="snap", required=True)
    e = s_sub.add_parser("export", help="from an eval run's audit log (evals/runs/*.sqlite)")
    e.add_argument("db")
    e.add_argument("--name", help="snapshot name (default: the log's file name)")
    s_sub.add_parser("oracle", help="the ground-truth replay of all 60 cases")
    args = p.parse_args(argv)

    if args.cmd == "snapshot":
        from priorauth import snapshot  # noqa: PLC0415

        try:
            if args.snap == "export":
                out = snapshot.export(Path(args.db), name=args.name)
            else:
                out = snapshot.build_oracle()
        except (OSError, ValueError) as err:
            print(f"error: {err}", file=sys.stderr)
            return 2
        print(f"wrote {out}")
        return 0

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
