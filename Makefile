test:
	python -m pytest -v -s tests/

coverage:
	python -m coverage run --source=llmdy -m pytest -v -s tests/ && coverage report -m

setup: .venv
	chmod +x setup.sh && ./setup.sh