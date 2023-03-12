migrate:
	docker-compose --env-file .env exec --workdir /opt/app/src auth_service alembic upgrade head