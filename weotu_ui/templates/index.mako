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


<%inherit file="site.mako"/>


<%def name="breadcrumb()" filter="trim">
</%def>


<%def name="container_content()" filter="trim">
    <%self:jumbotron/>
    <div id="index-box-container"></div>
</%def>


<%def name="jumbotron()" filter="trim">
    <div class="jumbotron">
        <div class="container">
            <h2>${_(u"Welcome to Weotu-UI")}</h2>
            <p>${_(u"Accounts & authentication user interface")}</p>
        </div>
    </div>
</%def>


<%def name="scripts()" filter="trim">
    <%parent:scripts/>
    <script>
var renderIndexBox = require('index');
<%
    session = ctx.session
%>\
    % if session is None:
var session = null;
    % else:
var session = {synchronizer_token: ${session.synchronizer_token | n, js}};
    % endif
renderIndexBox(
    document.getElementById('index-box-container'),
    session
);
    </script>
</%def>
