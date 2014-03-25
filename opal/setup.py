import os
import setuptools
from opal.version import get_version, read_requirements

readme = open('README.md').read()
dependencies, requirements = read_requirements('requirements.txt')

long_description = """
opal %s
Web API and dashboard for Onyx.

To install use pip install git+git://git@github.com:Deca-Technologies/opal.git

----

%s

----

For more information, please see: https://github.com/Deca-Technologies/opal
""" % (get_version('short'), readme)

setuptools.setup(
    name='opal',
    version=get_version('short'),
    author='jmatt',
    author_email='jmatt@jmatt.org',
    description="Web API and dashboard for Onyx.",
    long_description=long_description,
    url="https://github.com/Deca-Technologies/opal",
    packages=setuptools.find_packages(),
    dependency_links=dependencies,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration"
    ])
