#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from pip.req import parse_requirements

install_requires = parse_requirements("requirements.txt", session=False)
requires = [str(ir.req) for ir in install_requires]

setup(name='rsu',
      version='1.0.0',
      keywords=('record', 'manage'),
      description='record sync unit',
      long_description=open('README').read(),
      license='MIT License',
      author='zengtaoxian',
      author_email='zengtaoxian@163.com',
      platforms='any',
      install_requires=requires,
      entry_points={'console_scripts': ['rsu=rsu.rsu:main']},
      scripts=['conf.json', 'const.py', 'rsu.py', 'daemon.py'])
