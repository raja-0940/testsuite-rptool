"""
ReportPortal Release Summary Tool - Core Implementation

This module generates comprehensive release testing summaries for specific SUT versions.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import json
import csv
import sys
from tabulate import tabulate
from argparse import Namespace
from collections import defaultdict

from .rp_api_client import ReportPortalAPIClient
from . import rp_query_utils as utils


# =============================================================================
# Data Fetching
# =============================================================================

def fetch_filtered_launches(
    client: ReportPortalAPIClient,
    options: Namespace
) -> Optional[List[Dict]]:
    """
    Fetch all launches matching the specified attributes.

    Args:
        client: ReportPortal API client instance
        options: Parsed command line options

    Returns:
        List of launch dictionaries or None if request failed
    """
    logger.info(f"Fetching launches with attributes: {', '.join(options.attribute)}")

    # Get recent launches
    try:
        all_launches = client.get_launches(sort_by='startTime,DESC')
    except Exception as e:
        logger.error(f"Failed to fetch launches: {e}")
        return None

    if not all_launches:
        logger.warning("No launches found")
        return []

    # Filter by attributes (AND logic - must match all specified attributes)
    filtered_launches = utils.filter_by_attributes(
        all_launches,
        attribute_filters=options.attribute
    )

    # Filter by days if specified
    if options.days:
        cutoff_time = datetime.now() - timedelta(days=options.days)
        cutoff_ms = int(cutoff_time.timestamp() * 1000)

        filtered_launches = [
            launch for launch in filtered_launches
            if launch.get('startTime', 0) >= cutoff_ms
        ]

    logger.info(f"Found {len(filtered_launches)} launches matching criteria")
    return filtered_launches


def fetch_launch_test_items(
    launch_id: str,
    client: ReportPortalAPIClient
) -> Optional[List[Dict]]:
    """
    Fetch test items for a specific launch.

    Args:
        launch_id: Launch ID to fetch items for
        client: ReportPortal API client instance

    Returns:
        List of test item dictionaries or None if request failed
    """
    try:
        return client.get_test_items(launch_id)
    except Exception as e:
        logger.error(f"Failed to fetch test items for launch {launch_id}: {e}")
        return None


# =============================================================================
# Statistics Aggregation
# =============================================================================

def aggregate_launch_statistics(launches: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate statistics across multiple launches.

    Args:
        launches: List of launch dictionaries

    Returns:
        Dictionary containing aggregated statistics
    """
    stats = {
        'total_launches': len(launches),
        'passed_launches': 0,
        'failed_launches': 0,
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'total_duration_ms': 0,
        'defects': defaultdict(int),
        'earliest_launch': None,
        'latest_launch': None,
    }

    for launch in launches:
        # Launch status
        if launch.get('status') == 'PASSED':
            stats['passed_launches'] += 1
        else:
            stats['failed_launches'] += 1

        # Test execution statistics
        executions = launch.get('statistics', {}).get('executions', {})
        stats['total_tests'] += executions.get('total', 0)
        stats['passed_tests'] += executions.get('passed', 0)
        stats['failed_tests'] += executions.get('failed', 0)
        stats['skipped_tests'] += executions.get('skipped', 0)

        # Defect statistics
        defects = launch.get('statistics', {}).get('defects', {})
        for defect_type, defect_data in defects.items():
            stats['defects'][defect_type] += defect_data.get('total', 0)

        # Duration
        start_time = launch.get('startTime', 0)
        end_time = launch.get('endTime', 0)
        if start_time and end_time:
            stats['total_duration_ms'] += (end_time - start_time)

        # Time range
        if start_time:
            if stats['earliest_launch'] is None or start_time < stats['earliest_launch']:
                stats['earliest_launch'] = start_time
            if stats['latest_launch'] is None or start_time > stats['latest_launch']:
                stats['latest_launch'] = start_time

    # Calculate pass rate
    if stats['total_tests'] > 0:
        stats['pass_rate'] = (stats['passed_tests'] / stats['total_tests']) * 100
    else:
        stats['pass_rate'] = 0.0

    return stats


def group_launches_by_attribute(
    launches: List[Dict],
    attribute_key: str
) -> Dict[str, List[Dict]]:
    """
    Group launches by a specific attribute value.

    Args:
        launches: List of launch dictionaries
        attribute_key: Attribute key to group by

    Returns:
        Dictionary mapping attribute values to lists of launches
    """
    grouped = defaultdict(list)

    for launch in launches:
        attributes = launch.get('attributes', [])
        # Find attribute value
        value = None
        for attr in attributes:
            if attr.get('key') == attribute_key:
                value = attr.get('value', 'Unknown')
                break

        if value is None:
            value = 'No ' + attribute_key

        grouped[value].append(launch)

    return dict(grouped)


def analyze_test_coverage(
    launches: List[Dict],
    client: ReportPortalAPIClient,
    options: Namespace
) -> Dict[str, Any]:
    """
    Analyze test coverage by fetching test items for all launches.

    Args:
        launches: List of launch dictionaries
        client: ReportPortal API client instance
        options: Command line options

    Returns:
        Dictionary containing coverage analysis
    """
    all_test_names = set()
    test_results = defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0})

    for launch in launches:
        launch_id = launch.get('id')
        if not launch_id:
            continue

        test_items = fetch_launch_test_items(launch_id, client)
        if not test_items:
            continue

        # Filter to STEP items only
        steps = utils.filter_by_type(test_items, 'STEP')

        for item in steps:
            name = item.get('name', 'Unknown')
            all_test_names.add(name)

            status = item.get('status', 'UNKNOWN')
            test_results[name]['total'] += 1

            if status == 'PASSED':
                test_results[name]['passed'] += 1
            elif status == 'FAILED':
                test_results[name]['failed'] += 1
            elif status == 'SKIPPED':
                test_results[name]['skipped'] += 1

    return {
        'unique_tests': len(all_test_names),
        'test_results': dict(test_results),
        'all_test_names': sorted(all_test_names)
    }


# =============================================================================
# Output Formatting
# =============================================================================

def format_timestamp(timestamp_ms: Optional[int]) -> str:
    """Format timestamp in milliseconds to readable string."""
    if timestamp_ms is None:
        return "N/A"
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_duration(duration_ms: int) -> str:
    """Format duration in milliseconds to readable string."""
    if duration_ms <= 0:
        return "0s"

    seconds = duration_ms / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_report_title(options: Namespace) -> str:
    """
    Generate report title from options.

    Args:
        options: Command line options

    Returns:
        Report title string
    """
    if options.report_title:
        return options.report_title

    # Generate title from attributes
    attr_parts = []
    for attr in options.attribute:
        if ':' in attr:
            key, value = attr.split(':', 1)
            attr_parts.append(f"{key.upper()}: {value}")
        else:
            attr_parts.append(attr)

    return " | ".join(attr_parts)


def display_summary_text(
    stats: Dict[str, Any],
    options: Namespace,
    launches: List[Dict]
) -> None:
    """
    Display release summary in text format.

    Args:
        stats: Aggregated statistics
        options: Command line options
        launches: List of launches
    """
    title = get_report_title(options)
    print("\n" + "=" * 80)
    print(f"RELEASE TESTING SUMMARY - {title}")
    print("=" * 80)

    # Overview
    print("\n📊 OVERVIEW")
    print("-" * 80)
    overview_data = [
        ["Total Launches", stats['total_launches']],
        ["Passed Launches", f"{stats['passed_launches']} ({stats['passed_launches']/stats['total_launches']*100:.1f}%)" if stats['total_launches'] > 0 else "0"],
        ["Failed Launches", f"{stats['failed_launches']} ({stats['failed_launches']/stats['total_launches']*100:.1f}%)" if stats['total_launches'] > 0 else "0"],
        ["Time Period", f"{format_timestamp(stats['earliest_launch'])} to {format_timestamp(stats['latest_launch'])}"],
        ["Total Duration", format_duration(stats['total_duration_ms'])],
    ]
    print(tabulate(overview_data, tablefmt='simple'))

    # Test Results
    print("\n✅ TEST EXECUTION RESULTS")
    print("-" * 80)
    test_data = [
        ["Total Tests", stats['total_tests']],
        ["Passed", f"{stats['passed_tests']} ({stats['pass_rate']:.1f}%)"],
        ["Failed", f"{stats['failed_tests']} ({stats['failed_tests']/stats['total_tests']*100:.1f}%)" if stats['total_tests'] > 0 else "0"],
        ["Skipped", f"{stats['skipped_tests']} ({stats['skipped_tests']/stats['total_tests']*100:.1f}%)" if stats['total_tests'] > 0 else "0"],
    ]
    print(tabulate(test_data, tablefmt='simple'))

    # Defects
    if stats['defects']:
        print("\n🐛 DEFECT BREAKDOWN")
        print("-" * 80)
        defect_data = []
        for defect_type, count in sorted(stats['defects'].items()):
            defect_name = utils.format_defect_type(defect_type)
            percentage = (count / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
            defect_data.append([defect_name, count, f"{percentage:.1f}%"])
        print(tabulate(defect_data, headers=['Defect Type', 'Count', 'Percentage'], tablefmt='simple'))

    # Detailed launch breakdown
    if options.show_details:
        print("\n📋 LAUNCH DETAILS")
        print("-" * 80)
        launch_details = []
        for launch in sorted(launches, key=lambda x: x.get('startTime', 0), reverse=True):
            executions = launch.get('statistics', {}).get('executions', {})
            launch_details.append([
                launch.get('number', 'N/A'),
                launch.get('name', 'Unknown'),
                launch.get('status', 'Unknown'),
                executions.get('total', 0),
                executions.get('passed', 0),
                executions.get('failed', 0),
                format_timestamp(launch.get('startTime'))
            ])
        print(tabulate(
            launch_details,
            headers=['#', 'Name', 'Status', 'Total', 'Passed', 'Failed', 'Start Time'],
            tablefmt='grid'
        ))

    print("\n" + "=" * 80 + "\n")


def display_grouped_summary(
    launches: List[Dict],
    group_by: str,
    options: Namespace
) -> None:
    """
    Display summary grouped by attribute.

    Args:
        launches: List of launches
        group_by: Attribute key to group by
        options: Command line options
    """
    grouped = group_launches_by_attribute(launches, group_by)

    print(f"\n📊 SUMMARY GROUPED BY: {group_by.upper()}")
    print("=" * 80)

    group_data = []
    for group_value, group_launches in sorted(grouped.items()):
        stats = aggregate_launch_statistics(group_launches)
        group_data.append([
            group_value,
            len(group_launches),
            stats['total_tests'],
            stats['passed_tests'],
            stats['failed_tests'],
            f"{stats['pass_rate']:.1f}%"
        ])

    print(tabulate(
        group_data,
        headers=[group_by.title(), 'Launches', 'Total Tests', 'Passed', 'Failed', 'Pass Rate'],
        tablefmt='grid'
    ))
    print()


def display_summary_json(
    stats: Dict[str, Any],
    options: Namespace,
    launches: List[Dict]
) -> None:
    """
    Display release summary in JSON format.

    Args:
        stats: Aggregated statistics
        options: Command line options
        launches: List of launches
    """
    # Parse attributes into a dictionary
    attributes = {}
    for attr in options.attribute:
        if ':' in attr:
            key, value = attr.split(':', 1)
            attributes[key] = value
        else:
            attributes['filter'] = attr

    output = {
        'title': get_report_title(options),
        'attributes': attributes,
        'summary': {
            'total_launches': stats['total_launches'],
            'passed_launches': stats['passed_launches'],
            'failed_launches': stats['failed_launches'],
            'total_tests': stats['total_tests'],
            'passed_tests': stats['passed_tests'],
            'failed_tests': stats['failed_tests'],
            'skipped_tests': stats['skipped_tests'],
            'pass_rate': round(stats['pass_rate'], 2),
            'total_duration_seconds': stats['total_duration_ms'] / 1000,
            'earliest_launch': format_timestamp(stats['earliest_launch']),
            'latest_launch': format_timestamp(stats['latest_launch']),
        },
        'defects': dict(stats['defects']),
    }

    if options.show_details:
        output['launches'] = [
            {
                'id': launch.get('id'),
                'number': launch.get('number'),
                'name': launch.get('name'),
                'status': launch.get('status'),
                'statistics': launch.get('statistics'),
                'startTime': format_timestamp(launch.get('startTime')),
                'endTime': format_timestamp(launch.get('endTime')),
            }
            for launch in launches
        ]

    print(json.dumps(output, indent=2))


def display_summary_csv(
    stats: Dict[str, Any],
    options: Namespace,
    launches: List[Dict]
) -> None:
    """
    Display release summary in CSV format.

    Args:
        stats: Aggregated statistics
        options: Command line options
        launches: List of launches
    """
    writer = csv.writer(sys.stdout)

    # Summary section
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Report Title', get_report_title(options)])

    # Write filter attributes
    for attr in options.attribute:
        if ':' in attr:
            key, value = attr.split(':', 1)
            writer.writerow([f'Filter: {key}', value])
        else:
            writer.writerow(['Filter', attr])
    writer.writerow(['Total Launches', stats['total_launches']])
    writer.writerow(['Passed Launches', stats['passed_launches']])
    writer.writerow(['Failed Launches', stats['failed_launches']])
    writer.writerow(['Total Tests', stats['total_tests']])
    writer.writerow(['Passed Tests', stats['passed_tests']])
    writer.writerow(['Failed Tests', stats['failed_tests']])
    writer.writerow(['Skipped Tests', stats['skipped_tests']])
    writer.writerow(['Pass Rate %', f"{stats['pass_rate']:.2f}"])
    writer.writerow([])

    # Launch details if requested
    if options.show_details:
        writer.writerow(['Launch Number', 'Name', 'Status', 'Total Tests', 'Passed', 'Failed', 'Skipped', 'Start Time'])
        for launch in launches:
            executions = launch.get('statistics', {}).get('executions', {})
            writer.writerow([
                launch.get('number'),
                launch.get('name'),
                launch.get('status'),
                executions.get('total', 0),
                executions.get('passed', 0),
                executions.get('failed', 0),
                executions.get('skipped', 0),
                format_timestamp(launch.get('startTime'))
            ])


# =============================================================================
# Main Execution
# =============================================================================

def run_release_summary(options: Namespace) -> int:
    """
    Main execution function for release summary generation.

    Args:
        options: Parsed command line options

    Returns:
        Exit code (0 for success, 1 for error)
    """

    try:
        logger.warning("This is experimental feature, and subject to an active development.")
        # Create API client
        client = ReportPortalAPIClient(
            url=options.rp_url,
            project=options.rp_project,
            token=options.rp_token
        )

        # Fetch launches matching the specified attributes
        launches = fetch_filtered_launches(client, options)

        if not launches:
            logger.error(f"No launches found matching attributes: {', '.join(options.attribute)}")
            return 1

        # Aggregate statistics
        stats = aggregate_launch_statistics(launches)

        # Display summary based on output format
        if options.output_format == 'json':
            display_summary_json(stats, options, launches)
        elif options.output_format == 'csv':
            display_summary_csv(stats, options, launches)
        else:  # text
            display_summary_text(stats, options, launches)

            # Display grouped summary if requested
            if options.group_by:
                display_grouped_summary(launches, options.group_by, options)

        return 0

    except Exception as e:
        logger.error(f"Error generating release summary: {e}", exc_info=True)
        return 1
