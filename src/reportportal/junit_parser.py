"""
JUnit XML parsing utilities for ReportPortal integration.

This module provides classes and functions for parsing JUnit XML files
and extracting test results with their properties.
"""

from junitparser import JUnitXml, Element, Attr, Failure, Skipped, Error
from typing import List, Dict, Optional, Generator
import datetime
from loguru import logger


class PropertiesElement(Element):
    """Enables junitparser to support properties in testcase elements."""
    _tag = "properties"


class PropertyElement(Element):
    """Enables junitparser to support individual property elements."""
    _tag = "property"
    name = Attr()
    value = Attr()


def timestamp_junit_to_rp(iso_timestamp: str) -> int:
    """
    Convert jUnit timestamp to ReportPortal timestamp format.
    
    ReportPortal expects unix time in milliseconds as integer.
    
    Args:
        iso_timestamp: ISO format timestamp from jUnit XML
        
    Returns:
        Unix timestamp in milliseconds
        
    References:
        https://github.com/reportportal/client-Python/blob/develop/reportportal_client/helpers/common_helpers.py#L282
    """
    dt = datetime.datetime.fromisoformat(iso_timestamp)
    unix_ts = dt.timestamp()
    return int(unix_ts * 1000)


def timestamp_rp_to_junit(rp_timestamp: int|str|float) -> str:
    """
    Convert ReportPortal timestamp to jUnit timestamp format.

    ReportPortal uses unix time in milliseconds as integer.
    JUnit expects ISO format timestamp string.

    Args:
        rp_timestamp: Unix timestamp in milliseconds

    Returns:
        ISO format timestamp string
    """
    try:
        rp_timestamp = float(rp_timestamp)
    
        unix_ts_seconds = rp_timestamp / 1000
        dt = datetime.datetime.fromtimestamp(unix_ts_seconds, tz=datetime.timezone.utc)
        return dt.isoformat()
    except:
        return rp_timestamp


def extract_suite_properties(suite) -> List[Dict[str, str]]:
    """
    Extract properties from a JUnit test suite in ReportPortal format.
    
    Args:
        suite: JUnit test suite object
        
    Returns:
        List of property dictionaries with 'key' and 'value' keys
    """
    if not hasattr(suite, 'properties') or not suite.properties():
        return []
    
    return [{"key": p.name, "value": p.value} for p in suite.properties()]


def extract_case_properties(case) -> List[Dict[str, str]]:
    """
    Extract properties from a JUnit test case in ReportPortal format.
    
    Args:
        case: JUnit test case object
        
    Returns:
        List of property dictionaries with 'key' and 'value' keys
    """
    c_properties = case.child(PropertiesElement)
    if not c_properties:
        return []
        
    return [
        {"key": p.name, "value": p.value}
        for p in c_properties.iterchildren(PropertyElement)
    ]


def convert_test_case_name(classname: str, enable_conversion: bool = True) -> str:
    """
    Convert jUnit classname to pytest-style test case name.
    
    Args:
        classname: Original classname from jUnit XML
        enable_conversion: Whether to apply pytest-style conversion
        
    Returns:
        Converted test class name
    """
    if not enable_conversion:
        return classname
        
    return f'{classname.replace(".", "/")}.py'


def determine_test_status(case) -> str:
    """
    Determine the test status based on jUnit test case state.
    
    Args:
        case: JUnit test case object
        
    Returns:
        Status string: "PASSED", "FAILED", "ERROR", or "SKIPPED"
    """
    if case.is_error:
        return "ERROR"
    elif case.is_failure:
        return "FAILED"
    elif case.is_skipped:
        return "SKIPPED"
    else:
        return "PASSED"


class JUnitParser:
    """
    High-level JUnit XML parser for ReportPortal integration.
    
    This class provides methods to parse JUnit XML files and extract
    all necessary information for ReportPortal reporting.
    """
    
    def __init__(self, file_paths: list[str], enable_name_conversion: bool = True):
        """
        Initialize the parser.
        
        Args:
            file_path: Path to the JUnit XML file
            enable_name_conversion: Enable pytest-style name conversion
        """
        self.file_paths = file_paths
        self.enable_name_conversion = enable_name_conversion
        
    def parse_suites(self) -> Generator[Dict, None, None]:
        """
        Parse all test suites from the JUnit XML file.
        
        Yields:
            Dictionary containing suite information and test cases
        """
        logger.info(f"Parsing JUnit XML files: {self.file_paths}")
        
        try:
            logger.debug(f"Merging JUnit XML files")

            junit_xml = JUnitXml()

            for file_path in self.file_paths:
                logger.debug(f"merging: {file_path}")
                i_junit_xml = JUnitXml.fromfile(file_path)
                junit_xml += i_junit_xml

            # debugging output of merged xml
            # TODO: maybe add option
            # junit_xml.write('tmp_merged_junit.xml')

        except Exception as e:
            logger.error(f"Failed to parse JUnit XML file {file_path}: {e}")
            raise
            
        for suite in junit_xml:
            logger.debug(f"Processing suite: {suite.name}")
            
            suite_data = {
                'name': suite.name,
                'time': suite.time,
                'hostname': suite.hostname,
                'timestamp': timestamp_junit_to_rp(suite.timestamp),
                'properties': extract_suite_properties(suite),
                'test_cases': list(self._parse_test_cases(suite))
            }
            
            logger.debug(f"Suite {suite.name} contains {len(suite_data['test_cases'])} test cases")
            yield suite_data
    
    def _parse_test_cases(self, suite) -> Generator[Dict, None, None]:
        """
        Parse all test cases from a test suite.
        
        Args:
            suite: JUnit test suite object
            
        Yields:
            Dictionary containing test case information
        """
        for case in suite:
            logger.debug(f"Processing test case: {case.name}")
            
            case_data = {
                'name': case.name,
                'classname': case.classname,
                'converted_classname': convert_test_case_name(
                    case.classname, 
                    self.enable_name_conversion
                ),
                'time': int(float(case.time) * 1000),  # Convert to milliseconds
                'status': determine_test_status(case),
                'properties': extract_case_properties(case),
                'system_out': case.system_out,
                'system_err': case.system_err,
                'failures': [failure.text for failure in case.iterchildren(Failure)],
                'errors': [error.text for error in case.iterchildren(Error)],
                'skipped': [skip.text for skip in case.iterchildren(Skipped)]
            }
            
            yield case_data


def get_launch_name_from_file(file_path: str, custom_name: Optional[str] = None) -> str:
    """
    Generate a launch name from the file path or use custom name.
    
    Args:
        file_path: Path to the JUnit XML file
        custom_name: Custom launch name (takes precedence)
        
    Returns:
        Launch name for ReportPortal
    """
    if custom_name:
        return custom_name
        
    # Extract filename and clean it up for display
    import os
    filename = os.path.basename(file_path)
    return filename.replace('.xml', '').replace('_', ' ')