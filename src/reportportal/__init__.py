"""
ReportPortal Integration Components

This module contains all the core components for ReportPortal integration:
- JUnit XML parsing
- Property filtering and processing
- ReportPortal client wrapper
- Command line argument parsing
"""

from .property_enums import (
    ReportPortalProperties,
    MetadataProperties,
    ComponentProperties,
    PlatformType,
    BuildType,
    Level,
    PropertyEnum,  # Legacy compatibility
    validate_platform,
    validate_build_type,
    validate_test_level
)

from .junit_parser import (
    JUnitParser,
    get_launch_name_from_file,
    timestamp_junit_to_rp
)

from .property_processor import (
    PropertyFilter,
    LaunchPropertyBuilder,
    create_property_processor
)

from .reportportal_client_wrapper import (
    ReportPortalClientWrapper,
    AutoAnalysisTrigger,
    create_rp_client
)

from .writer import (
    RPWriter,
)

from .rp_trigger import (
    run_auto_trigger,
)

from .rp_dispatcher import (
    main as dispatcher_main,
)

__all__ = [
    # Property enums and validation
    "ReportPortalProperties",
    "MetadataProperties",
    "ComponentProperties",
    "PlatformType",
    "BuildType",
    "Level",
    "PropertyEnum",
    "validate_platform",
    "validate_build_type", 
    "validate_test_level",
    
    # JUnit parsing
    "JUnitParser",
    "get_launch_name_from_file",
    "timestamp_junit_to_rp",
    
    # Property processing
    "PropertyFilter",
    "LaunchPropertyBuilder",
    "create_property_processor",
    
    # ReportPortal client
    "ReportPortalClientWrapper",
    "AutoAnalysisTrigger",
    "create_rp_client",
    
    # Argument parsing
    "get_options",
    "get_trigger_options",
    "get_argument_parser",
    "get_trigger_parser",
    
    # Writer and auto-trigger
    "RPWriter",
    "run_auto_trigger",

    # Unified dispatcher
    "dispatcher_main",
    "create_main_parser",
]