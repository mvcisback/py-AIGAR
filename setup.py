from setuptools import find_packages, setup

DESC = 'TODO'

setup(
    name='py-aiger-analysis',
    version='0.0.0',
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
    packages=find_packages(),
)
