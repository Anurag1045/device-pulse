.PHONY: install test test-unit test-integration build run clean

install:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

build:
	docker build -t device-pulse:latest .

run:
	FLASK_APP=app.main flask run --host=0.0.0.0 --port=8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} +
