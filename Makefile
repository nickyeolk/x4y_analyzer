.PHONY: help install install-dev run test test-unit test-integration test-evaluation evaluate lint format clean

help:
	@echo "AgentLand - Multi-Agent Customer Support System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install           Install production dependencies"
	@echo "  make install-dev       Install development dependencies"
	@echo "  make run               Run the FastAPI server"
	@echo "  make test              Run all tests"
	@echo "  make test-unit         Run unit tests only"
	@echo "  make test-integration  Run integration tests only"
	@echo "  make test-evaluation   Run evaluation tests only"
	@echo "  make evaluate          Run full evaluation suite with reports"
	@echo "  make lint              Run linter (ruff)"
	@echo "  make format            Format code (black + ruff)"
	@echo "  make clean             Clean temporary files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-evaluation:
	pytest tests/evaluation/ -v -m evaluation

evaluate:
	@echo "Running evaluation suite with DeepEval..."
	deepeval test run tests/evaluation/
	@echo "Evaluation complete! Check reports in ./deepeval_results/"

lint:
	ruff check src/ config/ tests/

format:
	black src/ config/ tests/
	ruff check --fix src/ config/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .ruff_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
