# -*- coding: utf-8 -*-
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'duden', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

setup(
    author='Radomír Bosák',
    author_email='radomir.bosak@gmail.com',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
    ],
    description='CLI-based german dictionary',
    download_url='https://github.com/radomirbosak/duden/archive/' \
                 + about['__version__'] + '.tar.gz',
    entry_points={
        'console_scripts': [
            'duden = duden.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        "requests",
        "beautifulsoup4",
        "crayons",
        "pyxdg",
        "pyyaml"
    ],
    keywords=['duden', 'duden.de', 'dictionary', 'cli', 'word'],
    license='MIT',
    name='duden',
    packages=['duden'],
    url='https://github.com/radomirbosak/duden',
    version=about['__version__'],
)
