'''
This file allows us to build CADET by calling the file, or by the function
install().

Is called from .travis.yml for CI and from setup.py for building wheels.
'''

import install_tools


def install():
    install_tools.install(
            'cadet',
            'https://github.com/MarkusRabe/cadet/archive/v2.5.tar.gz')


if __name__ == "__main__":
    install()
