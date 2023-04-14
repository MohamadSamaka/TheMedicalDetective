.PHONY: install
install:
	pip3 install -r requirments.txt

.PHONY: run-server
run-server:
	python3 -m core.manage runserver

.PHONY: migrate
migrate:
	python3 -m core.manage migrate

.PHONY: migrations
migrations:
	python3 -m core.manage makemigrations

.PHONY: super-user
super-user:
	python3 -m core.manage createsuperuser

.PHONY: update
update: install  migrate;