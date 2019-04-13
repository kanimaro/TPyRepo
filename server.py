#!/usr/bin python
# -*- coding: utf-8 -*-
import re
import sys
import datetime
import smtplib
import socket
import threading
import requests
import select
#from module_name import class_name
import setting

from time import sleep
from email.mime.text import MIMEText
from email.utils import formatdate
from logging import getLogger, StreamHandler, DEBUG
from logging.handlers import SMTPHandler

#ここからは暗号系
import base64
import random
from Crypto.Cipher import AES
import hashlib

#ロガーの設定
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

#定義
SUCCESS = 0
FAILURE = -1
#ソケットの情報
HOST = '127.0.0.1'
PORT = 50007
BACKLOG = 5
BUFSIZE = 1024

class CheckClass:
  def CheckArgv(self):
    if (len(sys.argv) != 2):
      print('argv error usage: python argv[1] ')
      return FAILURE
  
    return SUCCESS

def CreateMsg(from_addr, to_addr, subject, body):
  msg = MIMEText(body)
  msg['Subject'] = subject
  msg['From'] = from_addr
  msg['To'] = to_addr
  msg['Date'] = formatdate()

  return msg

def JudgeHttp():

  url = 'https://google.com'
  try:
    res = requests.get(url)
  except requests.exceptions.RequestException as err:
    logger.debug(err)
    return FAILURE

  logger.debug(res)
  return SUCCESS

def SendMsg(from_addr, to_addr, msg):
  server = smtplib.SMTP('smtp.nifty.com',  587)
  server.ehlo
#  smtpobj.starttls()
  server.login(from_addr, setting.MY_PASS)
  server.sendmail(from_addr, to_addr, msg.as_string())
  server.quit()

def KnowTime():
  dt_start = datetime.datetime(2018, 2, 1, 0,0,0,0)
  dt_end = datetime.datetime(2018, 10, 1, 0,0,0,0)
  print(dt_end - dt_start)
  return SUCCESS

def HashStr(str):
  str = str.encode()
  hashedstr = hashlib.sha256(str).hexdigest()
  print(hashedstr)

  return hashedstr

def Uranai(str):
    hashedstr = HashStr(str)

    fortunekey = int(hashedstr[0:2], 16)
    print('fortunekey:%d' % fortunekey)
    if fortunekey <= 200 and fortunekey > 150:
      print('大吉')
    elif fortunekey <= 150 and fortunekey > 120:
      print('中吉')
    elif fortunekey <= 120 and fortunekey > 90:
      print('小吉')
    elif fortunekey <= 90 and fortunekey > 60:
      print('末吉')
    else: 
      print('凶')

def Worker(num):
    #for i in range(5):
    logger.debug('Worker%s' % num)
def RemoveConnection(conn, addr, clients):
    conn.close()
    clients.remove((conn,addr))
    

def Handler(conn, addr, server_sock, clients):
    while True:
      try:
        msg = conn.recv(BUFSIZE)
        if not msg:
          RemoveConnection(conn,addr, clients)
          break
        else:
          logger.debug(msg)
          for client in clients:
            client[0].sendto(msg, client[1])
      except ConnectionResetError:
        RemoveConnection(conn,addr, clients)
        break

        

if __name__ == '__main__':
    checkclass = CheckClass()
    if (checkclass.CheckArgv() == FAILURE):
      sys.exit(FAILURE)
    str = sys.argv[1]

    httpflg = False
    
    if JudgeHttp() == SUCCESS:
      httpflg = True

    if httpflg == True:
      from_addr = setting.FROM_ADDR
      to_addr = setting.TO_ADDR
      subject = setting.SUBJECT
      body = setting.BODY

      msg = CreateMsg(from_addr, to_addr, subject, body)
      SendMsg(from_addr, to_addr, msg)

    #Uranai(str)

    threadsarray = []

    for i in range(5):
      t1 = threading.Thread(target=Worker, args=(i, ), daemon=True)
#    t2 = threading.Thread(target=Worker2)
      t1.start()
      threadsarray.append(t1)
      sleep(1)
 #   t2.start()
    for t1 in threadsarray:
      t1.join()
   # under here, socket progtamming
    
    clients = []
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    readfds = set([server_sock])
    try:
      server_sock.bind((HOST, PORT))
      server_sock.listen(BACKLOG)
      
      while True:
        timeout = 15
        rready, wready, xready = select.select(readfds, [], [], timeout)
        if len(rready) == 0:
          logger.debug('TIMEOUT')
  #        server_sock.close()
          break;
        for sock in rready:
          if sock is server_sock:
            try:
              (conn,  addr) = server_sock.accept()
              readfds.add(conn)
              logger.debug('Connected by', addr)
            except KeyboardInterrupt:
              server_sock.close()
              break;

            clients.append((conn,addr))
            thread = threading.Thread(target=Handler, args=(conn, addr, server_sock, clients), daemon=True)
            thread.start()
            thread.join()
            break;
          else:
            msg = sock.recv(BUFSIZE)
            if not msg:
              sock.close()
              readfds.remove(sock)
              break
            else:
              logger.debug(msg)
              sock.send(msg)
    finally:
      for sock in readfds:
        sock.close()

