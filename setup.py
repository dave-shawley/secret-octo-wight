#!/usr/bin/env python
import os.path
import sys

from setuptools import find_packages, setup

from setupext import read_requirements_from_file
import familytree


def read_requirements(which):
    path = os.path.join(os.path.dirname(__file__), 'requirements', which)
    return read_requirements_from_file(path)


install_requires = read_requirements('install.txt')
setup_requires = read_requirements('setup.txt')
tests_require = read_requirements('test.txt')

if sys.version_info[:2] < (2, 7):
    tests_require.append('unittest2')

setup(
    name='family-tree',
    version=familytree.__version__,
    license='BSD',
    author='Dave Shawley',
    author_email='daveshawley@gmail.com',
    url='http://github.com/dave-shawley/family-tree',
    description='Web service for managing genealogical information',
    long_description='',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    data_files=[
        ('etc', ['etc/family-tree.yaml']),
        ('etc/init.d', ['etc/init.d/family-tree']),
        ('etc/default', ['etc/default/family-tree']),
    ],
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': ['family-tree-web = familytree.main:main'],
    },
)
