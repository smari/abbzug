from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='abbzug',
    version='0.1.0',
    description='A Static Site Generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/smari/abbzug',
    author='Smári McCarthy',
    author_email='smari@smarimccarthy.is',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',

        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='static website site generator',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['click', 'jinja2', 'jinja2_markdown', 'python-frontmatter', 'pyinotify', 'python-slugify'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    package_data={},

    entry_points={
        'console_scripts': [
            'abbzug=abbzug:cli',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/smari/abbzug/issues',
        'Source': 'https://github.com/smari/abbzug',
    },
)
