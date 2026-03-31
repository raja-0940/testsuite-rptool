
RESULTS_PATH?="../results"

collect: clean
	COLLECTOR_ENABLE=true pytest --junit-xml="${RESULTS_PATH}/junit_00_info_collector.xml" -o junit_logging=all tests/info_collector.py 

test: clean collect
	pytest -n4 --junit-xml="${RESULTS_PATH}/junit_smoke.xml" -o junit_logging=all -o junit_suite_name=smoke || true
	pytest -n4 --junit-xml="${RESULTS_PATH}/junit_acceptance.xml" -o junit_logging=all -o junit_suite_name=acceptance || true
	pytest -n4 --junit-xml="${RESULTS_PATH}/junit_fullsuite.xml" -o junit_logging=all -o junit_suite_name=fullsuite || true

clean:
	rm ${RESULTS_PATH}/*xml || true