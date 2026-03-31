"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_launch():
    """Sample launch data."""
    return {
        'id': 'abc123-def456-ghi789',
        'name': 'Test Launch',
        'number': 42,
        'startTime': 1640000000000,
        'endTime': 1640001000000,
        'status': 'PASSED',
        'statistics': {
            'executions': {
                'total': 100,
                'passed': 85,
                'failed': 10,
                'skipped': 5
            },
            'defects': {
                'to_investigate': {'total': 5},
                'product_bug': {'total': 3},
                'automation_bug': {'total': 2},
                'system_issue': {'total': 0}
            }
        },
        'attributes': [
            {'key': 'browser', 'value': 'chrome'},
            {'key': 'env', 'value': 'production'}
        ]
    }


@pytest.fixture
def sample_launches(sample_launch):
    """List of sample launches."""
    launch2 = sample_launch.copy()
    launch2['id'] = 'xyz789-uvw456-rst123'
    launch2['name'] = 'Previous Launch'
    launch2['number'] = 41
    return [sample_launch, launch2]


@pytest.fixture
def sample_test_item():
    """Sample test item data."""
    return {
        'id': 'item123-456',
        'name': 'test_login_success',
        'type': 'STEP',
        'status': 'PASSED',
        'startTime': 1640000000000,
        'endTime': 1640000001234,
        'issue': None,
        'attributes': [
            {'key': 'tier', 'value': 'p0'},
            {'key': 'browser', 'value': 'chrome'}
        ]
    }


@pytest.fixture
def sample_test_items():
    """List of sample test items."""
    return [
        {
            'id': 'item1',
            'name': 'test_api_login',
            'type': 'STEP',
            'status': 'PASSED',
            'startTime': 1640000000000,
            'endTime': 1640000001000,
            'issue': None,
            'attributes': [
                {'key': 'tier', 'value': 'p0'},
                {'key': 'type', 'value': 'api'}
            ]
        },
        {
            'id': 'item2',
            'name': 'test_api_logout',
            'type': 'STEP',
            'status': 'FAILED',
            'startTime': 1640000000000,
            'endTime': 1640000002000,
            'issue': {
                'issueType': 'to_investigate$ti001'
            },
            'attributes': [
                {'key': 'tier', 'value': 'p1'},
                {'key': 'type', 'value': 'api'}
            ]
        },
        {
            'id': 'item3',
            'name': 'test_ui_login',
            'type': 'STEP',
            'status': 'SKIPPED',
            'startTime': 1640000000000,
            'endTime': 1640000000500,
            'issue': None,
            'attributes': [
                {'key': 'tier', 'value': 'p2'},
                {'key': 'type', 'value': 'ui'}
            ]
        },
        {
            'id': 'suite1',
            'name': 'Login Suite',
            'type': 'SUITE',
            'status': 'PASSED',
            'startTime': 1640000000000,
            'endTime': 1640000003000,
            'issue': None,
            'attributes': []
        }
    ]


@pytest.fixture
def rp_config():
    """ReportPortal configuration."""
    return {
        'endpoint': 'https://rp.example.com',
        'project': 'test_project',
        'api_key': 'test_api_key'
    }


@pytest.fixture
def sample_junit_xml_file(tmp_path):
    """Create a sample JUnit XML file for integration testing."""
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="IntegrationTestSuite" tests="3" failures="1" skipped="1" time="1.234" timestamp="2024-01-01T12:00:00">
        <properties>
            <property name="platform" value="aws"/>
            <property name="version" value="1.3.0"/>
            <property name="__rp_suite_description" value="Integration test suite"/>
            <property name="__rp_launch_description" value="Full workflow test"/>
        </properties>
        <testcase classname="com.example.tests.TestClass" name="test_passing" time="0.123">
            <properties>
                <property name="color" value="green"/>
                <property name="component" value="TestComponent"/>
            </properties>
            <system-out>Test passed successfully</system-out>
        </testcase>
        <testcase classname="com.example.tests.TestClass" name="test_failing" time="0.456">
            <properties>
                <property name="color" value="red"/>
                <property name="__rp_case_description" value="Test case that fails"/>
            </properties>
            <failure message="Assertion failed" type="AssertionError">
                Expected: 5
                Got: 3
            </failure>
            <system-err>Error details here</system-err>
        </testcase>
        <testcase classname="com.example.tests.TestClass" name="test_skipped" time="0.001">
            <properties>
                <property name="color" value="yellow"/>
            </properties>
            <skipped message="Test skipped"/>
        </testcase>
    </testsuite>
</testsuites>
'''

    # Create temporary XML file
    xml_file = tmp_path / "sample_junit.xml"
    xml_file.write_text(xml_content)

    return str(xml_file)
