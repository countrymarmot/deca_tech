import os
import setuptools
from painite.version import get_version, read_requirements

readme = open('README.md').read()
dependencies, requirements = read_requirements('requirements.txt')

long_description = """
painite %s
Protocols for interacting with Zinc.

To install use pip install git+git://git@github.com:Deca-Technologies/painite.git

----

%s

----

For more information, please see: https://github.com/Deca-Technologies/painite
""" % (get_version('short'), readme)

setuptools.setup(
    name='painite',
    version=get_version('short'),
    author='jmatt',
    author_email='jmatt@jmatt.org',
    description="Web API and dashboard for Onyx.",
    long_description=long_description,
    url="https://github.com/Deca-Technologies/painite",
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
