import os
import shutil
import tarfile
import zipfile
from urllib.request import urlopen

INSTALL_DIR = os.path.expanduser("~/.cache/tools")


def install(tool, address):
    """
        Tool must be a tuple of name and address.
    """
    print(f'Installing {tool} to {INSTALL_DIR}')
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
    file_name = address.split('/')[-1]
    archive = os.path.join(INSTALL_DIR, file_name)
    download_archive(tool, address, archive)
    extract_archive(archive, tool)
    compile_solver(tool)


def download_archive(name, url, save_to):
    """
        Downloads an archive and saves locally (taken from PySMT).
    """
    # not downloading the file again if it exists
    if os.path.exists(save_to):
        print(f'Not downloading {save_to} since it exists locally')
        return
    else:
        print(f'Downloading: {url} to {save_to}')

    # make five attempts per source
    for i in range(5):
        # first attempt to get a response
        response = urlopen(url)

        # handling redirections
        u = urlopen(response.geturl())

        meta = u.info()
        if meta.get('Content-Length') and len(meta.get('Content-Length')) > 0:
            filesz = int(meta.get('Content-Length'))
            if os.path.exists(save_to) and os.path.getsize(save_to) == filesz:
                print(f'not downloading {save_to} since it exists locally')
                return

            print(f'downloading: {save_to} ({filesz} bytes)...', end=' ')
            with open(save_to, 'wb+') as fp:
                block_sz = 8192
                while True:
                    buff = u.read(block_sz)
                    if not buff:
                        break
                    fp.write(buff)

            print('done')
            break


def extract_archive(archive, solver, put_inside=False):
    """
        Unzips/untars a previously downloaded archive file.
    """
    print(f'Extracting {archive}')
    root = os.path.join(INSTALL_DIR, solver if put_inside else '')

    if archive.endswith('.tar.gz'):
        if os.path.exists(archive[:-7]):
            shutil.rmtree(archive[:-7])

        tfile = tarfile.open(archive, 'r:gz')
        tfile.extractall(root)

        '''
        Normally, directory should be the first name,
        but glucose4.1 has some garbage in the archive.
        '''
        for name in tfile.getnames():
            if not name.startswith('./.'):
                directory = name
                break
    elif archive.endswith('.zip'):
        if os.path.exists(archive[:-4]):
            shutil.rmtree(archive[:-4])

        myzip = zipfile.ZipFile(archive, 'r')
        myzip.extractall(root)
        directory = myzip.namelist()[0]
        myzip.close()

    if not put_inside:
        if os.path.exists(os.path.join(INSTALL_DIR, solver)):
            shutil.rmtree(os.path.join(INSTALL_DIR, solver))

        shutil.move(os.path.join(INSTALL_DIR, directory),
                    os.path.join(INSTALL_DIR, solver))


def compile_solver(solver):
    """
        Compiles a given solver as a library.
    """

    print(f'Compiling {solver}')
    os.system(f'cd {INSTALL_DIR}/{solver} && ./configure && make')
