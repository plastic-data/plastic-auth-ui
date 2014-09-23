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
from plastic_auth_ui import conf, model, urls
%>


<%inherit file="/site.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Account.get_admin_class_url(ctx)}">${_(u"Accounts")}</a></li>
            <li><a href="${account.get_admin_url(ctx)}">${account.get_title(ctx)}</a></li>
            <li class="active">${_(u'Edit')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <form action="${account.get_admin_url(ctx, 'edit')}" method="post" role="form">
            <%self:hidden_fields/>
            <fieldset>
                <legend>${_(u'Edition of %s') % account.get_title(ctx)}</legend>
                <%self:error_alert/>
                <%self:form_fields/>
                <button class="btn btn-primary" name="submit" type="submit"><span class="glyphicon glyphicon-ok"></span> ${_('Save')}</button>
            </fieldset>
        </form>
</%def>


<%def name="form_fields()" filter="trim">
<%
    error = errors.get('email') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="email">${_("Email")}</label>
                    <input class="form-control" id="email" name="email" required type="email" value="${
                            inputs['email'] or ''}">
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
<%
    error = errors.get('full_name') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="full_name">${_("Full Name")}</label>
                    <input class="form-control" id="full_name" name="full_name" required type="text" value="${
                            inputs['full_name'] or ''}">
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
    % if model.is_admin(ctx):
<%
        error = errors.get('admin') if errors is not None else None
%>\
                <div class="checkbox${' has-error' if error else ''}">
                    <label>
                        <input${' checked' if inputs['admin'] else ''} id="admin" name="admin" type="checkbox" value="1">
                        ${_(u'Administrator')}
                    </label>
        % if error:
                    <span class="help-block">${error}</span>
        % endif
                </div>
    % endif
</%def>


<%def name="hidden_fields()" filter="trim">
</%def>


<%def name="title_content()" filter="trim">
${_(u'Edit')} - ${account.get_title(ctx)} - ${parent.title_content()}
</%def>

