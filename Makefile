# Variables
# Mark all targets as phony
.PHONY: sqlite-run sqlite-run-8090 stop teardown network navigate start build help py-flake py-auto start-detach run-on-8080 run-on-8090 docker-run-8090 pip-list install-jwt
.DEFAULT_GOAL := help

DOCKER_COMPOSE = sudo docker compose
NETWORK_NAME = pycamuresandpower

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

# Navigate to pycam.docker.localhost
navigate: ## Navigate to pycam.docker.localhost
	@echo "Navigating to pycam.docker.localhost..."
	$(BROWSER) "http://pycam.docker.localhost"  # This opens the URL in the default web browser

# Start Docker app
start: ## Start the Docker app
	cd pycam && $(DOCKER_COMPOSE) up

start-detach: ## Start the Docker app
	cd pycam && $(DOCKER_COMPOSE) up -d


# Build Docker containers
build: ## Build Docker containers
	cd pycam && $(DOCKER_COMPOSE) build

collect:
	cd pycam && python manage.py collectstatic


# Local Development server
sqlite-run: ## Start the Django development server using sqlite3
	cd pycam && DJANGO_DATABASE=sqlite python manage.py makemigrations
	cd pycam && DJANGO_DATABASE=sqlite python manage.py migrate
	cd pycam && DJANGO_DATABASE=sqlite python manage.py runserver 0.0.0.0:8080

# dump data
dumpdata: ## dump data from docker db container
	docker exec -it pycam_web python manage.py dumpdata > db_backup.json

# load data
loaddata: ## load dumped data into docker db container
	docker exec -it pycam_web python manage.py loaddata db_backup.json


# Help command
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Start app on localhost:8080
run-on-8080: ## Run everything and make it accessible on localhost:8080
	@echo "Starting application on localhost:8080..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for services to start..."
	@sleep 5
	$(BROWSER) "http://localhost:8080"

# Start app on localhost:8090
run-on-8090: ## Run everything and make it accessible on localhost:8090
	@echo "Starting application on localhost:8090..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE) up -d
	@echo "Waiting for services to start..."
	@sleep 5
	$(BROWSER) "http://localhost:8090"

# Start app directly on port 8090
docker-run-8090: ## Run app on port 8090 with direct access
	@echo "Starting app on port 8090..."
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) up -d
	@echo "Application should be available at http://localhost:8090"
	$(BROWSER) "http://localhost:8090"

# Show installed packages in container
pip-list: ## Show installed packages in the web container
	docker exec -it pycam_web pip freeze


init-setup:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=setup init

init-setup-fmt:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=setup fmt

init-deploy:
	cd infra && sudo docker compose run --rm \
	  -e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	  -e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	  -e AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
	  terraform -chdir=deploy init

init-deploy-fmt:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=deploy fmt

plan-setup:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=setup plan

plan-deploy:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=deploy plan

validate-setup:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=setup validate

validate-deploy:
	cd infra && sudo docker compose run --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  terraform -chdir=deploy validate

