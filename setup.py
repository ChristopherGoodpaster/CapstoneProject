# setup.py
import os
from setuptools import setup, find_packages

setup(
    name='capstone_project',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'mplcursors',
        'requests',
        'beautifulsoup4',
        'schedule',
        'xlsxwriter',
    ],
    entry_points={
        'console_scripts': [
            # Example: 'run-generate-data=CapstoneProject.generate_data:main'
            # You can define scripts you want to run directly from CLI here
        ],
    },
    author='Chris Goodpaster',
    author_email='Chris.Goodpaster83@gmail.com',
    description='Amazon Product Price Tracker',
    long_description=open('readme.txt').read() if os.path.exists('readme.txt') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/YourRepoURLIfYouHaveOne',
)
