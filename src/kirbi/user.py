##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Kirbi User module

This is currently (Aug. 18 2007) not used.

The code is tested (see doctests at ftests/user.txt and below), but has
not been integrated into Kirbi because I am uncertain about the wisdom
of creating a UserFolder which will behave as a utility but also as a
container of content (User instances, which in turn would contain Copy
instances etc.). How would traversal work, form example?

For now, I'll stick with a regular PrincipalFolder/Internal principal for
user management, and create a plain Collection class to hold the user's
Copies.
"""

import grok
from interfaces import IUser
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.security.interfaces import IAuthentication
from zope.interface import Interface, implements, invariant, Invalid
import sha
import app

class UserFolder(grok.Container):
    implements(IAuthenticatorPlugin)

    def principalInfo(self, id):
        """Find a principal given an id"""
        if id in self:
            # in Kirbi, the login and the id are the same
            return IPrincipalInfo(self[id])
        
    def authenticateCredentials(self, credentials):
        """Authenticate a principal"""
        id = credentials['login']
        user = self.get(id)
        if user is not None:
            given_hash = sha.new(credentials['password']).hexdigest()
            if user.password_hash == given_hash:
                return IPrincipalInfo(self[id])

class User(grok.Container):
    """A Kirbi user implementation.

    A User will contain Copy instances, representing book copies
    owned by the user.

        >>> alice = User('alice', u'Alice Cooper', u'headless-chicken')
        >>> IUser.providedBy(alice)
        True
        >>> alice.name_and_login()
        u'Alice Cooper (alice)'
        
    The password is not saved, only a SHA hash::

        >>> alice.password is None
        True
        >>> alice.password_hash
        'f030ff587c602e0e9a68aba75f41c51a0dc22c62'

    """

    implements(IUser)

    login = u''
    name = u''
    password_hash = ''

    def __init__(self, login, name, password, password_confirmation=None):
        super(User, self).__init__()
        self.login = login
        self.name = name
        if ((password_confirmation is not None)
                and password != password_confirmation):
            raise ValueError, u'Password and confirmation do not match'
        self.password_hash = sha.new(password).hexdigest()
        # we don't want to store the clear password
        self.password = self.password_confirmation = None

    def name_and_login(self):
        if self.name:
            return '%s (%s)' % (self.name, self.login)
        else:
            return self.login

class PrincipalInfoAdapter(grok.Adapter):
    grok.context(User)
    grok.implements(IPrincipalInfo)

    def __init__(self, context):
        self.context = context

    def getId(self):
        return self.context.login

    def setId(self, id):
        self.context.login = id

    id = property(getId, setId)

    def getTitle(self):
        return self.context.name

    def setTitle(self, title):
        self.context.name = title

    title = property(getTitle, setTitle)

    @property
    def description(self):
        return self.context.name_and_login()

class UserSearch(grok.View):
    grok.context(UserFolder)
    grok.name('index')

    def update(self, query=None):
        self.results_title = '%d users' % len(self.context)

