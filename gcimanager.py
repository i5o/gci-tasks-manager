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

import textwrap
import re
import apikey
from api.client import GCIAPIClient

from gi.repository import Gdk
from gi.repository import Gtk


class GCIManager(Gtk.Window):

    def __init__(self):
        super(GCIManager, self).__init__()

        self.notebook = Gtk.Notebook()

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.label = Gtk.Label()

        self.add_page(1)

        self.vbox.pack_start(self.label, False, False, 0)
        self.vbox.pack_end(self.notebook, True, True, 0)

        self.set_gravity(Gdk.Gravity.CENTER)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(Gdk.Screen.get_default().get_width(), 768)
        self.add(self.vbox)
        self.show_all()

    def do_delete_event(self, *args):
        Gtk.main_quit()

    def add_page(self, page_num):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.notebook.append_page(scroll, Gtk.Label("Page %d" % page_num))

        tasks_list = GCITasksList(page_num, self.label, self.add_page)
        scroll.add_with_viewport(tasks_list)


class GCITasksList(Gtk.TreeView):

    def __init__(self, page, info_label, function):
        super(GCITasksList, self).__init__()

        self.info_label = info_label
        self.page = page

        columns = [
            ["Task\nname", str],
            ["Task\ndescription", str],
            ["Beginner", bool],
            ["Max\ninstances", int, 1, 50],
            ["Published", bool],
            ["Code\ntask", bool],
            ["User interface\ntask", bool],
            ["Doc\ntask", bool],
            ["QA\ntask", bool],
            ["Outreach\nResearch task", bool],
            ["Tags", str]
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
                column.set_fixed_width(200)

                renderer.set_fixed_height_from_font(1)
            elif column_type == bool:
                renderer = Gtk.CellRendererToggle()
                column = Gtk.TreeViewColumn(column_title, renderer, active=pos)
                event_name = "toggled"

            elif column_type == int:
                renderer = Gtk.CellRendererSpin()
                column = Gtk.TreeViewColumn(column_title, renderer, text=pos)
                event_name = "edited"
                renderer.set_property("editable", True)
                column.set_fixed_width(100)
                adjustment = Gtk.Adjustment(
                    0, column_data[2], column_data[3], 1, 10, 0)
                renderer.set_property("adjustment", adjustment)

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
            bool,
            str)

        self.set_model(self.model)
        self.get_tasks(function)

    def data_edited(self, widget, path, value, pos=None):
        if isinstance(widget, Gtk.CellRendererToggle):
            self.model[path][value] = not self.model[path][value]
        else:
            try:
                self.model[path][pos] = value
            except TypeError:
                self.model[path][pos] = int(value)

        return True

    def get_tasks(self, function):
        self.gci_client = GCIAPIClient(apikey.apikey)

        while self.page > 0:
            tasks = self.gci_client.ListTasks(page=self.page)
            self.info_label.set_text("Total tasks: %d" % (tasks["count"]))

            for task in tasks["results"]:
                task_data = []
                task_description = u"".join(
                    task["description"].replace(
                        "\n", " ")).encode("utf-8")
                task_description = task_description[
                    :20] + "..." + task_description[20:]
                task_data.append(task["name"].replace("\n", " "))
                task_data.append(task["description"].replace("\n", " "))
                task_data.append(task["is_beginner"])
                task_data.append(task["max_instances"])
                task_data.append(task["status"] == 2)
                task_data.append(1 in task["categories"])
                task_data.append(2 in task["categories"])
                task_data.append(3 in task["categories"])
                task_data.append(4 in task["categories"])
                task_data.append(5 in task["categories"])
                task_data.append(",".join(task["tags"]))
                self.model.append(task_data)

            self.page = 0
            if tasks['next']:
                result = re.search(r'page=(\d+)', tasks['next'])
                if result:
                    next_page = int(result.group(1))
                    function(next_page)

if __name__ == "__main__":
    window = GCIManager()
    window.show()
    Gtk.main()
