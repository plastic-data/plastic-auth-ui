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


"""The application's model objects"""


import sys

from suqui1 import accesses, setups, urls, wsgihelpers

from . import conf, templates


class Account(accesses.Account):
    description = None


class AuthenticationAccount(accesses.AuthenticationAccount):
    pass


class Session(accesses.Session):
    pass


def configure(ctx):
    setups.configure(ctx)


def get_user(ctx, check = False):
    user = ctx.user
    if user is UnboundLocalError:
#        session = ctx.session
#        ctx.user = user = session.user if session is not None else None
        ctx.user = user = None  # TODO: Remove.
    if user is None and check:
        raise wsgihelpers.unauthorized(ctx)
    return user


def init(components):
    setups.init(components)


def is_admin(ctx, check = False):
    user = get_user(ctx)
    if user is None or not user.admin:
        if user is not None and Account.find_one(dict(admin = True), []) is None:
            # Whem there is no admin, every logged user is an admin.
            return True
        if check:
            raise wsgihelpers.forbidden(ctx, message = ctx._(u"You must be an administrator to access this page."))
        return False
    return True


def setup(drop_indexes = False):
    """Setup MongoDb database."""
    import os
    from . import upgrades

    setups.setup(drop_indexes = drop_indexes, upgrades_dir = os.path.dirname(upgrades.__file__))

    Account.ensure_indexes()
    Session.ensure_indexes()

