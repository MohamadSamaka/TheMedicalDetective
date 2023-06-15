.PHONY: init-app
init-app: install migrations migrate init-data super-user

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: createcachetable
createcachetable:
	python3 -m core.manage createcachetable

.PHONY: init-data
init-data:
	python3 -m core.manage loaddata core
	python3 -m core.manage loaddata diseases
	python3 -m core.manage loaddata symptoms
	python3 -m core.manage loaddata hospitals
	python3 -m core.manage loaddata specilaizations
	python3 -m core.manage loaddata doctors_information

.PHONY: run-server
run-server:
	python3 -m core.manage runserver

.PHONY: unmigrate-delete-all
unmigrate-delete-all:
	python -m core.manage unmigrate-delete-all

.PHONY: migrate
migrate: createcachetable
	python -m core.manage migrate

.PHONY: migrations
migrations:
	python -m core.manage makemigrations

.PHONY: super-user
super-user:
	python -m core.manage createsuperuser

.PHONY: shell
shell:
	python -m core.manage shell

.PHONY: update
update: install  migrate;