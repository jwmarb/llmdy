test:
	python -m pytest -v -s tests/

coverage:
	python -m coverage run --include=llmdy/**/*.py --omit=__init__.py -m pytest -v -s tests/ && coverage report -m

setup: .venv
	chmod +x setup.sh && ./setup.sh