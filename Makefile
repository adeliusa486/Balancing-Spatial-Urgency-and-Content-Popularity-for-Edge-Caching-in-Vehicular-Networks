.PHONY: install dev-install lint format type-check test test-unit test-integration \
        smoke benchmark api docker-build docker-up clean help

PYTHON   := python
PIP      := pip
PYTEST   := pytest
SRC_DIR  := src/trajectorycache
RESULTS  := experiments/results

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Installation ──────────────────────────────────────────────────────────────

install:  ## Install package (runtime deps only)
	$(PIP) install -e .

dev-install:  ## Install package + dev + viz extras
	$(PIP) install -e ".[all]"

# ── Code quality ──────────────────────────────────────────────────────────────

lint:  ## Run ruff linter
	ruff check $(SRC_DIR) tests

format:  ## Auto-format with black
	black $(SRC_DIR) tests scripts

type-check:  ## Run mypy type checker
	mypy $(SRC_DIR) --ignore-missing-imports

# ── Testing ───────────────────────────────────────────────────────────────────

test:  ## Run full test suite with coverage
	$(PYTEST) tests/ --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

test-unit:  ## Run unit tests only
	$(PYTEST) tests/unit/ -v

test-integration:  ## Run integration tests only
	$(PYTEST) tests/integration/ -v

smoke:  ## Run quick smoke test
	$(PYTHON) scripts/smoke_test.py

# ── Experiments & Reproducibility ─────────────────────────────────────────────

benchmark:  ## Run full policy benchmark
	$(PYTHON) scripts/run_benchmark.py --output $(RESULTS)

sweep:  ## Run hyperparameter sweep
	$(PYTHON) scripts/sweep.py --config configs/sweep.yaml --output $(RESULTS)/sweep

pipeline: results-alpha08 results-alpha05 stats figures  ## Reproduce all paper results
	@echo "Full pipeline complete."

results-alpha08:
	$(PYTHON) scripts/run_multiseed.py --zipf-alpha 0.8 --output $(RESULTS)/alpha08

results-alpha05:
	$(PYTHON) scripts/run_multiseed.py --zipf-alpha 0.5 --output $(RESULTS)/alpha05

stats:
	$(PYTHON) scripts/compute_stats.py --input $(RESULTS)/alpha08/multiseed_alpha0.8.json

figures:
	$(PYTHON) scripts/generate_figures.py \
		--input $(RESULTS)/alpha08/multiseed_alpha0.8.json \
		--output experiments/figures/

paper: figures  ## Compile the LaTeX paper
	cd paper && pdflatex tc_paper_elsevier.tex \
		&& bibtex tc_paper_elsevier \
		&& pdflatex tc_paper_elsevier.tex \
		&& pdflatex tc_paper_elsevier.tex

# ── API ───────────────────────────────────────────────────────────────────────

api:  ## Start API server (dev mode with reload)
	uvicorn trajectorycache.api.app:app --reload --host 0.0.0.0 --port 8000

# ── Docker ────────────────────────────────────────────────────────────────────

docker-build:  ## Build Docker image
	docker build -t trajectorycache:latest .

docker-up:  ## Start services with docker compose
	docker compose up -d

docker-down:  ## Stop docker compose services
	docker compose down

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean:  ## Remove caches, build artefacts, coverage reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "*.egg-info"  -exec rm -rf {} + 2>/dev/null; true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build
