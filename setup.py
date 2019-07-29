# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='polka',
    version='0.1.0',
    description='',
    long_description=readme,
    author='CR Milburn',
    author_email='chad.r.milburn@gmail.com',
    url='https://github.com/chadrm9/polka',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

