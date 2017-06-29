import os
import unittest
import kirbi
from zope.testing import doctest
from zope.app.testing.functional import (FunctionalTestSetup, ZCMLLayer,
                                         FunctionalDocFileSuite,
                                         getRootFolder, HTTPCaller, sync)
import zope.testbrowser.browser
import zope.testbrowser.testing

ftesting_zcml = os.path.join(os.path.dirname(kirbi.__file__), 'ftesting.zcml')
KirbiFunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                                 'KirbiFunctionalLayer')

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    docfiles = ['xmlrpc.txt',
                'user.txt',
                'learning.txt',
                'addbook.txt',
                'pac.txt',
                'covers.txt',
                ]

    for docfile in docfiles:
        test = FunctionalDocFileSuite(
                    docfile,
                    setUp=setUp, tearDown=tearDown,
                    globs=dict(http=HTTPCaller(),
                        getRootFolder=getRootFolder,
                        Browser=zope.testbrowser.testing.Browser,
                        sync=sync),
                    optionflags=(doctest.ELLIPSIS
                        | doctest.NORMALIZE_WHITESPACE
                        | doctest.REPORT_NDIFF)
               )
        test.layer = KirbiFunctionalLayer
        suite.addTest(test)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
