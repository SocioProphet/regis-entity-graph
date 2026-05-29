.PHONY: validate validate-graph-contracts validate-epistemic-edge-records

validate: validate-graph-contracts validate-epistemic-edge-records

validate-graph-contracts:
	python3 tools/validate_regis_graph_contracts.py

validate-epistemic-edge-records:
	python3 tools/validate_epistemic_edge_records.py
