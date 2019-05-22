"""
hon
=====

Hon (本) is a tool for creating a book from markdown files.
"""
import ast
import io
import re
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

readme = ''
# with io.open('README.rst', 'rt', encoding='utf8') as f:
#     readme = f.read()

with io.open('hon/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


setup(
    name='hon',
    version=version,
    url='http://github.com/swquinn/hon/',
    author='Sean Quinn',
    author_email='sean-quinn@pluralsight.com',
    description='A tool for creating books from markdown files.',
    long_description=readme,
    packages=['hon'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=[
        'click>=7.0',
        'markdown>=3.1',
        'pyyaml>=5.1',
    ],
    extras_require={
        'dotenv': [],
        'dev': [
            'pytest>=4',
            'pytest-mock',
            'coverage',
            'tox',
        ],
        'docs': []
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'hon=hon.cli:main'
        ],
        # 'hon.commands': [
        #     'build=hon.commands:build_command',
        #     'clean=hon.commands:clean_command',
        #     'init=hon.commands:init_command',
        #     'serve=hon.commands:serve_command',
        #     'test=hon.commands:test_command',
        #     'watch=hon.commands:watch_command',
        # ]
    }
)
