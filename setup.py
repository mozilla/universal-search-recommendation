import os

from setuptools import setup, find_packages


__dirname = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(__dirname, 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(__dirname, 'app', 'requirements.txt')) as reqs:
    REQUIREMENTS = reqs.read()


setup(name='ghosttown',
      version='0.0.1',
      description='Universal Search recommendation server.',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
      ],
      author='Chuck Harmston',
      author_email='chuck@mozilla.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      )
