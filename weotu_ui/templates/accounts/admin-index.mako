## -*- coding: utf-8 -*-


## Weotu-UI -- Accounts & authentication user interface
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2014 Emmanuel Raviart
## https://gitorious.org/weotu
##
## This file is part of Weotu-UI.
##
## Weotu-UI is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## Weotu-UI is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
from weotu_ui import model, urls
%>


<%inherit file="/object-admin-index.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li class="active">${_(u'Accounts')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No account found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Account {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Accounts {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single account")}</h2>
        % else:
        <h2>${_(u"{} accounts").format(pager.item_count)}</h2>
        % endif
        <%self:pagination object_class="${model.Account}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
                    <th>${_(u"Email")}</th>
        % if data['sort'] == 'name':
                    <th>${_(u"Full Name")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
        % else:
                    <th><a href="${model.Account.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'slug'))}">${_(u"Full Name")}</a></th>
        % endif
                    <th>${_(u"Profile")}</th>
        % if data['sort'] == 'updated':
                    <th>${_(u"Updated")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
        % else:
                    <th><a href="${model.Account.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'updated'))}">${_(u"Updated")}</a></th>
        % endif
                 </tr>
            </thead>
            <tbody>
        % for account in accounts:
                <tr>
                    <td><a href="${account.get_admin_url(ctx)}">${account.email or ''}</a></td>
                    <td>${account.full_name or ''}</td>
                    <td>${_(u'Administrator') if account.admin else ''}</td>
                    <td>${account.updated or ''}</td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Account}" pager="${pager}"/>
    % endif
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Account.get_admin_class_url(ctx)}" method="get" role="form">
            <input name="sort" type="hidden" value="${inputs['sort'] or ''}">
<%
    error = errors.get('term') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="term">${_("Term")}</label>
                <input class="form-control" id="term" name="term" type="text" value="${inputs['term'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${_('Search')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Accounts')} - ${parent.title_content()}
</%def>

