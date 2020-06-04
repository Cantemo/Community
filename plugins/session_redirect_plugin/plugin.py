"""
This is your new plugin handler code.

Put your plugin handling code in here. remember to update the __init__.py file with 
you app version number. We have automatically generated a GUID for you, namespace, and a url 
that serves up index.html file
"""
import logging

from portal.pluginbase.core import Plugin, implements
from portal.generic.plugin_interfaces import (IPluginURL, IPluginBlock, IAppRegister)

log = logging.getLogger(__name__)

class SessionRedirectPluginURL(Plugin):
    """ Adds a plugin handler which creates url handler for the index page """
    implements(IPluginURL)

    def __init__(self):
        self.name = "session_Redirect_Plugin App"
        self.urls = 'portal.plugins.session_redirect_plugin.urls'
        self.urlpattern = r'^session_redirect_plugin/'
        self.namespace = r'session_redirect_plugin'
        self.plugin_guid = '21d04896-1f7c-440e-b0a2-808abc45cc3e'
        log.debug("Initiated Session_Redirect_Plugin App")

pluginurls = SessionRedirectPluginURL()

class SessionRedirectRegister(Plugin):
    # This adds it to the list of installed Apps
    # Please update the information below with the author etc..
    implements(IAppRegister)

    def __init__(self):
        self.name = "session_Redirect_Plugin Registration App"
        self.plugin_guid = '8f1af717-82da-4cff-9fd1-5ff94fd06993'
        log.debug('Register the App')

    def __call__(self):
        from .__init__ import __version__ as versionnumber
        _app_dict = {
                'name': 'session Redirect Plugin',
                'version': '0.0.1',
                'author': '',
                'author_url': '',
                'notes': 'Add your Copyright notice here.'}
        return _app_dict

regplugin = SessionRedirectRegister()
