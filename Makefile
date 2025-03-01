build:
	docker compose build $(args)

up:
	docker compose up -d $(args)

run:
	docker compose up $(args)

down:
	docker compose down $(args)

migrate:
	docker compose up -d db
	export DATABASE_HOST=localhost && alembic upgrade head

local-run-worker:
	docker compose up -d db
	export DATABASE_HOST=localhost && python -m app.worker

local-run-bot:
	docker compose up -d db
	export DATABASE_HOST=localhost && python -m app.bot

migrate-down:
	docker compose up -d db
	export DATABASE_HOST=localhost && alembic downgrade $(rev)

migrate-revision:
	docker compose up -d db
	export DATABASE_HOST=localhost && alembic revision --autogenerate -m "$(message)"

migrate-upgrade:
	docker compose up -d db
	export DATABASE_HOST=localhost && alembic upgrade head


clean:
	find . -name "*.pyc" -delete
	find . -iname "__pycache__" -delete

