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

import pytest

from indico.testing.mocks import MockConference, MockConferenceHolder
from MaKaC.conference import ConferenceHolder


@pytest.yield_fixture
def create_event(monkeypatch, monkeypatch_methods):
    """Returns a callable which lets you create dummy events"""
    monkeypatch_methods('MaKaC.conference.ConferenceHolder', MockConferenceHolder)
    monkeypatch.setattr('MaKaC.conference.Conference', MockConference)  # for some isinstance checks

    _events = []
    ch = ConferenceHolder()

    def _create_event(id_):
        event = MockConference()
        event.id = id_
        ch.add(event)
        _events.append(event)
        return event

    yield _create_event

    for event in _events:
        ch.remove(event)


@pytest.fixture
def dummy_event(create_event):
    """Creates a mocked dummy event"""
    return create_event('0')
