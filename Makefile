        PYTHON ?= python

        .PHONY: build unit scenarios verify demo

        build:
	$(PYTHON) scripts/build.py

        unit:
	$(PYTHON) -m unittest discover -s tests/unit -v

        scenarios:
	$(PYTHON) tests/run_scenarios.py

        verify:
	$(PYTHON) scripts/verify.py

        demo:
	$(PYTHON) -m scopeproof report --scope examples/scope.json --evidence examples/evidence --output output/demo.md
