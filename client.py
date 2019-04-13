# !/usr/bin/env python
import sys
import socket
import select

SUCCESS = 0
FAILURE = -1
HOST = '127.0.0.1'
PORT = 50007
BUFSIZE = 1024

def CheckArgv():
  if(len(sys.argv) != 2):
    print('argv error')
    return FAILURE

if __name__ == '__main__':

    if (CheckArgv() == FAILURE):
      sys.exit(FAILURE)
    try:
      msg = sys.argv[1]
      cli_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      cli_sock.connect((HOST,PORT))

      cli_sock.sendall(msg.encode())
      cli_sock.settimeout(10)
      data = cli_sock.recv(BUFSIZE)
      print('RECEIVED',repr(data))

    finally:
      if (int.from_bytes(cli_sock, 'little') > 0):
        for cli_sock in readfds:
          cli_sock.close()

