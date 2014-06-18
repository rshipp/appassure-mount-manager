import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'appassure',
    'beautifulsoup4'
    ]

setup(name='aamm',
      version='0.0',
      description='AppAssure Mount Manager',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: System :: Archiving :: Backup",
        ],
      author='george2',
      author_email='rpubaddr0@gmail.com',
      url='https://github.com/george2/appassure-mount-manager',
      keywords='web pyramid pylons appassure backup recovery mount manager',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="aamm",
      entry_points="""\
      [paste.app_factory]
      main = aamm:main
      """,
      )
