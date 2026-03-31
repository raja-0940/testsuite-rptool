"""Tests for rp_query_utils module."""

import pytest
from reportportal import rp_query_utils as utils


@pytest.mark.unit
class TestAttributeFiltering:
    """Test attribute filtering functions."""

    def test_matches_attribute_filter_key_value(self):
        """Test matching attribute with key:value format."""
        item = {'attributes': [{'key': 'browser', 'value': 'chrome'}]}

        assert utils.matches_attribute_filter(item, 'browser:chrome') is True
        assert utils.matches_attribute_filter(item, 'browser:firefox') is False
        assert utils.matches_attribute_filter(item, 'env:prod') is False

    def test_matches_attribute_filter_value_only(self):
        """Test matching attribute with value only."""
        item = {'attributes': [{'key': 'browser', 'value': 'chrome'}]}

        assert utils.matches_attribute_filter(item, 'chrome') is True
        assert utils.matches_attribute_filter(item, 'firefox') is False

    def test_matches_attribute_filter_no_attributes(self):
        """Test matching on item without attributes."""
        item = {'name': 'test'}

        assert utils.matches_attribute_filter(item, 'anything') is False

    def test_matches_attribute_regex_key_pattern(self):
        """Test matching attribute with key:pattern format."""
        item = {'attributes': [{'key': 'env', 'value': 'production'}]}

        assert utils.matches_attribute_regex(item, 'env:prod.*') is True
        assert utils.matches_attribute_regex(item, 'env:dev.*') is False

    def test_matches_attribute_regex_pattern_only(self):
        """Test matching attribute with pattern only."""
        item = {'attributes': [{'key': 'env', 'value': 'production'}]}

        assert utils.matches_attribute_regex(item, '(?i)PRODUCTION') is True
        assert utils.matches_attribute_regex(item, 'dev.*') is False

    def test_matches_attribute_regex_invalid_pattern(self):
        """Test invalid regex pattern."""
        item = {'attributes': [{'key': 'env', 'value': 'production'}]}

        # Invalid regex should return False
        assert utils.matches_attribute_regex(item, '[invalid(') is False

    def test_filter_by_attributes(self, sample_test_items):
        """Test filtering by exact attributes."""
        filtered = utils.filter_by_attributes(
            sample_test_items,
            attribute_filters=['tier:p0']
        )

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test_api_login'

    def test_filter_by_attributes_regex(self, sample_test_items):
        """Test filtering by regex attributes."""
        filtered = utils.filter_by_attributes(
            sample_test_items,
            attribute_regex_filters=['tier:p[01]']
        )

        assert len(filtered) == 2
        names = [item['name'] for item in filtered]
        assert 'test_api_login' in names
        assert 'test_api_logout' in names

    def test_filter_by_attributes_combined(self, sample_test_items):
        """Test filtering by both exact and regex attributes."""
        filtered = utils.filter_by_attributes(
            sample_test_items,
            attribute_filters=['type:api'],
            attribute_regex_filters=['tier:p[01]']
        )

        assert len(filtered) == 2


@pytest.mark.unit
class TestNameFiltering:
    """Test name filtering functions."""

    def test_matches_name_regex_success(self):
        """Test name regex matching."""
        item = {'name': 'test_login_success'}

        assert utils.matches_name_regex(item, r'test_.*_success') is True
        assert utils.matches_name_regex(item, r'^login') is False

    def test_matches_name_regex_invalid(self):
        """Test invalid regex pattern."""
        item = {'name': 'test_login'}

        assert utils.matches_name_regex(item, '[invalid(') is False

    def test_filter_by_name_regex(self, sample_test_items):
        """Test filtering by name regex."""
        filtered = utils.filter_by_name_regex(sample_test_items, r'test_api_.*')

        assert len(filtered) == 2
        names = [item['name'] for item in filtered]
        assert 'test_api_login' in names
        assert 'test_api_logout' in names

    def test_filter_by_name_regex_no_match(self, sample_test_items):
        """Test name regex with no matches."""
        filtered = utils.filter_by_name_regex(sample_test_items, r'nonexistent')

        assert len(filtered) == 0

    def test_filter_by_name_regex_invalid(self, sample_test_items):
        """Test invalid regex returns empty list."""
        filtered = utils.filter_by_name_regex(sample_test_items, '[invalid(')

        assert len(filtered) == 0


@pytest.mark.unit
class TestStatusAndTypeFiltering:
    """Test status and type filtering functions."""

    def test_filter_by_status(self, sample_test_items):
        """Test filtering by status."""
        failed = utils.filter_by_status(sample_test_items, 'FAILED')
        passed = utils.filter_by_status(sample_test_items, 'PASSED')

        assert len(failed) == 1
        assert failed[0]['name'] == 'test_api_logout'
        assert len(passed) == 2

    def test_filter_by_type(self, sample_test_items):
        """Test filtering by type."""
        steps = utils.filter_by_type(sample_test_items, 'STEP')
        suites = utils.filter_by_type(sample_test_items, 'SUITE')

        assert len(steps) == 3
        assert len(suites) == 1
        assert suites[0]['name'] == 'Login Suite'

    def test_exclude_type(self, sample_test_items):
        """Test excluding a type."""
        no_suites = utils.exclude_type(sample_test_items, 'SUITE')

        assert len(no_suites) == 3
        for item in no_suites:
            assert item['type'] != 'SUITE'


@pytest.mark.unit
class TestDataExtraction:
    """Test data extraction functions."""

    def test_extract_launch_statistics(self, sample_launch):
        """Test extracting launch statistics."""
        stats = utils.extract_launch_statistics(sample_launch)

        assert stats['total'] == 100
        assert stats['passed'] == 85
        assert stats['failed'] == 10
        assert stats['skipped'] == 5
        assert stats['to_investigate'] == 5
        assert stats['product_bug'] == 3
        assert stats['automation_bug'] == 2
        assert stats['system_issue'] == 0

    def test_extract_launch_statistics_missing_data(self):
        """Test extracting stats from launch with missing data."""
        launch = {'name': 'Test'}
        stats = utils.extract_launch_statistics(launch)

        assert stats['total'] == 0
        assert stats['passed'] == 0

    def test_extract_item_duration(self):
        """Test extracting item duration."""
        item = {
            'startTime': 1000000,
            'endTime': 1005000
        }

        duration = utils.extract_item_duration(item)

        assert duration == 5.0

    def test_extract_item_duration_zero(self):
        """Test duration extraction when times are same."""
        item = {
            'startTime': 1000000,
            'endTime': 1000000
        }

        duration = utils.extract_item_duration(item)

        assert duration == 0

    def test_extract_names(self, sample_test_items):
        """Test extracting names from items."""
        names = utils.extract_names(sample_test_items)

        assert len(names) == 4
        assert 'test_api_login' in names
        assert 'Login Suite' in names

    def test_extract_ids(self, sample_test_items):
        """Test extracting IDs from items."""
        ids = utils.extract_ids(sample_test_items)

        assert len(ids) == 4
        assert 'item1' in ids
        assert 'suite1' in ids


@pytest.mark.unit
class TestGroupingAndAggregation:
    """Test grouping and aggregation functions."""

    def test_group_by_status(self, sample_test_items):
        """Test grouping by status."""
        grouped = utils.group_by_status(sample_test_items)

        assert 'PASSED' in grouped
        assert 'FAILED' in grouped
        assert 'SKIPPED' in grouped
        assert len(grouped['PASSED']) == 2
        assert len(grouped['FAILED']) == 1
        assert len(grouped['SKIPPED']) == 1

    def test_count_by_status(self, sample_test_items):
        """Test counting by status."""
        counts = utils.count_by_status(sample_test_items)

        assert counts['PASSED'] == 2
        assert counts['FAILED'] == 1
        assert counts['SKIPPED'] == 1

    def test_group_by_attribute(self, sample_test_items):
        """Test grouping by attribute."""
        grouped = utils.group_by_attribute(sample_test_items, 'tier')

        assert 'p0' in grouped
        assert 'p1' in grouped
        assert 'p2' in grouped
        assert len(grouped['p0']) == 1
        assert len(grouped['p1']) == 1

    def test_group_by_attribute_no_key(self, sample_test_items):
        """Test grouping by non-existent attribute key."""
        grouped = utils.group_by_attribute(sample_test_items, 'nonexistent')

        assert len(grouped) == 0


@pytest.mark.unit
class TestFormattingUtilities:
    """Test formatting utility functions."""

    def test_format_attributes(self):
        """Test formatting attributes."""
        attrs = [
            {'key': 'browser', 'value': 'chrome'},
            {'key': 'env', 'value': 'prod'}
        ]

        formatted = utils.format_attributes(attrs)

        assert formatted == 'browser:chrome, env:prod'

    def test_format_attributes_no_key(self):
        """Test formatting attributes without keys."""
        attrs = [
            {'value': 'smoke'},
            {'key': 'tier', 'value': 'p0'}
        ]

        formatted = utils.format_attributes(attrs)

        assert 'smoke' in formatted
        assert 'tier:p0' in formatted

    def test_format_attributes_empty(self):
        """Test formatting empty attributes."""
        formatted = utils.format_attributes([])

        assert formatted == '-'

    def test_format_defect_type(self):
        """Test formatting defect types."""
        assert utils.format_defect_type('project_issue$pb001') == 'PB'
        assert utils.format_defect_type('to_investigate$ti001') == 'TI'
        assert utils.format_defect_type('ab123') == 'AB'
        assert utils.format_defect_type('-') == '-'
        assert utils.format_defect_type('N/A') == '-'

    def test_format_duration(self):
        """Test formatting duration."""
        assert utils.format_duration(1.234) == '1.23s'
        assert utils.format_duration(0.1, precision=3) == '0.100s'
        assert utils.format_duration(5.0) == '5.00s'


@pytest.mark.unit
class TestCompositeFiltering:
    """Test composite filtering function."""

    def test_apply_filters_single(self, sample_test_items):
        """Test applying single filter."""
        filtered = utils.apply_filters(
            sample_test_items,
            status='FAILED'
        )

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test_api_logout'

    def test_apply_filters_multiple(self, sample_test_items):
        """Test applying multiple filters."""
        filtered = utils.apply_filters(
            sample_test_items,
            status='PASSED',
            name_regex=r'test_api_.*',
            attribute_filters=['tier:p0']
        )

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test_api_login'

    def test_apply_filters_exclude_types(self, sample_test_items):
        """Test excluding types."""
        filtered = utils.apply_filters(
            sample_test_items,
            exclude_types=['SUITE']
        )

        assert len(filtered) == 3
        for item in filtered:
            assert item['type'] != 'SUITE'

    def test_apply_filters_custom_function(self, sample_test_items):
        """Test custom filter function."""
        def has_issue(item):
            return item.get('issue') is not None

        filtered = utils.apply_filters(
            sample_test_items,
            custom_filter=has_issue
        )

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test_api_logout'

    def test_apply_filters_no_match(self, sample_test_items):
        """Test filters with no matches."""
        filtered = utils.apply_filters(
            sample_test_items,
            status='IN_PROGRESS'
        )

        assert len(filtered) == 0


@pytest.mark.unit
class TestConstants:
    """Test that constants are defined."""

    def test_item_type_constants(self):
        """Test item type constants exist."""
        assert hasattr(utils, 'ITEM_TYPE_SUITE')
        assert hasattr(utils, 'ITEM_TYPE_STEP')
        assert hasattr(utils, 'ITEM_TYPE_TEST')

    def test_status_constants(self):
        """Test status constants exist."""
        assert hasattr(utils, 'STATUS_PASSED')
        assert hasattr(utils, 'STATUS_FAILED')
        assert hasattr(utils, 'STATUS_SKIPPED')

    def test_defect_constants(self):
        """Test defect type constants exist."""
        assert hasattr(utils, 'DEFECT_TO_INVESTIGATE')
        assert hasattr(utils, 'DEFECT_PRODUCT_BUG')
        assert hasattr(utils, 'DEFECT_AUTOMATION_BUG')
        assert hasattr(utils, 'DEFECT_SYSTEM_ISSUE')


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_filter_empty_list(self):
        """Test filtering empty list."""
        filtered = utils.filter_by_status([], 'PASSED')
        assert filtered == []

        filtered = utils.filter_by_name_regex([], r'test.*')
        assert filtered == []

        filtered = utils.filter_by_attributes([], ['tier:p0'])
        assert filtered == []

    def test_extract_from_empty_list(self):
        """Test extracting from empty list."""
        names = utils.extract_names([])
        assert names == []

        ids = utils.extract_ids([])
        assert ids == []

    def test_group_empty_list(self):
        """Test grouping empty list."""
        grouped = utils.group_by_status([])
        assert grouped == {}

        counted = utils.count_by_status([])
        assert counted == {}

        grouped = utils.group_by_attribute([], 'tier')
        assert grouped == {}

    def test_matches_attribute_filter_empty_filter(self):
        """Test matching with edge case filters."""
        item = {'attributes': [{'key': 'browser', 'value': 'chrome'}]}

        # Empty value
        assert utils.matches_attribute_filter(item, ':chrome') is False
        assert utils.matches_attribute_filter(item, 'browser:') is False

    def test_extract_item_duration_missing_fields(self):
        """Test duration extraction with missing fields."""
        item = {}
        duration = utils.extract_item_duration(item)
        assert duration == 0

        item = {'startTime': 1000000}
        duration = utils.extract_item_duration(item)
        assert duration == 0

    def test_extract_names_with_missing_name(self):
        """Test extracting names when some items lack name field."""
        items = [
            {'name': 'test1'},
            {'id': 'test2'},  # No name field
            {'name': 'test3'}
        ]
        names = utils.extract_names(items)
        assert len(names) == 3
        assert names[0] == 'test1'
        assert names[1] == ''
        assert names[2] == 'test3'

    def test_format_attributes_with_separator(self):
        """Test formatting attributes with custom separator."""
        attrs = [
            {'key': 'browser', 'value': 'chrome'},
            {'key': 'env', 'value': 'prod'}
        ]

        formatted = utils.format_attributes(attrs, separator=' | ')
        assert formatted == 'browser:chrome | env:prod'

    def test_format_defect_type_variations(self):
        """Test various defect type formats."""
        # Standard formats
        assert utils.format_defect_type('to_investigate$ti123') == 'TI'
        assert utils.format_defect_type('automation_bug$ab456') == 'AB'
        assert utils.format_defect_type('system_issue$si789') == 'SI'

        # Edge cases
        assert utils.format_defect_type(None) == '-'
        assert utils.format_defect_type('custom_type') == 'CU'

    def test_group_by_status_with_unknown(self):
        """Test grouping items with missing status field."""
        items = [
            {'name': 'test1', 'status': 'PASSED'},
            {'name': 'test2'},  # No status field
            {'name': 'test3', 'status': 'FAILED'}
        ]

        grouped = utils.group_by_status(items)
        assert 'PASSED' in grouped
        assert 'FAILED' in grouped
        assert 'UNKNOWN' in grouped
        assert len(grouped['UNKNOWN']) == 1

    def test_filter_by_attributes_multiple_same_key(self):
        """Test filtering when item has multiple attributes with same key."""
        items = [
            {
                'name': 'test1',
                'attributes': [
                    {'key': 'tag', 'value': 'smoke'},
                    {'key': 'tag', 'value': 'regression'}
                ]
            },
            {
                'name': 'test2',
                'attributes': [
                    {'key': 'tag', 'value': 'unit'}
                ]
            }
        ]

        filtered = utils.filter_by_attributes(items, attribute_filters=['tag:smoke'])
        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test1'

    def test_apply_filters_all_params(self):
        """Test apply_filters with all parameter types."""
        items = [
            {
                'name': 'test_api_login',
                'status': 'PASSED',
                'type': 'STEP',
                'startTime': 1000,
                'endTime': 2000,
                'attributes': [{'key': 'tier', 'value': 'p0'}]
            },
            {
                'name': 'Suite',
                'status': 'PASSED',
                'type': 'SUITE',
                'startTime': 1000,
                'endTime': 5000,
                'attributes': [{'key': 'tier', 'value': 'p0'}]
            },
            {
                'name': 'test_api_logout',
                'status': 'FAILED',
                'type': 'STEP',
                'startTime': 1000,
                'endTime': 3000,
                'attributes': [{'key': 'tier', 'value': 'p1'}]
            }
        ]

        # Complex multi-filter scenario
        filtered = utils.apply_filters(
            items,
            name_regex=r'test_.*',
            status='PASSED',
            exclude_types=['SUITE'],
            attribute_filters=['tier:p0']
        )

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'test_api_login'

    def test_matches_attribute_regex_case_insensitive(self):
        """Test case-insensitive regex matching."""
        item = {'attributes': [{'key': 'env', 'value': 'Production'}]}

        assert utils.matches_attribute_regex(item, '(?i)production') is True
        assert utils.matches_attribute_regex(item, 'PRODUCTION') is False  # Case sensitive
        assert utils.matches_attribute_regex(item, 'env:(?i)production') is True

    def test_count_by_status_multiple_same_status(self):
        """Test counting with many items of same status."""
        items = [
            {'status': 'PASSED'},
            {'status': 'PASSED'},
            {'status': 'PASSED'},
            {'status': 'FAILED'},
        ]

        counts = utils.count_by_status(items)
        assert counts['PASSED'] == 3
        assert counts['FAILED'] == 1

    def test_group_by_attribute_multiple_values(self):
        """Test grouping when items have multiple attributes."""
        items = [
            {
                'name': 'test1',
                'attributes': [
                    {'key': 'browser', 'value': 'chrome'},
                    {'key': 'tier', 'value': 'p0'}
                ]
            },
            {
                'name': 'test2',
                'attributes': [
                    {'key': 'browser', 'value': 'firefox'},
                    {'key': 'tier', 'value': 'p1'}
                ]
            }
        ]

        grouped = utils.group_by_attribute(items, 'browser')
        assert 'chrome' in grouped
        assert 'firefox' in grouped
        assert len(grouped['chrome']) == 1
        assert len(grouped['firefox']) == 1

    def test_apply_filters_with_none_filters(self):
        """Test apply_filters when all filters are None."""
        items = [
            {'name': 'test1', 'status': 'PASSED'},
            {'name': 'test2', 'status': 'FAILED'}
        ]

        # Should return all items when no filters applied
        filtered = utils.apply_filters(items)
        assert len(filtered) == 2

    def test_extract_launch_statistics_partial_data(self):
        """Test extracting stats with partial statistics."""
        launch = {
            'statistics': {
                'executions': {
                    'total': 50,
                    'passed': 40
                    # Missing failed, skipped
                }
                # Missing defects section
            }
        }

        stats = utils.extract_launch_statistics(launch)
        assert stats['total'] == 50
        assert stats['passed'] == 40
        assert stats['failed'] == 0
        assert stats['skipped'] == 0
        assert stats['to_investigate'] == 0
