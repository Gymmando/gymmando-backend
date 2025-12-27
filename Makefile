.PHONY: install test format lint run clean

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=gymmando

format:
	black gymmando/ tests/

lint:
	flake8 gymmando/ tests/
	mypy gymmando/

run:
	uvicorn gymmando.api.main:app --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov/
