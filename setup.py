#!/usr/bin/env python

import codecs
import os
import sys

from setuptools import setup

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

needs_setupext_pip = {'requirements'}.intersection(sys.argv)
setupext_pip = ['setupext-pip~=1.0.5'] if needs_setupext_pip else []

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version = read(*file_paths).strip()
    if version == '':
        raise RuntimeError('No version found')
    return version


def read_markdown(filename):
    try:
        import pandoc
        doc = pandoc.Document()
        doc.markdown = open(filename).read()
        return doc.rst
    except ImportError:
        return ''

setup(
    name='celery-cloudwatch',
    version=find_version("VERSION"),

    author='Nathan Muir',
    author_email='ndmuir@gmail.com',

    url='https://github.com/3stack-software/celery-cloudwatch',

    license='MIT',
    description='A monitor for celery queues that reports to AWS CloudWatch',
    long_description=read_markdown('README.md'),
    keywords='celery cloudwatch monitor stats',

    packages=['celery_cloudwatch'],

    setup_requires=[] + pytest_runner,
    install_requires=[
        'celery', 'boto', 'pyyaml', 'voluptuous', 'six'
    ],
    tests_require=[
        'pytest', 'unittest2',
    ],
    extras_require={
        'documentation': ['pyandoc'],
    },

    entry_points={
        'console_scripts': [
            'ccwatch = celery_cloudwatch.__main__:main'
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
