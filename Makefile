.PHONY: dev dev-frontend build test seed install clean

VENV = backend/.venv
PYTHON = $(VENV)/bin/python
PYTEST = $(VENV)/bin/pytest
UVICORN = $(VENV)/bin/uvicorn

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r backend/requirements.txt
	npm install --prefix frontend

test:
	$(PYTEST) -c backend/pytest.ini -v --durations=10
	npm run build --prefix frontend

dev:
	$(UVICORN) app.main:app --reload --port 8000 --app-dir backend

dev-frontend:
	npm run dev --prefix frontend -- --host 127.0.0.1 --port 5173

seed:
	PYTHONPATH=backend $(PYTHON) -m app.services.seed
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_graph
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_news
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_fundamentals
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_supply_chain

seed-supply-chain:
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_supply_chain

seed-fundamentals:
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_fundamentals

seed-news:
	PYTHONPATH=backend $(PYTHON) -m app.services.seed_news

ingest-news:
	PYTHONPATH=backend $(PYTHON) -m app.services.ingest_news

build:
	npm run build --prefix frontend

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
