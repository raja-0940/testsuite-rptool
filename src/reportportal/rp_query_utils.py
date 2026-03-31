"""
ReportPortal Query Utilities

Reusable functions for filtering, processing, and analyzing ReportPortal data.
This module provides utilities that can be used in custom scripts and tools.
"""

import re
from typing import List, Dict, Optional, Any, Callable


# Constants
ITEM_TYPE_SUITE = 'SUITE'
ITEM_TYPE_STEP = 'STEP'
ITEM_TYPE_TEST = 'TEST'

STATUS_PASSED = 'PASSED'
STATUS_FAILED = 'FAILED'
STATUS_SKIPPED = 'SKIPPED'
STATUS_INTERRUPTED = 'INTERRUPTED'
STATUS_IN_PROGRESS = 'IN_PROGRESS'

DEFECT_TO_INVESTIGATE = 'to_investigate'
DEFECT_PRODUCT_BUG = 'product_bug'
DEFECT_AUTOMATION_BUG = 'automation_bug'
DEFECT_SYSTEM_ISSUE = 'system_issue'


# =============================================================================
# Attribute Filtering
# =============================================================================

def matches_attribute_filter(item: Dict, attr_filter: str) -> bool:
    """
    Check if an item matches an attribute filter.

    Args:
        item: Launch or test item dictionary
        attr_filter: Attribute filter in format "key:value" or "value"

    Returns:
        True if item matches the filter, False otherwise

    Examples:
        >>> item = {'attributes': [{'key': 'browser', 'value': 'chrome'}]}
        >>> matches_attribute_filter(item, 'browser:chrome')
        True
        >>> matches_attribute_filter(item, 'chrome')
        True
        >>> matches_attribute_filter(item, 'firefox')
        False
    """
    attributes = item.get('attributes', [])
    if not attributes:
        return False

    if ':' in attr_filter:
        filter_key, filter_value = attr_filter.split(':', 1)
        return any(
            attr.get('key') == filter_key and attr.get('value') == filter_value
            for attr in attributes
        )
    else:
        return any(attr.get('value') == attr_filter for attr in attributes)


def matches_attribute_regex(item: Dict, attr_regex: str) -> bool:
    """
    Check if an item matches an attribute regex filter.

    Args:
        item: Launch or test item dictionary
        attr_regex: Attribute regex filter in format "key:pattern" or "pattern"

    Returns:
        True if item matches the regex filter, False otherwise

    Examples:
        >>> item = {'attributes': [{'key': 'env', 'value': 'production'}]}
        >>> matches_attribute_regex(item, 'env:prod.*')
        True
        >>> matches_attribute_regex(item, '(?i)PRODUCTION')
        True
    """
    attributes = item.get('attributes', [])
    if not attributes:
        return False

    try:
        if ':' in attr_regex:
            filter_key, pattern_str = attr_regex.split(':', 1)
            pattern = re.compile(pattern_str)
            return any(
                attr.get('key') == filter_key and pattern.search(attr.get('value', ''))
                for attr in attributes
            )
        else:
            pattern = re.compile(attr_regex)
            return any(pattern.search(attr.get('value', '')) for attr in attributes)
    except re.error:
        return False


def filter_by_attributes(items: List[Dict],
                        attribute_filters: Optional[List[str]] = None,
                        attribute_regex_filters: Optional[List[str]] = None) -> List[Dict]:
    """
    Filter items by exact and/or regex attribute filters.

    All filters must match (AND logic).

    Args:
        items: List of items to filter
        attribute_filters: List of exact attribute filters ("key:value" or "value")
        attribute_regex_filters: List of regex attribute filters ("key:pattern" or "pattern")

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'attributes': [{'key': 'tier', 'value': 'p0'}]},
        ...     {'attributes': [{'key': 'tier', 'value': 'p1'}]}
        ... ]
        >>> filter_by_attributes(items, attribute_filters=['tier:p0'])
        [{'attributes': [{'key': 'tier', 'value': 'p0'}]}]
    """
    result = items

    # Apply exact attribute filters
    if attribute_filters:
        for attr_filter in attribute_filters:
            result = [item for item in result if matches_attribute_filter(item, attr_filter)]

    # Apply regex attribute filters
    if attribute_regex_filters:
        for attr_regex in attribute_regex_filters:
            result = [item for item in result if matches_attribute_regex(item, attr_regex)]

    return result


# =============================================================================
# Name/Text Filtering
# =============================================================================

def matches_name_regex(item: Dict, pattern: str) -> bool:
    """
    Check if an item's name matches a regex pattern.

    Args:
        item: Item dictionary with 'name' field
        pattern: Regex pattern string

    Returns:
        True if name matches, False otherwise

    Examples:
        >>> item = {'name': 'test_login_success'}
        >>> matches_name_regex(item, r'test_.*_success')
        True
        >>> matches_name_regex(item, r'^login')
        False
    """
    try:
        compiled_pattern = re.compile(pattern)
        return compiled_pattern.search(item.get('name', '')) is not None
    except re.error:
        return False


def filter_by_name_regex(items: List[Dict], pattern: str) -> List[Dict]:
    """
    Filter items by name using regex pattern.

    Args:
        items: List of items to filter
        pattern: Regex pattern string

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'name': 'test_api_login'},
        ...     {'name': 'test_ui_login'},
        ...     {'name': 'test_api_logout'}
        ... ]
        >>> filter_by_name_regex(items, r'test_api_.*')
        [{'name': 'test_api_login'}, {'name': 'test_api_logout'}]
    """
    try:
        compiled_pattern = re.compile(pattern)
        return [item for item in items if compiled_pattern.search(item.get('name', ''))]
    except re.error:
        return []


# =============================================================================
# Status Filtering
# =============================================================================

def filter_by_status(items: List[Dict], status: str) -> List[Dict]:
    """
    Filter items by status.

    Args:
        items: List of items to filter
        status: Status to filter by (e.g., 'PASSED', 'FAILED')

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'name': 'test1', 'status': 'PASSED'},
        ...     {'name': 'test2', 'status': 'FAILED'}
        ... ]
        >>> filter_by_status(items, 'FAILED')
        [{'name': 'test2', 'status': 'FAILED'}]
    """
    return [item for item in items if item.get('status') == status]


def filter_by_type(items: List[Dict], item_type: str) -> List[Dict]:
    """
    Filter items by type.

    Args:
        items: List of items to filter
        item_type: Type to filter by (e.g., 'STEP', 'SUITE', 'TEST')

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'name': 'Suite1', 'type': 'SUITE'},
        ...     {'name': 'test1', 'type': 'STEP'}
        ... ]
        >>> filter_by_type(items, 'STEP')
        [{'name': 'test1', 'type': 'STEP'}]
    """
    return [item for item in items if item.get('type') == item_type]


def exclude_type(items: List[Dict], item_type: str) -> List[Dict]:
    """
    Exclude items of a specific type.

    Args:
        items: List of items to filter
        item_type: Type to exclude (e.g., 'SUITE')

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'name': 'Suite1', 'type': 'SUITE'},
        ...     {'name': 'test1', 'type': 'STEP'}
        ... ]
        >>> exclude_type(items, 'SUITE')
        [{'name': 'test1', 'type': 'STEP'}]
    """
    return [item for item in items if item.get('type') != item_type]


# =============================================================================
# Data Extraction
# =============================================================================

def extract_launch_statistics(launch: Dict) -> Dict[str, int]:
    """
    Extract execution statistics from a launch.

    Args:
        launch: Launch dictionary

    Returns:
        Dictionary with execution statistics

    Examples:
        >>> launch = {
        ...     'statistics': {
        ...         'executions': {'total': 100, 'passed': 95, 'failed': 5}
        ...     }
        ... }
        >>> stats = extract_launch_statistics(launch)
        >>> stats['total']
        100
        >>> stats['passed']
        95
    """
    statistics = launch.get('statistics', {})
    executions = statistics.get('executions', {})
    defects = statistics.get('defects', {})

    return {
        'total': executions.get('total', 0),
        'passed': executions.get('passed', 0),
        'failed': executions.get('failed', 0),
        'skipped': executions.get('skipped', 0),
        'to_investigate': defects.get(DEFECT_TO_INVESTIGATE, {}).get('total', 0),
        'product_bug': defects.get(DEFECT_PRODUCT_BUG, {}).get('total', 0),
        'automation_bug': defects.get(DEFECT_AUTOMATION_BUG, {}).get('total', 0),
        'system_issue': defects.get(DEFECT_SYSTEM_ISSUE, {}).get('total', 0),
    }


def extract_item_duration(item: Dict) -> float:
    """
    Extract duration in seconds from a test item.

    Args:
        item: Test item dictionary

    Returns:
        Duration in seconds

    Examples:
        >>> item = {'startTime': 1000000, 'endTime': 1005000}
        >>> extract_item_duration(item)
        5.0
    """
    start_time = item.get('startTime', 0)
    end_time = item.get('endTime', 0)
    duration_ms = end_time - start_time
    return duration_ms / 1000.0 if duration_ms > 0 else 0


def extract_names(items: List[Dict]) -> List[str]:
    """
    Extract names from a list of items.

    Args:
        items: List of items

    Returns:
        List of names

    Examples:
        >>> items = [{'name': 'test1'}, {'name': 'test2'}]
        >>> extract_names(items)
        ['test1', 'test2']
    """
    return [item.get('name', '') for item in items]


def extract_ids(items: List[Dict]) -> List[str]:
    """
    Extract IDs from a list of items.

    Args:
        items: List of items

    Returns:
        List of IDs

    Examples:
        >>> items = [{'id': 'abc123'}, {'id': 'def456'}]
        >>> extract_ids(items)
        ['abc123', 'def456']
    """
    return [item.get('id', '') for item in items]


# =============================================================================
# Grouping and Aggregation
# =============================================================================

def group_by_status(items: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group items by their status.

    Args:
        items: List of items

    Returns:
        Dictionary mapping status to list of items

    Examples:
        >>> items = [
        ...     {'name': 'test1', 'status': 'PASSED'},
        ...     {'name': 'test2', 'status': 'FAILED'},
        ...     {'name': 'test3', 'status': 'PASSED'}
        ... ]
        >>> grouped = group_by_status(items)
        >>> len(grouped['PASSED'])
        2
    """
    result = {}
    for item in items:
        status = item.get('status', 'UNKNOWN')
        if status not in result:
            result[status] = []
        result[status].append(item)
    return result


def count_by_status(items: List[Dict]) -> Dict[str, int]:
    """
    Count items by status.

    Args:
        items: List of items

    Returns:
        Dictionary mapping status to count

    Examples:
        >>> items = [
        ...     {'status': 'PASSED'},
        ...     {'status': 'FAILED'},
        ...     {'status': 'PASSED'}
        ... ]
        >>> count_by_status(items)
        {'PASSED': 2, 'FAILED': 1}
    """
    result = {}
    for item in items:
        status = item.get('status', 'UNKNOWN')
        result[status] = result.get(status, 0) + 1
    return result


def group_by_attribute(items: List[Dict], attribute_key: str) -> Dict[str, List[Dict]]:
    """
    Group items by a specific attribute key.

    Args:
        items: List of items
        attribute_key: The attribute key to group by

    Returns:
        Dictionary mapping attribute value to list of items

    Examples:
        >>> items = [
        ...     {'attributes': [{'key': 'browser', 'value': 'chrome'}]},
        ...     {'attributes': [{'key': 'browser', 'value': 'firefox'}]},
        ...     {'attributes': [{'key': 'browser', 'value': 'chrome'}]}
        ... ]
        >>> grouped = group_by_attribute(items, 'browser')
        >>> len(grouped['chrome'])
        2
    """
    result = {}
    for item in items:
        attributes = item.get('attributes', [])
        for attr in attributes:
            if attr.get('key') == attribute_key:
                value = attr.get('value', 'unknown')
                if value not in result:
                    result[value] = []
                result[value].append(item)
                break
    return result


# =============================================================================
# Formatting Utilities
# =============================================================================

def format_attributes(attributes: List[Dict], separator: str = ', ') -> str:
    """
    Format attributes as a string.

    Args:
        attributes: List of attribute dictionaries
        separator: Separator between attributes

    Returns:
        Formatted string

    Examples:
        >>> attrs = [
        ...     {'key': 'browser', 'value': 'chrome'},
        ...     {'key': 'env', 'value': 'prod'}
        ... ]
        >>> format_attributes(attrs)
        'browser:chrome, env:prod'
    """
    if not attributes:
        return "-"

    formatted = []
    for attr in attributes:
        key = attr.get('key')
        value = attr.get('value', '')
        formatted.append(f"{key}:{value}" if key else value)

    return separator.join(formatted) if formatted else "-"


def format_defect_type(issue_type: Any, abbrev_length: int = 2) -> str:
    """
    Format defect type into short abbreviation.

    Args:
        issue_type: Issue type string
        abbrev_length: Length of abbreviation

    Returns:
        Abbreviated defect type

    Examples:
        >>> format_defect_type('project_issue$pb001')
        'PB'
        >>> format_defect_type('to_investigate$ti001')
        'TI'
    """
    if isinstance(issue_type, str) and issue_type not in ('-', 'N/A'):
        if '$' in issue_type:
            return issue_type.split('$')[-1][:abbrev_length].upper()
        return issue_type[:abbrev_length].upper()
    return '-'


def format_duration(duration_seconds: float, precision: int = 2) -> str:
    """
    Format duration in seconds as a string.

    Args:
        duration_seconds: Duration in seconds
        precision: Number of decimal places

    Returns:
        Formatted duration string

    Examples:
        >>> format_duration(1.234)
        '1.23s'
        >>> format_duration(0.1, precision=3)
        '0.100s'
    """
    return f"{duration_seconds:.{precision}f}s"


# =============================================================================
# Composite Filtering
# =============================================================================

def apply_filters(items: List[Dict],
                 name_regex: Optional[str] = None,
                 status: Optional[str] = None,
                 item_type: Optional[str] = None,
                 exclude_types: Optional[List[str]] = None,
                 attribute_filters: Optional[List[str]] = None,
                 attribute_regex_filters: Optional[List[str]] = None,
                 custom_filter: Optional[Callable[[Dict], bool]] = None) -> List[Dict]:
    """
    Apply multiple filters to items.

    All filters are applied with AND logic.

    Args:
        items: List of items to filter
        name_regex: Regex pattern for name filtering
        status: Status to filter by
        item_type: Type to filter by
        exclude_types: Types to exclude
        attribute_filters: List of exact attribute filters
        attribute_regex_filters: List of regex attribute filters
        custom_filter: Custom filter function

    Returns:
        Filtered list of items

    Examples:
        >>> items = [
        ...     {'name': 'test_api', 'status': 'FAILED', 'type': 'STEP'},
        ...     {'name': 'test_ui', 'status': 'PASSED', 'type': 'STEP'}
        ... ]
        >>> filtered = apply_filters(items, status='FAILED', name_regex='test_.*')
        >>> len(filtered)
        1
    """
    result = items

    # Name regex filter
    if name_regex:
        result = filter_by_name_regex(result, name_regex)

    # Status filter
    if status:
        result = filter_by_status(result, status)

    # Type filter
    if item_type:
        result = filter_by_type(result, item_type)

    # Exclude types
    if exclude_types:
        for excluded_type in exclude_types:
            result = exclude_type(result, excluded_type)

    # Attribute filters
    if attribute_filters or attribute_regex_filters:
        result = filter_by_attributes(result, attribute_filters, attribute_regex_filters)

    # Custom filter
    if custom_filter:
        result = [item for item in result if custom_filter(item)]

    return result
