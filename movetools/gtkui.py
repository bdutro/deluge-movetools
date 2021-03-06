#
# gtkui.py
#
# Copyright (C) 2014 Ratanak Lun <ratanakvlun@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#


import gettext
import logging

from gi.repository import Gtk

from twisted.internet import reactor

from deluge.ui.client import client
from deluge.plugins.pluginbase import Gtk3PluginBase
import deluge.component as component

from .common import PLUGIN_NAME
from .common import MODULE_NAME
from .common import DISPLAY_NAME
from .common import STATUS_NAME
from .common import STATUS_MESSAGE
from .common import get_resource
from .common import dict_equals

_ = gettext.gettext

INIT_POLLING_INTERVAL = 3.0


log = logging.getLogger(__name__)


class GtkUI(Gtk3PluginBase):

  def enable(self):
    log.debug("[%s] Enabling GtkUI...", PLUGIN_NAME)
    self._poll_init()

  def _poll_init(self):
    client.movetools.is_initialized().addCallback(self._check_init)

  def _check_init(self, result):
    log.debug("[%s] Waiting for core to be initialized...", PLUGIN_NAME)
    if result == True:
      self._finish_init()
    else:
      reactor.callLater(INIT_POLLING_INTERVAL, self._poll_init)

  def _finish_init(self):
    log.debug("[%s] Resuming initialization...", PLUGIN_NAME)

    self.config = {}

    self.ui = Gtk.Builder.new_from_file(get_resource("wnd_preferences.ui"))

    lbl = self.ui.get_object("lbl_general")
    lbl.set_markup("<b>%s</b>" % lbl.get_text())

    lbl = self.ui.get_object("lbl_timeout")
    lbl.set_markup("<b>%s</b>" % lbl.get_text())

    component.get("Preferences").add_page(
        DISPLAY_NAME, self.ui.get_object("blk_preferences"))
    component.get("PluginManager").register_hook(
        "on_apply_prefs", self._do_save_settings)
    component.get("PluginManager").register_hook(
        "on_show_prefs", self._do_load_settings)

    self.menu = self._create_menu()
    self.menu.show_all()

    self.sep = component.get("MenuBar").add_torrentmenu_separator()
    component.get("MenuBar").torrentmenu.append(self.menu)

    self._add_column()

    self._do_load_settings()
    log.debug("[%s] GtkUI enabled", PLUGIN_NAME)

  def disable(self):
    log.debug("[%s] Disabling GtkUI...", PLUGIN_NAME)

    component.get("MenuBar").torrentmenu.remove(self.sep)
    component.get("MenuBar").torrentmenu.remove(self.menu)

    self.menu.destroy()

    component.get("Preferences").remove_page(DISPLAY_NAME)
    component.get("PluginManager").deregister_hook(
        "on_apply_prefs", self._do_save_settings)
    component.get("PluginManager").deregister_hook(
        "on_show_prefs", self._do_load_settings)

    self._remove_column()

    log.debug("[%s] GtkUI disabled", PLUGIN_NAME)

  def _do_save_settings(self):
    log.debug("[%s] Saving settings", PLUGIN_NAME)

    config = {
      "general": {
        "estimated_speed":
          self.ui.get_object("spn_estimated_speed").get_value(),
        "remove_empty": self.ui.get_object("chk_remove_empty").get_active(),
      },
      "timeout": {
        "success": self.ui.get_object("spn_success_timeout").get_value(),
        "error": self.ui.get_object("spn_error_timeout").get_value(),
      },
    }

    if not dict_equals(config, self.config):
      client.movetools.set_settings(config)
    else:
      log.debug("[%s] No settings were changed", PLUGIN_NAME)

  def _do_load_settings(self):
    log.debug("[%s] Requesting settings", PLUGIN_NAME)
    client.movetools.get_settings().addCallback(self._do_load)

  def _do_load(self, config):
    self.config = config

    spn = self.ui.get_object("spn_estimated_speed")
    spn.set_value(config["general"]["estimated_speed"])
    chk = self.ui.get_object("chk_remove_empty")
    chk.set_active(config["general"]["remove_empty"])

    spn = self.ui.get_object("spn_success_timeout")
    spn.set_value(config["timeout"]["success"])
    spn = self.ui.get_object("spn_error_timeout")
    spn.set_value(config["timeout"]["error"])

  def _create_menu(self):
    menu = Gtk.MenuItem(DISPLAY_NAME)
    submenu = Gtk.Menu()

    move_item = Gtk.MenuItem(_("Move"))
    move_submenu = Gtk.Menu()
    move_item.set_submenu(move_submenu)

    item = Gtk.MenuItem(_("Move Completed"))
    item.connect("activate", self._do_move_completed)
    move_submenu.append(item)

    item = Gtk.MenuItem(_("Cancel Pending"))
    item.connect("activate", self._do_cancel_pending)
    move_submenu.append(item)

    status_item = Gtk.MenuItem(_("Status"))
    status_submenu = Gtk.Menu()
    status_item.set_submenu(status_submenu)

    item = Gtk.MenuItem(_("Clear"))
    item.connect("activate", self._do_clear_selected)
    status_submenu.append(item)

    item = Gtk.MenuItem(_("Clear All"))
    item.connect("activate", self._do_clear_all)
    status_submenu.append(item)

    submenu.append(move_item)
    submenu.append(status_item)
    menu.set_submenu(submenu)

    return menu

  def _do_move_completed(self, widget):
    ids = component.get("TorrentView").get_selected_torrents()
    log.debug("[%s] Requesting move completed for: %s", PLUGIN_NAME, ids)
    client.movetools.move_completed(ids)

  def _do_cancel_pending(self, widget):
    ids = component.get("TorrentView").get_selected_torrents()
    log.debug("[%s] Requesting cancel pending for: %s", PLUGIN_NAME, ids)
    client.movetools.cancel_pending(ids)

  def _do_clear_selected(self, widget):
    ids = component.get("TorrentView").get_selected_torrents()
    log.debug("[%s] Requesting clear status results for: %s",
        PLUGIN_NAME, ids)
    client.movetools.clear_selected(ids)

  def _do_clear_all(self, widget):
    log.debug("[%s] Requesting clear all status results", PLUGIN_NAME)
    client.movetools.clear_all_status()

  def _add_column(self):
    renderer = Gtk.CellRendererProgress()

    component.get("TorrentView").add_column(
      header=STATUS_NAME,
      render=renderer,
      col_types=str,
      hidden=False,
      position=None,
      status_field=[STATUS_MESSAGE],
      function=self._render_cell,
      sortid=0,
      column_type="progress",
    )

  def _render_cell(self, column, cell, model, iter, data):
    cell.set_property("value", 0.0)
    cell.set_property("visible", False)

    status = model[iter][data[0]]
    if status:
      cell.set_property("visible", True)

      if status.startswith("Moving "):
        try:
          value = float(status.split()[-1])
          cell.set_property("value", value)

          status = "%s %.2f%%" % (_("Moving"), value)
        except ValueError:
          status = _("Status error")

        cell.set_property("text", status)
      else:
        if status == "Done":
          cell.set_property("value", 100.0)

        cell.set_property("text", _(status))

  def _remove_column(self):
    component.get("TorrentView").remove_column(STATUS_NAME)
