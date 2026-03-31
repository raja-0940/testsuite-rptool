"""
Sample JUnit XML data and fixtures for testing.

This module provides various sample JUnit XML configurations
to test different scenarios and edge cases.
"""

SIMPLE_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="SimpleTestSuite" timestamp="2024-01-01T12:00:00" tests="1" failures="0" errors="0" skipped="0">
        <testcase name="test_simple" classname="simple_module.TestClass" time="0.1">
        </testcase>
    </testsuite>
</testsuites>"""

COMPLEX_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="ComplexTestSuite" timestamp="2024-01-01T12:00:00" tests="4" failures="1" errors="1" skipped="1">
        <properties>
            <property name="platform" value="aws"/>
            <property name="version" value="2.1.0"/>
            <property name="build" value="kuadrant"/>
            <property name="component" value="TestComponent"/>
            <property name="__rp_suite_description" value="Complex test suite with all status types"/>
            <property name="__rp_launch_description" value="Launch for testing all scenarios"/>
        </properties>
        <testcase name="test_passing" classname="complex.module.TestClass" time="1.5">
            <properties>
                <property name="color" value="green"/>
                <property name="priority" value="high"/>
            </properties>
            <system-out>Test passed successfully with output</system-out>
        </testcase>
        <testcase name="test_failing" classname="complex.module.TestClass" time="0.8">
            <failure message="Assertion failed">AssertionError: Expected 5 but got 3</failure>
            <properties>
                <property name="color" value="red"/>
                <property name="issue" value="ISSUE-123"/>
                <property name="__rp_case_description" value="Test case that demonstrates failure"/>
            </properties>
            <system-err>Error details here</system-err>
        </testcase>
        <testcase name="test_error" classname="complex.module.TestClass" time="0.2">
            <error message="Runtime error">RuntimeError: Something went wrong</error>
            <properties>
                <property name="color" value="orange"/>
            </properties>
        </testcase>
        <testcase name="test_skipped" classname="complex.module.TestClass" time="0.0">
            <skipped message="Feature not implemented">NotImplementedError: Feature coming soon</skipped>
            <properties>
                <property name="color" value="yellow"/>
                <property name="reason" value="not_implemented"/>
            </properties>
        </testcase>
    </testsuite>
</testsuites>"""

MULTI_SUITE_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="UnitTestSuite" timestamp="2024-01-01T10:00:00" tests="2" failures="0" errors="0" skipped="0">
        <properties>
            <property name="level" value="smoke"/>
            <property name="platform" value="onprem"/>
        </properties>
        <testcase name="test_unit_1" classname="unit.tests.TestUnit" time="0.1">
            <properties>
                <property name="component" value="CoreModule"/>
            </properties>
        </testcase>
        <testcase name="test_unit_2" classname="unit.tests.TestUnit" time="0.2">
            <properties>
                <property name="component" value="CoreModule"/>
            </properties>
        </testcase>
    </testsuite>
    <testsuite name="IntegrationTestSuite" timestamp="2024-01-01T11:00:00" tests="2" failures="1" errors="0" skipped="0">
        <properties>
            <property name="level" value="acceptance"/>
            <property name="platform" value="aws"/>
            <property name="__rp_suite_description" value="Integration tests"/>
        </properties>
        <testcase name="test_integration_pass" classname="integration.tests.TestIntegration" time="2.0">
            <properties>
                <property name="component" value="APIModule"/>
                <property name="color" value="blue"/>
            </properties>
        </testcase>
        <testcase name="test_integration_fail" classname="integration.tests.TestIntegration" time="1.5">
            <failure message="Integration test failed">Connection timeout</failure>
            <properties>
                <property name="component" value="APIModule"/>
                <property name="color" value="red"/>
            </properties>
        </testcase>
    </testsuite>
</testsuites>"""

INFO_COLLECTOR_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="info-collector" timestamp="2024-01-01T12:00:00" tests="1" failures="0" errors="0" skipped="0">
        <properties>
            <property name="cluster_version" value="4.15.0"/>
            <property name="platform" value="rosa"/>
            <property name="region" value="us-east-1"/>
            <property name="kuadrant_version" value="v0.8.0"/>
            <property name="istio_version" value="1.20.0"/>
            <property name="__rp_suite_description" value="Environment information collector"/>
            <property name="__rp_launch_description" value="Cluster and component version information"/>
        </properties>
        <testcase name="collect_environment_info" classname="info_collector.EnvCollector" time="0.1">
            <properties>
                <property name="task" value="environment_collection"/>
                <property name="status" value="completed"/>
            </properties>
            <system-out>Successfully collected environment information</system-out>
        </testcase>
    </testsuite>
</testsuites>"""

PROPERTY_HEAVY_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="PropertyTestSuite" timestamp="2024-01-01T12:00:00" tests="1" failures="0" errors="0" skipped="0">
        <properties>
            <property name="platform" value="gcp"/>
            <property name="version" value="3.0.0"/>
            <property name="build" value="rhcl"/>
            <property name="level" value="fullsuite"/>
            <property name="env" value="staging"/>
            <property name="os" value="linux"/>
            <property name="custom_prop1" value="value1"/>
            <property name="custom_prop2" value="value2"/>
            <property name="__rp_suite_description" value="Suite with many properties"/>
            <property name="__rp_launch_description" value="Testing property handling"/>
            <property name="__rp_internal_prop" value="should_be_filtered"/>
            <property name="__rp_another_internal" value="also_filtered"/>
        </properties>
        <testcase name="test_with_properties" classname="property.tests.PropertyTest" time="0.5">
            <properties>
                <property name="color" value="purple"/>
                <property name="component" value="PropertyModule"/>
                <property name="priority" value="medium"/>
                <property name="issue" value="PROP-456"/>
                <property name="custom_case_prop" value="case_value"/>
                <property name="__rp_case_description" value="Test case with many properties"/>
                <property name="__rp_internal_case_prop" value="filtered_case_prop"/>
            </properties>
        </testcase>
    </testsuite>
</testsuites>"""

EMPTY_JUNIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="EmptyTestSuite" timestamp="2024-01-01T12:00:00" tests="0" failures="0" errors="0" skipped="0">
    </testsuite>
</testsuites>"""

# Sample property data for testing
SAMPLE_SUITE_PROPERTIES = [
    {"key": "platform", "value": "aws"},
    {"key": "version", "value": "1.5.0"},
    {"key": "build", "value": "kuadrant"},
    {"key": "level", "value": "smoke"},
    {"key": "__rp_suite_description", "value": "Test suite description"},
    {"key": "__rp_launch_description", "value": "Test launch description"},
    {"key": "__rp_internal", "value": "should be filtered"}
]

SAMPLE_CASE_PROPERTIES = [
    {"key": "color", "value": "green"},
    {"key": "component", "value": "TestComponent"},
    {"key": "priority", "value": "high"},
    {"key": "issue", "value": "ISSUE-789"},
    {"key": "__rp_case_description", "value": "Test case description"},
    {"key": "__rp_internal_case", "value": "should be filtered"}
]

# Expected filtered results
EXPECTED_FILTERED_SUITE_PROPERTIES = [
    {"key": "platform", "value": "aws"},
    {"key": "version", "value": "1.5.0"},
    {"key": "build", "value": "kuadrant"},
    {"key": "level", "value": "smoke"}
]

EXPECTED_FILTERED_CASE_PROPERTIES = [
    {"key": "color", "value": "green"},
    {"key": "component", "value": "TestComponent"},
    {"key": "priority", "value": "high"},
    {"key": "issue", "value": "ISSUE-789"}
]

# Auto-analysis properties
AUTO_ANALYSIS_PROPERTIES = [
    {"key": "auto_analyze", "system": "true", "value": "true"},
    {"key": "immediateAutoAnalysis", "system": "true", "value": "true"}
]


def get_junit_xml_samples():
    """
    Get all available JUnit XML samples.
    
    Returns:
        dict: Dictionary of sample names and their XML content
    """
    return {
        "simple": SIMPLE_JUNIT_XML,
        "complex": COMPLEX_JUNIT_XML,
        "multi_suite": MULTI_SUITE_JUNIT_XML,
        "info_collector": INFO_COLLECTOR_JUNIT_XML,
        "property_heavy": PROPERTY_HEAVY_JUNIT_XML,
        "empty": EMPTY_JUNIT_XML
    }


def get_property_samples():
    """
    Get all available property samples.
    
    Returns:
        dict: Dictionary of property sample names and data
    """
    return {
        "suite_properties": SAMPLE_SUITE_PROPERTIES,
        "case_properties": SAMPLE_CASE_PROPERTIES,
        "filtered_suite": EXPECTED_FILTERED_SUITE_PROPERTIES,
        "filtered_case": EXPECTED_FILTERED_CASE_PROPERTIES,
        "auto_analysis": AUTO_ANALYSIS_PROPERTIES
    }