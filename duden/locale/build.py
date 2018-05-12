#!/usr/bin/env python3

# Copyright (C) 2016 Julie Marchant <onpon4@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess


if __name__ == "__main__":
    for fname in os.listdir():
        root, ext = os.path.splitext(fname)
        if ext == ".po":
            print("Building {}...".format(fname))
            d, root = os.path.split(root)
            os.makedirs(os.path.join(d, root, "LC_MESSAGES"), exist_ok=True)
            oname = os.path.join(d, root, "LC_MESSAGES", "duden.mo")
            subprocess.call(["msgfmt", "-o", oname, fname])
