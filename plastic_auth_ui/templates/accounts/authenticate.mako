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


<%inherit file="/site.mako"/>


<%def name="breadcrumb()" filter="trim">
</%def>


<%def name="container_content()" filter="trim">
    <div id="sign-in-form"></div>
</%def>


<%def name="scripts()" filter="trim">
    <%parent:scripts/>
    <script>
var renderSignInBox = require('sign-in');
<%
    session = ctx.session
%>\
var session = {synchronizer_token: ${session.synchronizer_token | n, js}};
renderSignInBox(
    ${client_id | n, js},
    document.getElementById('sign-in-form'),
    session,
    ${state | n, js}
);
    </script>
</%def>


<%def name="title_content()" filter="trim">
${_(u'Authentication')} - ${parent.title_content()}
</%def>

