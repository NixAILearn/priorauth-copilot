.PHONY: lint test scan check eval

lint:
	ruff check .

test:
	pytest -q

scan:
	python scripts/scan_codes.py

check: lint test scan

eval:
	@echo "Eval runner not built yet (week 4): evals/run_eval.py"
