from setuptools import setup

setup(
    name='duden',
    version='0.10.0',
    packages=['duden'],
    description='CLI-based german dictionary',
    author='Radomír Bosák',
    author_email='radomir.bosak@gmail.com',
    url='https://github.com/radomirbosak/duden',
    download_url='https://github.com/radomirbosak/duden/archive/'
                 '0.10.0.tar.gz',
    keywords=['duden', 'duden.de', 'dictionary', 'cli', 'word'],
    entry_points={
        'console_scripts': [
            'duden = duden.main:main'
        ]
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
