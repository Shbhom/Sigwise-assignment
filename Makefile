init-postgres:
	docker run -d --name sigwise-psql -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -v postgres_data:/var/lib/postgresql/data -p 5432:5432 postgres:latest

run-postgres:
	docker start sigwise-psql

run-dev-server:
	RUNNING_ENV="DEV" uvicorn app:app --reload

run-server:
	RUNNING_ENV="PROD" uvicorn app:app
