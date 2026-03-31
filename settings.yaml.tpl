# ReportPortal Configuration Template
# Copy this file to your user config directory and customize as needed
#
# Config file locations (in order of precedence):
#   Linux:   ~/.config/rptool/settings.yaml
#   macOS:   ~/Library/Application Support/rptool/settings.yaml
#   Windows: %LOCALAPPDATA%\rptool\settings.yaml
#
# Configuration priority (highest to lowest):
#   1. CLI arguments
#   2. Environment variables
#   3. Config file
#   4. Built-in defaults

# ReportPortal instance URL (required)
# Example: https://reportportal.example.com
rp_url: ""

# ReportPortal project name (required)
# Example: my_project
rp_project: ""

# ReportPortal API token (required)
# WARNING: Storing tokens in config files is less secure than using
# environment variables. Consider using RP_TOKEN environment variable instead.
rp_token: ""

# Enable auto-analysis after upload (default: false)
trigger_auto_analysis: false

# Default launch name (optional)
# If not specified, will be derived from JUnit filename
launch_name: ""

# Default launch description (optional)
launch_description: ""

# Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
log_level: "INFO"

# Path to CA bundle for HTTPS requests (optional)
# If specified and REQUESTS_CA_BUNDLE is not set, will be injected into environment
# Example: /etc/pki/tls/certs/ca-bundle.crt
requests_ca_bundle: ""
