import codecs
from os.path import dirname, join, abspath

from setuptools import setup, find_packages

here = abspath(dirname(__file__))


def read(*parts):
    return codecs.open(join(here, *parts), 'r', encoding='utf-8').read()


def find_version(package):
    about = {}
    exec(read(package, '__version__.py'), about)
    return about['__version__']


setup(
    name='celery-cloudwatch',
    version=find_version('celery_cloudwatch'),

    author='Nathan Muir',
    author_email='ndmuir@gmail.com',

    url='https://github.com/3stack-software/celery-cloudwatch',

    license='MIT',
    description='A monitor for celery queues that reports to AWS CloudWatch',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    keywords='celery cloudwatch monitor stats',

    packages=find_packages(exclude=('tests',)),
    python_requires='>= 3.6',

    setup_requires=[],
    install_requires=[
        'celery',
        'boto3',
        'pyyaml',
        'voluptuous',
        'six',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'ccwatch = celery_cloudwatch.__main__:main'
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
