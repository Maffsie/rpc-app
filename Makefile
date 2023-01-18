# Core paths
SRCPATH := RPC
RESDPATH := resources.default

# Paths managed by Make
BUILDPATH := build
RESPATH := resources
VENVPATH := .venv

# Resources managed by Make
RESTGTS := $(shell find $(RESDPATH) -maxdepth 1 -mindepth 1 -not -name '.*' -exec basename {} \;|sed 's/^/$(RESPATH)\//g')

# Operational stuff
GITREPO := https://github.com/Maffsie/rpc-app.git
DOCKER_TAG := maffsie/rpc
GITEA_TAG := commit.pup.cloud/maff/rpc

ARM64USR ?= root
ARM64HOST ?= a64-p4-8-0.wuf.one
SWARM_SVC := api_rpc

EXPOSE_PORT ?= 8069

# non-literal targets
# organised by category

#output-only
.PHONY: banner help
#filesystem-only
.PHONY: clean
#setup-only
.PHONY: requirements requirements.dev
#code style, syntax and function validation
.PHONY: format lint test ci-test
#code-running
.PHONY: flask-run gunicorn-run
#container-only
.PHONY: docker-build docker-push docker-run docker
#misc. tasks
.PHONY: arm64build arm64deploy

# Help text
help: banner
	@echo yeah i could use some help lol

# Create build path
build:
	mkdir -p $(BUILDPATH)

# Clean up the working directory
clean:
	rm -rf $(BUILDPATH) $(RESPATH)
	pipenv --rm
	find . -name '*.pyc' -delete
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

# Install all runtime and development dependencies
requirements.dev: requirements
	pipenv install --dev

# Install all runtime dependencies
requirements: .venv
	pipenv install

# Ensure the virtual environment path is present for pipenv
.venv:
	mkdir $(VENVPATH)

# Build the docker container and ensure it's tagged with the necessary tags
docker-build:
	@docker build -t $(DOCKER_TAG):latest -t $(GITEA_TAG):latest .

# Push the built container up to all tagged repos, ensuring a fresh build first
docker-push: docker-build
	@docker push -a $(DOCKER_TAG)
	@docker push -a $(GITEA_TAG)

# Run the built container with the API exposed on the configured port, ensuring a fresh build first
docker-run: docker-build
	@docker run --rm -it -p $(EXPOSE_PORT):8080 $(DOCKER_TAG):latest

# Run automatic code formatting tools
format: requirements.dev
	pipenv run isort $(SRCPATH)
	pipenv run black $(SRCPATH)

# Run code linting tools and save their output in the build path
lint: build requirements.dev
	pipenv run isort -c $(SRCPATH) | tee $(BUILDPATH)/isort-lint.log
	pipenv run black --check $(SRCPATH) | tee $(BUILDPATH)/black-lint.log
	pipenv run flake8 $(SRCPATH) | tee $(BUILDPATH)/flake8-lint.log

# Run all tests interactively
test: build requirements.dev
	python -m pytest $(SRCPATH) $(ARGS)

# Run all tests and save the output, for CI purposes
ci-test: build requirements.dev
	python -m pytest $(SRCPATH) $(ARGS) | tee $(BUILDPATH)/pytest.log

# Ensure the resources path is created
resources:
	mkdir $(RESPATH)

# Copies all files and directories within the default resources into the resources folder
# for supporting Docker volumes
$(RESTGTS): resources
	cp -pr $(RESDPATH)/$(shell basename $@) $@

# Starts the Flask development server
flask-run: requirements $(RESTGTS) banner
	flask -A $(SRCPATH) run

# Starts the gunicorn production server
gunicorn-run: requirements $(RESTGTS) banner
	pipenv run gunicorn --config gunicorn_config.py "$(SRCPATH):create_app()"

# Outputs a fun lil banner.
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

gitpull:
	git pull

arm64build:
	ssh $(ARM64USR)@$(ARM64HOST) sh -c 'cd `mktemp -d` && git clone $(GITREPO) . && make docker-push'

arm64deploy:
	ssh $(ARM64USR)@$(ARM64HOST) docker service update --force --image $(GITEA_TAG):latest $(SWARM_SVC)
