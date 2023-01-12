SRCPATH := RPC
BUILDPATH := build

.PHONY: help
help:
	@echo build-path clean requirements.dev requirements $(BUILDPATH)/requirements.txt package format lint unit-test

.PHONY: build-path
build-path:
	mkdir -p $(BUILDPATH)

.PHONY: clean
clean:
	rm -rf $(BUILDPATH)
	find . -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete
	find . -type d -name .pytest_cache -delete

requirements.dev:
	pip --require-virtualenv install -Ur $@

requirements:
	pip --require-virtualenv install -Ur $@

$(BUILDPATH)/requirements.txt:
	pip --require-virtualenv freeze \
		--exclude black \
		--exclude click \
		--exclude flake8 \
		--exclude isort \
		--exclude mccabe \
		--exclude mypy-extensions \
		--exclude pathspec \
		--exclude pep517 \
		--exclude platformdirs \
		--exclude pycodestyle \
		--exclude pyflakes \
		--exclude tomli \
		--exclude typing_extensions \
		> $@

.PHONY: package
package: requirements $(BUILDPATH)/requirements.txt
	python -m pep517.build $(SRCPATH)

.PHONY: format
format: requirements.dev
	isort $(SRCPATH)
	black $(SRCPATH)

.PHONY: lint
lint: build-path requirements.dev
	isort -c $(SRCPATH) | tee $(BUILDPATH)/isort-lint.log
	black --check $(SRCPATH) | tee $(BUILDPATH)/black-lint.log
	flake8 $(SRCPATH) | tee $(BUILDPATH)/flake8-lint.log

.PHONY: unit-test
unit-test: build-path requirements.dev requirements
	python -m pytest $(SRCPATH) --cov $(ARGS) | tee $(BUILDPATH)/pytest.log

.PHONY: local-run
local-run: requirements
	flask -A $(SRCPATH) run
