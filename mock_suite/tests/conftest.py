
import os

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="issue"):
            issue_id = marker.kwargs['issue_id']
            item.user_properties.append(("issue", issue_id))
        for marker in item.iter_markers(name="env"):
            env_value = marker.args[0]
            item.user_properties.append(('env', env_value))
        for marker in item.iter_markers(name="color"):
            color_value = marker.args[0]
            item.user_properties.append(('color', color_value))
        for marker in item.iter_markers(name="component"):
            value = marker.args[0]
            item.user_properties.append(('component', value))
        
        ## extracting test's docstring for RP
        item.user_properties.append(['__rp_case_description', item._obj.__doc__])
        

def pytest_configure(config):
    # junit_suite_name = 'Default suite'
    # config.inicfg['junit_suite_name'] = junit_suite_name
    ## Overriding junit_suite_name for collector
    if os.environ.get('COLLECTOR_ENABLE'):
        config.inicfg['junit_suite_name'] = 'info-collector'
        # config.inicfg['junit_suite_name'] = junit_suite_name
