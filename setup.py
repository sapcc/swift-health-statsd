#!/usr/bin/env python

import os, setuptools

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name             = "swift-health-statsd",
    version          = "0.1.0",
    author           = "Stefan Majewsky",
    author_email     = "stefan.majewsky@sap.com",
    description      = "Submit health data from swift-dispersion and swift-recon to a statsd endpoint",
    license          = "Apache",
    url              = "https://github.com/sapcc/swift-health-statsd",
    long_description = read("README.md"),
    packages         = setuptools.find_packages(exclude=['contrib', 'docs', 'tests*']),
    classifiers      = [
        "Development Status :: 4 - Beta",
        "Environment :: OpenStack",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Monitoring",
    ],
    install_requires = [ "statsd >= 3.2" ],
    entry_points     = { 'console_scripts': [ 'swift-health-statsd=swift_health_statsd:main' ] },
    setup_requires   = [ "pytest-runner" ],
    tests_require    = [ "pytest" ],
)
