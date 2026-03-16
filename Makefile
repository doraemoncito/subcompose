# Make will automatically set the `MAKEFLAGS` variable when you run it with certain flags. The 's' flag is used for
# silent mode, which suppresses command output. We can check for this flag in our Makefile to conditionally set a
# QUIET variable that we can use to suppress output in our commands.  --silent and --quiet are synonyms for the 's'
# flag, so this will work regardless of which one is used.
ifeq ($(findstring s,$(MAKEFLAGS)),s)
QUIET => /dev/null 2>&1
else
QUIET =
endif

.PHONY: all dist distclean clean compile run docs format lint package sast sbom sbom-audit test typecheck help ensure-poetry-install

.DEFAULT_GOAL := help

ARGS ?= --help

ensure-poetry-install:
	@if ! command -v poetry $(QUIET) && [ ! -x $(HOME)/.local/bin/poetry ]; then \
		echo "🛠️  Poetry not found. Installing..."; \
		curl -sSL https://install.python-poetry.org | python3 - $(QUIET); \
	fi
	@if [ ! -d .venv ] || ! poetry run ruff --version $(QUIET); then \
		echo "🔄  Setting up Poetry environment..."; \
		poetry install --with dev,docs,sast,sbom,sbom-audit --no-interaction $(QUIET); \
	fi

all: ensure-poetry-install lint typecheck compile test docs sast sbom-audit package ## 🟢 run all checks and build
	@echo "🟢  All checks passed!"

compile: ensure-poetry-install ## 🐍 compile the example application to check for syntax errors
	@echo "🐍  Compiling example application..."
	@PYTHONPATH=src poetry run python -m py_compile src/subcompose/__main__.py $(QUIET)

clean: ## 🧹 remove all generated build artefacts
	@echo "🧹  Cleaning generated files..."
	@rm -rf build dist .mypy_cache .pytest_cache __pycache__ $(QUIET)
	@find . -type d -name __pycache__ -exec rm -rf {} + $(QUIET)

distclean: clean ## 🧹 remove all build artefacts and Python environment
	@echo "🧹  Deactivating Python virtual environment (if active)..."
	@if [ "$VIRTUAL_ENV" != "" ]; then \
		deactivate $(QUIET) || true; \
	fi
	@echo "🧹  Removing .venv directory..."
	@rm -rf .venv $(QUIET)

dist: all dist-post ## 📦 run all checks, security scan, SBOM audit, and build the distributable package
	@echo "📦  Distribution build complete!"

dist-post: sast sbom sbom-audit package

docs: ensure-poetry-install ## 📚 build the Sphinx documentation
	@echo "📚  Building documentation..."
	@poetry run sphinx-build -W --keep-going -b html docs build/docs/html $(QUIET)

show-docs: ## 🌐 open the built documentation in your web browser
	@echo "🌐  Opening documentation in your web browser..."
	@open build/docs/html/index.html $(QUIET)

format: ensure-poetry-install ## 🎨 format code with ruff
	@echo "🎨  Formatting code with ruff..."
	@poetry run ruff format . $(QUIET)

lint: ensure-poetry-install ## 🔍 check code with ruff
	@echo "🔍  Linting code with ruff..."
	@poetry run ruff check --fix . $(QUIET)

package: ensure-poetry-install ## 🏗️ build the distributable wheel and sdist with Poetry
	@echo "🏗️  Building distributable package..."
	@poetry build $(QUIET)

run: ensure-poetry-install ## ▶️ run example application to demonstrate usage of the client library
	@echo "▶️  Running example application..."
	@PYTHONPATH=src poetry run python src/subcompose/__main__.py $(ARGS) $(QUIET)

sast: ensure-poetry-install ## 🔒 scan for security issues with bandit
	@echo "🔒  Scanning for security issues..."
	@poetry run bandit --ini .bandit.ini --exit-zero src/subcompose $(QUIET)

sbom: ensure-poetry-install ## 🧾 generate CycloneDX SBOM (JSON)
	@echo "📦  Generating SBOM..."
	@mkdir -p build $(QUIET)
	@poetry run cyclonedx-py environment --pyproject pyproject.toml --mc-type library --of JSON -o build/subcompose.cdx.json $(QUIET)

sbom-audit: ensure-poetry-install sbom ## 🔬 audit SBOM for known vulnerabilities (CVEs)
	@echo "🔬  Auditing SBOM for vulnerabilities..."
	@poetry run pip-audit --local --skip-editable -s osv -f columns --progress-spinner off $(QUIET)

test: ensure-poetry-install ## 🧪 run tests with pytest
	@echo "🧪  Running tests with pytest..."
	@poetry run pytest . $(QUIET)

typecheck: ensure-poetry-install ## 🔎 check types with mypy
	@echo "🔎  Checking types with mypy..."
	@poetry run mypy --no-incremental src/subcompose $(QUIET)

help: ## 💡 show this help message
	@echo "\033[1msubcompose\033[0m — manage subsets of services in Docker compose.yaml files"
	@echo ""
	@echo "\033[1mUsage:\033[0m make [--quiet|--silent] [target] [target ...] [ARGS=\"...\"]"
	@echo ""
	@echo "  Use --quiet or --silent (e.g. make --quiet docs) to suppress command output."
	@echo "  To pass application parameters to \033[1m\"make run\"\033[0m, use ARGS (e.g. make run ARGS=\"--help\")."
	@echo "  \033[1mTip:\033[0m For faster builds, use 'make dist -j N' (N = CPU cores)"
	@echo ""
	@echo "\033[1mTargets:\033[0m"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v '^#' | awk 'BEGIN {FS = ":.*?## "}; {split($$2, a, " "); icon=a[1]; sub(a[1] " ", "", $$2); printf "  %s  \033[1m%-20s\033[0m %s\n", icon, $$1, $$2}'
