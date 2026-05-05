.PHONY: validate validate-graph-contracts

validate: validate-graph-contracts

validate-graph-contracts:
	python3 tools/validate_regis_graph_contracts.py
