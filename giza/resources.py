import pkg_resources

def register_ew_resources(manager):
    manager.register_directory(
        'giza', pkg_resources.resource_filename('giza', 'static'))
