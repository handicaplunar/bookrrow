import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='kirbifetch',
    version='0.1.0',
    author = "Luciano Ramalho",
    author_email = "lucian@ramalho.org",
    description = "Kirbifetch: fetch books into Kirbi",
    license = "ZPL 2.1",
    keywords = "zope3 kirbi grok",
    classifiers = [
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3 :: Grok'],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    install_requires=['setuptools',
                      'zc.twisted',
                      'zope.interface',
                      'zope.schema',
                      'lxml',
                     ],
    zip_safe = False,
    entry_points = {
    'console_scripts': [
       'kirbifetch = kirbifetch.fetch:main',
       ]
    },
    )

