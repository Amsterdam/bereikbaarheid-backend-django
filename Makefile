# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
#
# VERSION = 2020.01.29
.PHONY: help pip-tools install requirements update test init manifests deploy

dc = docker compose
run = $(dc) run --rm
manage = $(run) dev python manage.py

ENVIRONMENT ?= local
VERSION ?= latest
HELM_ARGS = manifests/chart \
	-f manifests/values.yaml \
	-f manifests/env/${ENVIRONMENT}.yaml \
	--set image.tag=${VERSION} \
	--set image.registry=${REGISTRY}

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pip-tools:
	pip install pip-tools

install: pip-tools                  ## Install requirements and sync venv with expected state as defined in requirements.txt
	pip-sync requirements.txt requirements_dev.txt

requirements: pip-tools             ## Upgrade requirements (in requirements.in) to latest versions and compile requirements.txt
	## The --allow-unsafe flag should be used and will become the default behaviour of pip-compile in the future
	## https://stackoverflow.com/questions/58843905
	pip-compile --upgrade --output-file requirements.txt --allow-unsafe requirements.in
	pip-compile --upgrade --output-file requirements_dev.txt --allow-unsafe requirements_dev.in

upgrade: requirements install       ## Run 'requirements' and 'install' targets

build:                              ## Build docker image
	$(dc) build

push: build                         ## Push docker image to registry
	$(dc) push

push_semver:
	VERSION=$${VERSION} $(MAKE) push
	VERSION=$${VERSION%\.*} $(MAKE) push
	VERSION=$${VERSION%%\.*} $(MAKE) push

clean:                              ## Clean docker stuff
	$(dc) down -v --remove-orphans

app:
	$(dc) up app

# the name option is explicitly set, so the back- and frontend can communicate
# with eachother while on the same docker network. The frontend docker-compose
# file contains a reference to the set name
dev: migrate
	$(run) --name bereikbaarheid-backend-django-dev --service-ports dev

test: lint							## Execute tests
	$(run) test pytest $(ARGS)

loadtest: migrate
	$(manage) make_partitions $(ARGS)
	$(run) locust $(ARGS)

test_data:
	$(manage) generate_test_data --num_days 25 --num_rows_per_day 2000

pdb:
	$(run) dev pytest --pdb $(ARGS)

bash:
	$(run) dev bash

shell:
	$(manage) shell_plus

dbshell:
	$(manage) dbshell

migrate:
	$(manage) migrate

migrations:
	$(manage) makemigrations $(ARGS)

trivy: 	    						## Detect image vulnerabilities
	$(dc) build --no-cache app
	trivy image --ignore-unfixed docker-registry.secure.amsterdam.nl/datapunt/bereikbaarheid-backend

lintfix:                            ## Execute lint fixes
	$(run) test black /src/$(APP) /tests/$(APP)
	$(run) test autoflake /src --recursive --in-place --remove-unused-variables --remove-all-unused-imports --quiet
	$(run) test isort /src/$(APP) /tests/$(APP)


lint:                               ## Execute lint checks
	$(run) test autoflake /app --check --recursive --quiet
	$(run) test isort --diff --check /app/src/$(APP) /app/tests/$(APP)

diff:
	@python3 ./deploy/diff.py

deploy: manifests
	helm upgrade --install backend $(HELM_ARGS) $(ARGS)

manifests:
	helm template backend $(HELM_ARGS) $(ARGS)

update-chart:
	rm -rf manifests/chart
	git clone --branch 1.8.0 --depth 1 git@github.com:Amsterdam/helm-application.git manifests/chart
	rm -rf manifests/chart/.git