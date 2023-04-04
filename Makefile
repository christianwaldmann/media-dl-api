.PHONY: run deploy

run:
	uvicorn main:app --reload

deploy:
	uvicorn main:app
