#!/usr/bin/env python
import versioneer

import setuptools

setuptools.setup(
    name="pingdom-uptime-report",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/kouk/pingdom-uptime-report",

    author="Konstantinos Koukopoulos",
    author_email="koukopoulos@gmail.com",

    description="Generate uptime reports using the Pingdom API.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'clize>=4.0.0',
        'PingdomLib>=2.0.0'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='MIT',
    entry_points={
        'console_scripts': [
            'uptimereport = uptime_report.cli:main',
        ]
    },
)
