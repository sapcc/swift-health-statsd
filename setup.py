#!/usr/bin/env python

import os, setuptools

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name             = "swift-health-statsd",
    version          = "0.0.1",
    author           = "Stefan Majewsky",
    author_email     = "stefan.majewsky@sap.com",
    description      = "Submit health data from swift-dispersion and swift-recon to a statsd endpoint",
    license          = "Apache",
    # url            = "",
    long_description = read("README.md"),
    packages         = setuptools.find_packages(exclude=['contrib', 'docs', 'tests*']),
    classifiers      = [
        "Development Status :: 3 - Alpha",
        "Environment :: OpenStack",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Monitoring",
    ],
    install_requires = [ "six" ],
    entry_points     = { 'console_scripts': [ 'swift-health-statsd=swift_health_statsd:main' ] },
)
