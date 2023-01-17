SRCPATH := RPC
BUILDPATH := build

DOCKER_TAG := maffsie/rpc
GITEA_TAG := commit.pup.cloud/maff/rpc

EXPOSE_PORT ?= 8069

PIPENV_IGNORE_VIRTUALENVS := 1

.PHONY: help build-path banner clean requirements requirements.dev docker docker-build
.PHONY: docker-push docker-run flask-run gunicorn-run format lint ci-test test package

help:
	@echo build-path clean requirements.dev requirements $(BUILDPATH)/requirements.txt package format lint unit-test

build-path:
	mkdir -p $(BUILDPATH)

clean:
	pipenv clean
	pipenv --rm
	rm -rf $(BUILDPATH)
	find . -name '*.pyc' -delete
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

requirements.dev: requirements
	pipenv install --dev
	#pip --require-virtualenv install -Ur $@

requirements:
	pipenv install
	#pip --require-virtualenv install -Ur $@

docker-build:
	@docker build -t $(DOCKER_TAG):latest -t $(GITEA_TAG):latest .

docker-push:
	@docker push -a $(DOCKER_TAG)
	@docker push -a $(GITEA_TAG)

docker: docker-build docker-push

package: requirements $(BUILDPATH)/requirements.txt
	python -m pep517.build $(SRCPATH)

format: requirements.dev
	pipenv run isort $(SRCPATH)
	pipenv run black $(SRCPATH)

lint: build-path requirements.dev
	pipenv run isort -c $(SRCPATH) | tee $(BUILDPATH)/isort-lint.log
	pipenv run black --check $(SRCPATH) | tee $(BUILDPATH)/black-lint.log
	pipenv run flake8 $(SRCPATH) | tee $(BUILDPATH)/flake8-lint.log

test: build-path requirements requirements.dev
	python -m pytest $(SRCPATH) $(ARGS)

ci-test: build-path requirements requirements.dev
	python -m pytest $(SRCPATH) $(ARGS) | tee $(BUILDPATH)/pytest.log

flask-run: requirements banner
	flask -A $(SRCPATH) run

gunicorn-run: banner
	gunicorn --config gunicorn_config.py "$(SRCPATH):create_app()"

docker-run: docker-build
	@docker run --rm -it -p $(EXPOSE_PORT):8080 $(DOCKER_TAG):latest

banner:
	@echo " 888888ba   888888ba   a88888b. "
	@echo " 88    \`8b  88    \`8b d8'   \`88 "
	@echo "a88aaaa8P' a88aaaa8P' 88        "
	@echo " 88   \`8b.  88        88        "
	@echo " 88     88  88        Y8.   .88 "
	@echo " dP     dP  dP         Y88888P' "
	@echo
	@echo "┬ ┬┌─┐┬ ┬  ┬  ┌─┐┌┬┐  ┌─┐  ┌─┐┬ ┬┌─┐┌─┐┬ ┬  ┬─┐┬ ┬┌┐┌  ┬ ┬┌─┐┬ ┬┬─┐  ┌─┐┌─┐┬┌─┐"
	@echo "└┬┘│ ││ │  │  ├┤  │   ├─┤  ├─┘│ │├─┘├─┘└┬┘  ├┬┘│ ││││  └┬┘│ ││ │├┬┘  ├─┤├─┘│ ┌┘"
	@echo " ┴ └─┘└─┘  ┴─┘└─┘ ┴   ┴ ┴  ┴  └─┘┴  ┴   ┴   ┴└─└─┘┘└┘   ┴ └─┘└─┘┴└─  ┴ ┴┴  ┴ o "
	@echo
