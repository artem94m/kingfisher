import zipfile
import tarfile

def unzip(archive_name):
    zf = zipfile.ZipFile(archive_name)
    zf.extractall(".")
    zf.close()

def untar(archive_name):
    tf = tarfile.TarFile(archive_name)
    tf.extractall()
    tf.close()