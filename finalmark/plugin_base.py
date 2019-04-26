def pluginfy(plugin):

    def wrapper(*args, **kwargs):
        return plugin(*args, **kwargs)

    return wrapper
