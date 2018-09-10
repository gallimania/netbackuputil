# Copyright (C) 2018 Illogical Mathmatical Hypothetical Numerical Lyrical Crew
#
# File containing collection of python functions written to deal with the backend 
# networking protocols by making use of the python socket package.
#
# Begin networking.py

import socket as s, random as r, datetime as dt
import re


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
      

# For more portability, I figured an object-oriented approach for our server/client implementations would be better
# Because of this I created a base connection class that lays the ground work for either connection
class Connection(object):
    # it is assumed that the address and port have been verified before, so we initialize the connection and bind our
    # socket when we initialize it. We don't go a step further we just create the descriptor so that the connection
    # base class can be used for all types of connections
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.socket = s.socket()

        # if for some reason our socket is already in use, we pick a random unassigned port to connect to instead.
        # we print the port used instead of the given one back to the user instead of throwing the exception and
        # making the user start again from scratch
        try:
            self.socket.bind((address, port))
        except s.error:
            self.port = r.randint(8675, 65535)
            self.socket.bind((address, port))
            printf("Could not use port requested, using port {d} instead", self.port)

    # for equality, all that matters is the socket file descriptor
    def __eq__(self, other):
        return self.socket == other.socket

    # if someone wants to print the string version of their connection, we give them some info about what the connection
    # is doing
    def __str__(self):
        if self.address == "127.0.0.1":
            return "Connection on local host on port " + str(self.port)
        else:
            return "attempting to connect to a server at " + str(self.address) + " on port" + str(self.port)

    # because the other attributes are passed in by the user, this is really the only getter we need
    def get_socket(self):
        return self.socket

    # the default type for our socket is AF_INET and SOCK_STREAM, but if a user wants a different kind of connection,
    # this function allows them to change to whatever type they want, and rebinds it. If an invalid type, it raises an
    # InvalidSocketType exception. arguments are passed like the regular socket creation function.
    def change_socket_type(self, af_vers, sock_type):
        af_versions = [s.AF_UNIX, s.AF_INET, s.AF_INET6]
        socket_types = [s.SOCK_STREAM, s.SOCK_DGRAM, s.SOCK_RAW, s.SOCK_RDM, s.SOCK_SEQPACKET]

        if not(af_vers in af_versions) or not(sock_type in socket_types):
            raise InvalidSocketType("Not a defined socket type in the python socket library")
        # close the old socket so it isn't left hanging there unused
        self.socket.close()
        self.socket = s.socket(af_vers, sock_type)
        self.socket.bind((self.address, self.port))


# now we have our specific implementation of the netbackuputil server
class Server(Connection):

    # A server is obviously bound to a local port, and has one socket for listening for connections,
    # and binds a separate socket for data transmission with clients that connect to it
    def __init__(self, port):
        Connection.__init__("127.0.0.1", port)
        self.data_socket = None

    # we only need one more getter for this object
    def get_data_socket(self):
        return self.data_socket

    # We now wait for a client to connnect to us and set the data_socket to the socketfd returned from accepting the
    # client connection, queue length is how many the server will allow, exceeding this number will mean new connections
    # are rejected. If none, a number will be selected by the operating system
    def connect_to_client(self, queue_length=None):
        if queue_length:
            self.socket.listen(queue_length)
        else:
            self.socket.listen()

        self.data_socket = self.socket.accept()

    # for run_server, you set the size (in bytes) of how much you want to receive at a time from the client,
    # this is the max amount allowed. First the client sends the filename, then the raw data, and we save it to the
    # output file
    def run_server(self, rec_size):
        if not self.data_socket:
            raise ValueError("Data transfer socket not initialized, please run connect_to_client()")

        raw_data = self.data_socket.recv(rec_size)
        if not raw_data:
            return None
        # if '.' is in the filename, we are dealing with a file, otherwise we are dealing with a directory so we write
        # to an ISO image
        if "." in raw_data:
            outfile = open(raw_data, 'a')
            filename = raw_data
        else:
            outfile = open(str(dt.date.today()) + ".iso", 'a')
            filename = str(dt.date.today()) + ".iso"
        # as long as the client doesn't send and empty bit of data we can keep receiving and writing
        while raw_data:
            raw_data = self.data_socket.recv(rec_size)
            outfile.write(raw_data)
        return filename

    # when we are done with the server, we close the data connection, allowing for future connections so that the server
    # object can be run continuously
    def end_server(self):
        self.data_socket.close()
        self.data_socket = None


# The client is a bit more simple, since all we are doing is sending data
class Client(Connection):

    # the client version goes ahead and completes the connection to the server if everything goes well.
    # will return a Null object if connection cannot be created
    def __init__(self, address, port, timeout=100):
        Connection.__init__(address, port)
        self.socket = s.create_connection((self.address, timeout, self.port))
        if not self.socket:
            return None

    # here we send the filepath and then all of our data. Once we are done, we send an empty string which tells the
    # server that all data has been sent
    def run_client(self, path):
        if "." in path:
            self.socket.send(path.split("/")[-1])
        else:
            self.socket.send(path)

        file = open(path, 'r')

        for line in file.readlines():
            self.socket.send(line)
        self.socket.send("")

    # we don't want to hog then socket when we are done.
    def close_client(self):
        self.socket.close()
