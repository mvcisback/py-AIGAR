from setuptools import find_packages
from distutils.core import setup

DESC = 'An extension of py-aiger providing advanced tool support, '\
       + ' including SAT and QBF solvers.'


setup(
    name='py-aiger-analysis',
    version='0.0.1',
    description=DESC,
    url='http://github.com/mvcisback/py-aiger-analysis',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'bidict',
        'py-aiger',
        'py-aiger-bv',
        'funcy',
        'toposort',
    ],
    extras_require={
        'BDD':  ['dd'],
        'SAT': ['python-sat'],
    },
    packages=find_packages(),
)
