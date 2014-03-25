import os
import setuptools
from xenotime.version import get_version, read_requirements

readme = open('README.md').read()
dependencies, requirements = read_requirements('requirements.txt')

print "requirements = %s" % requirements

long_description = """
xenotime %s
Onyx worker node tasks.

To install use pip install git+git://git@github.com:Deca-Technologies/xenotime.git

----

%s

----

For more information, please see: https://github.com/Deca-Technologies/xenotime
""" % (get_version('short'), readme)

setuptools.setup(
    name='xenotime',
    version=get_version('short'),
    author='jmatt',
    author_email='jmatt@jmatt.org',
    description="Common code from Archerite, Xenotime and Opal.",
    long_description=long_description,
    url="https://github.com/Deca-Technologies/xenotime",
    packages=setuptools.find_packages(),
    dependency_links=dependencies,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: System",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration"
    ])
