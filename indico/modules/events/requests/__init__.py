# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from flask import session

from indico.core import signals
from indico.modules.events.requests.util import get_request_definitions, is_request_manager
from indico.modules.events.requests.base import RequestDefinitionBase, RequestFormBase
from indico.modules.events.requests.models.requests import Request, RequestState
from indico.web.flask.util import url_for
from MaKaC.webinterface.wcomponents import SideMenuItem


__all__ = ('RequestDefinitionBase', 'RequestFormBase')


@signals.app_created.connect
def _check_request_definitions(app, **kwargs):
    # This will raise RuntimeError if the request type names are not unique
    get_request_definitions()


@signals.event_management.sidemenu.connect
def _extend_event_management_menu(event, **kwargs):
    visible = bool(get_request_definitions()) and (event.canModify(session.user) or
                                                   is_request_manager(session.user))
    return 'requests', SideMenuItem('Services', url_for('requests.event_requests', event), visible=visible)


@signals.users.merged.connect
def _merge_users(target, source, **kwargs):
    Request.find(created_by_id=source.id).update({Request.created_by_id: target.id})
    Request.find(processed_by_id=source.id).update({Request.processed_by_id: target.id})


@signals.event.deleted.connect
def _event_deleted(event, **kwargs):
    if event.has_legacy_id:
        return
    event_id = int(event.id)
    requests = Request.find(event_id=event_id)
    for req in requests.filter(Request.state.in_((RequestState.accepted, RequestState.pending))):
        req.definition.withdraw(req, notify_event_managers=False)
    requests.delete()
