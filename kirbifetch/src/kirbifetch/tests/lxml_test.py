#!/usr/bin/env python
# encoding: utf-8
"""
lxml_test.py

Groo notes:
fixed another Amazon corner case: sometimes the Author element is duplicated
with the same content! For example: ISBN=0141000511
fix to handle Amazon corner-case: sometimes they don't have an Author
element

"""
from lxml import etree, objectify
from StringIO import StringIO

from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed()
# ipshell() # this call anywhere in your program will start IPython

def main():
    xml = file('item-oss.xml')
    
    parser = etree.XMLParser(remove_blank_text=True)
    lookup = objectify.ObjectifyElementClassLookup()
    parser.setElementClassLookup(lookup)
    tree = etree.parse(xml, parser)
    #ipshell()
    raiz = tree.getroot()
    assert len(raiz.Items.Item) == 1
    for attr in raiz.Items.Item.ItemAttributes.getchildren():
        tag = attr.tag[attr.tag.find('}')+1:]
        print '%s\t%s' % (tag, attr),
        if tag == 'Creator':
            print '(%s)' % attr.get('Role')
        else:
            print
    


if __name__ == '__main__':
    main()

