.PHONY: init-app
init-app: install migrations migrate loaddata super-user

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: createcachetable
createcachetable:
	python3 -m core.manage createcachetable

.PHONY: loaddata
loaddata:
	python3 -m core.manage loaddata core
	
.PHONY: run-server
run-server:
	python3 -m core.manage runserver

.PHONY: unmigrate-all
unmigrate-all:
	python -m core.manage unapply_all_migrations

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