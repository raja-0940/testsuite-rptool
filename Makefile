
MOCK_SUITE="mock_suite"
RESULTS_PATH?=results

# Mock suite operations
.PHONY: collect
collect:
	make -C ${MOCK_SUITE} collect

.PHONY: results
results: 
	make -C ${MOCK_SUITE} test

.PHONY: clean
clean: clean-results clean-pytest clean-python

.PHONY: clean-results
clean-results:
	rm ${RESULTS_PATH}/*xml || true

.PHONY: clean-pytest
clean-pytest:
	rm -fr .pytest_cache

.PHONY: clean-python
clean-python:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete


.PHONY: build
build: clean-python
	docker build -t rptool .

.PHONY: build-mock-suite
build-mock-suite:
	docker build -t mock_suite mock_suite

.PHONY: build-all
build-all: build build-mock-suite

.PHONY: run
run: build
	docker run -it --name rptool --rm rptool:latest

.PHONY: run-mock-suite
run-mock-suite: build-mock-suite
	docker run -it --name mock_suite --rm mock_suite:latest

.PHONY: build-clean
build-clean:
	docker image rm rptool:latest
	docker image rm mock_suite:latest
	docker builder prune -f --filter="until=1h"

.PHONY: image-load
image-load:
	kind load docker-image rptool:latest
	kind load docker-image mock_suite:latest

# Test targets
.PHONY: test
test:
	python -m pytest tests/
