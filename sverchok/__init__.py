#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>
#  and write to the Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA  02110-1301, USA..
#
#  The Original Code is Copyright (C) 2013-2014 by Gorodetskiy Nikita  ###
#  All rights reserved.
#
#  Contact:      sverchok-b3d@yandex.ru    ###
#  Information:  http://nikitron.cc.ua/sverchok.html   ###
#
#  The Original Code is: all of this file.
#
#  Contributor(s): Nedovizin Alexander, Gorodetskiy Nikita, Linus Yng, Agustin Gimenez.
#
#  ***** END GPL LICENSE BLOCK *****
#
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Sverchok",
    "author": "Nedovizin Alexander, Gorodetskiy Nikita, Linus Yng, Agustin Jimenez, Dealga McArdle",
    "version": (0, 3, 0),
    "blender": (2, 7, 0),
    "location": "Nodes > CustomNodesTree > Add user nodes",
    "description": "Do parametric node-based geometry programming",
    "warning": "requires nodes window",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Nodes/Sverchok",
    "tracker_url": "http://www.blenderartists.org/forum/showthread.php?272679-Addon-WIP-Sverchok-parametric-tool-for-architects",
    "category": "Node"}


import os
import sys

path = sys.path
flag = False
for item in path:
    if "sverchok" in item:
        flag = True
        break
if flag is False:
    #sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sverchok_nodes'))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sverchok'))

    print("Sverchok_nodes: added to pythonpath :-)")
    print("Have a nice day with Sverchok")


# use importlib instead of imp, which is deprecated since python 3.4
# importing first allows to stores a list of nodes before eventually reloading
# potential problem : are new nodes imported???
import importlib
import data_structure
import node_tree
from .utils import sv_tools
import nodes
nodes_list = []
for category, names in nodes.nodes_dict.items():
    nodes_cat = importlib.import_module('.{}'.format(category), 'nodes')
    for name in names:
        node = importlib.import_module('.{}'.format(name),
                                       'nodes.{}'.format(category))
        nodes_list.append(node)

if "bpy" in locals():
    import importlib
    importlib.reload(data_structure)
    importlib.reload(node_tree)
    importlib.reload(nodes)
    importlib.reload(sv_tools)
    # (index_)viewer_draw -> name not defined error, because I never used it??
    #importlib.reload(viewer_draw)
    #importlib.reload(index_viewer_draw)
    for n in nodes_list:
        importlib.reload(n)

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty
import data_structure


def update_debug_mode(self, context):
    data_structure.DEBUG_MODE = self.show_debug


class SverchokPreferences(AddonPreferences):

    bl_idname = __name__

    show_debug = BoolProperty(name="Print update timings",
                              description="Print update timings in console",
                              default=False, subtype='NONE',
                              update=update_debug_mode)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_debug")


def register():
    import nodeitems_utils
    from .utils import sv_tools, text_editor_plugins, text_editor_submenu

    node_tree.register()
    for n in nodes_list:
        n.register()
    sv_tools.register()
    text_editor_plugins.register()
    text_editor_submenu.register()

    bpy.utils.register_class(SverchokPreferences)

    if 'SVERCHOK' not in nodeitems_utils._node_categories:
        nodeitems_utils.register_node_categories("SVERCHOK",
                                                 node_tree.make_categories())


def unregister():
    import nodeitems_utils
    from .utils import sv_tools, text_editor_plugins, text_editor_submenu

    node_tree.unregister()
    for n in nodes_list:
        n.unregister()
    sv_tools.unregister()
    text_editor_plugins.unregister()
    text_editor_submenu.unregister()

    bpy.utils.unregister_class(SverchokPreferences)

    if 'SVERCHOK' not in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("SVERCHOK",
                                                   node_tree.make_categories())