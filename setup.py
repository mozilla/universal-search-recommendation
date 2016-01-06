import os

from setuptools import setup, find_packages


__dirname = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(__dirname, 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(__dirname, 'requirements.txt')) as reqs:
    REQUIREMENTS = reqs.read()


setup(
    name='universal-search-recommendation',
    version='0.1.0',
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
