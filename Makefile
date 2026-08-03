.PHONY: validate validate-graph-contracts validate-epistemic-edge-records validate-ioes-graph-extension validate-ner-contracts validate-decision-ledger-seals validate-temporal-supersession validate-semantic-token-tree validate-span-alignment

validate: validate-graph-contracts validate-epistemic-edge-records validate-ioes-graph-extension validate-ner-contracts validate-decision-ledger-seals validate-temporal-supersession validate-semantic-token-tree validate-span-alignment

validate-graph-contracts:
	python3 tools/validate_regis_graph_contracts.py

validate-epistemic-edge-records:
	python3 tools/validate_epistemic_edge_records.py

validate-ioes-graph-extension:
	python3 tools/validate_ioes_graph_extension.py

validate-ner-contracts:
	python3 tools/validate_ner_contracts.py

validate-decision-ledger-seals:
	python3 tools/validate_decision_ledger_seals.py

validate-temporal-supersession:
	python3 tools/validate_temporal_supersession.py

validate-semantic-token-tree:
	python3 tools/validate_semantic_token_tree.py

validate-span-alignment:
	python3 tools/validate_span_alignment.py
