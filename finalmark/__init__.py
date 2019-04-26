from plugin_base import pluginfy
import contexts

class FinalmarkRefresherPlugin(object):
    ACTIONS = contexts.ACTIONS

REFRESHER_PLUGIN = pluginfy(FinalmarkRefresherPlugin)
