up:
	docker compose up -d --build --force-recreate

down:
	docker compose down

stop:
	docker compose stop

start:
	docker compose start

restart:
	docker compose restart

ps:
	docker compose ps

logs:
	docker compose logs -f -t --tail=200

