from setuptools import setup
from upsetplotly.__init__ import __version__

setup(
    name='UpSetPlotly',
    version=__version__,
    packages=['upsetplotly'],
    url='https://github.com/kevinkovalchik/UpSetPlotly',
    license='MIT',
    author='Kevin Kovalchik',
    author_email='',
    install_requires=['plotly'],
    description='A Python package for creating UpSet-style plots using the Plotly framework.'
)
