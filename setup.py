from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Giza',
      version=version,
      description="Some functions I've found useful in creating Pyramid applications",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='rick@arborian.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      # -*- Entry points: -*-
      [easy_widgets.resources]
      giza=giza.resources:register_ew_resources
      """,
      )
