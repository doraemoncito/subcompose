.PHONY: all dist clean compile run docs format lint package sast sbom sbom-audit test typecheck help

.DEFAULT_GOAL := help

ARGS ?= --help

all: lint typecheck compile test docs sast sbom-audit package ## 🟢 run all checks and build
	@echo "🟢 All checks passed!"

compile: ## 🐍 compile the example application to check for syntax errors
	@echo "🐍 Compiling example application..."
	@PYTHONPATH=src poetry run python -m py_compile src/subcompose/__main__.py

clean: ## 🧹 remove all generated build artefacts
	@echo "🧹 Cleaning generated files..."
	@rm -rf build dist .mypy_cache .pytest_cache __pycache__
	@find . -type d -name __pycache__ -exec rm -rf {} +

dist: lint typecheck compile test docs package ## 📦 build the distributable package after running all checks
	@echo "📦 Distribution build complete!"

docs: ## 📚 build the Sphinx documentation
	@echo "📚 Building documentation..."
	@poetry install --with docs --no-interaction
	@poetry run sphinx-build -W --keep-going -b html docs build/docs/html

show-docs: ## 🌐 open the built documentation in your web browser
	@echo "🌐 Opening documentation in your web browser..."
	@open build/docs/html/index.html

format: ## 🎨 format code with ruff
	@echo "🎨 Formatting code with ruff..."
	@poetry run ruff format .

lint: ## 🔍 check code with ruff
	@echo "🔍 Linting code with ruff..."
	@poetry run ruff check --fix .

package: ## 🏗️ build the distributable wheel and sdist with Poetry
	@echo "🏗️ Building distributable package..."
	@poetry build

run: ## ▶️ run example application to demonstrate usage of the client library
	@echo "▶️ Running example application..."
	@PYTHONPATH=src poetry run python src/subcompose/__main__.py $(ARGS)

sast: ## 🔒 scan for security issues with bandit
	@echo "🔒 Scanning for security issues..."
	@poetry install --with sast --no-interaction
	@poetry run bandit --ini .bandit.ini --exit-zero src/subcompose

sbom: ## 🧾 generate CycloneDX SBOM (JSON)
	@echo "📦 Generating SBOM..."
	@poetry install --with sbom --no-interaction
	@mkdir -p build
	@poetry run cyclonedx-py environment --pyproject pyproject.toml --mc-type library --of JSON -o build/subcompose.cdx.json

sbom-audit: sbom ## 🔬 audit SBOM for known vulnerabilities (CVEs)
	@echo "🔬 Auditing SBOM for vulnerabilities..."
	@poetry install --with sbom-audit --no-interaction
	@poetry run pip-audit --local --skip-editable -s osv -f columns --progress-spinner off

test: ## 🧪 run tests with pytest
	@echo "🧪 Running tests with pytest..."
	@poetry run pytest .

typecheck: ## 🔎 check types with mypy
	@echo "🔎 Checking types with mypy..."
	@poetry run mypy --no-incremental src/subcompose

help: ## 💡 show this help message
	@echo "\033[1msubcompose\033[0m — manage subsets of services in Docker compose.yaml files"
	@echo ""
	@echo "\033[1mUsage:\033[0m make [target] [target ...] [ARGS=\"...\"]"
	@echo ""
	@echo "  To pass application parameters to \033[1m\"make run\"\033[0m, use ARGS (e.g. make run ARGS=\"--help\")."
	@echo ""
	@echo "\033[1mTargets:\033[0m"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v '^#' | awk 'BEGIN {FS = ":.*?## "}; {split($$2, a, " "); icon=a[1]; sub(a[1] " ", "", $$2); printf "  %s  \033[1m%-20s\033[0m %s\n", icon, $$1, $$2}'
