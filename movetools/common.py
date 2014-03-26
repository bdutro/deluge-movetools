#
# common.py
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


import os
import pkg_resources


PLUGIN_NAME = "MoveTools"
MODULE_NAME = "movetools"
DISPLAY_NAME = _("MoveTools")

STATUS_NAME = _("Move Status")
STATUS_MESSAGE = "%s_message" % MODULE_NAME


def get_resource(filename):
  return pkg_resources.resource_filename(
      MODULE_NAME, os.path.join("data", filename))


def dict_equals(a, b):

  if len(a) != len(b):
    return False

  for key in a:
    if key not in b:
      return False

    if isinstance(a[key], dict):
      if not isinstance(b[key], dict):
        return False

      if a[key] is not b[key]:
        result = dict_equals(a[key], b[key])
        if not result:
          return False
    else:
      if a[key] != b[key]:
        return False

  return True
