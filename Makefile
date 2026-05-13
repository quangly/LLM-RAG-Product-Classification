# Makefile for local development and running the Nielsen RAG classifier

.PHONY: help venv install build-index classify serve download list-models clean

help:
	@echo "Available targets:"
	@echo "  venv         - create the Python virtual environment"
	@echo "  install      - install Python dependencies into .venv"
	@echo "  build-index  - embed Nielsen categories and save to SQLite"
	@echo "  classify     - run the RAG classifier"
	@echo "  serve        - start the local Ollama server"
	@echo "  download     - download the Ollama llama2 model"
	@echo "  list-models  - list installed Ollama models"
	@echo "  clean        - remove generated SQLite index"

venv:
	python3 -m venv .venv
	@echo "Created .venv virtual environment."

install: venv
	.venv/bin/pip install -r requirements.txt

build-index:
	.venv/bin/python embed_and_index.py

classify:
	.venv/bin/python classify.py

serve:
	ollama serve

download:
	ollama run llama2

list-models:
	ollama list

clean:
	rm -f nielsen_embeddings.db
	@echo "Removed nielsen_embeddings.db"
