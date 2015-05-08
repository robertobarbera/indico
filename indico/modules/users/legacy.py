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

from persistent import Persistent

from indico.core.auth import multipass
from indico.modules.groups import GroupProxy
from indico.modules.rb.util import rb_is_admin
from indico.modules.users import User, logger
from indico.modules.auth import Identity
from indico.util.caching import memoize_request
from indico.util.fossilize import fossilizes, Fossilizable
from indico.util.string import to_unicode, return_ascii, encode_utf8
from indico.util.redis import write_client as redis_write_client
from indico.util.redis import avatar_links
from MaKaC.common import HelperMaKaCInfo
from MaKaC.common.Locators import Locator
from MaKaC.fossils.user import IAvatarFossil, IAvatarMinimalFossil


class AvatarUserWrapper(Persistent, Fossilizable):
    """Avatar-like wrapper class that holds a DB-stored user."""

    fossilizes(IAvatarFossil, IAvatarMinimalFossil)

    def __init__(self, user_id):
        self.id = str(user_id)

    @property
    @memoize_request
    def _original_user(self):
        # A proper user, with an id that can be mapped directly to sqlalchemy
        if isinstance(self.id, int) or self.id.isdigit():
            return User.get(int(self.id))
        # A user who had no real indico account but an ldap identifier/email.
        # In this case we try to find his real user and replace the ID of this object
        # with that user's ID.
        data = self.id.split(':')
        # TODO: Once everything is in SQLAlchemy this whole thing needs to go away!
        user = None
        if data[0] == 'LDAP':
            identifier = data[1]
            email = data[2]
            # You better have only one ldap provider or at least different identifiers ;)
            identity = Identity.find_first(Identity.provider != 'indico', Identity.identifier == identifier)
            if identity:
                user = identity.user
        elif data[0] == 'Nice':
            email = data[1]
        else:
            return None
        if not user:
            user = User.find_first(User.all_emails.contains(email))
        if user:
            self._old_id = self.id
            self.id = str(user.id)
            logger.info("Updated legacy user id ({} => {})"
                        .format(self._old_id, self.id))
        return user

    @property
    @memoize_request
    def user(self):
        user = self._original_user
        if user is not None and user.is_deleted and user.merged_into_id is not None:
            while user.merged_into_id is not None:
                user = user.merged_into_user
        return user

    def getId(self):
        return str(self.user.id) if self.user else str(self.id)

    @property
    def api_key(self):
        return self.user.api_key if self.user else None

    def linkTo(self, obj, role):
        if not self.user or self.user.is_deleted:
            return
        link = self.user.link_to(obj, role)
        if link and redis_write_client:
            event = avatar_links.event_from_obj(obj)
            if event:
                avatar_links.add_link(self, event, '{}_{}'.format(link.type, link.role))

    def unlinkTo(self, obj, role):
        if not self.user or self.user.is_deleted:
            return
        links = self.user.unlink_to(obj, role)
        if redis_write_client:
            for link in links:
                event = avatar_links.event_from_obj(obj)
                if event:
                    avatar_links.del_link(self, event, '{}_{}'.format(link.type, link.role))

    def getStatus(self):
        return 'deleted' if not self.user or self.user.is_deleted else 'activated'

    def isActivated(self):
        # All accounts are activated during the transition period
        return True

    def isDisabled(self):
        # The user has been blocked or deleted (due to merge)
        return not self.user or self.user.is_blocked or self.user.is_deleted

    def setName(self, name, reindex=False):
        self.user.first_name = to_unicode(name)

    @encode_utf8
    def getName(self):
        return self.user.first_name if self.user else ''

    getFirstName = getName

    def setSurName(self, surname, reindex=False):
        self.user.last_name = to_unicode(surname)

    @encode_utf8
    def getSurName(self):
        return self.user.last_name if self.user else ''

    getFamilyName = getSurName

    @encode_utf8
    def getFullName(self):
        if not self.user:
            return ''
        return self.user.get_full_name(last_name_first=True, last_name_upper=True,
                                       abbrev_first_name=False, show_title=False)

    @encode_utf8
    def getStraightFullName(self, upper=True):
        if not self.user:
            return ''
        return self.user.get_full_name(last_name_first=False, last_name_upper=upper,
                                       abbrev_first_name=False, show_title=False)

    getDirectFullNameNoTitle = getStraightFullName

    @encode_utf8
    def getAbrName(self):
        if not self.user:
            return ''
        return self.user.get_full_name(last_name_first=True, last_name_upper=False,
                                       abbrev_first_name=True, show_title=False)

    @encode_utf8
    def getStraightAbrName(self):
        if not self.user:
            return ''
        return self.user.get_full_name(last_name_first=False, last_name_upper=False,
                                       abbrev_first_name=True, show_title=False)

    def setOrganisation(self, affiliation, reindex=False):
        self.user.affiliation = to_unicode(affiliation)

    @encode_utf8
    def getOrganisation(self):
        return self.user.affiliation if self.user else ''

    getAffiliation = getOrganisation

    def setTitle(self, title):
        self.user.title = to_unicode(title)

    @encode_utf8
    def getTitle(self):
        return self.user.title if self.user else ''

    def setTimezone(self, tz):
        self.user.settings.set('timezone', to_unicode(tz))

    @encode_utf8
    def getTimezone(self):
        default = HelperMaKaCInfo.getMaKaCInfoInstance().getTimezone()
        return self.user.settings.get('timezone', default) if self.user else default

    def getDisplayTZMode(self):
        return 'MyTimezone' if self.user and self.user.settings.get('force_timezone') else 'Event Timezone'

    def setDisplayTZMode(self, display_tz='Event Timezone'):
        self.user.settings.set('force_timezone', display_tz == 'MyTimezone')

    @encode_utf8
    def getAddress(self):
        return self.user.address if self.user else ''

    def setAddress(self, address):
        self.user.address = to_unicode(address)

    def getEmails(self):
        # avoid 'stale association proxy'
        user = self.user
        return set(user.all_emails) if user else set()

    @encode_utf8
    def getEmail(self):
        return self.user.email if self.user else ''

    email = property(getEmail)

    def setEmail(self, email, reindex=False):
        self.user.email = to_unicode(email)

    def hasEmail(self, email):
        user = self.user  # avoid 'stale association proxy'
        if not user:
            return False
        return email.lower() in user.all_emails

    @encode_utf8
    def getTelephone(self):
        return self.user.phone if self.user else ''

    def getFax(self):
        # Some older code still clones fax, etc...
        # it's never shown in the interface anyway.
        return ''

    getPhone = getTelephone

    def setTelephone(self, phone):
        self.user.phone = to_unicode(phone)

    setPhone = setTelephone

    def isRegisteredInConf(self, conf):
        if not self.user:
            return False
        return any(obj for obj in self.user.get_linked_objects('registration', 'registrant')
                   if obj.getConference() == conf)

    def getRegistrantById(self, conf_id):
        if not self.user:
            return None
        return next((obj for obj in self.user.get_linked_objects('registration', 'registrant')
                    if obj.getConference().id == conf_id), None)

    def hasSubmittedEvaluation(self, evaluation):
        if not self.user:
            return False
        for submission in evaluation.getSubmissions():
            submitter = submission.getSubmitter()
            if submitter and submitter.id == self.user.id:
                return True
        return False

    def containsUser(self, avatar):
        if self.user is None:
            return False
        return int(avatar.id) == self.user.id if avatar else False

    containsMember = containsUser

    def canModify(self, aw_or_user):
        if hasattr(aw_or_user, 'getUser'):
            aw_or_user = aw_or_user.getUser()
        return self.canUserModify(aw_or_user)

    def canUserModify(self, avatar):
        if not self.user:
            return False
        return avatar.id == str(self.user.id) or avatar.user.is_admin

    def getLocator(self):
        d = Locator()
        if self.user:
            d["userId"] = self.user.id
        return d

    def isAdmin(self):
        if not self.user:
            return False
        return self.user.is_admin

    @encode_utf8
    def getLang(self):
        return self.user.settings.get('lang') if self.user else HelperMaKaCInfo.getMaKaCInfoInstance().getLang()

    def setLang(self, lang):
        self.user.settings.set('lang', to_unicode(lang))

    def __eq__(self, other):
        if not isinstance(other, (AvatarUserWrapper, User)):
            return False
        elif str(self.id) == str(other.id):
            return True
        elif self.user:
            return str(self.user.id) == str(other.id)
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(str(self.id))

    @return_ascii
    def __repr__(self):
        if self.user is None:
            return u'<AvatarUserWrapper {}: user does not exist>'.format(self.id)
        elif self._original_user.merged_into_user:
            return u'<AvatarUserWrapper {}: {} ({}) [{}]>'.format(
                self.id, self._original_user.full_name, self._original_user.email, self.user.id)
        else:
            return u'<AvatarUserWrapper {}: {} ({})>'.format(self.id, self.user.full_name, self.user.email)


class AvatarProvisionalWrapper(Fossilizable):
    """
    Wraps provisional data for users that are not in the DB yet
    """

    fossilizes(IAvatarFossil, IAvatarMinimalFossil)

    def __init__(self, identity_info):
        self.identity_info = identity_info
        self.data = identity_info.data

    def getId(self):
        return u"{}:{}".format(self.identity_info.provider.name, self.identity_info.identifier)

    id = property(getId)

    @encode_utf8
    def getEmail(self):
        return self.data['email']

    def getEmails(self):
        return [self.data['email']]

    @encode_utf8
    def getFirstName(self):
        return self.data.get('first_name', '')

    @encode_utf8
    def getFamilyName(self):
        return self.data.get('last_name', '')

    def getStraightFullName(self):
        return '{} {}'.format(self.data.get('first_name', ''), self.data.get('last_name', ''))

    def getTitle(self):
        return ''

    @encode_utf8
    def getTelephone(self):
        return self.data.get('phone', '')

    getPhone = getTelephone

    @encode_utf8
    def getOrganisation(self):
        return self.data.get('affiliation', '')

    getAffiliation = getOrganisation

    def getFax(self):
        return None

    def getAddress(self):
        return u''

    @return_ascii
    def __repr__(self):
        return u'<AvatarProvisionalWrapper {}: {} ({first_name} {last_name})>'.format(
            self.identity_info.provider.name,
            self.identity_info.identifier,
            **self.data.to_dict())
