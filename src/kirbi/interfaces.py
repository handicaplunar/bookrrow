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
"""Kirbi interfaces
"""

from zope.interface import Interface, Attribute, invariant, Invalid
from zope import schema
from isbn import isValidISBN

class IUser(Interface):
    """A Kirbi user"""
    login = schema.TextLine(title=u"Login",
                            required=True)
    name = schema.TextLine(title=u"Name",
                            required=False)
    password = schema.Password(title=u"Password",
                            required=True)
    password_confirmation = schema.Password(title=u"Confirm password",
                            required=True)

    @invariant
    def passwordConfirm(user):
        if (user.password != user.password_confirmation):
            raise Invalid(u'The password and confirmation do not match.')


class InvalidISBN(schema.ValidationError):
    """This is not a valid ISBN-10 or ISBN-13"""

def validateISBN(isbn):
    if not isValidISBN(isbn):
        raise InvalidISBN
    else:
        return True

class IBook(Interface):
    """A book record"""
    title = schema.TextLine(title=u"Title",
                            required=False,
                            default=u'',
                            missing_value=u'')
    isbn = schema.TextLine(title=u"ISBN",
                           required=False,
                           constraint=validateISBN,
                           description=u"ISBN in 10 or 13 digit format",
                           min_length=10,
                           max_length=17 #978-3-540-33807-9
                           )

    creators = schema.Tuple(title=u"Authors",
                            value_type=schema.TextLine(),
                            default=())
    edition = schema.TextLine(title=u"Edition", required=False)
    publisher = schema.TextLine(title=u"Publisher", required=False)
    issued = schema.TextLine(title=u"Issued", required=False)
    # TODO: set a vocabulary for language
    language = schema.TextLine(title=u"Language", required=False)

    subjects = schema.Tuple(title=u"Subjects",
                            value_type=schema.TextLine(),
                            default=())

    source = schema.TextLine(title=u"Metadata source",
                             required=False,
                             description=u"Name of the source of this record.")
    source_url = schema.URI(title=u"Source URL",
                            required=False,
                            description=u"URL of the source of this record.")
    source_item_id = schema.TextLine(title=u"Item ID at Source",
                            required=False,
                            description= (u"Product number or other identifier"
                                          u" for this item at source.")
    )

    @invariant
    def titleOrIsbnGiven(book):
        if (not book.title or not book.title.strip()) and (not book.isbn):
            raise Invalid(u'Either the title or the ISBN must be given.')

class IItem(Interface):
    """A physical exemplar of a manifestation (book, DVD or other medium).

    The terms ``Item`` and ``manifestation`` are borrowed from the terminology
    of the FRBR - `Functional Requirements for Bibliographic Records`__.

    __ http://www.ifla.org/VII/s13/frbr/frbr.htm

    The FRBR defines these relationships::

        work >---is realized through---> expression
                    expression >---is embodied in---> manifestation
                                manifestation >---is exemplified by---> item

    For example, Hamlet is a work by Shakespeare, and has many expressions:
    the written text of the play, performances, movies etc. A particular
    rendition of the written text is an expression.

    A specific edition of an expression is a manifestation (commonly identified
    by an ISBN). An exemplar of a manifestation is an item, a physical book
    that sits in a shelf and can be borrowed or stolen.

    Currently, Kirbi supports only one kind of manifestation: books.
    So some identifiers embedded in code use the term ``manifestation`` but all
    user-visible strings use ``book`` for now.

    """

    manifestation_id = schema.ASCII(title=u"Book id",
                    description=u"Id of the book of which this item is a copy.",
                    required=True)
    manifestation = Attribute(u"Hard reference to the manifestation instance.")
    owner_login = Attribute(u"Login of the owner.")
    description = schema.Text(title=u"Description",
                    description=(u"Details of this copy, such as autographs,"
                                 u"marks, damage etc."),
                            required=False)
    #XXX: This should be filled automatically.
    catalog_datetime = schema.Datetime(title=u"Catalog date",
                    description=u"Datetime when added to your collection.",
                            required=False)

class ICollection(Interface):
    """A collection of Items belonging to a User"""
    title = schema.TextLine(title=u"Title",
             description=u"The full name of the user who owns the collection.",
             required=True)
    private = schema.Bool(title=u"Private",
             description=u"If true, items will not appear in public searches.",
             default=True)

class ILease(Interface):
    """A book lease."""

    item_id = Attribute(u"The id of the copy being lent.")

    # Note: the lender_login can usually be obtained from the item.__parent__,
    # however if an item is given to a new owner, the lease history would
    # become incomplete.
    lender_login = Attribute(u"Lender login.")

    borrower_login = Attribute(u"Borrower login.")

    request_date = Attribute(u"When the lease was requested.")

    expected_delivery_date = Attribute(u"When the copy is to be delivered to the borrower.")

    delivery_date = Attribute(u"When the copy was delivered to the borrower.")

    expected_return_date = Attribute(u"When the copy is to be returned.")

    return_date = Attribute(u"When the copy was returned.")

    # XXX: This should have a vocabulary
    duration = Attribute(u"One of: minute week month quarter semester year")
    
    # XXX: This should have a vocabulary
    status = Attribute(u"One of: pending approved denied")

