#!/usr/bin/env python
# encoding: utf-8

from zope.interface import implements
from interfaces import IMetadataSource

try:
    from lxml import etree
except ImportError:
    try:
        # normal cElementTree install
        import cElementTree as etree
    except ImportError:
        try:
            import elementtree.ElementTree as etree
        except ImportError:
            print "Failed to import ElementTree from any known place"

from urllib import quote
from StringIO import StringIO

from amazonsource_config import ACCESS_KEY_ID, ASSOCIATE_TAG

"""
Structure of the AmazonECS XML response:

ItemLookupResponse
    OperationRequest
        (...)
    Items
        Request
            IsValid
            ItemLookupRequest
                ItemId
                ResponseGroup
            (Errors)
                (Error)
                    (Code)
                    (Message)
        (Item)
            (ItemAttributes)
                (Author)
                (Creator Role=...)

Notes:
- Errors element occurs when ISBN is non-existent;
        in that case, Code contains the string "AWS.InvalidParameterValue"
- Author element is not always present
- Author element may be duplicated with the same content,
        except for whitespace; for example: ISBN=0141000511
"""

FIELD_MAP = [
    # Book schema -> Amazon ECS element path, relative to Item element
    ('title', 'ItemAttributes/Title'),
    ('isbn13', 'ItemAttributes/EAN'),
    ('edition', 'ItemAttributes/Edition'),
    ('publisher', 'ItemAttributes/Publisher'),
    ('issued', 'ItemAttributes/PublicationDate'),
    ('subjects', 'ItemAttributes/DeweyDecimalNumber'),
    ('image_url', 'LargeImage/URL'),
    ('source_url', 'DetailPageURL'),
    ('source_item_id', 'ASIN'),
    ]

CREATOR_TAGS = ['ItemAttributes/Author', 'ItemAttributes/Creator']

AMAZON_CODE_NO_MATCH = 'AWS.ECommerceService.NoExactMatches'

class AmazonSource(object):
    implements(IMetadataSource)
    
    name = 'amazon.com'
    max_ids_per_request = 10


    base_url = """http://ecs.amazonaws.com/onca/xml"""

    def __init__(self):
        self.base_params = { 'Service':'AWSECommerceService',
                             'AWSAccessKeyId':ACCESS_KEY_ID,
                             'AssociateTag': ASSOCIATE_TAG
                           }
        self.xml = ''
        self.http_response = {}

    def buildURL(self, **kw):
        query = []
        kw.update(self.base_params)
        for key, val in kw.items():
            query.append('%s=%s' % (key,quote(val)))
        return self.base_url + '?' + '&'.join(query)

    def buildItemLookupURL(self,itemId,response='ItemAttributes'):
        params = {  'Operation':'ItemLookup',
                    'ItemId':itemId,
                    'ResponseGroup':response
                 }
        return self.buildURL(**params)

    def buildItemSearchURL(self,query,response='ItemAttributes,Images'):
        params = {  'Operation':'ItemSearch',
                    'SearchIndex':'Books',
                    'Power':query,
                    'ResponseGroup':response
                 }
        return self.buildURL(**params)
    
    def buildMultipleBookDetailsURL(self, isbns):
        query = 'isbn:' + ' or '.join(isbns)
        return self.buildItemSearchURL(query)

    def nsPath(self, *paths):
        """Prepend namespace to each part of the path."""
        parts = []
        for path in paths:
            parts.extend(path.split('/'))
        return '/'.join([self.ns+part for part in parts])
    
    def parseMultipleBookDetails(self, xml):
        xml = StringIO(xml)
        tree = etree.parse(xml)
        root = tree.getroot()
        # get the XML namespace from the root tag
        self.ns = root.tag.split('}')[0] + '}'
        request = root.find(self.nsPath('Items/Request'))
        error_code = request.findtext(self.nsPath('Errors/Error/Code'))
        if error_code is None:
            book_list = []
            for item in root.findall(self.nsPath('Items/Item')):
                book_dic = {}
                for field, tag in FIELD_MAP:
                    elem = item.find(self.nsPath(tag))
                    if elem is not None:
                        book_dic[field] = elem.text
                creators = []
                for tag in CREATOR_TAGS:
                    for elem in item.findall(self.nsPath(tag)):
                        if elem is None: continue
                        role = elem.attrib.get('Role')
                        if role:
                            creator = '%s (%s)' % (elem.text, role)
                        else:
                            creator = elem.text
                        creators.append(creator)
                if creators:
                    book_dic['creators'] = creators
                if book_dic.get('subjects'):
                    # subjects is a Tuple field
                    book_dic['subjects'] = (book_dic['subjects'],)
                book_dic['source'] = self.name

                book_list.append(book_dic)
            return book_list
    
        elif error_code == AMAZON_CODE_NO_MATCH:
            return []
        else:
            raise EnvironmentError, error_code
        
if __name__=='__main__':
    import sys
    from pprint import pprint
    xml = file(sys.argv[1]).read()
    amz = AmazonSource()
    pprint(amz.parseMultipleBookDetails(xml))