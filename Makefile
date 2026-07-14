.PHONY: install test generate generate-coupons api

install:
	cd services/cad_engine && python -m pip install -e '.[dev]'

test:
	cd services/cad_engine && pytest

generate:
	cd services/cad_engine && birdhouse-cad generate ../../sample_projects/basic_colonial.json --output ../../generated/basic_colonial

generate-coupons:
	cd services/cad_engine && birdhouse-cad generate-coupons --output ../../generated/test_coupons

api:
	cd services/cad_engine && uvicorn birdhouse_cad.api:app --reload --port 8000
