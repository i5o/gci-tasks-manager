#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Google Code In (unofficial) tasks manager.
# Copyright (C) 2015 Ignacio Rodríguez <ignacio@sugarlabs.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import apikey

from gi.repository import Gdk
from gi.repository import Gtk


class GCIManager(Gtk.Window):

    def __init__(self):
        super(GCIManager, self).__init__()

        self.tasks_list = GCITasksList()

        self.set_gravity(Gdk.Gravity.CENTER)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1024, 768)
        self.add(self.tasks_list)
        self.show_all()

    def do_delete_event(self, *args):
        Gtk.main_quit()


class GCITasksList(Gtk.TreeView):

    def __init__(self):
        super(GCITasksList, self).__init__()

        # Columnas:
        # nombre tarea, descripcion tarea, es beginner, categorias, instancias,
        # publicadas
        columns = [
            ["Task name", str],
            ["Task description", str],
            ["Beginner task", bool],
            ["Max instances", int, 1, 50],
            ["Published", bool],
            ["Code task", bool],
            ["User interface task", bool],
            ["Documentation task", bool],
            ["QA task", bool],
            ["Outreach / Research task", bool]
        ]

        for column_data in columns:
            pos = columns.index(column_data)
            column_title = column_data[0]
            column_type = column_data[1]

            if column_type == str:
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=pos)
                event_name = "edited"
                renderer.set_property("editable", True)

            elif column_type == bool:
                renderer = Gtk.CellRendererToggle()
                column = Gtk.TreeViewColumn(column_title, renderer, active=pos)
                event_name = "toggled"

            elif column_type == int:
                renderer = Gtk.CellRendererSpin()
                column = Gtk.TreeViewColumn(column_title, renderer, text=pos)
                event_name = "edited"
                renderer.set_property("editable", True)

                adjustment = Gtk.Adjustment(
                    0, column_data[2], column_data[3], 1, 10, 0)
                renderer.set_property("adjustment", adjustment)

            renderer.set_alignment(0, 0.1)
            renderer.connect(event_name, self.data_edited, pos)
            self.append_column(column)

        self.model = Gtk.ListStore(
            str,
            str,
            bool,
            int,
            bool,
            bool,
            bool,
            bool,
            bool,
            bool)

        for x in range(10):
            self.model.append(["Hello", "From the other side",
                               True, 1, False, False, False, True, False, False])

        self.set_model(self.model)

    def data_edited(self, widget, path, value, pos=None):
        if isinstance(widget, Gtk.CellRendererToggle):
            self.model[path][value] = not self.model[path][value]
        else:
            try:
                self.model[path][pos] = value
            except TypeError:
                self.model[path][pos] = int(value)

        return True

if __name__ == "__main__":
    window = GCIManager()
    window.show()
    Gtk.main()
