import os.path
import kirbi
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(kirbi.__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')
