#!/usr/bin/env python

import contextlib
import os
import subprocess
import tarfile
import zipfile
from pathlib import Path

GET_ABC_CMD = "wget https://github.com/berkeley-abc/abc/archive/master.zip"
GET_AIGER_CMD = "wget http://fmv.jku.at/aiger/aiger-1.9.9.tar.gz"
GET_CADET_CMD = "wget https://github.com/MarkusRabe/cadet/archive/v2.5.tar.gz"

INSTALL_ABC_CMD = "cmake . && make"
INSTALL_AIGER_CMD = "./configure.sh && make"
INSTALL_CADET_CMD = "./configure.sh && make"


# https://stackoverflow.com/questions/41742317/how-can-i-change-directory-with-python-pathlib
@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def install_aiger():
    aiger_path = Path(os.environ['HOME']) / ".cache" / "aiger"
    print("Installing AIGER.")
    if not aiger_path.exists():
        aiger_path.mkdir()
    elif (aiger_path / "aiger-1.9.9").exists():
        print("Using cached version.")
        return

    with working_directory(aiger_path):
        subprocess.check_call(GET_AIGER_CMD, shell=True)

        with tarfile.open("aiger-1.9.9.tar.gz") as f:
            f.extractall()

    with working_directory(aiger_path / "aiger-1.9.9"):
        subprocess.check_call(INSTALL_AIGER_CMD, shell=True)


def install_abc():
    abc_path = Path(os.environ["HOME"]) / ".cache" / "abc"
    print("Installing ABC.")
    if not abc_path.exists():
        abc_path.mkdir()
    elif (abc_path / "abc-master").exists():
        print("Using cached version.")
        return

    with working_directory(abc_path):
        subprocess.check_call(GET_ABC_CMD, shell=True)

        with zipfile.ZipFile(abc_path / "master.zip", "r") as f:
            f.extractall()

    with working_directory(abc_path / 'abc-master'):
        subprocess.check_call(INSTALL_ABC_CMD, shell=True)


def install_cadet():
    cadet_path = Path(os.environ['HOME']) / ".cache" / "cadet"
    print("Installing CADET.")
    if not cadet_path.exists():
        cadet_path.mkdir()
    elif (cadet_path / "cadet").exists():
        print("Using cached version.")
        return

    with working_directory(cadet_path):
        subprocess.check_call(GET_CADET_CMD, shell=True)

        with zipfile.ZipFile(cadet_path / "v2.5.tar.gz", "r") as f:
            f.extractall()

    with working_directory(cadet_path / "cadet-2.5"):
        subprocess.check_call(INSTALL_CADET_CMD, shell=True)


def main():
    install_abc()
    install_aiger()
    install_cadet()


if __name__ == '__main__':
    main()
