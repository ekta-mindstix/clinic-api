install:
	poetry install

migrate:
	poetry run flask --app api.main db upgrade

seed:
	poetry run flask --app api.main seed

run:
	poetry run python -m api.main
