from setuptools import setup
from upsetplotly.__init__ import __version__
from os import path

# read the contents of the README.md file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# replace relative paths to images with web links
long_description = long_description.replace('.README_images',
    'https://raw.githubusercontent.com/kevinkovalchik/UpSetPlotly/master/.README_images')

# good to go!

setup(
    name='UpSetPlotly',
    version=__version__,
    packages=['upsetplotly'],
    url='https://github.com/kevinkovalchik/UpSetPlotly',
    license='MIT',
    author='Kevin Kovalchik',
    author_email='',
    install_requires=['plotly'],
    description='A Python package for creating UpSet-style plots using the Plotly framework.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
