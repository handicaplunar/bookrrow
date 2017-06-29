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
"""Kirbi
"""

import grok
from grok import index
from kirbi.pac import Pac
from kirbi.book import Book
from kirbi.collection import Collection
from kirbi.interfaces import IItem, IUser, ILease
from zope.interface import Interface, implements
from zope.component import getSiteManager
from zope.traversing import browser
from urllib import urlencode

from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager, IRole
from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.role import LocalRole
from zope import schema
from zope.component import getUtility

from zope.app.container.contained import NameChooser
from zope.app.container.interfaces import INameChooser

PAC_NAME = u'pac'
COLLECTIONS_FOLDER_NAME = u'u'

class AddCopy(grok.Permission):
    grok.name('kirbi.AddCopy')

class ManageBook(grok.Permission):
    grok.name('kirbi.ManageBook')

def setup_pau(pau):
    pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals',)

    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login'
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
    
def role_factory(*args):
    def factory():
        return LocalRole(*args)
    return factory

class Kirbi(grok.Application, grok.Container):
    """Peer-to-peer library system."""
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    grok.local_utility(role_factory(u'Book Owner'), IRole,
                       name='kirbi.Owner',
                       name_in_container='kirbi.Owner')
    def __init__(self):
        super(Kirbi, self).__init__()
        self.pac = self[PAC_NAME] = Pac()
        self.collections = self[COLLECTIONS_FOLDER_NAME] = CollectionsFolder()

@grok.subscribe(Kirbi, grok.IObjectAddedEvent)
def grant_permissions(app, event):
    role_manager = IRolePermissionManager(app)
    role_manager.grantPermissionToRole('kirbi.AddCopy', 'kirbi.Owner')
    role_manager.grantPermissionToRole('kirbi.ManageBook', 'kirbi.Owner')

class Index(grok.View):
    grok.context(Kirbi)

    def pac_url(self):
        return self.url(self.context.pac)

    def login_url(self):
        return self.url(self.context.userFolder,'login')

class BookIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(Book)

    title = index.Text()
    isbn13 = index.Field()
    searchableText = index.Text()

    creatorsSet = index.Set()
    
class ItemIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(IItem)
    
    manifestation_id = index.Field()
    owner_login = index.Field()
    
class LeaseIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(ILease)

    item_id = index.Field()
    lender_login = index.Field()
    borrower_login = index.Field()
    expected_return_date = index.Field()
    request_date = index.Field()
    status = index.Field()


class Master(grok.View):
    """The master page template macro."""
    # register this view for all objects
    grok.context(Interface)

class Login(grok.View):
    grok.context(Kirbi)

    def update(self, login_submit=None, login=None):
        # XXX: need to display some kind of feedback when the login fails
        if (not IUnauthenticatedPrincipal.providedBy(self.request.principal)
            and login_submit is not None):
            destination = self.request.get('camefrom')
            if not destination:
                home = self.context.collections[self.request.principal.id]
                destination = browser.absoluteURL(home, self.request)
            self.redirect(destination)

class Logout(grok.View):
    grok.context(Interface)
    def render(self):
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        self.redirect(self.application_url())

class Join(grok.AddForm):
    """User registration form"""
    grok.context(Kirbi)

    form_fields = grok.AutoFields(IUser)
    template = grok.PageTemplateFile('form.pt')
    form_title = u'User registration'

    ### XXX: find out how to display message of the Invalid exception raised
    ### by the password confirmation invariant (see interfaces.IUser)
    @grok.action('Save')
    def join(self, **data):
        #XXX: change this method to use our UserFolder and User class instead
        #     of PrincipalFolder and InternalPrincipal
        login = data['login']
        if login in self.context.collections: # duplicate login name
            ### XXX: find out how to display this message in the form template
            msg = u'Duplicate login. Please choose a different one.'
            self.redirect(self.url()+'?'+urlencode({'error_msg':msg}))
        else:
            title = data.get('name') or login # if name is blank or None, use login
            self.context.collections[login] = Collection(title)
        
            # add principal to principal folder
            pau = getUtility(IAuthentication)
            principals = pau['principals']
            principals[login] = InternalPrincipal(login, data['password'],
                                                  data['name'])
    
            # assign role to principal
            role_manager = IPrincipalRoleManager(self.context)
            role_manager.assignRoleToPrincipal('kirbi.Owner', 
                                   principals.prefix + login)
            self.redirect(self.url('login')+'?'+urlencode({'login':login}))
        
class CollectionsFolder(grok.Container):
    pass

class QuickNameChooser(grok.Adapter, NameChooser):
    """INameChooser adapter to generate sequential numeric ids without
       resorting to a linear search."""
    grok.context(grok.Container)
    implements(INameChooser)

    def nextId(self,fmt='%s'):
        """Binary search to quickly find an unused numbered key.

        This was designed to scale well when importing large batches of books
        without ISBN, while keeping the ids short.

        The algorithm generates a key right after the largest numbered key or
        in some unused lower numbered slot found by the second loop.

        If keys are later deleted in random order, some of the resulting slots
        will be reused and some will not.
        """
        i = 1
        while fmt%i in self.context:
            i *= 2
        blank = i
        full = i//2
        while blank > (full+1):
            i = (blank+full)//2
            if fmt%i in self.context:
                full = i
            else:
                blank = i
        return fmt%blank

    def chooseName(self, name, object):
        prefix = object.__class__.__name__[0].lower()
        name = name or self.nextId(prefix+'%d')
        # Note: potential concurrency problems of nextId are (hopefully)
        # handled by calling the super.QuickNameChooser
        return super(QuickNameChooser, self).chooseName(name, object)

 
