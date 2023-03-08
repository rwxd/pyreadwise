PROJECT_NAME := "wallabag2readwise"

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Setup required things
	python3 -m pip install -U -r requirements.txt
	python3 -m pip install -U -r requirements-dev.txt
	python3 -m pip install -U -r requirements-docs.txt
	pre-commit install
	

serve-docs: ## Serve the documentation locally
	mkdocs serve

build-docs: ## Build the documentation
	mkdocs build
