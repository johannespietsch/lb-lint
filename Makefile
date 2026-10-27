.PHONY: setup test

setup:
	uv sync

test:
	uv run pytest -q

demo:
	-uv run lb-lint pruefe samples/laptops_schulen.md
