from plugin_base import pluginfy
import contexts

class FinalmarkRefresherPlugin(object):
    ACTIONS = contexts.REFRESHER_ACTIONS

class FinalmarkWorkerPlugin(object):
    ACTIONS = contexts.WORKER_ACTIONS

REFRESHER_PLUGIN = pluginfy(FinalmarkRefresherPlugin)

WORKER_PLUGIN = pluginfy(FinalmarkWorkerPlugin)
