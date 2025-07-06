run-server:
	uv run python3 run_app.py

init_db:
	uv run aerich init -t core.database.db_postgresql.TORTOISE_ORM --location src/app/migrations
	uv run aerich init-db