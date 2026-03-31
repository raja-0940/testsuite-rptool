"""
Unit tests for junit_parser module.
"""

import pytest
import datetime
from unittest.mock import patch, Mock

from reportportal.junit_parser import (
    JUnitParser,
    timestamp_junit_to_rp,
    extract_suite_properties,
    extract_case_properties,
    convert_test_case_name,
    determine_test_status,
    get_launch_name_from_file
)


@pytest.mark.unit
class TestTimestampConversion:
    """Test timestamp conversion functions."""
    
    def test_timestamp_junit_to_rp(self):
        """Test JUnit to ReportPortal timestamp conversion."""
        # Test ISO timestamp conversion
        iso_timestamp = "2024-01-01T12:00:00"
        rp_timestamp = timestamp_junit_to_rp(iso_timestamp)
        
        # Should return milliseconds since epoch
        assert isinstance(rp_timestamp, int)
        assert rp_timestamp > 0
        
        # Verify the actual conversion
        dt = datetime.datetime.fromisoformat(iso_timestamp)
        expected = int(dt.timestamp() * 1000)
        assert rp_timestamp == expected
    
    def test_timestamp_with_microseconds(self):
        """Test timestamp conversion with microseconds."""
        iso_timestamp = "2024-01-01T12:00:00.123456"
        rp_timestamp = timestamp_junit_to_rp(iso_timestamp)
        
        dt = datetime.datetime.fromisoformat(iso_timestamp)
        expected = int(dt.timestamp() * 1000)
        assert rp_timestamp == expected


@pytest.mark.unit
class TestPropertyExtraction:
    """Test property extraction functions."""
    
    def test_extract_suite_properties(self):
        """Test suite property extraction."""
        # Mock suite object
        mock_property = Mock()
        mock_property.name = "platform"
        mock_property.value = "aws"
        
        mock_suite = Mock()
        mock_suite.properties.return_value = [mock_property]
        
        properties = extract_suite_properties(mock_suite)
        
        assert len(properties) == 1
        assert properties[0] == {"key": "platform", "value": "aws"}
    
    def test_extract_suite_properties_no_properties(self):
        """Test suite property extraction with no properties."""
        mock_suite = Mock()
        mock_suite.properties.return_value = []
        
        properties = extract_suite_properties(mock_suite)
        assert properties == []
    
    def test_extract_suite_properties_missing_attr(self):
        """Test suite property extraction with missing properties attribute."""
        mock_suite = Mock()
        del mock_suite.properties  # Remove the properties method
        
        properties = extract_suite_properties(mock_suite)
        assert properties == []
    
    def test_extract_case_properties(self):
        """Test test case property extraction."""
        # Mock property element
        mock_property = Mock()
        mock_property.name = "color"
        mock_property.value = "green"
        
        # Mock properties element
        mock_properties_element = Mock()
        mock_properties_element.iterchildren.return_value = [mock_property]
        
        # Mock test case
        mock_case = Mock()
        mock_case.child.return_value = mock_properties_element
        
        properties = extract_case_properties(mock_case)
        
        assert len(properties) == 1
        assert properties[0] == {"key": "color", "value": "green"}
    
    def test_extract_case_properties_no_properties(self):
        """Test test case property extraction with no properties."""
        mock_case = Mock()
        mock_case.child.return_value = None
        
        properties = extract_case_properties(mock_case)
        assert properties == []


@pytest.mark.unit
class TestTestCaseNameConversion:
    """Test test case name conversion."""
    
    def test_convert_test_case_name_enabled(self):
        """Test test case name conversion when enabled."""
        classname = "test.module.TestClass"
        converted = convert_test_case_name(classname, enable_conversion=True)
        assert converted == "test/module/TestClass.py"
    
    def test_convert_test_case_name_disabled(self):
        """Test test case name conversion when disabled."""
        classname = "test.module.TestClass"
        converted = convert_test_case_name(classname, enable_conversion=False)
        assert converted == "test.module.TestClass"
    
    def test_convert_test_case_name_no_dots(self):
        """Test test case name conversion with no dots."""
        classname = "TestClass"
        converted = convert_test_case_name(classname, enable_conversion=True)
        assert converted == "TestClass.py"


@pytest.mark.unit
class TestStatusDetermination:
    """Test test status determination."""
    
    def test_determine_test_status_passed(self):
        """Test status determination for passed test."""
        mock_case = Mock()
        mock_case.is_error = False
        mock_case.is_failure = False
        mock_case.is_skipped = False
        
        status = determine_test_status(mock_case)
        assert status == "PASSED"
    
    def test_determine_test_status_error(self):
        """Test status determination for error test."""
        mock_case = Mock()
        mock_case.is_error = True
        mock_case.is_failure = False
        mock_case.is_skipped = False
        
        status = determine_test_status(mock_case)
        assert status == "ERROR"
    
    def test_determine_test_status_failure(self):
        """Test status determination for failed test."""
        mock_case = Mock()
        mock_case.is_error = False
        mock_case.is_failure = True
        mock_case.is_skipped = False
        
        status = determine_test_status(mock_case)
        assert status == "FAILED"
    
    def test_determine_test_status_skipped(self):
        """Test status determination for skipped test."""
        mock_case = Mock()
        mock_case.is_error = False
        mock_case.is_failure = False
        mock_case.is_skipped = True
        
        status = determine_test_status(mock_case)
        assert status == "SKIPPED"
    
    def test_determine_test_status_error_priority(self):
        """Test that error status takes priority over failure."""
        mock_case = Mock()
        mock_case.is_error = True
        mock_case.is_failure = True
        mock_case.is_skipped = False
        
        status = determine_test_status(mock_case)
        assert status == "ERROR"


@pytest.mark.unit
class TestLaunchNameGeneration:
    """Test launch name generation."""
    
    def test_get_launch_name_custom(self):
        """Test launch name with custom name provided."""
        file_path = "/path/to/junit_results.xml"
        custom_name = "Custom Launch Name"
        
        launch_name = get_launch_name_from_file(file_path, custom_name)
        assert launch_name == custom_name
    
    def test_get_launch_name_from_file(self):
        """Test launch name generation from file path."""
        file_path = "/path/to/junit_smoke_tests.xml"
        
        launch_name = get_launch_name_from_file(file_path, None)
        assert launch_name == "junit smoke tests"
    
    def test_get_launch_name_simple_file(self):
        """Test launch name from simple filename."""
        file_path = "results.xml"
        
        launch_name = get_launch_name_from_file(file_path, None)
        assert launch_name == "results"


@pytest.mark.unit
class TestJUnitParser:
    """Test JUnitParser class."""
    
    @patch('reportportal.junit_parser.JUnitXml.fromfile')
    def test_junit_parser_initialization(self, mock_fromfile):
        """Test JUnitParser initialization."""
        parser = JUnitParser(["/path/to/test.xml"], enable_name_conversion=True)
        
        assert parser.file_paths == ["/path/to/test.xml"]
        assert parser.enable_name_conversion is True
    
    @patch('reportportal.junit_parser.JUnitXml')
    @patch('reportportal.junit_parser.JUnitXml.fromfile')
    def test_parse_suites_success(self, mock_fromfile, mock_junitxml_class):
        """Test successful suite parsing."""
        # Mock suite object
        mock_suite = Mock()
        mock_suite.name = "test_suite"
        mock_suite.timestamp = "2024-01-01T12:00:00"

        # Mock case object
        mock_case = Mock()
        mock_case.name = "test_case"
        mock_case.classname = "test_module"
        mock_case.time = "1.0"
        mock_case.is_error = False
        mock_case.is_failure = False
        mock_case.is_skipped = False
        mock_case.system_out = "output"
        mock_case.system_err = None
        mock_case.iterchildren.return_value = []
        mock_case.child.return_value = None

        mock_suite.__iter__ = Mock(return_value=iter([mock_case]))
        mock_suite.properties.return_value = []

        # Mock the JUnit XML returned from file
        mock_junit_from_file = Mock()
        mock_junit_from_file.__iter__ = Mock(return_value=iter([mock_suite]))
        mock_fromfile.return_value = mock_junit_from_file

        # Mock the merged JUnit XML object
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter([mock_suite]))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Mock JUnitXml() constructor to return the merged object
        mock_junitxml_class.return_value = mock_merged_junit

        parser = JUnitParser(["/path/to/test.xml"])
        suites = list(parser.parse_suites())

        assert len(suites) == 1
        suite_data = suites[0]

        assert suite_data['name'] == "test_suite"
        assert 'timestamp' in suite_data
        assert 'properties' in suite_data
        assert 'test_cases' in suite_data
        assert len(suite_data['test_cases']) == 1

        case_data = suite_data['test_cases'][0]
        assert case_data['name'] == "test_case"
        assert case_data['classname'] == "test_module"
        assert case_data['converted_classname'] == "test_module.py"
        assert case_data['time'] == 1000  # Converted to milliseconds
        assert case_data['status'] == "PASSED"
    
    @patch('reportportal.junit_parser.JUnitXml.fromfile')
    def test_parse_suites_file_error(self, mock_fromfile):
        """Test suite parsing with file error."""
        mock_fromfile.side_effect = Exception("File not found")
        
        parser = JUnitParser(["/path/to/nonexistent.xml"])
        
        with pytest.raises(Exception, match="File not found"):
            list(parser.parse_suites())
    
    @patch('reportportal.junit_parser.JUnitXml')
    @patch('reportportal.junit_parser.JUnitXml.fromfile')
    def test_parse_suites_with_name_conversion_disabled(self, mock_fromfile, mock_junitxml_class):
        """Test suite parsing with name conversion disabled."""
        # Mock suite and case
        mock_case = Mock()
        mock_case.name = "test_case"
        mock_case.classname = "test.module.TestClass"
        mock_case.time = "0.5"
        mock_case.is_error = False
        mock_case.is_failure = False
        mock_case.is_skipped = False
        mock_case.system_out = None
        mock_case.system_err = None
        mock_case.iterchildren.return_value = []
        mock_case.child.return_value = None

        mock_suite = Mock()
        mock_suite.name = "test_suite"
        mock_suite.timestamp = "2024-01-01T12:00:00"
        mock_suite.__iter__ = Mock(return_value=iter([mock_case]))
        mock_suite.properties.return_value = []

        # Mock the JUnit XML returned from file
        mock_junit_from_file = Mock()
        mock_junit_from_file.__iter__ = Mock(return_value=iter([mock_suite]))
        mock_fromfile.return_value = mock_junit_from_file

        # Mock the merged JUnit XML object
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter([mock_suite]))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Mock JUnitXml() constructor to return the merged object
        mock_junitxml_class.return_value = mock_merged_junit

        parser = JUnitParser(["/path/to/test.xml"], enable_name_conversion=False)
        suites = list(parser.parse_suites())

        case_data = suites[0]['test_cases'][0]
        assert case_data['converted_classname'] == "test.module.TestClass"

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_multiple_files(self, mock_junitxml_class):
        """Test merging multiple JUnit XML files."""
        # Mock suite 1 from file 1
        mock_suite1 = Mock()
        mock_suite1.name = "test_suite_1"
        mock_suite1.timestamp = "2024-01-01T12:00:00"

        mock_case1 = Mock()
        mock_case1.name = "test_case_1"
        mock_case1.classname = "test_module_1"
        mock_case1.time = "1.0"
        mock_case1.is_error = False
        mock_case1.is_failure = False
        mock_case1.is_skipped = False
        mock_case1.system_out = None
        mock_case1.system_err = None
        mock_case1.iterchildren.return_value = []
        mock_case1.child.return_value = None

        mock_suite1.__iter__ = Mock(return_value=iter([mock_case1]))
        mock_suite1.properties.return_value = []

        # Mock suite 2 from file 2
        mock_suite2 = Mock()
        mock_suite2.name = "test_suite_2"
        mock_suite2.timestamp = "2024-01-01T13:00:00"

        mock_case2 = Mock()
        mock_case2.name = "test_case_2"
        mock_case2.classname = "test_module_2"
        mock_case2.time = "2.0"
        mock_case2.is_error = False
        mock_case2.is_failure = False
        mock_case2.is_skipped = False
        mock_case2.system_out = None
        mock_case2.system_err = None
        mock_case2.iterchildren.return_value = []
        mock_case2.child.return_value = None

        mock_suite2.__iter__ = Mock(return_value=iter([mock_case2]))
        mock_suite2.properties.return_value = []

        # Mock JUnit XML objects from files
        mock_junit_file1 = Mock()
        mock_junit_file1.__iter__ = Mock(return_value=iter([mock_suite1]))

        mock_junit_file2 = Mock()
        mock_junit_file2.__iter__ = Mock(return_value=iter([mock_suite2]))

        # Mock the merged JUnit XML object (contains both suites)
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter([mock_suite1, mock_suite2]))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Setup JUnitXml class mock
        # Constructor returns merged object
        mock_junitxml_class.return_value = mock_merged_junit
        # fromfile returns different objects for each file
        mock_junitxml_class.fromfile.side_effect = [mock_junit_file1, mock_junit_file2]

        parser = JUnitParser(["/path/to/test1.xml", "/path/to/test2.xml"])
        suites = list(parser.parse_suites())

        # Verify both suites are present
        assert len(suites) == 2

        # Verify first suite
        assert suites[0]['name'] == "test_suite_1"
        assert len(suites[0]['test_cases']) == 1
        assert suites[0]['test_cases'][0]['name'] == "test_case_1"
        assert suites[0]['test_cases'][0]['classname'] == "test_module_1"

        # Verify second suite
        assert suites[1]['name'] == "test_suite_2"
        assert len(suites[1]['test_cases']) == 1
        assert suites[1]['test_cases'][0]['name'] == "test_case_2"
        assert suites[1]['test_cases'][0]['classname'] == "test_module_2"

        # Verify fromfile was called for both files
        assert mock_junitxml_class.fromfile.call_count == 2
        mock_junitxml_class.fromfile.assert_any_call("/path/to/test1.xml")
        mock_junitxml_class.fromfile.assert_any_call("/path/to/test2.xml")

        # Verify merge operations occurred
        assert mock_merged_junit.__iadd__.call_count == 2

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_three_files(self, mock_junitxml_class):
        """Test merging three JUnit XML files with different test cases."""
        # Create mock suites for three files
        mock_suites = []
        mock_junit_files = []

        for i in range(3):
            # Create suite
            mock_suite = Mock()
            mock_suite.name = f"suite_{i+1}"
            mock_suite.timestamp = f"2024-01-0{i+1}T12:00:00"

            # Create case
            mock_case = Mock()
            mock_case.name = f"test_{i+1}"
            mock_case.classname = f"module_{i+1}"
            mock_case.time = f"{i+1}.0"
            mock_case.is_error = False
            mock_case.is_failure = (i == 1)  # Second test fails
            mock_case.is_skipped = False
            mock_case.system_out = f"output_{i+1}"
            mock_case.system_err = None
            mock_case.iterchildren.return_value = []
            mock_case.child.return_value = None

            mock_suite.__iter__ = Mock(return_value=iter([mock_case]))
            mock_suite.properties.return_value = []
            mock_suites.append(mock_suite)

            # Create file
            mock_junit_file = Mock()
            mock_junit_file.__iter__ = Mock(return_value=iter([mock_suite]))
            mock_junit_files.append(mock_junit_file)

        # Mock merged object with all suites
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter(mock_suites))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Setup JUnitXml class mock
        mock_junitxml_class.return_value = mock_merged_junit
        mock_junitxml_class.fromfile.side_effect = mock_junit_files

        parser = JUnitParser(["/path/file1.xml", "/path/file2.xml", "/path/file3.xml"])
        suites = list(parser.parse_suites())

        # Verify all three suites are present
        assert len(suites) == 3

        # Verify each suite has correct data
        for i in range(3):
            assert suites[i]['name'] == f"suite_{i+1}"
            assert len(suites[i]['test_cases']) == 1
            assert suites[i]['test_cases'][0]['name'] == f"test_{i+1}"
            assert suites[i]['test_cases'][0]['status'] == ("FAILED" if i == 1 else "PASSED")

        # Verify all files were loaded
        assert mock_junitxml_class.fromfile.call_count == 3

        # Verify merge happened 3 times (one for each file)
        assert mock_merged_junit.__iadd__.call_count == 3

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_multiple_suites_per_file(self, mock_junitxml_class):
        """Test merging files where each file contains multiple test suites."""
        # File 1 has 2 suites
        file1_suites = []
        for i in range(2):
            suite = Mock()
            suite.name = f"file1_suite_{i+1}"
            suite.timestamp = "2024-01-01T12:00:00"

            case = Mock()
            case.name = f"file1_test_{i+1}"
            case.classname = "module_file1"
            case.time = "1.0"
            case.is_error = False
            case.is_failure = False
            case.is_skipped = False
            case.system_out = None
            case.system_err = None
            case.iterchildren.return_value = []
            case.child.return_value = None

            suite.__iter__ = Mock(return_value=iter([case]))
            suite.properties.return_value = []
            file1_suites.append(suite)

        # File 2 has 2 suites
        file2_suites = []
        for i in range(2):
            suite = Mock()
            suite.name = f"file2_suite_{i+1}"
            suite.timestamp = "2024-01-01T13:00:00"

            case = Mock()
            case.name = f"file2_test_{i+1}"
            case.classname = "module_file2"
            case.time = "2.0"
            case.is_error = False
            case.is_failure = False
            case.is_skipped = False
            case.system_out = None
            case.system_err = None
            case.iterchildren.return_value = []
            case.child.return_value = None

            suite.__iter__ = Mock(return_value=iter([case]))
            suite.properties.return_value = []
            file2_suites.append(suite)

        # Mock JUnit XML from files
        mock_junit_file1 = Mock()
        mock_junit_file1.__iter__ = Mock(return_value=iter(file1_suites))

        mock_junit_file2 = Mock()
        mock_junit_file2.__iter__ = Mock(return_value=iter(file2_suites))

        # Mock merged object with all 4 suites
        all_suites = file1_suites + file2_suites
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter(all_suites))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Setup JUnitXml class mock
        mock_junitxml_class.return_value = mock_merged_junit
        mock_junitxml_class.fromfile.side_effect = [mock_junit_file1, mock_junit_file2]

        parser = JUnitParser(["/path/file1.xml", "/path/file2.xml"])
        suites = list(parser.parse_suites())

        # Verify all 4 suites are present (2 from each file)
        assert len(suites) == 4

        # Verify file1 suites
        assert suites[0]['name'] == "file1_suite_1"
        assert suites[0]['test_cases'][0]['name'] == "file1_test_1"
        assert suites[1]['name'] == "file1_suite_2"
        assert suites[1]['test_cases'][0]['name'] == "file1_test_2"

        # Verify file2 suites
        assert suites[2]['name'] == "file2_suite_1"
        assert suites[2]['test_cases'][0]['name'] == "file2_test_1"
        assert suites[3]['name'] == "file2_suite_2"
        assert suites[3]['test_cases'][0]['name'] == "file2_test_2"

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_file_error_first_file(self, mock_junitxml_class):
        """Test that error in first file during merge stops processing."""
        mock_merged_junit = Mock()
        mock_junitxml_class.return_value = mock_merged_junit
        mock_junitxml_class.fromfile.side_effect = Exception("Failed to read file")

        parser = JUnitParser(["/path/file1.xml", "/path/file2.xml"])

        with pytest.raises(Exception, match="Failed to read file"):
            list(parser.parse_suites())

        # Should only try to read the first file
        assert mock_junitxml_class.fromfile.call_count == 1

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_file_error_second_file(self, mock_junitxml_class):
        """Test that error in second file during merge raises exception."""
        mock_junit_file1 = Mock()
        mock_suite1 = Mock()
        mock_suite1.name = "suite_1"
        mock_junit_file1.__iter__ = Mock(return_value=iter([mock_suite1]))

        mock_merged_junit = Mock()
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)
        mock_junitxml_class.return_value = mock_merged_junit

        # First file succeeds, second file fails
        mock_junitxml_class.fromfile.side_effect = [
            mock_junit_file1,
            Exception("Failed to read second file")
        ]

        parser = JUnitParser(["/path/file1.xml", "/path/file2.xml"])

        with pytest.raises(Exception, match="Failed to read second file"):
            list(parser.parse_suites())

        # Should have tried to read both files
        assert mock_junitxml_class.fromfile.call_count == 2

    @patch('reportportal.junit_parser.JUnitXml')
    def test_parse_suites_merge_preserves_properties(self, mock_junitxml_class):
        """Test that suite and case properties are preserved during merge."""
        # Suite 1 with properties
        mock_prop1 = Mock()
        mock_prop1.name = "platform"
        mock_prop1.value = "aws"

        mock_suite1 = Mock()
        mock_suite1.name = "suite_1"
        mock_suite1.timestamp = "2024-01-01T12:00:00"
        mock_suite1.properties.return_value = [mock_prop1]

        mock_case1 = Mock()
        mock_case1.name = "test_1"
        mock_case1.classname = "module_1"
        mock_case1.time = "1.0"
        mock_case1.is_error = False
        mock_case1.is_failure = False
        mock_case1.is_skipped = False
        mock_case1.system_out = None
        mock_case1.system_err = None
        mock_case1.iterchildren.return_value = []

        # Case property
        mock_case_prop = Mock()
        mock_case_prop.name = "color"
        mock_case_prop.value = "green"

        mock_properties_element = Mock()
        mock_properties_element.iterchildren.return_value = [mock_case_prop]
        mock_case1.child.return_value = mock_properties_element

        mock_suite1.__iter__ = Mock(return_value=iter([mock_case1]))

        # Suite 2 with different properties
        mock_prop2 = Mock()
        mock_prop2.name = "platform"
        mock_prop2.value = "gcp"

        mock_suite2 = Mock()
        mock_suite2.name = "suite_2"
        mock_suite2.timestamp = "2024-01-01T13:00:00"
        mock_suite2.properties.return_value = [mock_prop2]

        mock_case2 = Mock()
        mock_case2.name = "test_2"
        mock_case2.classname = "module_2"
        mock_case2.time = "2.0"
        mock_case2.is_error = False
        mock_case2.is_failure = False
        mock_case2.is_skipped = False
        mock_case2.system_out = None
        mock_case2.system_err = None
        mock_case2.iterchildren.return_value = []
        mock_case2.child.return_value = None

        mock_suite2.__iter__ = Mock(return_value=iter([mock_case2]))

        # Mock files
        mock_junit_file1 = Mock()
        mock_junit_file1.__iter__ = Mock(return_value=iter([mock_suite1]))

        mock_junit_file2 = Mock()
        mock_junit_file2.__iter__ = Mock(return_value=iter([mock_suite2]))

        # Mock merged object
        mock_merged_junit = Mock()
        mock_merged_junit.__iter__ = Mock(return_value=iter([mock_suite1, mock_suite2]))
        mock_merged_junit.__iadd__ = Mock(return_value=mock_merged_junit)

        # Setup JUnitXml class mock
        mock_junitxml_class.return_value = mock_merged_junit
        mock_junitxml_class.fromfile.side_effect = [mock_junit_file1, mock_junit_file2]

        parser = JUnitParser(["/path/file1.xml", "/path/file2.xml"])
        suites = list(parser.parse_suites())

        # Verify properties from both files are preserved
        assert len(suites) == 2

        # Check suite 1 properties
        assert len(suites[0]['properties']) == 1
        assert suites[0]['properties'][0] == {"key": "platform", "value": "aws"}

        # Check suite 1 case properties
        assert len(suites[0]['test_cases'][0]['properties']) == 1
        assert suites[0]['test_cases'][0]['properties'][0] == {"key": "color", "value": "green"}

        # Check suite 2 properties
        assert len(suites[1]['properties']) == 1
        assert suites[1]['properties'][0] == {"key": "platform", "value": "gcp"}

        # Check suite 2 has no case properties
        assert len(suites[1]['test_cases'][0]['properties']) == 0