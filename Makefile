.PHONY: run deploy

run:
	uvicorn main:app --reload

deploy:
	docker-compose up --build
