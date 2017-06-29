#!/usr/bin/env python

from xmlrpclib import ServerProxy
from sys import argv, maxint

if __name__=='__main__':
    from collection import collection
    instance = argv[1]
    if len(argv)==3:
        qty = int(argv[2])
    else:
        qty = maxint
    srv = ServerProxy("http://localhost:8080/%s/pac" % instance)
    for book in collection:
        if book['name']:
            book['creators'] = [creator.strip() for creator in book['name'].split('|')]
            del book['name']
        for key in book.keys():
            if book[key] is None:
                del book[key]
        try:
            print srv.add(book)
        except TypeError:
            print book
        qty -= 1
        if qty == 0: break
