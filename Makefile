SPACY_MODEL := de_core_news_lg-3.8.0

.PHONY: setup

setup:
	uv sync
	uv run python -m spacy download $(SPACY_MODEL) --direct
