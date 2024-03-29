# Core paths
SRCPATH := RPC
RESDPATH := resources.default

# Toolpaths
ENVBIN := /usr/bin/env

# Paths managed by Make
BUILDPATH := build
RESPATH := resources
VENVPATH := .venv

# Resources managed by Make
RESTGTS := $(shell $(ENVBIN) find $(RESDPATH) -maxdepth 1 -mindepth 1 -not -name '.*' -exec $(ENVBIN) basename {} \;|$(ENVBIN) sed 's/^/$(RESPATH)\//g')

# Operational stuff
GITREPO := https://github.com/Maffsie/rpc-app.git
DOCKER_TAG := maffsie/rpc
GITEA_TAG := commit.pup.cloud/maff/rpc

ARCH := $(shell $(ENVBIN) uname -m)
TSDOMAIN ?= wuf.one
ARM64USR ?= root
ARM64HOST ?= a64-p4-8-0.$(TSDOMAIN)
I386USR ?= maff
I386HOST ?= x40.$(TSDOMAIN)
X64USR ?= root
X64HOST ?= eu-fsn-hv3.$(TSDOMAIN)
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
#code-debugging
.PHONY: flask-debug repl
#operational checks
.PHONY: healthcheck
#container-only
.PHONY: docker-build docker-push docker-run docker
#misc. tasks
##git workflow
.PHONY: gitcommit gitpull gitpush push
##build - multiarch
.PHONY: docker-build-aarch64 docker-build-i386 docker-build-x64
##deployment - arm64
.PHONY: arm64deploy
##dev helping
.PHONY: localtest

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
	@$(ENVBIN) docker build \
		-t $(DOCKER_TAG):latest \
		-t $(DOCKER_TAG):latest-$(ARCH) \
		-t $(GITEA_TAG):latest \
		-t $(GITEA_TAG):latest-$(ARCH) \
		.

# Push the built container up to all tagged repos, ensuring a fresh build first
docker-push: docker-build
	@$(ENVBIN) docker push $(DOCKER_TAG):latest
	@$(ENVBIN) docker push $(DOCKER_TAG):latest-$(ARCH)
	@$(ENVBIN) docker push $(GITEA_TAG):latest
	@$(ENVBIN) docker push $(GITEA_TAG):latest-$(ARCH)

# Run the built container with the API exposed on the configured port, ensuring a fresh build first
docker-run: docker-build
	@$(ENVBIN) docker run --rm -it -p $(EXPOSE_PORT):8080 $(DOCKER_TAG):latest-$(ARCH)

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
	cp -pr $(RESDPATH)/$(shell $(ENVBIN) basename $@) $@

# Starts the Flask development server
#  Depends on requirements because you'd normally run this during dev, where requirements
#   are being changed
flask-run: requirements $(RESTGTS) banner
	pipenv run flask -A $(SRCPATH) run -h 0.0.0.0 -p $(EXPOSE_PORT) $(ARGS)

# Starts the Flask development server in debug mode
flask-debug: requirements $(RESTGTS) banner
	pipenv run flask --debug -A $(SRCPATH) run -h 0.0.0.0 -p $(EXPOSE_PORT) $(ARGS)

# Opens a REPL
repl: requirements $(RESTGTS)
	pipenv run python

# Starts the gunicorn production server
#  Does not depend on requirements, because this would be run in a packaged scenario
gunicorn-run: $(RESTGTS) banner
	pipenv run gunicorn --config gunicorn_config.py "$(SRCPATH):create_app()"

healthcheck:
	$(ENVBIN) curl -s http://127.0.0.1:8080/ping | $(ENVBIN) grep 'pong'
	$(ENVBIN) curl -s http://127.0.0.1:8080/v1/health/alive | $(ENVBIN) grep 'alive!'
	$(ENVBIN) curl -s http://127.0.0.1:8080/v2/health/alive | $(ENVBIN) grep 'alive!'

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

# Lazy extra targets for easy dev

gitpull:
	git pull

gitcommit:
	git commit -p

gitpush:
	git push

push: gitcommit gitpush

# These can be parallelised but how do i tell make it can do that
# hashtag too afraid to just do make -j2
docker-build-aarch64:
	ssh $(ARM64USR)@$(ARM64HOST) git clone $(GITREPO) /tmp/a64rpc
	ssh $(ARM64USR)@$(ARM64HOST) make -C /tmp/a64rpc docker-push
	ssh $(ARM64USR)@$(ARM64HOST) rm -rf /tmp/a64rpc

docker-build-i386:
	ssh $(I386USR)@$(I386HOST) git clone $(GITREPO) /tmp/i386rpc
	ssh $(I386USR)@$(I386HOST) make -C /tmp/i386rpc docker-push
	ssh $(I386USR)@$(I386HOST) rm -rf /tmp/i386rpc

docker-build-x64:
	ssh $(X64USR)@$(X64HOST) git clone $(GITREPO) /tmp/x64rpc
	ssh $(X64USR)@$(X64HOST) make -C /tmp/x64rpc docker-push
	ssh $(X64USR)@$(X64HOST) rm -rf /tmp/x64rpc

# TODO: docker-build-arch targets
# 	arm32v5, arm32v6, arm32v7 - maybe the CHIPs, the android things board
# 	arm32 - rpi2
# 	i386 - x40, one of the vaios, the wibrain, dunno
# 	mipsel - GL750
# 	mips64le - dunno if any openwrt boxen exist for this, may have to use qemu
# 	ppc32 - does docker for ppc32 even exist? could use the ibook
# 	ppc64le - will have to use qemu for that i think
# 	riscv64 - need to buy a riscv host tbh
# 	s390x - will have to use qemu for that

arm64deploy:
	ssh $(ARM64USR)@$(ARM64HOST) docker service update --force --image $(GITEA_TAG):latest-aarch64 $(SWARM_SVC)

.PHONY: 386dev
386dev: docker-build
	docker run --rm -it --user root -v $(SRCPATH):/app/RPC -v ./Pipfile:/app/Pipfile -v ./Pipfile.lock:/app/Pipfile.lock $(GITEA_TAG):latest-$(ARCH) /bin/sh


localtest: format gitcommit gitpush docker-build-aarch64 arm64deploy
