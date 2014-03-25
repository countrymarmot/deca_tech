"""
shareutil.py provides helper methods for NetBIOS and SMB (Samba).
Created by Craig Bishop on 17 July 2013

archerite
Copyright Deca Technologies 2013 All Rights Reserved.
"""


import hashlib
from io import BytesIO
import re

from nmb.NetBIOS import NetBIOS

from smb.SMBConnection import SMBConnection

import bernhard

import config
import model



SMB_IGNORE_RE = [re.compile("\.\."),
                 re.compile("\."),
                 re.compile(".*DS_Store")]
smb_share_format = "//{0}/{1}/{2}"

try:
    riemann = bernhard.Client(host=config.RIEMANN_HOST, port=config.RIEMANN_PORT)
except:
    pass


class RemoteNameException(Exception):
    """
    NetBIOS is unable to find a remote SMB location.
    """
    pass


class SMBConnectionException(Exception):
    """
    Unable to create an SMB connection.
    """
    pass


class SMBFetchFileException(Exception):
    """
    Unable to store or retrieve the file using a SMB connection.
    """
    pass


class ChecksumFailed(Exception):
    """
    The checksum for the data provided by the model failed.
    """
    pass


def get_connection(location):
    """
    Get a SMB connnection using the location and verify the remote
    location.

    Get the formatted location name, otherwise throw a
    RemoteNameException. Create the SMB connection, otherwise throw a
    SMBConnectionException.
    """
    location_name = smb_share_format.format(location.server_ip,
                                            location.share_name,
                                            location.path)
    netbios = NetBIOS()
    remote_name = netbios.queryIPForName(location.server_ip)
    if not remote_name:
        raise RemoteNameException("Unable to get remote name for {0}!".
                                  format(location.server_ip))
    if not location.username:
        location.username=""
    if not location.password:
        location.password=""
    connection = SMBConnection(location.username, location.password, 'ONYX',
        remote_name[0])
    if not connection.connect(location.server_ip):
        riemann.send({"host": config.HOST,
                      "service": "shareutil.get_connection",
                      "state": "start"})
        raise SMBConnectionException("Unable to connect to {0}".
                                     format(location_name))
    return connection


def write_data_to_share(location, file_name, data):
    """
    Write data to a file at a SMB location.

    Get a connection to the location. Create a BytesIO python object using
    data. Create the new SMB path using location and file_name. Write
    the data to the file at the SMB location, otherwise throw a
    SMBFetchFileException.
    """
    connection = get_connection(location)

    fileobj = BytesIO(data)
    path = "\\".join([location.path, file_name])
    len_written = connection.storeFile(location.share_name,
                                       path, fileobj)
    if len_written == 0:
        
        raise SMBFetchFileException("Unable to write file {0} to {1}".
                                    format(file_name, location_name))


def delete_existing_file(location, file_name):
    """
    Delete a file at a SMB location.

    Get a connection to the location. Delete the file at the SMB
    location.
    """
    connection = get_connection(location)

    path = "\\".join([location.path, file_name])
    connection.deleteFiles(location.share_name, path)


def data_for_file_on_share(location, file_name):
    """
    Get data from a file at a SMB location.

    Get a connection to the location. Get the data from the file at
    the SMB location, otherwise throw a SMBFetchFileException.
    Returns a str (bytearray).
    """
    connection = get_connection(location)

    fileobj = BytesIO()
    path = "\\".join([location.path, file_name])
    attr, lenwritten = connection.retrieveFile(location.share_name,
                                               path, fileobj)
    if lenwritten == 0:
        raise SMBFetchFileException("Unable to fetch file {0} from {1}".
                                    format(file_name, location_name))
    return fileobj.getvalue()


def data_for_measurement_file(measurement_file):
    """
    Get the SMB Location and file name from the measurement_file and
    call the data_for_file_on_share method.

    Returns a str (bytearray).
    """
    location = measurement_file.watch.measurement_location
    return data_for_file_on_share(location, measurement_file.file_name)


def smb_ignored(file_name):
    """
    If the the file name matches the SMB_IGNORE_RE regex then
    return True otherwise return False.
    """
    for ignore in SMB_IGNORE_RE:
        if ignore.match(file_name) is not None:
            return True
    return False


def file_names_in_location(location):
    """
    Return the file names at a SMB location.

    Returns a list of smb.base.SharedFiles.
    """
    connection = get_connection(location)

    shared_files = connection.listPath(location.share_name,
                                       location.path)
    file_names = [f.filename for f in shared_files
                  if not smb_ignored(f.filename)]
    return file_names


class OnyxFileNotFoundException(Exception):
    """
    Onyx file could not be found in SMB locations.
    """
    pass


def get_checksum(data):
    """
    The sha1 checksum of data.
    """
    return hashlib.sha1(data).hexdigest()


def set_checksum(db, job):
    """
    Set the sha1 checksum of the job design file data.
    """
    data = data_for_design_file(db, job.onyx_file)
    job.onyx_file_checksum = get_checksum(data)


def data_for_design_file(db, onyx_file_name, checksum=None):
    """
    Return data for a Onyx design file.

    Query the database to get design locations. In each directory check
    for the design file. If it's found then break and use that location
    to get the data, otherwise throw an OnyxFileNotFoundException. If
    a checksum is provided then validate using the checksum. Return
    the data.
    """
    design_dirs = db.query(model.DesignLocation).all()
    design_location = None
    design = None
    for dir in design_dirs:
        location = dir.location
        if onyx_file_name in file_names_in_location(location):
            design = dir
            design_location = location            
            break
    if not design_location:
        raise OnyxFileNotFoundException(
            "Could not find design {0}"
            " in search locations".format(onyx_file_name))
    data = data_for_file_on_share(location, onyx_file_name)
    if checksum and get_checksum(data) != checksum:
        raise ChecksumFailed("Checksum failed for %s in %s" % (onyx_file_name,
                                                               location))
    return data
