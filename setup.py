"""A setuptools based setup module.

Based on:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # project name
    name='wavy',
    # project version
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # short description
    description='A pure python module for working with WAVE files with '
                'support for all common file formats for both RIFF and RIFX.',
    # readme
    long_description=long_description,
    # GitHub url
    url='https://github.com/acelletti/wavy',
    # author
    author='Andrea Celletti',
    # author email.
    author_email='celletti.andrea87@gmail.com',

    # Classifiers help users find your project by categorizing it.
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Sound/Audio',

        # MIT license
        'License :: OSI Approved :: MIT License',

        # Only compatible with Python 3
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='audio wave wav',

    # specify package
    packages=['wavy', 'wavy.detail'],

    # required packages
    install_requires=['numpy'],

    # extra required packages
    extras_require={
        'dev': ['scipy'],
        'test': ['pytest', 'pytest-mock'],
    },

    # List additional URLs that are relevant to your project as a dict.
    project_urls={
        'Bug Reports': 'https://github.com/acelletti/wavy/issues',
        'Source': 'https://github.com/acelletti/wavy',
    }
)
