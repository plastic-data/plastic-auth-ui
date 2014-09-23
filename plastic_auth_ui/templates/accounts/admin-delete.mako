## -*- coding: utf-8 -*-


## Plastic-Auth-UI -- Accounts & authentication user interface
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2014 Emmanuel Raviart
## https://github.com/plastic-data/plastic-auth-ui
##
## This file is part of Plastic-Auth-UI.
##
## Plastic-Auth-UI is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## Plastic-Auth-UI is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
from plastic_auth_ui import model, urls
%>


<%inherit file="/site.mako"/>
<%namespace name="view" file="admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Account.get_admin_class_url(ctx)}">${_(u"Accounts")}</a></li>
            <li><a href="${account.get_admin_url(ctx)}">${account.get_title(ctx)}</a></li>
            <li class="active">${_(u'Delete')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${_(u'Deletion of {}').format(account.get_title(ctx))}</h2>
        <p class="confirm">${_(u"Are you sure that you want to delete this account?")}</p>
        <form method="post" action="${account.get_admin_url(ctx, 'delete')}">
            <%view:view_fields/>
            <button class="btn btn-danger" name="submit" type="submit"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_(u'Delete')} - ${account.get_title(ctx)} - ${parent.title_content()}
</%def>

