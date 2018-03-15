# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

from __future__ import print_function

import xbmcgui
import xbmc
import xbmcaddon
import json
import time
from threading import Timer

import AutoCompletion

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')


def get_kodi_json(method, params):
    json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "%s", "params": %s, "id": 1}' % (method, params))
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    return json.loads(json_query)


class Monitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        pass

    def onNotification(self, sender, method, data):
        if sender == "autocompletions":
            try:
                window_id = xbmcgui.getCurrentWindowDialogId()
                window = xbmcgui.Window(window_id)
            except Exception:
                return None
            window.setFocusId(300)
            get_kodi_json(method="Input.SendText",
                          params='{"text":"%s", "done":false}' % method[6:])


class Daemon(object):

    def __init__(self, *args, **kwargs):
        self.previous = False
        self.prev_time = 0
        self.timer = None
        self.mon = Monitor()
        xbmc.log("AutoCompletion version %s started" % ADDON_VERSION)
        while True:
            xbmc.sleep(100)
            if xbmc.getCondVisibility("Window.IsActive(virtualkeyboard)"):
                search_string = xbmc.getInfoLabel("Control.GetLabel(312).index(1)")
                if search_string != self.previous:
                    self.previous = search_string
                    self.set_items(search_string)
                    xbmc.log(search_string)
        xbmc.log('finished')

    def set_items(self, search_string):
        wnd = xbmcgui.Window(10000)
        wnd.clearProperties()
        listitems = AutoCompletion.get_autocomplete_items(search_string, 10)
        for i, item in enumerate(listitems):
            for key, value in item.iteritems():
                wnd.setProperty("AutoCompletions.{}.{}".format(i, key), value)


monitor_thread = Daemon()
