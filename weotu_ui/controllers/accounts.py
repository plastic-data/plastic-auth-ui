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


"""Controllers for accounts"""


import collections
import datetime
import json
import logging
import re
import urllib2
import urlparse
import uuid

from biryani1 import strings
import pymongo
import requests
from suq1 import paginations
from suqui1 import urls, wsgihelpers
import webob
import webob.multidict

from .. import conf, contexts, conv, model, templates


inputs_to_account_admin_data = conv.struct(
    dict(
        admin = conv.pipe(
            conv.guess_bool,
            conv.default(False),
            ),
        email = conv.pipe(
            conv.input_to_email,
            conv.not_none,
            ),
        full_name = conv.pipe(
            conv.cleanup_line,
            conv.not_none,
            ),
        ),
    default = 'drop',
    )
inputs_to_account_data = conv.struct(
    dict(
        email = conv.pipe(
            conv.input_to_email,
            conv.not_none,
            ),
        full_name = conv.pipe(
            conv.cleanup_line,
            conv.not_none,
            ),
        ),
    default = 'drop',
    )
log = logging.getLogger(__name__)


@wsgihelpers.wsgify
def admin_delete(req):
    ctx = contexts.Ctx(req)
    account = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Deletion unauthorized"),
            message = ctx._("You can not delete an account."),
            title = ctx._('Operation denied'),
            )
    if user._id != account._id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete an account."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        account.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Account.get_admin_class_url(ctx))
    return templates.render(ctx, '/accounts/admin-delete.mako', account = account)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    account = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Edition unauthorized"),
            message = ctx._("You can not edit an account."),
            title = ctx._('Operation denied'),
            )
    if user._id != account._id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit an account."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            admin = u'1' if account.admin else None,
            email = account.email,
            full_name = account.full_name,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_account_inputs_from_params(ctx, req.POST)
        if model.is_admin(ctx):
            data, errors = inputs_to_account_admin_data(inputs, state = ctx)
        else:
            data, errors = inputs_to_account_data(inputs, state = ctx)
        if errors is None:
            data['slug'], error = conv.pipe(
                conv.input_to_slug,
                conv.not_none,
                )(data['full_name'], state = ctx)
            if error is not None:
                errors = dict(full_name = error)
        if errors is None:
            if model.Account.find(
                    dict(
                        _id = {'$ne': account._id},
                        email = data['email'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('An account with the same email already exists.'))
            if model.Account.find(
                    dict(
                        _id = {'$ne': account._id},
                        slug = data['slug'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(full_name = ctx._('An account with the same name already exists.'))
        if errors is None:
            account.set_attributes(**data)
            if account.api_key is None:
                account.api_key = unicode(uuid.uuid4())
            account.compute_attributes()
            account.save(ctx, safe = True)

            # View account.
            return wsgihelpers.redirect(ctx, location = account.get_admin_url(ctx))
    return templates.render(ctx, '/accounts/admin-edit.mako', account = account, errors = errors, inputs = inputs)


@wsgihelpers.wsgify
def admin_index(req):
    ctx = contexts.Ctx(req)
    model.is_admin(ctx, check = True)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        page = params.get('page'),
        sort = params.get('sort'),
        term = params.get('term'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                page = conv.pipe(
                    conv.input_to_int,
                    conv.test_greater_or_equal(1),
                    conv.default(1),
                    ),
                sort = conv.pipe(
                    conv.cleanup_line,
                    conv.test_in(['slug', 'updated']),
                    ),
                term = conv.input_to_words,
                ),
            ),
        conv.rename_item('page', 'page_number'),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Account search error: {}').format(errors))

    criteria = {}
    if data['term'] is not None:
        criteria['words'] = {'$all': [
            re.compile(u'^{}'.format(re.escape(word)))
            for word in data['term']
            ]}
    cursor = model.Account.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'slug':
        cursor.sort([('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'updated':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('slug', pymongo.ASCENDING)])
    accounts = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/accounts/admin-index.mako', accounts = accounts, data = data, errors = errors,
        inputs = inputs, pager = pager)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    account = ctx.node

    user = model.get_user(ctx, check = True)
    if user._id != account._id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("View forbidden"),
            message = ctx._("You can not view an account."),
            title = ctx._('Operation denied'),
            )

    return templates.render(ctx, '/accounts/admin-view.mako', account = account)


@wsgihelpers.wsgify
def api1_authenticate(req):
    ctx = contexts.Ctx(req)

    assert req.method == 'POST', req.method

    session = ctx.session
    if session is None:
        ctx.session = session = model.Session()
        session.synchronizer_token = unicode(uuid.uuid4())
        session.token = unicode(uuid.uuid4())
    session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
    session.save(ctx, safe = True)
    session_json = collections.OrderedDict((
        ('synchronizer_token', session.synchronizer_token),
        ))

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(object_pairs_hook = collections.OrderedDict),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request POST body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    session = session_json,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                )
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)

    data, errors = conv.struct(
        dict(
            client_id = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_object_id_str,
                conv.not_none,
                ),
            email = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_email,
                conv.not_none,
                ),
            password = conv.pipe(
                conv.test_isinstance(basestring),
                conv.cleanup_line,
                conv.not_none,
                ),
            state = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_uuid_str,
                conv.not_none,
                ),
            synchronizer_token = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_uuid_str,
                conv.test_equals(session.synchronizer_token),
                conv.not_none,
                ),
            ),
        )(inputs, state = ctx)
    if inputs.get('password'):
        # Replace password in inputs to ensure that it will not be sent back to caller.
        inputs['password'] = u'X' * len(inputs['password'])
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [errors],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                session = session_json,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )

    # Require an authentication session to API.
    request = urllib2.Request(
        urlparse.urljoin(
            conf['api_site_url'],
            u'api/1/authenticate',
            ).encode('utf-8'),
        headers = {
            'Content-Type': 'application/json',
#            'User-Agent': TODO,
            },
        )
    try:
        response = urllib2.urlopen(request, unicode(json.dumps(
            dict(
                access_token = conf['api_token'],
                email = data['email'],
                password = data['password'],
                relying_party_id = data['client_id'],
                state = data['state'],
                ),
            encoding = 'utf-8',
            ensure_ascii = False,
            indent = 2,
            )).encode('utf-8'))
    except urllib2.HTTPError as response:
        response_text = response.read()
        if 400 <= response.code < 404:
            response_json, error = conv.pipe(
                conv.make_input_to_json(object_pairs_hook = collections.OrderedDict),
                conv.test_isinstance(dict),
                conv.struct(
                    dict(
                        error = conv.pipe(
                            conv.test_isinstance(dict),
                            conv.struct(
                                dict(
                                    code = conv.pipe(
                                        conv.test_isinstance(int),
                                        conv.not_none,
                                        ),
                                    errors = conv.pipe(
                                        conv.test_isinstance(list),
                                        conv.test(lambda errors: len(errors) == 1),
                                        conv.uniform_sequence(
                                            conv.pipe(
                                                conv.test_isinstance(dict),
                                                conv.not_none,
                                                ),
                                            ),
                                        conv.not_none,
                                        ),
                                    message = conv.pipe(
                                        conv.test_isinstance(basestring),
                                        conv.not_none,
                                        ),
                                    ),
                                default = conv.noop,
                                ),
                            conv.not_none,
                            ),
                        ),
                    default = conv.noop,
                    ),
                conv.not_none,
                )(response_text, state = ctx)
            if error is not None:
                log.exception(response_text)
                raise
            error = response_json['error']
            errors = error['errors'][0]
            errors.pop('access_token', None)
            relying_party_id_error = errors.pop('relying_party_id', None)
            if relying_party_id_error is not None:
                errors['client_id'] = relying_party_id_error
            if not errors:
                log.exception(response_text)
                raise
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = error['code'],
                        errors = [errors],
                        message = error['message'],
                        ).iteritems())),
                    method = req.script_name,
                    params = inputs,
                    session = session_json,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                )
        else:
            log.exception(response_text)
            raise
    response_text = response.read()
    authentication = conv.check(conv.pipe(
        conv.make_input_to_json(object_pairs_hook = collections.OrderedDict),
        conv.test_isinstance(dict),
        conv.struct(
            dict(
                authentication = conv.pipe(
                    conv.test_isinstance(dict),
                    conv.not_none,
                    ),
                ),
            default = conv.noop,
            ),
        conv.function(lambda response: response['authentication']),
        conv.not_none,
        ))(response_text, state = ctx)
    session.authentication = authentication
    session.save(ctx, safe = True)

    if req.cookies.get(conf['cookie']) != session.token:
        req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            authentication = authentication,
            method = req.script_name,
            params = inputs,
            session = session_json,
            url = req.url.decode('utf-8'),
            ).iteritems())),
        )


@wsgihelpers.wsgify
def api1_typeahead(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        q = params.get('q'),
        )
    data, errors = conv.struct(
        dict(
            q = conv.input_to_words,
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Account search error: {}').format(errors))

    criteria = {}
    if data['q'] is not None:
        criteria['words'] = {'$all': [
            re.compile(u'^{}'.format(re.escape(word)))
            for word in data['q']
            ]}
    cursor = model.Account.get_collection().find(criteria, ['full_name'])
    return wsgihelpers.respond_json(ctx,
        [
            account_attributes['full_name']
            for account_attributes in cursor.limit(10)
            ],
        headers = headers,
        )


@wsgihelpers.wsgify
def authenticate(req):
    """Process authorization request and authenticate user."""
    ctx = contexts.Ctx(req)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        client_id = params.get('client_id'),
        state = params.get('state'),
        )
    data, errors = conv.struct(
        dict(
            client_id = conv.pipe(
                conv.input_to_object_id_str,
                conv.not_none,
                ),
            state = conv.pipe(
                conv.input_to_uuid_str,
                conv.not_none,
                ),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.bad_request(ctx, explanation = ctx._(u'Authentication Error: {0}').format(errors))

    session = ctx.session
    if session is None:
        ctx.session = session = model.Session()
        session.synchronizer_token = unicode(uuid.uuid4())
        session.token = unicode(uuid.uuid4())
    session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
    session.save(ctx, safe = True)

    if req.cookies.get(conf['cookie']) != session.token:
        req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return templates.render(ctx, '/accounts/authenticate.mako', client_id = data['client_id'], state = data['state'])


def extract_account_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        admin = params.get('admin'),
        email = params.get('email'),
        full_name = params.get('full_name'),
        )


@wsgihelpers.wsgify
def login(req):
    """Authorization request"""
    ctx = contexts.Ctx(req)

    assert req.method == 'POST'
    params = req.POST
    inputs = dict(
        assertion = params.get('assertion'),
        )
    data, errors = conv.struct(
        dict(
            assertion = conv.pipe(
                conv.cleanup_line,
                conv.not_none,
                ),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.bad_request(ctx, explanation = ctx._(u'Login Error: {0}').format(errors))

    response = requests.post('https://verifier.login.persona.org/verify',
        data = dict(
            audience = urls.get_full_url(ctx),
            assertion = data['assertion'],
            ),
        verify = True,
        )
    if not response.ok:
        return wsgihelpers.internal_error(ctx,
            dump = response.text,
            explanation = ctx._(u'Error while verifying authentication assertion'),
            )
    verification_data = json.loads(response.content)
    # Check if the assertion was valid.
    if verification_data['status'] != 'okay':
        return wsgihelpers.internal_error(ctx,
            dump = response.text,
            explanation = ctx._(u'Error while verifying authentication assertion'),
            )

    user = model.Account.find_one(
        dict(
            email = verification_data['email'],
            ),
        as_class = collections.OrderedDict,
        )
    if user is None:
        user = model.Account()
        user._id = unicode(uuid.uuid4())
        user.api_key = unicode(uuid.uuid4())
        user.email = verification_data['email']
        user.full_name = verification_data['email']
        user.slug = strings.slugify(user.full_name)
        user.compute_attributes()
        user.save(ctx, safe = True)
    ctx.user = user

    session = ctx.session
    if session is None:
        ctx.session = session = model.Session()
        session.synchronizer_token = unicode(uuid.uuid4())
        session.token = unicode(uuid.uuid4())
    session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
    session.user_id = user._id
    session.save(ctx, safe = True)

    if req.cookies.get(conf['cookie']) != session.token:
        req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return 'Login succeeded.'


@wsgihelpers.wsgify
def logout(req):
    ctx = contexts.Ctx(req)

    assert req.method == 'POST'

    session = ctx.session
    if session is not None:
        session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
        if session.user_id is not None:
            del session.user_id
        session.save(ctx, safe = True)
        if req.cookies.get(conf['cookie']) != session.token:
            req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return 'Logout succeeded.'

#    session = ctx.session
#    if session is not None:
#        session.delete(ctx, safe = True)
#        ctx.session = None
#        if req.cookies.get(conf['cookie']) is not None:
#            req.req.response.delete_cookie(conf['cookie'])
#    return 'Logout succeeded.'


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    account, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Account.make_id_or_slug_or_words_to_instance(),
        )(req.urlvars.get('id_or_slug_or_words'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Account Error: {}').format(error))(
            environ, start_response)

    ctx.node = account

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
        (('GET', 'POST'), '^/delete/?$', admin_delete),
        (('GET', 'POST'), '^/edit/?$', admin_edit),
        )
    return router(environ, start_response)


def route_admin_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', admin_index),
        (None, '^/(?P<id_or_slug_or_words>[^/]+)(?=/|$)', route_admin),
        )
    return router(environ, start_response)


def route_api1(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    account, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Account.make_id_or_slug_or_words_to_instance(),
        )(req.urlvars.get('id_or_slug_or_words'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Account Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = account

    router = urls.make_router(
        ('DELETE', '^/?$', api1_delete),
        ('GET', '^/?$', api1_get),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', api1_index),
        ('GET', '^/typeahead/?$', api1_typeahead),
        (None, '^/(?P<id_or_slug_or_words>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
