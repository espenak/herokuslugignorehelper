from setuptools import setup, find_packages

setup(
    name = "herokuslugignorehelper",
    version = "0.2",
    license = 'BSD',
    url = 'https://github.com/espenak/herokuslugignorehelper',
    author = 'Espen Angell Kristiansen',
    packages = find_packages(exclude=['ez_setup']),
    include_package_data = True,
    long_description = 'See https://github.com/espenak/herokuslugignorehelper',
    zip_safe = True,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Programming Language :: Python'
    ],
    entry_points = {
        'console_scripts': [
            'herokuslugignorehelper = herokuslugignorehelper.cli:cli',
        ],
    }
)
