import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='kirbi',
    version='0.1.0',
    author = "Luciano Ramalho",
    author_email = "lucian@ramalho.org",
    description = "Kirbi: p2p library management system",
    long_description=(
        read('README.txt')
        ),
    license="ZPL",
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
    url = 'http://svn.zope.org/Sandbox/luciano/kirbi',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['kirbi'],
    install_requires=['setuptools',
                      'grok',
                      'elementtree',
                      'zc.twisted'
                     ],
    zip_safe = False,
    )

