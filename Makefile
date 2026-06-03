.PHONY: install lint type test coverage build validate clean

install:
	python -m pip install -e ".[dev]"

lint:
	python -m ruff check .

type:
	python -m mypy src

test:
	python -m pytest

coverage:
	python -m pytest --cov=log_to_playbook --cov-report=term-missing --cov-fail-under=80

build:
	python -m build

validate:
	python -m log_to_playbook.cli validate-playbooks

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['build', 'dist', 'htmlcov', '.pytest_cache', '.ruff_cache']]"
