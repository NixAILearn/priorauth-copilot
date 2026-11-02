.PHONY: lint test scan cases-check check eval

lint:
	ruff check .

test:
	pytest -q

scan:
	python scripts/scan_codes.py

cases-check:
	python -m generator check

check: lint test scan cases-check

eval:
	@echo "Eval runner not built yet (week 4): evals/run_eval.py"
