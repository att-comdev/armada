# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# APP INFO
DOCKER_REGISTRY ?= quay.io
IMAGE_PREFIX    ?= attcomdev
IMAGE_NAME      ?= armada
IMAGE_TAG       ?= latest
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

.PHONY: images
images: check-docker
	build_armada

.PHONY: dry-run
dry-run: clean
	tools/helm_tk.sh $(HELM)
	$(HELM) dep up charts/$(CHART)
	$(HELM) template charts/$(CHART)

.PHONY: docs
docs: clean build_docs

.PHONY: run_images
run_images: run_armada

.PHONY: run_armada
run_armada:
	ID=$(docker run -d $(IMAGE))
	ifeq ($(findstring "204 No Content", $(curl -v GET localhost:8000/api/v1.0/health)),"204 No Content")
		echo "Successful Health Check"
	else
		echo "Failed Health Check"
		exit 2
	endif
	docker rm -fv $(ID)

.PHONY: build_docs
build_docs:
	tox -e docs

.PHONY: build_armada
build_armada:
	docker build -t $(IMAGE) --label $(LABEL) -f Dockerfile .

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

.PHONY: health-check
health-check:
ifeq ($(findstring "204 No Content", $(curl -v GET localhost:8000/api/v1.0/health)),"204 No Content")
	echo "Health Check Complete"
else
	echo "Failed Health Check"
endif
