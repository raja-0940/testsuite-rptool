"""
ReportPortal Auto Analysis Trigger - Core Implementation

This module handles triggering auto-analysis for ReportPortal launches that have
items marked for investigation.
"""

from typing import List, Dict, Optional
from loguru import logger

from .reportportal_client_wrapper import AutoAnalysisTrigger
from .rp_api_client import ReportPortalAPIClient




def trigger_auto_analysis(launch_id: str, client: ReportPortalAPIClient) -> bool:
    """
    Trigger auto-analysis in ReportPortal on a specific launch.

    Args:
        launch_id: UUID of the launch to analyze
        client: ReportPortal API client instance

    Returns:
        bool: True if request was successful, False otherwise
    """
    try:
        return client.trigger_analysis(launch_id)
    except Exception as e:
        logger.error(f"Failed to trigger analysis: {e}")
        return False


def get_launches(client: ReportPortalAPIClient) -> Optional[List[Dict]]:
    """
    Get launches that have items to investigate.

    Args:
        client: ReportPortal API client instance

    Returns:
        List of launch dictionaries or None if request failed
    """
    logger.debug("Fetching launches with items to investigate")

    # Filter for launches with items to investigate
    filters = {
        'filter.gt.statistics$defects$to_investigate$ti001': '0'
    }

    try:
        return client.get_launches(filters=filters)
    except Exception as e:
        logger.error(f"Failed to fetch launches: {e}")
        return None


def process_launches(launches: List[Dict], client: ReportPortalAPIClient) -> int:
    """
    Process launches and trigger auto-analysis where needed.

    Args:
        launches: List of launch dictionaries
        client: ReportPortal API client instance

    Returns:
        Number of launches processed successfully
    """
    triggered_count = 0

    for launch in launches:
        try:
            launch_id = launch['id']
            statistics = launch.get('statistics', {})

            defects = statistics.get('defects', {})
            to_investigate = defects.get('to_investigate', {}).get('total', 0)

            logger.info(f'Launch {launch_id}: {to_investigate} items to investigate')

            if to_investigate > 0:
                logger.info(f'Triggering auto-analysis for launch {launch_id}')
                if trigger_auto_analysis(launch_id, client):
                    triggered_count += 1
            else:
                logger.debug(f'Launch {launch_id}: no items to investigate, skipping')

        except KeyError as e:
            logger.error(f'Error processing launch {launch.get("id", "unknown")}: missing key {e}')
        except Exception as e:
            logger.error(f'Unexpected error processing launch {launch.get("id", "unknown")}: {e}')

    return triggered_count


def run_auto_trigger(options) -> int:
    """
    Main function to run the auto-trigger process.

    Args:
        options: Parsed command line options

    Returns:
        Exit code (0 for success, 1 for failure)
    """

    logger.info(f"Starting auto-trigger script with log level: {options.log_level}")
    logger.debug(f"ReportPortal URL: {options.rp_url}")
    logger.debug(f"ReportPortal project: {options.rp_project}")

    # Create API client
    client = ReportPortalAPIClient(
        url=options.rp_url,
        project=options.rp_project,
        token=options.rp_token
    )

    launches = get_launches(client)
    if launches is None:
        logger.error("Failed to retrieve launches")
        return 1

    if not launches:
        logger.info("No launches found with items to investigate")
        return 0

    logger.info(f"Found {len(launches)} launches with items to investigate")
    triggered_count = process_launches(launches, client)

    logger.info(f"Summary: Triggered auto-analysis on {triggered_count}/{len(launches)} launches")

    if triggered_count == len(launches):
        logger.info("All launches processed successfully")
    elif triggered_count > 0:
        logger.warning(f"Only {triggered_count} out of {len(launches)} launches processed successfully")
    else:
        logger.error("No launches were processed successfully")
        return 1

    return 0