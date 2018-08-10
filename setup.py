from setuptools import find_packages
import distutils.command.build
from distutils.core import setup
import install_cadet

DESC = 'An extension of py-aiger providing advanced tool support, '\
       + ' including SAT and QBF solvers.'


class MyBuild(distutils.command.build.build):
    '''
    Custom build class to enable compilation of CADET.
    Adapted from python-sat.
    '''
    def run(self):
        # download and compile cadet
        install_cadet.install()

        # now, do standard build
        distutils.command.build.build.run(self)


setup(
    name='py-aiger-analysis',
    version='0.1',
    description=DESC,
    url='http://github.com/mvcisback/py-aiger-analysis',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'py-aiger',
        'py-aiger-bv',
        'funcy',
        'dd',
        'python-sat',
    ],
    cmdclass={'build': MyBuild},
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
)
