# Mock Test Suite

This is a mock test suite used for producing testing results and demonstrating how to pass custom properties/attributes from your test suite through JUnit XML to ReportPortal.

## Custom Properties & Attributes

### Overview

Custom properties allow you to attach metadata to your tests that flows through the reporting pipeline:

```
Test Suite → JUnit XML → ReportPortal
```

Properties can be attached at three levels:
1. **Launch level** - Applies to the entire test run
2. **Suite level** - Applies to a test suite
3. **Test case level** - Applies to individual tests

### Property Types

#### 1. ReportPortal-Specific Properties (Description Fields)

These properties start with `__rp_` prefix and are used for special ReportPortal functionality:

| Property Key | Level | Purpose | Example |
|-------------|-------|---------|---------|
| `__rp_launch_description` | Launch | Sets the launch description in ReportPortal | Cluster info, environment details |
| `__rp_suite_description` | Suite | Sets the test suite description | Suite purpose, context |
| `__rp_case_description` | Test Case | Sets individual test description | Usually auto-filled from docstring |

**Note:** Other `__rp_*` properties are filtered out and not shown as attributes in ReportPortal.

#### 2. Standard Metadata Properties (Attributes)

These properties become visible **attributes/tags** in ReportPortal for filtering and analysis:

| Property Key | Purpose | Example Values |
|-------------|---------|----------------|
| `issue` | Issue tracker ID | `JIRA-123`, `ISSUE-456` |
| `env` | Environment name | `staging`, `production`, `dev` |
| `os` | OpenShift/OS version | `ocp-4.18`, `ocp-4.20` |
| `platform` | Platform type | `onprem`, `aws`, `rosa`, `aro`, `gcp` |
| `version` | Product version | `1.3.0`, `1.3.0-rc1` |
| `build` | Build type | `kuadrant`, `rhcl` |
| `level` | Test level | `release`, `nightly`, `smoke` |
| `component` | Component name | `Adder`, `DNS`, `Gateway` |
| `color` | Custom tag | Any custom value |

Any property that doesn't start with `__rp_` will appear as an attribute in ReportPortal.

### How to Add Properties in pytest

#### Test Case Level Properties

**Method 1: Using pytest markers**

```python
import pytest

@pytest.mark.issue(issue_id='ISSUE-123')
@pytest.mark.component('Adder')
@pytest.mark.color('red')
@pytest.mark.env('staging')
def test_addition():
    '''This docstring becomes the test description in ReportPortal'''
    assert 1 + 1 == 2
```

**Method 2: Using `conftest.py` to convert markers to properties**

```python
# conftest.py
def pytest_collection_modifyitems(session, config, items):
    for item in items:
        # Convert @pytest.mark.issue to property
        for marker in item.iter_markers(name="issue"):
            issue_id = marker.kwargs['issue_id']
            item.user_properties.append(("issue", issue_id))

        # Convert @pytest.mark.color to property
        for marker in item.iter_markers(name="color"):
            color_value = marker.args[0]
            item.user_properties.append(('color', color_value))

        # Automatically extract docstring as test description
        item.user_properties.append(['__rp_case_description', item._obj.__doc__])
```

#### Suite Level Properties

**Using `record_testsuite_property` fixture:**

```python
@pytest.fixture(scope="session")
def suite_metadata(record_testsuite_property):
    # Standard attributes
    record_testsuite_property("os", "ocp-4.20")
    record_testsuite_property("platform", "aws")
    record_testsuite_property("version", "1.3.0")
    record_testsuite_property("build", "kuadrant")
    record_testsuite_property("level", "release")

    # Suite description (ReportPortal-specific)
    suite_description = """
    # Test Suite Description

    This suite tests the core functionality.
    """
    record_testsuite_property("__rp_suite_description", suite_description)
```

#### Launch Level Properties

**Using the info-collector pattern:**

The `info-collector` suite is a special pattern that promotes suite-level properties to launch level:

```python
# conftest.py
def pytest_configure(config):
    if os.environ.get('COLLECTOR_ENABLE'):
        config.inicfg['junit_suite_name'] = 'info-collector'

@pytest.fixture(scope="session")
def launch_metadata(record_testsuite_property):
    launch_description = """
    # Test Launch Description

    **Cluster Information:**
    - Cluster: https://console.cluster1.example.com
    - OCP: 4.18
    - Kuadrant: v1.3.1
    """
    record_testsuite_property("__rp_launch_description", launch_description)

@pytest.mark.skipif(not os.environ.get('COLLECTOR_ENABLE'), reason="collector not enabled")
def test_collect(record_testsuite_property, launch_metadata):
    '''Main collector test'''
    # Additional launch-level properties can be added here
    record_testsuite_property('collector', 'true')
    assert True
```

**Run the info-collector:**

```bash
# Run info-collector to gather launch metadata
COLLECTOR_ENABLE=1 pytest tests/info_collector.py --junit-xml=collector.xml

# Run main test suite
pytest tests/ --junit-xml=results.xml

# Upload both to ReportPortal (they'll be merged)
rptool write --junits collector.xml results.xml
```

### Complete Example

```python
# tests/conftest.py
import os

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        # Extract markers as properties
        for marker in item.iter_markers(name="issue"):
            item.user_properties.append(("issue", marker.kwargs['issue_id']))
        for marker in item.iter_markers(name="component"):
            item.user_properties.append(('component', marker.args[0]))

        # Auto-extract docstring
        item.user_properties.append(['__rp_case_description', item._obj.__doc__])

@pytest.fixture(scope="session")
def env_properties(record_testsuite_property):
    record_testsuite_property("os", "ocp-4.20")
    record_testsuite_property("platform", "aws")
    record_testsuite_property("version", "1.3.0")
    record_testsuite_property("level", "release")

# tests/test_example.py
import pytest

@pytest.mark.issue(issue_id='JIRA-123')
@pytest.mark.component('Gateway')
def test_gateway(env_properties):
    '''Tests the gateway functionality with proper routing'''
    assert True
```

**Resulting JUnit XML:**

```xml
<testsuite name="test_example" properties="...">
    <properties>
        <property name="os" value="ocp-4.20"/>
        <property name="platform" value="aws"/>
        <property name="version" value="1.3.0"/>
        <property name="level" value="release"/>
    </properties>
    <testcase classname="tests.test_example" name="test_gateway">
        <properties>
            <property name="issue" value="JIRA-123"/>
            <property name="component" value="Gateway"/>
            <property name="__rp_case_description" value="Tests the gateway functionality with proper routing"/>
        </properties>
    </testcase>
</testsuite>
```

**In ReportPortal:**
- Launch description: (from info-collector if used)
- Suite attributes: `os=ocp-4.20`, `platform=aws`, `version=1.3.0`, `level=release`
- Test attributes: `issue=JIRA-123`, `component=Gateway`
- Test description: "Tests the gateway functionality with proper routing"

### Best Practices

1. **Use the info-collector pattern** for launch-level metadata (environment info, cluster details)
2. **Use suite-level properties** for test run configuration (OS version, platform, build type)
3. **Use test-level markers** for test-specific metadata (issue tracking, component tags)
4. **Extract docstrings automatically** to populate test descriptions
5. **Use standard property keys** (issue, env, os, platform, version, build, level, component) for consistency
6. **Avoid `__rp_*` properties** except for the three description fields

### Running Tests

```bash
# Run tests with JUnit XML output
pytest tests/ --junit-xml=results.xml

# Run with info-collector for launch metadata
COLLECTOR_ENABLE=1 pytest tests/info_collector.py --junit-xml=collector.xml
pytest tests/ --junit-xml=results.xml

# Upload to ReportPortal
rptool write --junits results.xml
# or merge multiple files
rptool write --junits collector.xml results.xml
```