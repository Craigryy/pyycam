# Variables
# Mark all targets as phony
.PHONY: sqlite-run stop teardown network navigate start build help py-flake py-auto start-detach
.DEFAULT_GOAL := help

DOCKER_COMPOSE = sudo docker compose
NETWORK_NAME = scripturesandpower

ifeq ($(shell uname), Linux)
    # This is a Linux system
    BROWSER := xdg-open
else
    # This is not a Linux system (e.g., macOS, Windows)
    BROWSER := open
endif


# Flake8 linting
py-flake: ## Run Flake8 linter
	flake8 script

# Autopep8 formatting
py-auto: ## Run autopep8 formatter
	autopep8 -r script --in-place

# Stop containers
stop: ## Stop the Docker containers
	$(DOCKER_COMPOSE) stop

# Teardown app
teardown: ## Stop and remove the Docker containers and associated volumes
	$(DOCKER_COMPOSE) down -v

# View network
network: ## View the Docker network
	@docker network inspect $(NETWORK_NAME)

# Navigate to script.docker.localhost
navigate: ## Navigate to script.docker.localhost
	@echo "Navigating to script.docker.localhost..."
	$(BROWSER) "http://script.docker.localhost"  # This opens the URL in the default web browser

# Start Docker app
start: ## Start the Docker app
	$(DOCKER_COMPOSE) up

start-detach: ## Start the Docker app
	$(DOCKER_COMPOSE) up -d


# Build Docker containers
build: ## Build Docker containers
	$(DOCKER_COMPOSE) build

collect:
	python manage.py collectstatic


# Local Development server
sqlite-run: ## Start the Django development server using sqlite3
	DJANGO_DATABASE=sqlite python manage.py makemigrations
	DJANGO_DATABASE=sqlite python manage.py migrate
	DJANGO_DATABASE=sqlite python manage.py runserver 0.0.0.0:8001

# dump data
dumpdata: ## dump data from docker db container
	docker exec -it pycam_web python manage.py dumpdata > db_backup.json

# load data
loaddata: ## load dumped data into docker db container
	docker exec -it pycam_web python manage.py loaddata db_backup.json


# Help command
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
