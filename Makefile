.PHONY: lint test scan cases-check check eval eval-smoke eval-oracle

lint:
	ruff check .

test:
	pytest -q

scan:
	python scripts/scan_codes.py

cases-check:
	python -m generator check

check: lint test scan cases-check

# Scorecard: all 60 cases, dev and held-out test reported separately, dated report written to
# evals/reports/. Backend from PRIORAUTH_BACKEND (default anthropic, which needs
# ANTHROPIC_API_KEY). The v0.1 headline is `make eval BACKEND=lmstudio WORKERS=1` (D-057).
BACKEND ?= $(or $(PRIORAUTH_BACKEND),anthropic)
WORKERS ?= 4

eval:
	python -m evals.run_eval --set all --backend $(BACKEND) --workers $(WORKERS)

# CI smoke set: 10 dev cases, safety gate only (D-006). Free and deterministic on the oracle.
eval-smoke:
	python -m evals.run_eval --set smoke --gate-only --no-write --backend $(or $(SMOKE_BACKEND),oracle)

# Harness check: the ground truth replayed through the real pipeline, no key needed.
eval-oracle:
	python -m evals.run_eval --set all --backend oracle
