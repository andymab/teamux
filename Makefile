# Default tools
COMPOSE ?= docker compose
API      ?= api
WEB      ?= web
API_PORT ?= 8000
WEB_PORT ?= 5173

.PHONY: help env build up start stop down restart logs ps api-logs web-logs api-shell web-shell \
        curl-analyze curl-url image publish

help: ## Show available commands
	@echo "Available targets:"; \
	awk -F':.*##' '/^[a-zA-Z0-9_-]+:.*##/{printf "  %-20s %s
	", $$1, $$2}' $(MAKEFILE_LIST)

env: ## Create .env from example if missing
	@test -f .env || (cp .env.example .env && echo '→ Created .env from .env.example')

build: ## Build all images
	$(COMPOSE) build

up: env ## Run in foreground (build if needed)
	$(COMPOSE) up --build

start: ## Run detached
	$(COMPOSE) up -d

stop: ## Stop containers
	$(COMPOSE) stop

down: ## Stop and remove containers
	$(COMPOSE) down

restart: ## Recreate and start detached
	$(COMPOSE) down && $(COMPOSE) up -d --build

logs: ## Tail all logs
	$(COMPOSE) logs -f

ps: ## Show containers status
	$(COMPOSE) ps

api-logs: ## Tail API logs
	$(COMPOSE) logs -f $(API)

web-logs: ## Tail Web logs
	$(COMPOSE) logs -f $(WEB)

api-shell: ## Shell inside API container
	$(COMPOSE) exec $(API) sh -lc 'bash || sh'

web-shell: ## Shell inside Web container
	$(COMPOSE) exec $(WEB) sh -lc 'bash || sh'

curl-analyze: ## Test /analyze endpoint with sample text
	@curl -s -X POST http://localhost:$(API_PORT)/analyze \
	  -H 'Content-Type: application/json' \
	  -d '{"text":"Пример текста для анализа"}'

curl-url: ## Test /analyze-url endpoint with sample URL
	@curl -s -X POST http://localhost:$(API_PORT)/analyze-url \
	  -H 'Content-Type: application/json' \
	  -d '{"url":"https://example.com"}'

image: ## Test /image endpoint with a minimal EN prompt
	@curl -s -X POST http://localhost:$(API_PORT)/image \
	  -H 'Content-Type: application/json' \
	  -d '{"prompt_en":"minimalist flat illustration"}'

publish: ## Test /publish endpoint (Telegram)
	@curl -s -X POST http://localhost:$(API_PORT)/publish \
	  -H 'Content-Type: application/json' \
	  -d '{"text":"Hello from teamux"}'

node-ver:
	docker compose exec web sh -lc "node -v && npm -v"

docker-restore:
	docker compose build --no-cache web
	docker compose up -d
	docker compose logs -f web