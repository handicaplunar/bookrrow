#!/usr/bin/env python

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from pprint import pprint

PORT = 8080

class Server(object):
    # incomplete will behave like an ordered set (no duplicates)
    incomplete = []

    def __init__(self, incomplete = None):
        if incomplete is not None:
            self.incomplete = incomplete

    def addIncomplete(self, isbns):
        print 'add%s' % isbns
        added = 0
        for isbn in isbns:
            if isbn not in self.incomplete:
                self.incomplete.append(isbn)
                added += 1
        return added
    
    def delIncomplete(self, isbns):
        print 'del%s' % isbns
        deleted = 0
        for isbn in isbns:
            if isbn in self.incomplete:
                self.incomplete.remove(isbn)
                deleted += 1
        return deleted
    
    def listIncomplete(self):
        print 'list%s' % self.incomplete
        return self.incomplete

    def dumpIncomplete(self, max=0):
        print 'dump%s' % self.incomplete
        if max == 0:
            max = len(self.incomplete)
        dump = self.incomplete[:max]
        self.incomplete = self.incomplete[max:]
        return dump
        
    def updateBooks(self, books):
        print 'updated:'
        pprint(books)
        return len(books)
    
    def addError(self, isbn, msg):
        print 'error(%s): %s' % (isbn, msg)


if __name__=='__main__':
    if len(sys.argv) not in [2,3]:
        print 'usage: %s <filename> [<n>]' % sys.argv[0]
        print '  <filename> names a text file containing' 
        print '             ISBN-13 numbers, one per line'
        print '  <n> (optional) max ISBN numbers loaded'
        sys.exit()
        
    incomplete = file(sys.argv[1]).read().split()    
    if len(sys.argv) == 3:
        incomplete = incomplete[:int(sys.argv[2])]

    srv = Server(incomplete)

    xmlrpc = SimpleXMLRPCServer(("localhost", PORT))

    xmlrpc.register_instance(srv)

    print 'SimpleXMLRPCServer running on port %s...' % PORT    
    xmlrpc.serve_forever()


