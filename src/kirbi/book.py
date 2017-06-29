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
"""Kirbi Book record class and views
"""

import grok
from interfaces import IBook
from zope.interface import implements
from zope import schema
from isbn import isValidISBN, isValidISBN10, isValidISBN13, filterDigits
from isbn import convertISBN10toISBN13, convertISBN13toLang
from zope.component import getUtility, getMultiAdapter
from zope.app.catalog.interfaces import ICatalog


import os

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')

ARTICLES = {
    'en': u'the a an'.split(),
    'fr': u'le la les un une des'.split(),
    'de': (u'der das die den dem ein eine einen einem einer'
           u'kein keine keinen keiner').split(),
    'es': u'el los la las un unos una unas'.split(),
    'pt': u'o os a as um uns uma umas'.split(),
}

class Book(grok.Model):
    """A book record implementation.

    >>> alice = Book()
    >>> IBook.providedBy(alice)
    True

    >>> alice.title = u"Alice's Adventures in Wonderland"
    >>> alice.title
    u"Alice's Adventures in Wonderland"

    The ISBN can be set and retrieved in ISBN-10 or ISBN-13 format:

    >>> alice.isbn = '0486275434'
    >>> alice.isbn13
    '9780486275437'

    The filing title is obtained by moving a leading article to the end of the
    main title (before the sub-title). This depends on the language property,
    so that information must be given or will be presumed from the ISBN prefix.

    >>> won = Book( u'The Wealth of Networks: How Social Production...')
    >>> won.filing_title
    u'The Wealth of Networks: How Social Production...'
    >>> won.isbn = '978-0300110562'
    >>> won.language
    'en'
    >>> won.setFilingTitle()
    >>> won.filing_title
    u'Wealth of Networks, The: How Social Production...'
    """

    implements(IBook)
    __title = ''        # = __main_title + __title_glue + __sub_title
    __main_title = ''   # title without sub-title
    __sub_title = ''    # sub-title: whatever comes after a ":" or the first "("
    __title_glue = ''   # may be either ":" or ""
    __filing_title = '' # title with article at end (for sorting and display)
    __isbn = ''     # the ISBN as entered by the user
    __isbn13 = ''   # ISBN-13, digits only (no dashes)
    __language = None

    def __init__(self, title='', isbn13=None, isbn=None,
                 creators=None, edition=None, publisher=None, issued=None,
                 language=None, subjects=None, source=None, source_url=None,
                 source_item_id=None):
        super(Book, self).__init__()
        if isbn13:
            self.isbn13 = isbn13
        elif isbn:
            self.isbn = isbn
        # Note: the title is set after the isbn13 so the language can be
        # guessed from the isbn13 and the __filing_title can be set
        self.title = title
        if creators is None:
            self.creators = []
        else:
            self.creators = creators
        self.edition = edition
        self.publisher = publisher
        self.issued = issued
        self.language = language
        if subjects is None:
            self.subjects = []
        else:
            self.subjects = subjects
        self.source = source
        self.source_url = source_url
        self.source_item_id = source_item_id

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        self.setFilingTitle()

    title = property(getTitle, setTitle)

    def getISBN(self):
        return self.__isbn

    def setISBN(self, isbn):
        if isbn is None: return
        self.__isbn = isbn
        if isValidISBN13(isbn):
            self.__isbn13 = filterDigits(isbn)
        elif isValidISBN10(isbn):
            self.__isbn13 = convertISBN10toISBN13(isbn)

    isbn = property(getISBN, setISBN)

    def getISBN13(self):
        if self.isbn and self.__isbn13 is None:
            self.setISBN13(self.isbn) #cache it
        return self.__isbn13

    def setISBN13(self, isbn):
        if isValidISBN13(isbn):
            self.__isbn13 = isbn
        elif isValidISBN10(isbn):
            self.__isbn13 = convertISBN10toISBN13(isbn)
        else:
            raise ValueError, '%s is not a valid ISBN-10 or ISBN-13' % isbn
        # if the isbn field is empty, fill it with the isbn13
        if not self.isbn:
            self.isbn = self.__isbn13

    isbn13 = property(getISBN13, setISBN13)

    def getShortTitle(self):
        if u':' in self.title:
            title = self.title.split(u':')[0].strip()
        else:
            title = self.title
        words = title.split()
        if words <= 7:
            return title
        else:
            return u' '.join(words[:7])+u'...'

    def splitTitle(self):
        if not self.__main_title and self.title.strip():
            main_title = title = self.title.strip()
            sub_title = ''
            glue = ''
            pos_colon = title.find(u':')
            pos_paren = title.find(u'(')
            if pos_colon >= 0 and ((pos_paren >= 0 and pos_colon < pos_paren)
                or pos_paren < 0):
                main_title = title[:pos_colon]
                sub_title =  title[pos_colon+1:] # exclude the colon
                glue = ':'
            elif pos_paren >= 0:
                main_title = title[:pos_paren]
                sub_title =  title[pos_paren:]
                glue = ''
            self.__main_title = main_title
            self.__title_glue = glue
            self.__sub_title = sub_title
        return (self.__main_title, self.__title_glue, self.__sub_title)

    def getLanguage(self):
        if not self.__language and self.__isbn13: # guess from ISBN
            self.__language = convertISBN13toLang(self.__isbn13)
        return self.__language

    def setLanguage(self, language):
        self.__language = language
        self.setFilingTitle()

    language = property(getLanguage, setLanguage)

    def getFilingTitle(self):
        if not self.__filing_title:
            self.setFilingTitle()
        return self.__filing_title

    def setFilingTitle(self, filing_title=None):
        if filing_title:
            self.__filing_title = filing_title
        elif not self.title or not self.title.strip():
            self.__filing_title = '{isbn: %s}' % self.__isbn13
        else: # generate automatically
            # Do we know the language and it's articles?
            if self.language and self.language in ARTICLES:
                main_title, glue, sub_title = self.splitTitle()
                word0 = main_title.split()[0]
                if word0.lower() in ARTICLES[self.language]:
                    main_title = main_title[len(word0):].strip()+u', '+word0
                    if glue != u':': # need to add space after the article
                        main_title += u' '
                self.__filing_title = (main_title + glue + sub_title).strip()
            else:
                self.__filing_title = self.title

    filing_title = property(getFilingTitle, setFilingTitle)

    def getMainTitle(self):
        if not self.__main_title:
            self.splitTitle()
        return self.__main_title

    main_title = property(getMainTitle)

    def getSubTitle(self):
        # Note: the __sub_title maybe empty even after a splitTitle,
        # so we check for the __main_title
        if not self.__main_title:
            self.splitTitle()
        return self.__sub_title

    sub_title = property(getSubTitle)

    def creatorsLine(self):
        return ', '.join(self.creators)

    def creatorsListDict(self):
        creators = []
        for creator in self.creators:
            name = creator.strip()
            role = u''
            if u'(' in creator: # remove role string
                name = name.split(u'(')[0].strip()
                if u')' in creator:
                    role = creator[creator.find(u'(')+1:
                                   creator.find(u')')].strip()
            creators.append({'name':name, 'role':role})
        return creators

    def creatorsSet(self):
        creators = set()
        for creator in self.creators:
            if '(' in creator: # remove role string
                creator = creator.split('(')[0]
            creators.add(creator.strip().lower())
        return list(creators)

    def searchableText(self):
        return self.title + ' ' + ' '.join(self.creators)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self,key,value)
            
    def getCoverId(self):
        return self.__name__
    
    def getItems(self):
        catalog = getUtility(ICatalog)
        res = catalog.searchResults(
                    manifestation_id=(self.__name__,self.__name__))
        return [{'owner':item.__parent__.__name__, 'item_id':item.__name__}
                    for item in res]
    
    def itemOwnedBy(self, login):
        catalog = getUtility(ICatalog)
        res = catalog.searchResults(
                    manifestation_id=(self.__name__,self.__name__),
                    owner_login=(login,login))
        if res:
            return list(res)[0].manifestation_id
        else:
            return None

class Edit(grok.EditForm):
    grok.require('kirbi.ManageBook')

    form_fields = grok.AutoFields(IBook)
    template = grok.PageTemplateFile('form.pt')
    form_title = u'Edit book record'

class Display(grok.DisplayForm):
    pass

class Index(grok.View):
    grok.context(IBook)

    def __init__(self, context, request):
        super(Index, self).__init__(context, request)

        # XXX: this method was created because calling context properties
        # from the template raises a traversal error. Is that to be expected?
        self.main_title = self.context.main_title
        self.sub_title = self.context.sub_title
        self.isbn13 = self.context.isbn13
        self.creator_search_url =  self.application_url('pac')+'?query=cr:'
        self.subjects = ', '.join(self.context.subjects)
        if (self.context.source_url and self.context.source
                                    and self.context.source_item_id):
            self.source = '%s #%s' % (self.context.source,
                                     self.context.source_item_id)
            self.source_url = self.context.source_url
        else:
            self.source = self.context.source
            self.source_url = None

    def coverUrl(self):
        cover = getMultiAdapter((self.context, self.request), name='cover')
        return cover()


class Cover(grok.View):
    grok.context(IBook)

    def render(self):
        prefix = 'covers/large/' + self.context.getCoverId()
        tries = [prefix + ext for ext in '.gif .jpg .png'.split()]
        tries.append('covers/small-placeholder.jpg')
        for path in tries:
            cover = self.static.get(path, None)
            if cover:
                return cover()
        raise LookupError("Cover placeholder not found")
