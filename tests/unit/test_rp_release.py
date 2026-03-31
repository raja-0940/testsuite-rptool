"""
Unit tests for rp_release module.
"""

import pytest
import json
import io
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

from reportportal.rp_release import (
    fetch_filtered_launches,
    aggregate_launch_statistics,
    group_launches_by_attribute,
    get_report_title,
    format_timestamp,
    format_duration,
    display_summary_text,
    display_summary_json,
    display_summary_csv,
    display_grouped_summary,
    run_release_summary,
)


@pytest.mark.unit
class TestFormatting:
    """Test formatting utility functions."""

    def test_format_timestamp_valid(self):
        """Test formatting valid timestamp."""
        # 2024-01-15 10:00:00 UTC (timestamp varies by local timezone)
        timestamp_ms = 1705316400000
        result = format_timestamp(timestamp_ms)
        assert '2024-01-15' in result
        # Time portion varies by timezone, just verify format
        assert ':' in result  # Has time separator

    def test_format_timestamp_none(self):
        """Test formatting None timestamp."""
        result = format_timestamp(None)
        assert result == "N/A"

    def test_format_duration_seconds(self):
        """Test formatting duration in seconds."""
        assert format_duration(5000) == "5s"
        assert format_duration(500) == "0s"

    def test_format_duration_minutes(self):
        """Test formatting duration in minutes."""
        assert format_duration(65000) == "1m 5s"
        assert format_duration(125000) == "2m 5s"

    def test_format_duration_hours(self):
        """Test formatting duration in hours."""
        assert format_duration(3665000) == "1h 1m 5s"
        assert format_duration(7325000) == "2h 2m 5s"

    def test_format_duration_zero(self):
        """Test formatting zero or negative duration."""
        assert format_duration(0) == "0s"
        assert format_duration(-100) == "0s"


@pytest.mark.unit
class TestReportTitle:
    """Test report title generation."""

    def test_get_report_title_custom(self):
        """Test custom report title."""
        options = Namespace(
            report_title="Custom Title",
            attribute=["kuadrant:v1.3.1"]
        )
        assert get_report_title(options) == "Custom Title"

    def test_get_report_title_single_attribute(self):
        """Test auto-generated title with single attribute."""
        options = Namespace(
            report_title=None,
            attribute=["kuadrant:v1.3.1"]
        )
        assert get_report_title(options) == "KUADRANT: v1.3.1"

    def test_get_report_title_multiple_attributes(self):
        """Test auto-generated title with multiple attributes."""
        options = Namespace(
            report_title=None,
            attribute=["kuadrant:v1.3.1", "platform:aws"]
        )
        result = get_report_title(options)
        assert "KUADRANT: v1.3.1" in result
        assert "PLATFORM: aws" in result
        assert "|" in result

    def test_get_report_title_value_only(self):
        """Test title generation with value-only attribute."""
        options = Namespace(
            report_title=None,
            attribute=["somevalue"]
        )
        assert get_report_title(options) == "somevalue"


@pytest.mark.unit
class TestAggregateStatistics:
    """Test statistics aggregation."""

    def test_aggregate_empty_launches(self):
        """Test aggregating empty launch list."""
        stats = aggregate_launch_statistics([])
        assert stats['total_launches'] == 0
        assert stats['total_tests'] == 0
        assert stats['pass_rate'] == 0.0

    def test_aggregate_single_launch(self):
        """Test aggregating single launch."""
        launches = [{
            'id': 'launch1',
            'status': 'PASSED',
            'startTime': 1640000000000,
            'endTime': 1640003600000,
            'statistics': {
                'executions': {
                    'total': 100,
                    'passed': 95,
                    'failed': 3,
                    'skipped': 2
                },
                'defects': {
                    'product_bug': {'total': 2},
                    'automation_bug': {'total': 1}
                }
            }
        }]

        stats = aggregate_launch_statistics(launches)

        assert stats['total_launches'] == 1
        assert stats['passed_launches'] == 1
        assert stats['failed_launches'] == 0
        assert stats['total_tests'] == 100
        assert stats['passed_tests'] == 95
        assert stats['failed_tests'] == 3
        assert stats['skipped_tests'] == 2
        assert stats['pass_rate'] == 95.0
        assert stats['defects']['product_bug'] == 2
        assert stats['defects']['automation_bug'] == 1

    def test_aggregate_multiple_launches(self):
        """Test aggregating multiple launches."""
        launches = [
            {
                'status': 'PASSED',
                'startTime': 1640000000000,
                'endTime': 1640003600000,
                'statistics': {
                    'executions': {
                        'total': 100,
                        'passed': 95,
                        'failed': 5,
                        'skipped': 0
                    },
                    'defects': {
                        'product_bug': {'total': 3}
                    }
                }
            },
            {
                'status': 'FAILED',
                'startTime': 1640010000000,
                'endTime': 1640013600000,
                'statistics': {
                    'executions': {
                        'total': 200,
                        'passed': 180,
                        'failed': 15,
                        'skipped': 5
                    },
                    'defects': {
                        'product_bug': {'total': 10},
                        'automation_bug': {'total': 5}
                    }
                }
            }
        ]

        stats = aggregate_launch_statistics(launches)

        assert stats['total_launches'] == 2
        assert stats['passed_launches'] == 1
        assert stats['failed_launches'] == 1
        assert stats['total_tests'] == 300
        assert stats['passed_tests'] == 275
        assert stats['failed_tests'] == 20
        assert stats['skipped_tests'] == 5
        assert round(stats['pass_rate'], 2) == 91.67
        assert stats['defects']['product_bug'] == 13
        assert stats['defects']['automation_bug'] == 5

    def test_aggregate_duration_calculation(self):
        """Test duration calculation."""
        launches = [{
            'status': 'PASSED',
            'startTime': 1640000000000,
            'endTime': 1640003600000,  # 1 hour later
            'statistics': {
                'executions': {'total': 10, 'passed': 10, 'failed': 0, 'skipped': 0}
            }
        }]

        stats = aggregate_launch_statistics(launches)
        assert stats['total_duration_ms'] == 3600000  # 1 hour in ms

    def test_aggregate_time_range(self):
        """Test earliest and latest launch tracking."""
        launches = [
            {
                'status': 'PASSED',
                'startTime': 1640000000000,
                'endTime': 1640000000000,
                'statistics': {
                    'executions': {'total': 1, 'passed': 1, 'failed': 0, 'skipped': 0}
                }
            },
            {
                'status': 'PASSED',
                'startTime': 1650000000000,
                'endTime': 1650000000000,
                'statistics': {
                    'executions': {'total': 1, 'passed': 1, 'failed': 0, 'skipped': 0}
                }
            }
        ]

        stats = aggregate_launch_statistics(launches)
        assert stats['earliest_launch'] == 1640000000000
        assert stats['latest_launch'] == 1650000000000


@pytest.mark.unit
class TestGroupByAttribute:
    """Test grouping launches by attribute."""

    def test_group_by_single_attribute(self):
        """Test grouping by single attribute value."""
        launches = [
            {
                'id': 'launch1',
                'attributes': [
                    {'key': 'platform', 'value': 'aws'}
                ]
            },
            {
                'id': 'launch2',
                'attributes': [
                    {'key': 'platform', 'value': 'gcp'}
                ]
            },
            {
                'id': 'launch3',
                'attributes': [
                    {'key': 'platform', 'value': 'aws'}
                ]
            }
        ]

        grouped = group_launches_by_attribute(launches, 'platform')

        assert len(grouped) == 2
        assert 'aws' in grouped
        assert 'gcp' in grouped
        assert len(grouped['aws']) == 2
        assert len(grouped['gcp']) == 1

    def test_group_by_missing_attribute(self):
        """Test grouping when some launches don't have the attribute."""
        launches = [
            {
                'id': 'launch1',
                'attributes': [
                    {'key': 'platform', 'value': 'aws'}
                ]
            },
            {
                'id': 'launch2',
                'attributes': [
                    {'key': 'other', 'value': 'value'}
                ]
            }
        ]

        grouped = group_launches_by_attribute(launches, 'platform')

        assert len(grouped) == 2
        assert 'aws' in grouped
        assert 'No platform' in grouped

    def test_group_by_empty_list(self):
        """Test grouping empty launch list."""
        grouped = group_launches_by_attribute([], 'platform')
        assert len(grouped) == 0


@pytest.mark.unit
class TestFetchFilteredLaunches:
    """Test fetching filtered launches."""

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.utils.filter_by_attributes')
    def test_fetch_filtered_launches_success(self, mock_filter, mock_client_class):
        """Test successful fetch with filtering."""
        # Use recent timestamps (within last 30 days)
        now = datetime.now()
        recent_time_1 = int((now - timedelta(days=5)).timestamp() * 1000)
        recent_time_2 = int((now - timedelta(days=10)).timestamp() * 1000)

        mock_launches = [
            {'id': 'launch1', 'startTime': recent_time_1},
            {'id': 'launch2', 'startTime': recent_time_2}
        ]

        # Mock the client instance
        mock_client = Mock()
        mock_client.get_launches.return_value = mock_launches
        mock_client.logger = Mock()
        mock_client_class.return_value = mock_client

        mock_filter.return_value = mock_launches

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            days=30
        )

        result = fetch_filtered_launches(mock_client, options)

        assert len(result) == 2
        assert result[0]['id'] == 'launch1'
        assert result[1]['id'] == 'launch2'
        mock_client.get_launches.assert_called_once()
        mock_filter.assert_called_once_with(mock_launches, attribute_filters=['kuadrant:v1.3.1'])

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    def test_fetch_filtered_launches_no_results(self, mock_client_class):
        """Test fetch with no launches found."""
        # Mock the client instance
        mock_client = Mock()
        mock_client.get_launches.return_value = []
        mock_client.logger = Mock()
        mock_client_class.return_value = mock_client

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            days=30
        )

        result = fetch_filtered_launches(mock_client, options)

        assert result == []

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.utils.filter_by_attributes')
    def test_fetch_filtered_launches_with_days_filter(self, mock_filter, mock_client_class):
        """Test fetch with time-based filtering."""
        now = datetime.now()
        recent_time = int((now - timedelta(days=5)).timestamp() * 1000)
        old_time = int((now - timedelta(days=35)).timestamp() * 1000)

        all_launches = [
            {'id': 'launch1', 'startTime': recent_time},
            {'id': 'launch2', 'startTime': old_time}
        ]

        # Mock the client instance
        mock_client = Mock()
        mock_client.get_launches.return_value = all_launches
        mock_client.logger = Mock()
        mock_client_class.return_value = mock_client

        mock_filter.return_value = all_launches

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            days=30
        )

        result = fetch_filtered_launches(mock_client, options)

        # Should only include recent launch
        assert len(result) == 1
        assert result[0]['id'] == 'launch1'

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.utils.filter_by_attributes')
    def test_fetch_filtered_launches_multiple_attributes(self, mock_filter, mock_client_class):
        """Test fetch with multiple attribute filters."""
        mock_launches = [{'id': 'launch1'}]

        # Mock the client instance
        mock_client = Mock()
        mock_client.get_launches.return_value = mock_launches
        mock_client.logger = Mock()
        mock_client_class.return_value = mock_client

        mock_filter.return_value = mock_launches

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1', 'platform:aws'],
            days=30
        )

        result = fetch_filtered_launches(mock_client, options)

        mock_filter.assert_called_once_with(
            mock_launches,
            attribute_filters=['kuadrant:v1.3.1', 'platform:aws']
        )


@pytest.mark.unit
class TestDisplayFunctions:
    """Test display output functions."""

    def test_display_summary_text(self, capsys):
        """Test text summary display."""
        stats = {
            'total_launches': 10,
            'passed_launches': 8,
            'failed_launches': 2,
            'total_tests': 1000,
            'passed_tests': 950,
            'failed_tests': 40,
            'skipped_tests': 10,
            'pass_rate': 95.0,
            'total_duration_ms': 3600000,
            'earliest_launch': 1640000000000,
            'latest_launch': 1640100000000,
            'defects': {
                'product_bug': 20,
                'automation_bug': 10
            }
        }

        options = Namespace(
            attribute=['kuadrant:v1.3.1'],
            report_title=None,
            show_details=False
        )

        display_summary_text(stats, options, [])

        captured = capsys.readouterr()
        output = captured.out

        assert 'RELEASE TESTING SUMMARY' in output
        assert 'KUADRANT: v1.3.1' in output
        assert '10' in output  # total launches
        assert '95.0%' in output  # pass rate
        assert '1000' in output  # total tests

    def test_display_summary_json(self, capsys):
        """Test JSON summary display."""
        stats = {
            'total_launches': 10,
            'passed_launches': 8,
            'failed_launches': 2,
            'total_tests': 1000,
            'passed_tests': 950,
            'failed_tests': 40,
            'skipped_tests': 10,
            'pass_rate': 95.0,
            'total_duration_ms': 3600000,
            'earliest_launch': 1640000000000,
            'latest_launch': 1640100000000,
            'defects': {
                'product_bug': 20
            }
        }

        options = Namespace(
            attribute=['kuadrant:v1.3.1'],
            report_title=None,
            show_details=False
        )

        display_summary_json(stats, options, [])

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output['title'] == 'KUADRANT: v1.3.1'
        assert output['attributes'] == {'kuadrant': 'v1.3.1'}
        assert output['summary']['total_launches'] == 10
        assert output['summary']['pass_rate'] == 95.0
        assert output['defects']['product_bug'] == 20

    def test_display_summary_csv(self, capsys):
        """Test CSV summary display."""
        stats = {
            'total_launches': 10,
            'passed_launches': 8,
            'failed_launches': 2,
            'total_tests': 1000,
            'passed_tests': 950,
            'failed_tests': 40,
            'skipped_tests': 10,
            'pass_rate': 95.0,
            'defects': {}
        }

        options = Namespace(
            attribute=['kuadrant:v1.3.1'],
            report_title=None,
            show_details=False
        )

        display_summary_csv(stats, options, [])

        captured = capsys.readouterr()
        output = captured.out

        assert 'Metric,Value' in output
        assert 'KUADRANT: v1.3.1' in output
        assert 'Total Launches,10' in output
        assert '95.00' in output  # pass rate

    def test_display_grouped_summary(self, capsys):
        """Test grouped summary display."""
        launches = [
            {
                'id': 'launch1',
                'status': 'PASSED',
                'attributes': [{'key': 'platform', 'value': 'aws'}],
                'statistics': {
                    'executions': {'total': 100, 'passed': 95, 'failed': 5, 'skipped': 0}
                }
            },
            {
                'id': 'launch2',
                'status': 'PASSED',
                'attributes': [{'key': 'platform', 'value': 'gcp'}],
                'statistics': {
                    'executions': {'total': 50, 'passed': 48, 'failed': 2, 'skipped': 0}
                }
            }
        ]

        options = Namespace(
            attribute=['kuadrant:v1.3.1']
        )

        display_grouped_summary(launches, 'platform', options)

        captured = capsys.readouterr()
        output = captured.out

        assert 'SUMMARY GROUPED BY: PLATFORM' in output
        assert 'aws' in output
        assert 'gcp' in output


@pytest.mark.unit
class TestRunReleaseSummary:
    """Test main execution function."""

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    @patch('reportportal.rp_release.aggregate_launch_statistics')
    @patch('reportportal.rp_release.display_summary_text')
    def test_run_release_summary_success(self, mock_display, mock_aggregate, mock_fetch, mock_client_class):
        """Test successful release summary execution."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_launches = [
            {
                'id': 'launch1',
                'status': 'PASSED',
                'statistics': {
                    'executions': {'total': 100, 'passed': 95, 'failed': 5, 'skipped': 0}
                }
            }
        ]
        mock_fetch.return_value = mock_launches
        mock_aggregate.return_value = {
            'total_launches': 1,
            'total_tests': 100,
            'pass_rate': 95.0
        }

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            output_format='text',
            group_by=None,
            show_details=False,
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 0
        mock_fetch.assert_called_once_with(mock_client, options)
        mock_aggregate.assert_called_once_with(mock_launches)
        mock_display.assert_called_once()

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    def test_run_release_summary_no_launches(self, mock_fetch, mock_client_class):
        """Test execution when no launches found."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_fetch.return_value = []

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            output_format='text',
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 1

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    @patch('reportportal.rp_release.aggregate_launch_statistics')
    @patch('reportportal.rp_release.display_summary_json')
    def test_run_release_summary_json_output(self, mock_display, mock_aggregate, mock_fetch, mock_client_class):
        """Test execution with JSON output format."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_fetch.return_value = [{'id': 'launch1'}]
        mock_aggregate.return_value = {'total_launches': 1}

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            output_format='json',
            group_by=None,
            show_details=False,
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 0
        mock_display.assert_called_once()

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    @patch('reportportal.rp_release.aggregate_launch_statistics')
    @patch('reportportal.rp_release.display_summary_csv')
    def test_run_release_summary_csv_output(self, mock_display, mock_aggregate, mock_fetch, mock_client_class):
        """Test execution with CSV output format."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_fetch.return_value = [{'id': 'launch1'}]
        mock_aggregate.return_value = {'total_launches': 1}

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            output_format='csv',
            group_by=None,
            show_details=False,
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 0
        mock_display.assert_called_once()

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    @patch('reportportal.rp_release.aggregate_launch_statistics')
    @patch('reportportal.rp_release.display_summary_text')
    @patch('reportportal.rp_release.display_grouped_summary')
    def test_run_release_summary_with_grouping(self, mock_grouped, mock_display, mock_aggregate, mock_fetch, mock_client_class):
        """Test execution with grouping enabled."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_launches = [{'id': 'launch1'}]
        mock_fetch.return_value = mock_launches
        mock_aggregate.return_value = {'total_launches': 1}

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            output_format='text',
            group_by='platform',
            show_details=False,
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 0
        mock_grouped.assert_called_once_with(mock_launches, 'platform', options)

    @patch('reportportal.rp_release.ReportPortalAPIClient')
    @patch('reportportal.rp_release.fetch_filtered_launches')
    def test_run_release_summary_exception(self, mock_fetch, mock_client_class):
        """Test execution when exception occurs."""
        # Mock the client instance
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_fetch.side_effect = Exception("API Error")

        options = Namespace(
            rp_url='https://rp.example.com',
            rp_project='project',
            rp_token='key',
            attribute=['kuadrant:v1.3.1'],
            log_level='INFO'
        )

        result = run_release_summary(options)

        assert result == 1
