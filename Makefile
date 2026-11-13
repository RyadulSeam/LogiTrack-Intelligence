.PHONY: install test lint clean

install:
	pip install -e ".[all]"

install-core:
	pip install -e .

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --tb=short --cov=src/logitrack --cov-report=html

lint:
	python -m py_compile src/logitrack/__init__.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
