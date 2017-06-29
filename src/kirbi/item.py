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
"""Kirbi book exemplar class
"""

import grok
from interfaces import IItem, IBook, ILease
from zope.interface import Interface, implements, invariant
from zope import schema
from datetime import datetime, timedelta
from zope.app.container.interfaces import INameChooser


class Item(grok.Container):
    """An exemplar of a book.

    See note at interfaces.IItem.

    >>> it = Item('','Nobody')
    >>> IItem.providedBy(it)
    True

    Now let's make it provide IBook.

    >>> from kirbi.book import Book
    >>> book = Book('Any Book')
    >>> it.manifestation = book

    >>> IBook.providedBy(it)
    True

    """

    implements(IItem, IBook)

    def __init__(self, manifestation_id, owner_login, description=u'',
                 catalog_datetime=None):
        super(Item, self).__init__()
        self.manifestation_id = manifestation_id
        if manifestation_id:
            self.manifestation = grok.getSite().pac.get(manifestation_id)
        self.description = description
        self.owner_login = owner_login
        if catalog_datetime is None:
            self.catalog_datetime = datetime.now()

    def getCoverId(self):
        return self.manifestation.__name__

    def __getattr__(self,name):
        # XXX: Martijn Faassen sugests a refactoring here, implementing
        # the Item->Manifestation relationship not using this sort of
        # dynamically hacked inheritance but as an association
        return getattr(self.manifestation, name)
    
    def addLease(self, lease):
        name = INameChooser(self).chooseName(lease.borrower_login, lease)
        self[name] = lease
        return lease.__name__

    
class Borrow(grok.View):
    # control: duration needed
    # text area: suggested time/place for pickup
    grok.context(Item)
    
    
    def __init__(self, context, request):
        super(Borrow, self).__init__(context, request)
    
        self.form_title = u'Borrow item'
        self.borrow_from = u'%s (%s)' % (context.__parent__.title,
                                         context.__parent__.__name__)

    def getDurations(self):
        return u'minute week month quarter semester year'.split()

    def coverUrl(self):
        cover_name = 'covers/large/'+self.context.manifestation_id+'.jpg'
        return self.static.get(cover_name,
                               self.static['covers/small-placeholder.jpg'])()
    
    def update(self, duration=None, pickup=''):
        if duration is not None:
            lease = Lease(self.context.__name__, self.context.__parent__.__name__,
                          self.request.principal.id, duration, pickup)
            
            self.context.addLease(lease)
    
            self.redirect(self.url(self.context))
            
class Lease(grok.Model):
    """A book lease.
    
    >>> start = datetime(2007,1,1,0,0,0)
    >>> start.isoformat()
    '2007-01-01T00:00:00'

    >>> Lease.calculateDue(start,u'minute').isoformat()
    '2007-01-01T00:01:00'
    >>> Lease.calculateDue(start,u'hour').isoformat()
    '2007-01-01T01:00:00'
    >>> Lease.calculateDue(start,u'day').isoformat()
    '2007-01-02T00:00:00'
    >>> Lease.calculateDue(start,u'week').isoformat()
    '2007-01-08T00:00:00'
    >>> Lease.calculateDue(start,u'month').isoformat()
    '2007-02-01T00:00:00'
    >>> Lease.calculateDue(start,u'quarter').isoformat()
    '2007-04-01T00:00:00'
    >>> Lease.calculateDue(start,u'semester').isoformat()
    '2007-07-01T00:00:00'
    >>> Lease.calculateDue(start,u'year').isoformat()
    '2008-01-01T00:00:00'
        
    Test year wrap-around:

    >>> start = datetime(2007,12,1,0,0,0)
    >>> start.isoformat()
    '2007-12-01T00:00:00'
    >>> Lease.calculateDue(start,u'month').isoformat()
    '2008-01-01T00:00:00'
    >>> Lease.calculateDue(start,u'quarter').isoformat()
    '2008-03-01T00:00:00'
    >>> Lease.calculateDue(start,u'semester').isoformat()
    '2008-06-01T00:00:00'
    
    """
    implements(ILease)

    def __init__(self, item_id, lender_login, borrower_login, duration, pickup):
        super(Lease, self).__init__()

        self.item_id = item_id
        self.lender_login = lender_login
        self.borrower_login = borrower_login
        self.duration = duration
        self.pickup = pickup
        self.request_date = datetime.now()
        self.status = u'pending' # One of: pending approved denied

    def getDue(self):
        return Lease.calculateDue(self.request_date, self.duration)

    expected_return_date = property(getDue)

    @staticmethod
    def calculateDue(fromDateTime, interval):
        MONTHLY_INTERVALS = {u'month':1, u'quarter':3, u'semester':6}
        if interval in [u'minute',u'hour',u'day',u'week']:
            interval = timedelta(**{interval+u's':1})
            return fromDateTime + interval
        elif interval in MONTHLY_INTERVALS:
            months = MONTHLY_INTERVALS[interval]    
            if fromDateTime.month < (13-months):
                return fromDateTime.replace(month=fromDateTime.month+months)
            else:
                return fromDateTime.replace(year=fromDateTime.year+1,
                                            month=fromDateTime.month-(12-months))
        elif interval == u'year':
            return fromDateTime.replace(year=fromDateTime.year+1)
        else:
            raise ValueError, u'Unknown interval: "%s"' % interval
                
