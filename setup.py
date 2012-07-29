'''
Created on Jul 14, 2012

@author: Michele Sama (m.sama@puzzledev.com)
'''

#!/usr/bin/env python

from distutils.core import setup

setup(name = 'django-puzzledev-uploadcleaner',
      version = '1.0',
      author = "Michele Sama",
      author_email = "m.sama@puzzledev.com",
      maintainer = "Michele Sama",
      maintainer_email = "m.sama@puzzledev.com",
      url = "www.puzzledev.com/",
      description = "Upload file cleaner for Django",
      long_description = "Django file fields no longer delete files when a model is  deleted. This maintenance package removes all the lefto over files.",
      download_url = "https://github.com/msama/django-uploadcleaner",
      classifiers = [
                'Environment :: Web Environment',
                'Programming Language :: Python',
                ],
      platforms = [
                "Linux",
                ],
      license = "LGPL",
      packages = [
                'uploadcleaner',
                'uploadcleaner.management',
                'uploadcleaner.management.commands',
                'uploadcleaner.admin',
                ],
     )