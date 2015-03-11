__author__="Karan S. Sisodia"
__date__ ="$Sep 15, 2014 3:44:47 PM$"

from setuptools import setup,find_packages

setup (
  name = 'CommonSense',
  version = '0.1',
  packages = find_packages(),

  # Declare your packages' dependencies here, for eg:
  install_requires=['foo>=3'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'Karan S. Sisodia',
  author_email = 'karansinghsisodia@gmail.com',

  summary = '',
  url = '',
  license = '',
  long_description= 'Long description of the package',

  # could also include long_description, download_url, classifiers, etc.

  
)