# Copyright (C) 2018 Garrett Fifer
#
# This file contains the functions needed to provide to main python file with the ability
# create and write ISO image files in order to provide an easy container for backed-up files.
#
# Begin diskimager.py


try:
  from cStringIO import StringIO as BytesIO
except ImportError:
  from io import BytesIO
  
import pycdlib

def create_iso_image():
  """ Creates instance of pycdlib and initializes new iso object in system RAM. """
  backup_iso = pycdlib.PyCdlib()
  iso.new()

def add_iso_dir():
  """ Allows user to specify a specific directory containing a group of files in
  which will be eventually written to the created iso file. """
  dir_path = input('Path to directory with files you wish to backup to server: ')
  iso.add_directory(dir_path)
  
def write_iso():
  """ Writes the ISO to the hard disk before sending over the network to recieving backup server. """
  iso_filename = input('Name your new backup file: ')
  iso.write(iso_filename)
