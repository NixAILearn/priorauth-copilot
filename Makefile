.PHONY: lint test scan cases-check check eval eval-smoke eval-oracle app snapshot-oracle demo-gif

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

# Reviewer app (week 5, docs/app-design.md). Opens on the newest scorecard snapshot (D-068).
app:
	streamlit run app/streamlit_app.py

# Rebuild the ground-truth replay snapshot the app falls back to.
snapshot-oracle:
	python -m priorauth snapshot oracle

# Re-record docs/assets/demo.gif from the real app (D-074). Needs: pip install -e ".[demo]"
# and `playwright install chromium`.
demo-gif:
	python scripts/record_demo.py
