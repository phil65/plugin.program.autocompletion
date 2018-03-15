# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import simplejson as json
import AutoCompletion
import routing

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')

plugin = routing.Plugin()


def get_kodi_json(method, params):
    data = {"jsonrpc": "2.0",
            "method": method,
            "params": json.dumps(params),
            "id": 1}
    json_query = xbmc.executeJSONRPC(json.dumps(data))
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    return json.loads(json_query)


@plugin.route('/completions/<word>')
def completions(self, word):
    listitems = AutoCompletion.get_autocomplete_items(word, 10)
    pass_list_to_skin(data=listitems,
                      handle=plugin.handle,
                      limit=10)


@plugin.route("select/<word>")
def select(self, word):
    if plugin.handle:
        xbmcplugin.setResolvedUrl(handle=plugin.handle,
                                  succeeded=False,
                                  listitem=xbmcgui.ListItem())
    try:
        window_id = xbmcgui.getCurrentWindowDialogId()
        window = xbmcgui.Window(window_id)
    except:
        return None
    window.setFocusId(300)
    get_kodi_json(method="Input.SendText",
                  params='{"text":"%s", "done":false}' % word)


def pass_list_to_skin(data=[], handle=None, limit=False):
    if data and limit and int(limit) < len(data):
        data = data[:int(limit)]
    if not handle:
        return None
    if data:
        items = create_listitems(data)
        xbmcplugin.addDirectoryItems(handle=handle,
                                     items=[(i.getProperty("path"), i, False) for i in items],
                                     totalItems=len(items))
    xbmcplugin.endOfDirectory(handle)


def create_listitems(data=None):
    if not data:
        return []
    items = []
    for (count, result) in enumerate(data):
        listitem = xbmcgui.ListItem(str(count))
        for (key, value) in result.iteritems():
            if not value:
                continue
            value = unicode(value)
            if key.lower() in ["label"]:
                listitem.setLabel(value)
            elif key.lower() in ["search_string"]:
                path = "plugin://plugin.program.autocompletion/completions/%s" % value
                listitem.setPath(path=path)
                listitem.setProperty('path', path)
        listitem.setProperty("index", str(count))
        listitem.setProperty("isPlayable", "false")
        items.append(listitem)
    return items


if (__name__ == "__main__"):
    xbmc.log("version %s started" % ADDON_VERSION)
    plugin.run()
    xbmc.log('finished')

