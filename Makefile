.PHONY: validate validate-acr-contracts

validate: validate-acr-contracts

validate-acr-contracts:
	python3 tools/validate_acr_contracts.py
