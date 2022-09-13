import setuptools
from src.version import __version__

setuptools.setup(
    # Includes all other files that are within your project folder
    include_package_data=True,

    # Name of your Package
    name='rss-reader',

    # Project Version
    version=__version__,

    # Description of your Package
    description='Pure Python command-line RSS reader',

    # Website for your Project or Github repo
    url="https://github.com/RichardEliasEpam/rss-reader",

    # Name of the Creator
    author='Richard Elias',

    # Creator's mail address
    author_email='richard_elias@epam.com',

    # Projects you want to include in your Package
    package_dir = {"": "src"},

    # Dependencies/Other modules required for your package to work
    install_requires=['feedparser'],

    # Detailed description of your package
    long_description='Python RSS-reader command line tool',

    # Format of your Detailed Description
    long_description_content_type="text/markdown",

    # Python version requirement
    python_requires=">=3.9",

    # Entrypoint
    entry_points={
        'console_scripts': [
            'rss-reader = reader:run_rss_reader',
        ]
    }
)