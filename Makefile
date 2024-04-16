# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
#
# VERSION = 2020.01.29

UID:=$(shell id --user)
GID:=$(shell id --group)

dc = docker compose
dc_dev = $(dc) -f compose.yml -f compose.dev.yml
run = run --rm -u ${UID}:${GID}
manage = $(dc_dev) $(run) django-dev python manage.py

all: help pip-tools install requirements upgrade build push push_semver clean app dev test loadtest test_data pdb bash shell dbshell migrate migrations trivy lintfix lint diff
.PHONY: all

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

dev:
	$(dc_dev) build
	$(dc_dev) run --rm django-dev python manage.py migrate
	$(dc_dev) up django-dev

test: lint                          ## Execute tests
	$(dc) $(run) test pytest $(ARGS)

loadtest: migrate
	$(manage) make_partitions $(ARGS)
	$(dc) $(run) locust $(ARGS)

test_data:
	$(manage) generate_test_data --num_days 25 --num_rows_per_day 2000

pdb:
	$(dc_dev) $(run) django-dev pytest --pdb $(ARGS)

bash:
	$(dc_dev) $(run) django-dev bash

shell:
	$(manage) shell_plus

dbshell:
	$(manage) dbshell

migrate:
	$(manage) migrate

migrations:
	$(manage) makemigrations $(ARGS)

trivy:                              ## Detect image vulnerabilities
	$(dc) build --no-cache app
	trivy image --ignore-unfixed docker-registry.secure.amsterdam.nl/datapunt/bereikbaarheid-backend

lintfix:                            ## Execute lint fixes
	$(dc) $(run) test black /src/$(APP) /tests/$(APP)
	$(dc) $(run) test autoflake /src --recursive --in-place --remove-unused-variables --remove-all-unused-imports --quiet
	$(dc) $(run) test isort /src/$(APP) /tests/$(APP)


lint:                               ## Execute lint checks
	$(dc) $(run) test autoflake /src --check --recursive --quiet
	$(dc) $(run) test isort --diff --check /src/$(APP) /tests/$(APP)

diff:
	@python3 ./deploy/diff.py
