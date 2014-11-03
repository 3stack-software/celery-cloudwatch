#!/usr/bin/env python
__author__ = 'nathan.muir'


import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='celery-cloudwatch',
    version='1.0.0a',

    author='Nathan Muir',
    author_email='ndmuir@gmail.com',

    url='https://github.com/3stack-software/celery-cloudwatch',

    license='MIT',
    description='A monitor for celery queues that reports to AWS CloudWatch',
    long_description=read('README.md'),
    keywords='celery cloudwatch monitor stats',


    packages=['celery_cloudwatch'],
    include_package_data=True,
    install_requires=[
        'celery', 'boto'
    ],

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
