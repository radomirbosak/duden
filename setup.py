# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import setup

this_directory = Path(__file__).parent

about = {}
version_file = this_directory / "duden" / "__version__.py"
with open(version_file, 'r', encoding='utf-8') as f:
    exec(f.read(), about)

long_description = (this_directory / "README.md").read_text()

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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
    ],
    description='CLI-based german dictionary',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    keywords=['duden', 'duden.de', 'dictionary', 'cli', 'word', 'german'],
    license='MIT',
    name='duden',
    packages=['duden'],
    url='https://github.com/radomirbosak/duden',
    version=about['__version__'],
)
