# APP INFO
DOCKER_REGISTRY ?= quay.io
IMAGE_PREFIX    ?= attcomdev
IMAGE_NAME      ?= armada
HELM            ?= helm
LABEL           ?= commit-id
PYTHON          = python3
CHART           = armada

# VERSION INFO
GIT_COMMIT = $(shell git rev-parse HEAD)
GIT_SHA    = $(shell git rev-parse --short HEAD)
GIT_TAG    = $(shell git describe --tags --abbrev=0 --exact-match 2>/dev/null)
GIT_DIRTY  = $(shell test -n "`git status --porcelain`" && echo "dirty" || echo "clean")

ifdef VERSION
	DOCKER_VERSION = $(VERSION)
endif

IMAGE_TAG ?= git-${GIT_SHA}
IMAGE := ${DOCKER_REGISTRY}/${IMAGE_PREFIX}/${IMAGE_NAME}:${IMAGE_TAG}
SHELL = /bin/bash

info:
	@echo "Version:           ${VERSION}"
	@echo "Git Tag:           ${GIT_TAG}"
	@echo "Git Commit:        ${GIT_COMMIT}"
	@echo "Git Tree State:    ${GIT_DIRTY}"
	@echo "Docker Version:    ${DOCKER_VERSION}"
	@echo "Registry:          ${DOCKER_REGISTRY}"

.PHONY: all
all: lint charts images

.PHONY: build
build: bootstrap
	$(PYTHON) setup.py install

.PHONY: bootstrap
bootstrap:
	pip install -r requirements.txt

.PHONY: bootstrap-all
bootstrap-all: bootstrap
	pip install -r test-requirements.txt

.PHONY: check-docker
check-docker:
	@if [ -z $$(which docker) ]; then \
		echo "Missing \`docker\` client which is required for development"; \
		exit 2; \
	fi

.PHONY: check-tox
check-tox:
	@if [ -z $$(which tox) ]; then \
		echo "Missing \`tox\` client which is required for development"; \
		exit 2; \
	fi

.PHONY: docker-build
images: check-docker
	docker build --rm -t ${IMAGE} --label $(LABEL) .

.PHONY: dry-run
dry-run: clean
	tools/helm_tk.sh $(HELM)
	$(HELM) dep up charts/$(CHART)
	$(HELM) template charts/$(CHART)

# make tools
.PHONY: protoc
protoc:
	@tools/helm-hapi.sh

.PHONY: clean
clean:
	rm -rf build

# testing checks
.PHONY: test-all
test-all: check-tox helm_lint
	tox

.PHONY: test-unit
test-unit: check-tox
	tox -e py35

.PHONY: test-coverage
test-coverage: check-tox
	tox -e coverage

.PHONY: test-bandit
test-bandit: check-tox
	tox -e bandit

# style checks
.PHONY: lint
lint: test-pep8 helm_lint

.PHONY: test-pep8
test-pep8: check-tox
	tox -e pep8

.PHONY: helm-lint
helm_lint:
	@tools/helm_tk.sh $(HELM)
	$(HELM) dep up charts/$(CHART)
	$(HELM) lint charts/$(CHART)

.PHONY: charts
charts: clean
	$(HELM) dep up charts/$(CHART)
	$(HELM) package charts/$(CHART)
