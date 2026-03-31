"""
Unit tests for property_enums module.
"""

import pytest
from reportportal.property_enums import (
    ReportPortalProperties,
    MetadataProperties,
    ComponentProperties,
    PlatformType,
    BuildType,
    Level,
    PropertyEnum,
    validate_platform,
    validate_build_type,
    validate_test_level
)


@pytest.mark.unit
class TestReportPortalProperties:
    """Test ReportPortalProperties enum."""
    
    def test_rp_property_values(self):
        """Test ReportPortal property values."""
        assert ReportPortalProperties.PREFIX.value == '__rp_'
        assert ReportPortalProperties.LAUNCH_DESCRIPTION.value == '__rp_launch_description'
        assert ReportPortalProperties.SUITE_DESCRIPTION.value == '__rp_suite_description'
        assert ReportPortalProperties.CASE_DESCRIPTION.value == '__rp_case_description'
    
    def test_is_rp_property(self):
        """Test is_rp_property method."""
        assert ReportPortalProperties.is_rp_property('__rp_test') is True
        assert ReportPortalProperties.is_rp_property('__rp_launch_description') is True
        assert ReportPortalProperties.is_rp_property('regular_property') is False
        assert ReportPortalProperties.is_rp_property('') is False
        assert ReportPortalProperties.is_rp_property('_rp_test') is False
    
    def test_get_description_keys(self):
        """Test get_description_keys method."""
        description_keys = ReportPortalProperties.get_description_keys()
        expected_keys = [
            '__rp_launch_description',
            '__rp_suite_description', 
            '__rp_case_description'
        ]
        assert description_keys == expected_keys


@pytest.mark.unit
class TestMetadataProperties:
    """Test MetadataProperties enum."""
    
    def test_metadata_property_values(self):
        """Test metadata property values."""
        assert MetadataProperties.ISSUE.value == 'issue'
        assert MetadataProperties.ENV.value == 'env'
        assert MetadataProperties.OS.value == 'os'
        assert MetadataProperties.PLATFORM.value == 'platform'
        assert MetadataProperties.VERSION.value == 'version'
        assert MetadataProperties.BUILD.value == 'build'
        assert MetadataProperties.LEVEL.value == 'level'


@pytest.mark.unit
class TestComponentProperties:
    """Test ComponentProperties enum."""
    
    def test_component_property_values(self):
        """Test component property values."""
        assert ComponentProperties.KUADRANT.value == 'kuadrant'
        assert ComponentProperties.DNS_OPERATOR.value == 'dns-operator'
        assert ComponentProperties.SAIL_OPERATOR.value == 'sail-operator'


@pytest.mark.unit
class TestPlatformType:
    """Test PlatformType enum."""
    
    def test_platform_values(self):
        """Test platform type values."""
        assert PlatformType.ONPREM.value == 'onprem'
        assert PlatformType.AWS.value == 'aws'
        assert PlatformType.ROSA.value == 'rosa'
        assert PlatformType.ARO.value == 'aro'
        assert PlatformType.AWS_OSD.value == 'aws-osd'
        assert PlatformType.GCP_OSD.value == 'gcp-osd'
        assert PlatformType.GCP.value == 'gcp'


@pytest.mark.unit
class TestBuildType:
    """Test BuildType enum."""
    
    def test_build_values(self):
        """Test build type values."""
        assert BuildType.KUADRANT.value == 'kuadrant'
        assert BuildType.RHCL.value == 'rhcl'


@pytest.mark.unit
class TestLevel:
    """Test Level enum."""
    
    def test_test_level_values(self):
        """Test test level values."""
        assert Level.RELEASE.value == 'release'
        assert Level.NIGHTLY.value == 'nightly'
        assert Level.SMOKE.value == 'smoke'
        assert Level.ACCEPTANCE.value == 'acceptance'
        assert Level.FULLSUITE.value == 'fullsuite'


@pytest.mark.unit
class TestValidationFunctions:
    """Test validation utility functions."""
    
    def test_validate_platform(self):
        """Test platform validation."""
        assert validate_platform('aws') is True
        assert validate_platform('rosa') is True
        assert validate_platform('invalid-platform') is False
        assert validate_platform('') is False
        assert validate_platform(None) is False
    
    def test_validate_build_type(self):
        """Test build type validation."""
        assert validate_build_type('kuadrant') is True
        assert validate_build_type('rhcl') is True
        assert validate_build_type('invalid-build') is False
        assert validate_build_type('') is False
        assert validate_build_type(None) is False
    
    def test_validate_test_level(self):
        """Test test level validation."""
        assert validate_test_level('release') is True
        assert validate_test_level('smoke') is True
        assert validate_test_level('invalid-level') is False
        assert validate_test_level('') is False
        assert validate_test_level(None) is False


@pytest.mark.unit
class TestPropertyEnumLegacy:
    """Test legacy PropertyEnum for backward compatibility."""
    
    def test_legacy_rp_properties(self):
        """Test legacy ReportPortal properties."""
        assert PropertyEnum.RP_PREFIX.value == '__rp_'
        assert PropertyEnum.RP_LAUNCH_DESCRIPTION_KEY.value == '__rp_launch_description'
        assert PropertyEnum.RP_SUITE_DESCRIPTION_KEY.value == '__rp_suite_description'
        assert PropertyEnum.RP_CASE_DESCRIPTION_KEY.value == '__rp_case_description'
    
    def test_legacy_metadata_properties(self):
        """Test legacy metadata properties."""
        assert PropertyEnum.ISSUE.value == 'issue'
        assert PropertyEnum.ENV.value == 'env'
        assert PropertyEnum.OS.value == 'os'
        assert PropertyEnum.PLATFORM.value == 'platform'
        assert PropertyEnum.VERSION.value == 'version'
        assert PropertyEnum.BUILD.value == 'build'
        assert PropertyEnum.LEVEL.value == 'level'
    
    def test_legacy_component_properties(self):
        """Test legacy component properties."""
        assert PropertyEnum.KUADRANT.value == 'kuadrant'
        assert PropertyEnum.DNS_OPERATOR.value == 'dns-operator'
        assert PropertyEnum.SAIL_OPERATOR.value == 'sail-operator'