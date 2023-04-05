.PHONY: run deploy

run:
	uvicorn app.main:app --reload

deploy:
	docker-compose up --build
