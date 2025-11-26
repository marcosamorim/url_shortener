# Ensure commands run inside the project's virtualenv
ifeq ($(VIRTUAL_ENV),)
  $(error You must activate your virtualenv first: `source .venv/bin/activate`)
endif

PYTHON      ?= python
PIP         ?= pip

APP_DIR     := app
TESTS_DIR   := tests
TEST_DB     := test_shortener.db

.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  make dev        - install dev dependencies (incl. pytest, pre-commit, black, isort)"
	@echo "  make install    - install runtime dependencies only"
	@echo "  make run        - run FastAPI app with uvicorn (reload)"
	@echo "  make test       - run tests (pytest, uses pytest.ini)"
	@echo "  make format     - run isort + black on app and tests"
	@echo "  make pre-commit - run all pre-commit hooks on all files"
	@echo "  make clean      - remove test DB, coverage file, and __pycache__"

dev:
	$(PIP) install -r requirements-dev.txt

install:
	$(PIP) install -r requirements.txt

run:
	uvicorn $(APP_DIR).main:app --reload

test:
	pytest

format:
	isort $(APP_DIR) $(TESTS_DIR)
	black $(APP_DIR) $(TESTS_DIR)

pre-commit:
	pre-commit run --all-files

clean:
	@echo "Cleaning test DB, coverage file, and __pycache__..."
	rm -f $(TEST_DB) .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
