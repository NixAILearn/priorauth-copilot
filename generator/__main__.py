"""python -m generator {brief|finalize|check|status} [CASE-… …]"""

from __future__ import annotations

import argparse
import sys

from generator import core
from priorauth.case_spec import load_case


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m generator")
    ap.add_argument("command", choices=["brief", "finalize", "check", "status"])
    ap.add_argument("cases", nargs="*", help="case IDs; default: every case the command applies to")
    args = ap.parse_args(argv)
    all_ids = [p.stem for p in sorted(core.SPECS.glob("CASE-*.json"))]

    if args.command == "status":
        for cid, st in core.status().items():
            print(f"{cid}  {st}")
        return 0
    if args.command == "brief":
        for cid in args.cases or all_ids:
            print(core.write_prompts(load_case(core.SPECS / f"{cid}.json")))
        return 0
    if args.command == "finalize":
        bad = 0
        for cid in args.cases:
            errors = core.finalize(cid)
            print(f"{cid}: {'ok' if not errors else f'{len(errors)} problem(s)'}")
            for e in errors:
                print(f"  - {e}")
            bad += bool(errors)
        return 1 if bad else 0
    # check: every case that has been finalized
    ids = args.cases or [c for c in all_ids if (core.case_dir(c) / "manifest.json").exists()]
    bad = 0
    for cid in ids:
        errors = core.verify(cid)
        if errors:
            bad += 1
            print(f"{cid}: FAIL")
            for e in errors:
                print(f"  - {e}")
    print(f"generator check: {len(ids) - bad} of {len(ids)} cases pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
