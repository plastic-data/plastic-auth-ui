#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Weotu-UI -- Accounts & authentication user interface
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2014 Emmanuel Raviart
# https://gitorious.org/weotu
#
# This file is part of Weotu-UI.
#
# Weotu-UI is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Weotu-UI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Setup application (Create indexes, launch upgrade scripts, etc)."""


import argparse
import logging
import os
import sys

import paste.deploy

from weotu_ui import environment


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = "path of Weotu-UI configuration file")
    parser.add_argument('-s', '--section', default = 'main',
        help = "Name of configuration section in configuration file")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    site_conf = paste.deploy.appconfig('config:{0}#{1}'.format(os.path.abspath(args.config), args.section))
    environment.load_environment(site_conf.global_conf, site_conf.local_conf)
    environment.setup_environment()

    return 0


if __name__ == "__main__":
    sys.exit(main())
