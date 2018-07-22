# Copyright (C) 2018 Garrett Fifer
#
# File containing collection of python functions written to deal with the backend 
# networking protocols by making use of the python socket package.
#
# Begin networking.py

import socket as sckt
import re

# Create lan socket variable. AF_INET refers to the IPV4 address protocol 
# while SOCK_STREAM specifies to creates a TCP-based connection between the client and server.
def create_socket():
  lan_socket = sckt.socket(sckt.AF_INET, sckt.SOCK_STRAM)


# Prompts the user to input the IP address associated with the recieving file backup server.
# Checks to ensure user-inputed IP address is valid.
def server_address_prompt():
  # Prompts user for back-up server IP address
  server_ip = input('Backup server IP address: ')
  
  # Ensures that the string inputted follows the IPv4 format before continuing.
  # Returns true if the input is of the correct format and False if the input
  # does not match the specified format.
  check_input = re.match('^[0-9]{3}.[0-9]{3}.[0-9]{3}.[0-9]{3}$', server_ip)
  
  # If check_input returns True, then have the immediately have 
  # the function return the properly formatted user-inputted IP address.
  if check_input is True:
    return server_ip
  else:
    # For inputs returning False, the user is alerted of their improper input and given unlimited attempts
    # to input a correctly formatted IP address. Once the input check returns True, the loop breaks and the
    # script continues as normal.
    while check_input is False:
      print('Invalid IP address format. Please re-check IP and try again.')
      server_ip = input('Backup server IP address: ')
      if check_input is True:
        return server_ip
