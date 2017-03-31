from setuptools import setup

setup(
    name='duden',
    version='0.9.0',
    packages=['duden'],
    description='CLI-based german dictionary',
    author='Radomír Bosák',
    author_email='radomir.bosak@gmail.com',
    url='https://github.com/radomirbosak/duden-down',
    download_url='https://github.com/radomirbosak/duden-down/archive/'
                 '0.9.0.tar.gz',
    keywords=['duden', 'duden.de', 'dictionary', 'cli', 'word'],
    entry_points={
        'console_scripts': [
            'duden = duden.main:main'
        ]
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
    ]
)
