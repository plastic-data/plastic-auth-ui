# -*- coding: utf-8 -*-


# Plastic-Auth-UI -- Accounts & authentication user interface
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2014 Emmanuel Raviart
# https://github.com/plastic-data/plastic-auth-ui
#
# This file is part of Plastic-Auth-UI.
#
# Plastic-Auth-UI is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Plastic-Auth-UI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Context loaded and saved in WSGI requests"""


from suqui1 import contexts

from . import conf


__all__ = ['Ctx', 'null_ctx']


class Ctx(contexts.Ctx):
    conf = conf


null_ctx = Ctx()
null_ctx._lang = ['fr-FR', 'fr']

