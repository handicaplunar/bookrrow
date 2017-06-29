#!/usr/bin/env python
# encoding: utf-8

from twisted.internet import reactor
from twisted.web import xmlrpc, client
from os import path

#XXX this is to run from the buildout
#from kirbifetch.amazonsource import AmazonSource
from amazonsource import AmazonSource

from pprint import pprint
from sys import stdout

KEEP_FILES = True
# directory where XML files will be saved (include trailing slash)

POLL_INTERVAL = 1 # minimum seconds to wait between calls to fetch.poll

VERBOSE = False

class Fetch(object):

    def __init__(self, xmlrpc_url, poll, callback, source):
        self.pollServer = xmlrpc.Proxy(xmlrpc_url)
        self.pollMethod = poll
        self.callback = callback
        self.source = source

    def poll(self):
        deferred = self.pollServer.callRemote(self.pollMethod)
        deferred.addCallback(self.polled).addErrback(self.pollError)

    def polled(self, isbns):
        i = 0
        if isbns:
            if VERBOSE: print 'polled:', ' '.join(isbns)
            # fetch max_ids_per_request, and one request per second
            for i, start in enumerate(range(0,len(isbns),
                                            self.source.max_ids_per_request)):
                end = start + self.source.max_ids_per_request
                reactor.callLater(i, self.downloadItemsPage, isbns[start:end])
        elif VERBOSE:
            stdout.write('.')
            stdout.flush()
        reactor.callLater(i+POLL_INTERVAL, self.poll)

    def pollError(self, error):
        print 'Error in deferred poll call:', error
        # if there was an error, wait a bit longer to try again
        reactor.callLater(POLL_INTERVAL*4, self.poll)

    def downloadItemsPage(self, isbns):
        url = self.source.buildMultipleBookDetailsURL(isbns)
        deferred = client.getPage(url)
        deferred.addCallback(self.downloadedItemsPage, isbns)
        deferred.addErrback(self.downloadError, url)

    def downloadedItemsPage(self, xml, isbns):
        book_list = self.source.parseMultipleBookDetails(xml)
        deferred = self.pollServer.callRemote(self.callback, book_list)
        deferred.addCallback(self.uploaded).addErrback(self.uploadError)
        for book in book_list:
            url = book.get('image_url')
            if url:
                filename = book.get('isbn13',book['source_item_id'])
                filename += '.' + url.split('.')[-1]
                # XXX: find a proper way to calculate the static image dir
                filepath = '../../..'
                filepath = path.join(filepath,'src','kirbi','static',
                                    'covers','large',filename)
                # avoid duplicate downloads
                if not path.exists(filepath):
                    deferred = client.getPage(url)
                    deferred.addCallback(self.downloadedImage, filepath)
                    deferred.addErrback(self.downloadError, url)
                else:
                    print 'skipping existing:', filepath

        if KEEP_FILES:
            filename = '_'.join(isbns)+'.xml'
            out = file(path.join(self.source.name,filename), 'w')
            out.write(xml.replace('><','>\n<'))
            out.close()


    def downloadedImage(self, bytes, filepath):
        print 'saving:', filepath
        out = file(filepath, 'wb')
        out.write(bytes)
        out.close()

    def downloadError(self, error, url):
        print 'Error in deferred download (url=%s): %s' % (url, error)

    def uploaded(self, number):
        print 'books uploaded:', number

    def uploadError(self, error):
        print 'Error in deferred upload:', error


def main():
    xmlrpc_url = 'http://localhost:8080/kirbi/pac'
    poll_method = 'dumpIncomplete'
    callback = 'updateBooks'
    fetcher = Fetch(xmlrpc_url, poll_method, callback, AmazonSource())
    reactor.callLater(0, fetcher.poll)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'

if __name__ == '__main__':
    main()
