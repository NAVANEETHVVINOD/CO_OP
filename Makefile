# CO_OS Makefile

.PHONY: dev test lint format clean setup

dev:
	@echo "Starting backend and frontend development servers..."
	@echo "Backend starting on another terminal or background process."
	cd services/api && .venv/Scripts/Activate.ps1 && uvicorn app.main:app --reload
	# (Note: Frontend can be started separately with 'cd apps/web && pnpm run dev')

test:
	@echo "Running backend tests..."
	cd services/api && .venv/Scripts/Activate.ps1 && \
	$$env:PYTHONPATH="f:/kannan/projects/CO_OS/services/api" && \
	pytest tests/ --tb=short

lint:
	@echo "Linting backend..."
	cd services/api && .venv/Scripts/Activate.ps1 && ruff check app tests
	@echo "Linting frontend..."
	cd apps/web && pnpm lint

format:
	@echo "Formatting backend..."
	cd services/api && .venv/Scripts/Activate.ps1 && ruff format app tests
	@echo "Formatting frontend..."
	cd apps/web && pnpm format

clean:
	@echo "Cleaning up caches and build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf apps/web/.next
