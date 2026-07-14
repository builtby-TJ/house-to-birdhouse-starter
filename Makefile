.PHONY: install test generate generate-coupons generate-blank-shell generate-production api

install:
	cd services/cad_engine && python -m pip install -e '.[dev]'

test:
	cd services/cad_engine && pytest

generate:
	cd services/cad_engine && birdhouse-cad generate ../../sample_projects/basic_colonial.json --output ../../generated/basic_colonial

generate-coupons:
	cd services/cad_engine && birdhouse-cad generate-coupons --output ../../generated/test_coupons

generate-blank-shell:
	cd services/cad_engine && birdhouse-cad generate-blank-shell ../../sample_projects/basic_colonial.json --output ../../generated/production_blank_shell

generate-production:
	cd services/cad_engine && birdhouse-cad generate-production ../../sample_projects/basic_colonial.json --output ../../generated/production_model

api:
	cd services/cad_engine && uvicorn birdhouse_cad.api:app --reload --port 8000
