all: format lint test coverage

format:
	black src/ tests/

lint:
	ruff .

test:
	pytest

coverage:
	pytest --cov=cerebrus